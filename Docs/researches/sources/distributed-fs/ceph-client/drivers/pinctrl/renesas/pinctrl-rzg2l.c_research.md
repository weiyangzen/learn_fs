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
