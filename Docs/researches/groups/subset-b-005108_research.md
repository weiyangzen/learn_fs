# Research Report: subset-b-005108

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzg2l.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzg2l.c

## Purpose

`pinctrl-rzg2l.c` is the pin control, pin configuration, GPIO, interrupt, and suspend/resume driver for the Renesas RZ/G2L-family pin controller block. Despite the filename, it also covers multiple related SoCs through match data: RZ/G2L (`r9a07g044`), RZ/G2UL/RZ/Five (`r9a07g043` plus RISC-V-only variable pin data), RZ/G3S (`r9a08g045`), RZ/G3E (`r9a09g047`), and RZ/V2H(P) variants (`r9a09g056`, `r9a09g057`). The driver registers a Linux pinctrl device, a GPIO chip, and a hierarchical GPIO IRQ domain backed by the SoC's parent interrupt controller.

The file is data-driven. Port pins and dedicated pins are described with packed `u64` capability words that encode valid pin bitmaps, register offsets, dedicated-pin indexes, and supported per-pin features. Runtime behavior is selected by `struct rzg2l_pinctrl_data` and `struct rzg2l_hwcfg`, which define SoC register offsets, drive-strength tables, function-number base adjustments, output-enable semantics, power-source support, custom RZ/V2H pinconf properties, and helper callbacks.

## Important APIs, Types, And Functions

The primary private state is `struct rzg2l_pinctrl`: it owns the pinctrl descriptor, generated pin descriptors, device base address, clock, GPIO chip/range, hierarchical IRQ slot bitmap, `hwirq[]` child-to-parent mapping table, raw register lock, DT mapping mutex, software pin settings, register caches, and wakeup-path count. `struct rzg2l_pinctrl_data` binds static SoC data to callbacks such as `pwpr_pfc_lock_unlock`, `pmc_writeb`, `pin_to_oen_bit`, `hw_to_bias_param`, and `bias_param_to_hw`. `struct rzg2l_pinctrl_pin_settings` persists software-visible power-source and microamp drive-strength choices for pins where the hardware cannot report all requested state directly.

Packed descriptor macros are central: `RZG2L_GPIO_PORT_PACK`, `RZG2L_GPIO_PORT_SPARSE_PACK`, `RZG2L_GPIO_PORT_PACK_VARIABLE`, `RZG2L_SINGLE_PIN_PACK`, and `RZG2L_VARIABLE_PIN_CFG_PACK` populate the SoC tables. `RZG2L_PIN_CFG_TO_PORT_OFFSET` hides the difference between port pins and dedicated pins when calculating register offsets.

The pinctrl integration uses generic pinctrl/pinmux helpers. `rzg2l_dt_node_to_map()` and `rzg2l_dt_subnode_to_map()` parse `pinmux` and `pins` DT properties, allocate mux/config maps, and dynamically register one generic pin group and one generic function per DT mux node. `rzg2l_pinctrl_set_mux()` retrieves the generated group/function data and calls `rzg2l_pinctrl_set_pfc_mode()` for each pin. Pin configuration is handled by `rzg2l_pinctrl_pinconf_get()`, `rzg2l_pinctrl_pinconf_set()`, and group wrappers.

GPIO integration is provided by `rzg2l_gpio_request()`, direction/get/set/free callbacks, and `rzg2l_gpio_register()`. IRQ integration is implemented by `rzg2l_gpio_child_to_parent_hwirq()`, `rzg2l_gpio_irq_enable()/disable()`, `rzg2l_gpio_irq_domain_free()`, `rzg2l_init_irq_valid_mask()`, and `rzg2l_gpio_irq_restore()`. Probe and registration flow is in `rzg2l_pinctrl_probe()`, `rzg2l_pinctrl_register()`, and `rzg2l_gpio_register()`.

## Control Flow

Probe allocates `struct rzg2l_pinctrl`, loads match data, maps the MMIO resource, enables the clock, initializes locks and wakeup accounting, then calls `rzg2l_pinctrl_register()`. Registration builds the pin descriptor table by walking all port pins and dedicated pins, attaches per-pin packed capability data as `drv_data`, resolves variable per-pin capability overrides, initializes software power-source defaults when microamp drive strength is enabled, allocates suspend/resume caches, registers/enables the pinctrl device, and finally registers the GPIO chip.

DT mapping accepts either a `pinmux` list or a `pins` string list, but not both in one node. `pinmux` nodes become a mux map, optionally accompanied by a group config map. `pins` nodes are config-only maps per named pin and require at least one parsed generic config. The mux path stores pin IDs and PSEL values in dynamically allocated arrays, registers a generated group and function under a derived node name, and later `set_mux` programs the hardware.

Mux programming validates each pin against the encoded port bitmap and register offset. `rzg2l_pinctrl_set_pfc_mode()` then moves the pin through a hardware-safe sequence: force non-use/Hi-Z in `PM`, unlock write-protected PFC/PMC access, clear `PMC` to temporary GPIO mode, update the `PFC` function field, set `PMC` back to peripheral mode, and relock PWPR. RZ/V2H-family variants use different PWPR semantics and `rzv2h_pmc_writeb()`.

Pinconf get/set first resolves the packed capability word and register bit position, including dedicated-pin encoding. Each generic property is accepted only if its capability bit is present. Supported properties include input-enable, output-enable, power-source, slew-rate, bias, drive strength in mA or uA, output impedance, open-drain/push-pull, Schmitt input, and the custom `renesas,output-impedance`. Power-source and drive-strength-uA are applied as a pair after all requested configs are parsed so the driver can validate the final power-source/drive-strength tuple against SoC tables before writing `IOLH`.

GPIO request validates the pin, asks pinctrl core for the line, and switches the pin to GPIO mode by clearing `PMC`. Direction writes update `PM`, output writes update `P`, and reads choose `PIN` or `P` depending on configured direction. Free releases the pinctrl GPIO request, disposes an IRQ mapping if present, and puts the line back into input mode.

For GPIO IRQs, child lines are translated to a compact GPIO interrupt index based on valid pins in earlier ports, then a free TINT slot is allocated from `tint_slot`. The parent hardware IRQ is encoded by `RZG2L_PACK_HWIRQ(gpioint, tint_irq)` and presented as level-high to the parent domain. Enable toggles the pin's `ISEL` bit and enables the parent IRQ. Free disables ISEL, frees the GPIO line, releases the TINT slot, and clears `hwirq[]`.

Suspend caches port and dedicated-pin registers, voltage/power-source registers, QSPI, and OEN. If no IRQ wakeup path is active, it disables the clock; otherwise it marks the device as a wakeup path. Resume re-enables the clock as needed, restores QSPI/OEN and voltage registers, restores PFC using the documented GPIO/PFC/PMC sequence, restores port and dedicated-pin config registers, and replays IRQ type/enable state.

## State And Persistence

Hardware state lives in MMIO registers: `P`, `PM`, `PMC`, `PFC`, `PIN`, `IOLH`, `SR`, `IEN`, `PUPD`, `ISEL`, `NOD`, `SMT`, SD/ETH/QSPI power registers, OEN, and PWPR. Software state includes generated pin descriptors, `settings[]` for power-source and drive-strength-uA, `tint_slot` and `hwirq[]` for hierarchical IRQ allocation, `wakeup_path`, and suspend caches. All device-managed allocations are tied to the platform device lifetime.

Register writes are protected by `raw_spinlock_t lock` where updates can race with GPIO, pinconf, IRQ, or PM paths. Generic group/function creation is serialized by `mutex`. TINT slot allocation uses a separate spinlock. The driver does not persist state across reboot; persistence only spans system suspend/resume through the cache arrays.

## Dependencies And Integration Points

The driver depends on Linux pinctrl, pinmux, pinconf-generic, gpiolib, hierarchical IRQ domains, OF/DT parsing, platform devices, clocks, and MMIO helpers. It consumes Renesas DT binding constants from `dt-bindings/pinctrl/rzg2l-pinctrl.h`, `renesas,r9a09g047-pinctrl.h`, and `renesas,r9a09g057-pinctrl.h`. The DT binding must provide compatible strings, MMIO resource, clock, `gpio-ranges`, a parent interrupt controller, and pinctrl state nodes using the expected `pinmux`/`pins` conventions.

The driver registers at `core_initcall`, suppresses bind attributes, and exports no symbols. It integrates with the parent interrupt controller through `of_irq_find_parent()` and `irq_find_host()`, and with GPIO consumers through `devm_gpiochip_add_data()`.

## Risks

The packed capability encoding is dense and SoC-table mistakes can silently map a valid Linux pin to the wrong register offset or unsupported capability. Variable pin configuration adds another failure mode: a missing override yields zero, which causes later validation failures. The suspend/resume cache path is complex and hardware-order sensitive; mistakes can leave pins in the wrong mux mode or restore stale IRQ state. TINT allocation supports only 32 interrupt slots and can return `-ENOSPC` even when many GPIO lines exist. GPIO free disposes any IRQ mapping on the line, so ownership assumptions between GPIO and IRQ users must match gpiolib expectations. Power-source and drive-strength-uA validation depends on accurate voltage tables and software `settings[]`; applying drive strength before power-source in DT still works only because set defers the final write until after parsing.

## Test Signals

Useful signals include boot-time probe messages, pinctrl DT state application for each compatible SoC, `gpioinfo`/GPIO direction and value tests, hierarchical GPIO IRQ request/free/retrigger tests, wake-capable GPIO IRQ suspend/resume, and pinconf round-trip tests for supported and unsupported properties. Edge cases should cover invalid `gpio-ranges`, `pinmux` nodes that also contain `pins`, unsupported pins in sparse ports, variable-config pins, RZ/V2H custom output-impedance config, OEN pins, and TINT exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzg2l.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzn1.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzn1.c

## Purpose

`pinctrl-rzn1.c` implements the pinctrl and pinconf driver for Renesas RZ/N1 SoCs. The hardware has 170 configurable `PL_GPIO` pins and a multi-level mux model. Level 1 functions are encoded directly in each pin's level-1 config register; selecting level-2 muxing is represented by level-1 function `0xf` and a separate level-2 register. A third logical level selects MDIO sources for two MDIO channels and two MDIO-related level-2 functions. The driver exposes this as a normal Linux pinctrl device whose functions and groups are built entirely from device tree children.

## Important APIs, Types, And Functions

`struct rzn1_pinctrl_regs` models both level-1 and level-2 register banks: 170 per-pin `conf[]` words, a `status_protect` write-protect register at offset `0x400`, and two level-2 MDIO mux registers. `struct rzn1_pinctrl` stores the device, clock, pinctrl handle, mapped level-1/level-2 banks, physical addresses used by the write-protect protocol, current MDIO selections, and dynamically parsed function/group tables.

`rzn1_hw_set_lock()` implements the unusual lock protocol, writing the physical address of `status_protect` to itself, with bit 0 controlling unlock. `rzn1_set_hw_pin_func()` is the core mux writer. It recognizes compound MDIO function IDs from the DT binding, translates them into level-2 function numbers plus an MDIO source write, validates pin/function ranges, and updates level-1 and level-2 registers. `rzn1_set_mux()` wraps group programming by unlocking both levels, applying every pin's mux ID, then relocking.

Group and function discovery is device-tree-driven. `rzn1_pinctrl_parse_functions()` and `rzn1_pinctrl_parse_groups()` allocate arrays with `devm_kmalloc_array()`, parse `pinmux` cells into pin numbers and 7-bit function IDs, and assign group names and owning function names from DT node names. Runtime pinctrl ops are implemented by `rzn1_get_groups_count()`, `rzn1_get_group_name()`, `rzn1_get_group_pins()`, `rzn1_pmx_get_*()`, and `rzn1_dt_node_to_map()`.

Pin configuration support is in `rzn1_pinconf_get()`, `rzn1_pinconf_set()`, and group wrappers. Supported generic configs are pull-up, pull-down, bias-disable, drive-strength in mA, and high-impedance.

## Control Flow

Probe allocates state, initializes MDIO selections to `-1`, maps two MMIO resources for level 1 and level 2, calculates both write-protect physical addresses, enables the clock, assigns the descriptor name, parses DT functions/groups, registers/enables pinctrl, and leaves the clock enabled until remove. The driver does not register a GPIO chip; pin names are provided as pinctrl descriptors only.

DT parsing treats each direct child of the controller as a function. A function may contain a `pinmux` property directly, child groups with `pinmux`, or both. Each `pinmux` cell encodes the low 8 bits as the pin number and bits `[14:8]` as the mux/function selector. `rzn1_dt_node_to_map()` creates mux maps by looking up group names already parsed from DT and optionally attaches generic config maps to each group. Applying a state calls `rzn1_set_mux()` for the group and then pinconf group operations if present.

Pinconf get reads level-1 config bits for pull and drive strength, optionally level-2 config for high-impedance. Set modifies only the level-1 register bits it owns and unlocks level 1 around the write. High-impedance is represented as level-1 function `RZN1_FUNC_HIGHZ`.

## State And Persistence

Persistent runtime state is limited to hardware registers, parsed DT metadata, clock state, and software MDIO conflict tracking. `mdio_func[2]` records the selected source per MDIO channel and warns on conflicting settings, but the later write still occurs. There is no suspend/resume cache and no explicit register lock other than hardware write-protect. The comments state that `rzn1_set_hw_pin_func()` assumes serialization by callers; pinctrl core state application is expected to provide that serialization.

## Dependencies And Integration Points

The driver depends on `dt-bindings/pinctrl/rzn1-pinctrl.h` for compound function ID constants, platform MMIO resources for two banks, a clock, and OF child nodes describing all functions/groups. It integrates with pinctrl generic maps through `pinctrl-utils` helpers and with pinconf-generic parsing. It registers as compatible `renesas,rzn1-pinctrl` using `subsys_initcall`.

## Risks

Because all mux topology comes from DT, malformed group names, missing `pinmux`, or wrong pin/function cell encoding can make the driver register incomplete or incorrect functions. There is no spinlock around pinconf and mux writes beyond the hardware lock protocol; concurrent calls outside pinctrl's normal serialization would race. MDIO conflicts produce warnings instead of hard failure. Function ID range checks prevent values past the MDIO compound range, but DT can still request legal IDs that are electrically invalid for a board. Clock disable only occurs on remove or probe failure; no system PM handling is present.

## Test Signals

Test with representative DT nodes covering direct-function groups and child group nodes, level-1 functions, level-2 functions, MDIO compound functions, high-impedance, each pull mode, and drive strengths 4/6/8/12 mA. Negative tests should include missing `pinmux`, empty `pinmux`, unknown group names in pinctrl states, invalid pin numbers, unsupported drive strength, and conflicting MDIO selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzn1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzt2h.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzt2h.c

## Purpose

`pinctrl-rzt2h.c` is the pinctrl, GPIO, pinconf, and optional GPIO IRQ driver for Renesas RZ/T2H and RZ/N2H-family SoCs. It is based on the RZ/G2L driver but adapted for a different register layout, 64-bit PFC/DRCTL registers, optional safety-region ports, and a fixed GPIO-to-parent-IRQ mapping table. It supports compatibles `renesas,r9a09g077-pinctrl` and `renesas,r9a09g087-pinctrl`.

## Important APIs, Types, And Functions

`struct rzt2h_pinctrl_data` supplies the number of pins, per-port valid-pin bitmasks, and port count. `struct rzt2h_pinctrl` owns pinctrl and GPIO descriptors, two optional MMIO bases (`base0` normal/security and `base1` safety), a bitmap of used parent IRQs, register lock, DT group/function mutex, safety-port flag, and wakeup-path counter.

The register helpers `RZT2H_GET_BASE()` and generated `rzt2h_pinctrl_read/write{b,w,q}()` route accesses to the correct MMIO base based on port number. `rzt2h_validate_pin()` rejects out-of-range pins, disabled safety ports, and pins absent from the SoC bitmask. `rzt2h_pinctrl_set_pfc_mode()` performs safe mux switching by forcing Hi-Z, enabling GPIO temporarily through `PMC`, writing the 8-bit function field in `PFC`, and returning the pin to peripheral mode.

Pinconf support uses the `DRCTL` register. `rzt2h_pinctrl_pinconf_get()` and `_set()` support slew-rate, bias-disable/pull-up/pull-down, Schmitt input, and drive-strength-uA using the fixed table `{2500, 5000, 9000, 11800}`. GPIO callbacks implement request/free, direction, value get/set, and mode switching. IRQ support is provided by `rzt2h_gpio_irq_map`, `rzt2h_gpio_child_to_parent_hwirq()`, `rzt2h_gpio_irq_domain_free()`, and parent-forwarding irqchip callbacks.

## Control Flow

Probe allocates state, loads match data, maps the required `nsr` region, optionally maps the `srs` region, selects safety region `0x812c0xxx` by clearing `RSELP` for safety ports when `srs` is present, initializes locks, and registers pinctrl plus GPIO. Registration builds one pin descriptor per possible GPIO name, registers/enables pinctrl, then registers a GPIO chip after validating `gpio-ranges`.

DT mapping is similar to the RZ/G2L pattern: a node contains either `pinmux` cells or a `pins` string list. `pinmux` cells encode a pin ID and an 8-bit function. The parser dynamically creates one generic group and one generic function per mux node and optionally adds a config map. `pins` nodes are config-only and require at least one generic pinconf property.

Mux set validates every requested pin and writes the PFC sequence. GPIO request also validates and switches the line to GPIO mode. Direction writes update two-bit `PM` fields; output writes update `P`; input reads come from `PIN`, output reads from `P`. `get_direction()` has special handling for interrupt function mode because an IRQ line is not in GPIO mode but must still report as input to gpiolib.

IRQ translation is optional and enabled only if the DT node has `interrupt-controller`. Child lines index into `rzt2h_gpio_irq_map`; invalid entries and parent IRQs below `RZT2H_INTERRUPTS_START` are rejected. A parent IRQ can be used by only one child at a time through `used_irqs`. The child is muxed to `PFC_FUNC_INTERRUPT`, parent type is inherited from the child request, and wake enable increments `wakeup_path`. Domain free clears the used bit and disables GPIO mode for the pin.

## State And Persistence

The driver persists no state across reboot and has minimal system PM handling. Hardware state lives in `P`, `PM`, `PMC`, `PFC`, `PIN`, `DRCTL`, and `RSELP`. Runtime state includes the generated pinctrl structures, `used_irqs`, `safety_port_enabled`, and `wakeup_path`. `rzt2h_pinctrl_suspend_noirq()` only marks the device as a wakeup path when needed; unlike RZ/G2L it does not cache and restore registers.

## Dependencies And Integration Points

The driver depends on pinctrl, gpiolib, hierarchical IRQ domain helpers, OF matching, platform resources named `nsr` and optional `srs`, and `dt-bindings/pinctrl/renesas,r9a09g077-pinctrl.h`. It expects a correct `gpio-ranges` tuple and a parent interrupt domain when IRQ support is enabled. It registers at `core_initcall` and suppresses bind attributes.

## Risks

The optional safety-region split means the same logical port can be invalid if `srs` is absent; board DT must match available hardware. `rzt2h_gpio_irq_domain_free()` computes the used IRQ bit from the child hwirq, while allocation sets it from the parent IRQ number; this deserves close review because child offsets and parent IRQ IDs are different namespaces. The fixed IRQ map has many zero entries and shared parent IRQs, making off-by-one or reuse bugs high impact. Lack of full suspend/resume restore means firmware or low-power states that reset PFC/GPIO registers may lose pin state.

## Test Signals

Exercise probe with and without `srs`, mux states on safety and non-safety ports, config-only `pins` nodes, invalid sparse pins for `r9a09g087`, GPIO direction/value operations, IRQ allocation conflicts for shared parent IRQs, IRQ free/reallocate, wake-enabled IRQ suspend, and DT validation failures for mismatched `gpio-ranges`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzt2h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzv2m.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzv2m.c

## Purpose

`pinctrl-rzv2m.c` implements pinctrl, pinconf, and GPIO support for Renesas RZ/V2M (`renesas,r9a09g011-pinctrl`). It is derived from the RZ/G2L style but uses RZ/V2M-specific registers with write-enable bits in the upper word, 16-pin ports, a dedicated-pin pseudo-port, and drive-strength tables selected by voltage/group capability.

## Important APIs, Types, And Functions

The key static descriptions are `rzv2m_gpio_names`, `rzv2m_gpio_configs`, and `rzv2m_dedicated_pins`. `RZV2M_GPIO_PORT_PACK()` encodes pin count, register index, and capability bits; `RZV2M_SINGLE_PIN_PACK()` encodes dedicated pins using `RZV2M_DEDICATED_PORT_IDX`. `struct rzv2m_pinctrl_data` binds these tables, and `struct rzv2m_pinctrl` stores pinctrl/GPIO descriptors, the MMIO base, device pointer, spinlock, and DT group/function mutex.

`rzv2m_writel_we()` is the critical register helper for write-enable style registers. `rzv2m_pinctrl_set_pfc_mode()` masks input/output, writes the function select field in `PFSEL`, then unmasks input/output. DT parsing and generic pinctrl integration are handled by `rzv2m_dt_node_to_map()`, `rzv2m_dt_subnode_to_map()`, and `rzv2m_pinctrl_set_mux()`. Pinconf support is in `rzv2m_pinctrl_pinconf_get()` and `_set()`, with group wrappers. GPIO support is in `rzv2m_gpio_request()`, direction/value callbacks, `rzv2m_gpio_free()`, and `rzv2m_gpio_register()`.

## Control Flow

Probe allocates state, resolves match data, maps one MMIO resource, enables the clock with `devm_clk_get_enabled()`, initializes locks, and registers pinctrl/GPIO. Registration creates descriptors for all port pins plus seven dedicated pins, stores a per-pin copy of the packed config in `drv_data`, registers/enables pinctrl, validates `gpio-ranges`, and registers a GPIO chip.

DT mapping supports either `pinmux` or config-only `pins`. `pinmux` nodes become a generated generic group/function pair. Unlike RZ/G2L, the code parses configs in mux nodes but only creates config maps for `pins`; mux-node configs are not added to `nmaps`, so only config-only pin lists apply pinconf through DT mapping. Mux set iterates generated pins/PSEL values and writes the PFC sequence without per-pin validation in the mux path.

Pinconf resolves either a dedicated-pin encoding or a port-pin encoding. Bias reads/writes two-bit `PUPD` values, where hardware values map to pull-down, pull-up, or disable. Drive-strength-uA selects one of four tables based on capability group (`1.8V group2`, `1.8V group3`, `SWIO`, or `3.3V`) and writes a two-bit `DRV` field. Slew-rate uses `SR` with write-enable semantics.

GPIO request asks pinctrl core for the line and switches function to GPIO (`func 0`). Direction uses `OE` and `IE` write-enable registers, output value uses `DO`, input value uses `DI`, and free returns the line to input.

## State And Persistence

Runtime state is device-managed and not persisted across suspend by this driver. Hardware state is in `DO`, `OE`, `IE`, `PFSEL`, `DI`, `PUPD`, `DRV`, `SR`, and mask registers. The spinlock protects read-modify-write operations for pinconf registers, but several write-enable-only writes do not need readback. There is no IRQ support and no system PM callback in this file.

## Dependencies And Integration Points

The driver depends on Linux pinctrl, pinconf-generic, gpiolib, OF platform probing, one clock, one MMIO resource, and `dt-bindings/pinctrl/rzv2m-pinctrl.h`. It expects a correct `gpio-ranges` property whose count equals `n_port_pins`. It registers at `core_initcall` as `pinctrl-rzv2m`.

## Risks

Mux path lacks the explicit port/pin capability validation used by other Renesas drivers, so incorrect DT `pinmux` cells may program unexpected PFSEL fields. DT mux-node configs appear parsed but not mapped, which can surprise board authors who put pinconf next to `pinmux`. Bit-position mutation inside `rzv2m_pinctrl_pinconf_set()` multiplies `bit` by two for bias or drive-strength; if multiple configs for the same pin are applied in one call, later configs may use the mutated bit and target the wrong field. There is no suspend/resume restore, so low-power states that reset pin registers would lose configuration.

## Test Signals

Test mux state application for representative ports, config-only `pins` nodes for bias/drive/slew, applying multiple configs in one pinconf call, GPIO direction/value paths, invalid `gpio-ranges`, dedicated-pin pinconf, and unsupported drive strengths for each capability group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzv2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl.c

## Purpose

`pinctrl.c` is the SuperH/R-Mobile/R-Car Pin Function Controller pinctrl integration layer. It adapts the common `struct sh_pfc` core and per-SoC `struct sh_pfc_soc_info` data tables into Linux pinctrl, pinmux, and pinconf operations. It does not define a specific SoC's pins; instead it consumes the tables and helper callbacks declared in `sh_pfc.h` and implemented by the SH-PFC core/SoC files.

## Important APIs, Types, And Functions

`struct sh_pfc_pinctrl` owns the pinctrl descriptor, generated `pinctrl_pin_desc` array, per-pin software config state, and back-pointer to `struct sh_pfc`. `struct sh_pfc_pin_config` tracks whether a pin is currently GPIO-enabled and the last mux mark configured for function mode. These software flags allow the pinmux ops to reject function muxing while GPIO owns a pin and to restore function mux after GPIO free.

Pinctrl group/function ops are thin accessors over `pfc->info->groups` and `pfc->info->functions`. DT mapping is implemented by `sh_pfc_dt_node_to_map()` and `sh_pfc_dt_subnode_to_map()`, which parse `function`, `groups`, `pins`, and generic pinconf properties into pinctrl maps. Muxing is implemented by `sh_pfc_func_set_mux()`, which calls `sh_pfc_config_mux()` for every group mux mark under `pfc->lock`.

GPIO handoff is handled through pinmux callbacks: `sh_pfc_gpio_request_enable()`, `sh_pfc_gpio_disable_free()`, and optionally `sh_pfc_gpio_set_direction()` when `CONFIG_PINCTRL_SH_PFC_GPIO` is enabled. Pinconf support includes bias, drive strength, and power source through `sh_pfc_pinconf_get()`, `sh_pfc_pinconf_set()`, and `sh_pfc_pinconf_group_set()`. Helper functions `rcar_pinmux_get_bias()`, `rcar_pinmux_set_bias()`, `rmobile_pinmux_get_bias()`, and `rmobile_pinmux_set_bias()` implement common SoC bias register patterns.

## Control Flow

`sh_pfc_register_pinctrl()` is called by the SH-PFC core after `struct sh_pfc` and its `info` table are ready. It allocates the wrapper, maps SoC pins into pinctrl descriptors with `sh_pfc_map_pins()`, fills the pinctrl descriptor with ops and pin arrays, registers/enables pinctrl, and returns status to the core.

For mux state application, the pinctrl core selects a function/group. `sh_pfc_func_set_mux()` takes the global PFC spinlock, checks that no group pin is currently owned as GPIO, applies each mux mark through the core's `sh_pfc_config_mux()`, and records successful mux marks in `configs[]`. GPIO request either marks the pin as GPIO-owned or, when no separate GPIO chip exists and no function mux has been set, explicitly configures the pin's enum ID as GPIO. GPIO free clears ownership and reapplies the saved mux mark if one exists.

Pinconf validation is per-pin and table-driven by `SH_PFC_PIN_CFG_*` flags. Bias get/set delegates to SoC ops, drive-strength get/set searches `drive_regs`, and power-source get/set uses a SoC `pin_to_pocctrl()` callback to locate the POCCTRL bit and convert the table's allowed voltage range into low/high millivolt values.

## State And Persistence

The layer maintains per-pin software state for GPIO ownership and saved mux marks. Hardware state lives in SH-PFC registers accessed through `sh_pfc_read()`, `sh_pfc_write()`, and `sh_pfc_config_mux()`. All critical hardware and software state updates use `pfc->lock`. This file does not implement suspend/resume itself; persistence depends on the broader SH-PFC core and platform power behavior.

## Dependencies And Integration Points

The file depends on `drivers/pinctrl/renesas/core.h`, local `sh_pfc.h`, generic pinctrl/pinmux/pinconf APIs, OF mapping when `CONFIG_OF` is enabled, and optional SH-PFC GPIO integration. It is exported to other Renesas PFC code through `sh_pfc_register_pinctrl()` and bias helper declarations in `sh_pfc.h`.

## Risks

The mux/GPIO ownership model is intentionally conservative and can return `-EBUSY` if a consumer tries to mux a GPIO-owned pin. DT mapping permits function-only, config-only, and combined nodes; bad group/pin strings are not validated here and rely on pinctrl core lookup. Drive-strength conversion assumes a full-scale 24 mA model with 3 mA or 6 mA steps based on field width; inaccurate SoC tables or different electrical models would produce wrong values. Bias and power-source behavior depends heavily on optional SoC callbacks and table flags.

## Test Signals

Tests should apply OF states with function/groups, config-only pins, and combined mux/config nodes; request GPIOs before and after function muxing; verify `-EBUSY` behavior; round-trip bias, drive-strength, and power-source configs on SoCs that provide the relevant tables; and cover missing optional SoC callbacks returning `-ENOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/sh_pfc.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/sh_pfc.h

## Purpose

`sh_pfc.h` is the shared data-model and macro header for the Renesas SuperH/R-Mobile/R-Car Pin Function Controller stack. It defines the generic SoC description structures consumed by the SH-PFC core and pinctrl layer, the enum/data-register representations used to describe pinmux topology, and a large set of macros that let per-SoC files declare thousands of pins, groups, functions, data registers, bias registers, drive-strength fields, and GPIO aliases in a compact and compile-time-checked form.

## Important APIs, Types, And Macros

`struct sh_pfc` is the central runtime object: device pointer, `struct sh_pfc_soc_info`, spinlock, mapped MMIO windows, IRQs, pin ranges, GPIO chip pointer, and saved registers. `struct sh_pfc_soc_info` is the primary static SoC contract. It contains optional operations, GPIO input/output/function ranges, IRQ maps, pin arrays, group arrays, function arrays, config registers, drive registers, bias registers, IO control registers, data registers, pinmux data, and an unlock register.

The header defines pin capability flags such as `SH_PFC_PIN_CFG_INPUT`, `OUTPUT`, pull-up/down, IO-voltage ranges, drive-strength, and `NO_GPIO`. Pin topology structures include `struct sh_pfc_pin`, `sh_pfc_pin_group`, `sh_pfc_function`, `pinmux_func`, `pinmux_cfg_reg`, `pinmux_drive_reg`, `pinmux_bias_reg`, `pinmux_data_reg`, `pinmux_irq`, `pinmux_range`, and `sh_pfc_window`. `struct sh_pfc_soc_operations` provides optional callbacks for init, bias get/set, POCCTRL lookup, and PORTCR lookup.

Macros such as `SH_PFC_PIN_GROUP`, `SH_PFC_PIN_GROUP_SUBSET`, `BUS_DATA_PIN_GROUP`, `SH_PFC_FUNCTION`, `PINMUX_CFG_REG`, `PINMUX_CFG_REG_VAR`, `PINMUX_DATA_REG`, `PINMUX_DRIVE_REG`, `PINMUX_BIAS_REG`, and `PINMUX_IRQ` build static descriptions with array-size validation. The `PINMUX_IPSR_*` family describes common R-Car IPSR/GPSR/MOD_SEL/physical-selector relationships. The `PORT_GP_*`, `PINMUX_GPIO_GP_ALL()`, `PINMUX_DATA_GP_ALL()`, `GP_ASSIGN_LAST()`, `PORT_*`, `PINMUX_DATA_ALL()`, `PORT_ASSIGN_LAST()`, `GPIO_FN()`, and `PINMUX_NOGP_ALL()` macro families generate repetitive port and GPIO data from per-SoC `CPU_ALL_*` macros.

## Control Flow And Use Pattern

Per-SoC files include this header, define enums and `CPU_ALL_GP`/`CPU_ALL_PORT`/`CPU_ALL_NOGP` expansion macros as needed, use the helper macros to build static arrays, and export a `const struct sh_pfc_soc_info`. The SH-PFC core selects one such `soc_info` for a platform device, maps windows and initializes `struct sh_pfc`, then the pinctrl layer uses the arrays and callbacks to register pinctrl, pinmux, pinconf, GPIO, and IRQ behavior.

The macros are deliberately declarative. For example, a mux function is represented in `pinmux_data` as a mark followed by all enum IDs needed to select it, terminated by zero. Config/data register macros encode field widths and enum choices so the core can translate a mark into register writes. Bias, drive, and voltage support are opt-in per pin through capability flags plus matching register/callback data.

## State And Persistence

This header defines state shapes but owns no storage. Runtime state is allocated by core C files in `struct sh_pfc`; static SoC data is usually read-only. Persistence across suspend/resume depends on the core's use of `saved_regs` and platform-specific behavior, not on this header.

## Dependencies And Integration Points

The header depends on Linux bit helpers, pinconf generic enums, spinlocks, and stringification. It declares many external `sh_pfc_soc_info` objects for supported Renesas SoCs and declares bias helper functions implemented in `pinctrl.c`. It is the contract between SoC table files, the SH-PFC core, the pinctrl integration layer, and optional GPIO support.

## Risks

Most correctness is compile-time and table-driven. Macro misuse can create wrong enum order, wrong field widths, or mismatched pin/mux arrays that still compile if not caught by the embedded `BUILD_BUG_ON_ZERO` checks. Several macros depend on externally defined `CPU_ALL_*` expansion contracts, which can be hard to inspect. The dense data representation makes review difficult: a single wrong enum ID can route a peripheral to the wrong register field. Capability flags must agree with actual bias/drive/voltage register data or pinconf will either reject valid configs or permit invalid ones.

## Test Signals

Build coverage is a major signal because the macros intentionally embed static assertions. Runtime signals include successful `sh_pfc_register_pinctrl()` on SoCs using GP, PORT, and NOGP styles; pinmux state application across IPSR/GPSR/MOD_SEL patterns; bias helper behavior for both R-Car and R-Mobile register layouts; and pinconf support only where the declared capability flags and register tables agree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/sh_pfc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/Kconfig

## Purpose

This `Kconfig` fragment defines the build-time configuration symbols for Samsung pin control drivers. It separates a private common symbol, SoC-family visible symbols, and architecture-specific helper objects for Exynos ARM and ARM64 support.

## Important Symbols And Dependencies

`PINCTRL_SAMSUNG` is a hidden boolean selected by all Samsung pinctrl implementations. It selects `GPIOLIB`, `PINMUX`, and `PINCONF`, ensuring the common Samsung driver builds only when the core pinctrl/GPIO infrastructure is available. `PINCTRL_EXYNOS` is the visible common Exynos/S5PV210 option. It depends on `ARCH_EXYNOS`, `ARCH_S5PV210`, or `COMPILE_TEST && OF`, selects the common Samsung symbol, and conditionally selects `PINCTRL_EXYNOS_ARM` or `PINCTRL_EXYNOS_ARM64` based on architecture. `PINCTRL_EXYNOS_ARM` and `PINCTRL_EXYNOS_ARM64` depend on `PINCTRL_EXYNOS` and are visible only for compile-test coverage. `PINCTRL_S3C64XX` is the visible S3C64XX option and depends on `ARCH_S3C64XX` or `COMPILE_TEST && OF`.

## Control Flow And Integration

Kconfig selection controls the object list in the sibling Makefile. Enabling either Exynos or S3C64XX selects the shared Samsung core object. Exynos selects additional architecture-specific object files so the common Exynos driver can be paired with ARMv7 or ARMv8 data/quirk code.

## State And Persistence

This file has no runtime state. Its state is the kernel `.config`, which determines what objects are compiled into the kernel or module build.

## Risks

Incorrect select/dependency logic can omit required common infrastructure or build architecture-specific files for the wrong target. The hidden common symbol is selected, not user-enabled, so any new Samsung family symbol must remember to select it. Compile-test dependencies require OF because these drivers are DT-oriented.

## Test Signals

Useful checks include `olddefconfig`/`allmodconfig`/`allyesconfig` coverage for Exynos, S5PV210, S3C64XX, ARM, ARM64, and `COMPILE_TEST && OF`, plus verifying that selected symbols produce the expected object list in the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/Makefile

## Purpose

This Makefile maps Samsung pinctrl Kconfig symbols to object files. It is the build integration point for the common Samsung pinctrl core, Exynos common code, Exynos ARM/ARM64-specific code, and S3C64XX code.

## Important Rules

`obj-$(CONFIG_PINCTRL_SAMSUNG) += pinctrl-samsung.o` builds the common Samsung pinctrl core whenever a family driver selects the hidden common symbol. `CONFIG_PINCTRL_EXYNOS` adds `pinctrl-exynos.o`, `CONFIG_PINCTRL_EXYNOS_ARM` adds `pinctrl-exynos-arm.o`, `CONFIG_PINCTRL_EXYNOS_ARM64` adds `pinctrl-exynos-arm64.o`, and `CONFIG_PINCTRL_S3C64XX` adds `pinctrl-s3c64xx.o`.

## Control Flow And Integration

The file is evaluated by Kbuild after Kconfig has resolved symbols. It assumes `Kconfig` selects the common symbol before any family-specific object needs it. The Makefile contains no ordering constraints beyond line order; Kbuild links selected objects into the enclosing built-in or module archive as appropriate.

## State And Persistence

There is no runtime state. Build state is derived entirely from `CONFIG_*` variables.

## Risks

If a new Kconfig symbol is added without a corresponding Makefile rule, its driver will never build. If a Makefile rule references a symbol that cannot be selected, dead code can accumulate. If family drivers forget to select `PINCTRL_SAMSUNG`, they may build without the shared core object.

## Test Signals

Build matrix checks should confirm the expected `.o` files appear for each Kconfig combination, especially Exynos common-only, ARM-specific, ARM64-specific, S3C64XX, and compile-test configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/Makefile -->
