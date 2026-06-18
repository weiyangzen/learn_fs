# subset-b-005117 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.c

## Purpose
Implements the shared Allwinner/sunxi pinctrl, pinmux, pin configuration, GPIO, and GPIO-backed IRQ controller logic. SoC-specific sunxi files provide pin/function descriptors; this file turns those descriptors and device-tree nodes into Linux pinctrl, gpiolib, regulator, and irqdomain registrations.

## Important APIs, Types, And Functions
Key entry points are `sunxi_pinctrl_init_with_flags`, `sunxi_pinctrl_init`, and `sunxi_pinctrl_dt_table_init` from the companion header. Register helpers `sunxi_mux_reg`, `sunxi_data_reg`, `sunxi_dlevel_reg`, and `sunxi_pull_reg` calculate banked MMIO offsets. Pinctrl callbacks include `sunxi_pctrl_dt_node_to_map`, `sunxi_pconf_get/set`, `sunxi_pmx_set_mux`, `sunxi_pmx_gpio_set_direction`, and GPIO callbacks for direction, get/set, OF translation, and `to_irq`. IRQ logic is handled by `sunxi_pinctrl_irq_set_type`, mask/unmask/ack helpers, chained handler `sunxi_pinctrl_irq_handler`, and `sunxi_pinctrl_irq_domain_ops`.

## Control Flow
Probe allocates `struct sunxi_pinctrl`, maps MMIO, derives register layout flags, builds runtime group/function state from descriptor pins, registers pinctrl, registers a gpiochip and pin ranges, enables the APB clock, creates an IRQ domain, maps each hardware IRQ, masks/clears banks, installs chained parent handlers, and optionally programs debounce clocks. Device-tree pin state parsing accepts generic and legacy Allwinner properties, validates that each pin supports the requested function, and emits mux/config maps. GPIO IRQ requests lock the GPIO line, optionally move reset mux state to input, then mux the pin to its IRQ function.

## State And Persistence Behavior
Driver state persists in `struct sunxi_pinctrl`: MMIO base, descriptor pointer, runtime groups/functions, irq map arrays, irq domain, gpiochip, pinctrl device, flags, register layout parameters, spinlock, and per-bank regulator/refcount state. Hardware state persists in mux, data, drive, pull, IO-bias, IRQ config/control/status, and debounce registers. The code does not save/restore registers itself; it relies on normal pinctrl states and platform power handling.

## Dependencies And Integration Points
Integrates with Linux pinctrl core, gpiolib, irqdomain/chained IRQs, regulators named `vcc-p<bank>`, device tree pinctrl bindings, optional APB/oscillator clocks, and Allwinner DT binding constants. SoC descriptor files provide pins, functions, variants, IRQ bank maps, and IO-bias behavior.

## Risks And Edge Cases
Register offset calculation is layout-sensitive, especially D1/new layouts and bank K at `0x500`. Function lookup must respect pin and function variants or unsupported mux values can be exposed. The shared spinlock protects read-modify-write MMIO paths but not all IO-bias writes use identical locking. Regulator refcounts are per logical bank and depend on correct pin base/bank arithmetic. IRQ readback may temporarily remux lines on SoCs with `irq_read_needs_mux`.

## Test Signals
Probe on old and new register layouts, DT parsing for generic and legacy properties, GPIO request/free regulator refcounts, pin mux changes, drive and pull get/set, GPIO input/output, gpio-to-irq mapping, edge and level IRQ delivery, wake propagation, debounce programming, variant-specific pins/functions, and failure injection for clocks, regulators, IRQs, and pinctrl/gpio registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.h

## Purpose
Defines the shared descriptor and register-layout contract for Allwinner/sunxi pinctrl drivers. It gives SoC-specific files the macros and types needed to describe pins, functions, IRQ mappings, variants, IO-bias behavior, and controller initialization.

## Important APIs, Types, And Functions
Important constants define bank bases `PA_BASE` through `PN_BASE`, bank/register sizes, mux/data/drive/pull field widths, IRQ register offsets, debounce offsets, mux values for input/IRQ/disabled, variant flags, IO-bias registers, and the bank K extended offset. Core types are `struct sunxi_desc_function`, `struct sunxi_desc_pin`, `struct sunxi_pinctrl_desc`, `struct sunxi_pinctrl_function`, `struct sunxi_pinctrl_group`, `struct sunxi_pinctrl_regulator`, and `struct sunxi_pinctrl`. Descriptor macros include `SUNXI_PIN`, `SUNXI_PIN_VARIANT`, `SUNXI_FUNCTION`, `SUNXI_FUNCTION_VARIANT`, `SUNXI_FUNCTION_IRQ`, and `SUNXI_FUNCTION_IRQ_BANK`. Inline helpers compute IRQ config/control/status/debounce and group config registers.

## Control Flow
The header has no standalone execution. SoC files populate `struct sunxi_pinctrl_desc` and call `sunxi_pinctrl_init` or `sunxi_pinctrl_init_with_flags`; dynamic DT-table users call `sunxi_pinctrl_dt_table_init`. Runtime code uses the inline IRQ helpers when programming or handling each interrupt.

## State And Persistence Behavior
The descriptor structs are usually static, read-only SoC data. `struct sunxi_pinctrl` is the mutable per-device state container for MMIO, pinctrl/gpio/IRQ registrations, function/group tables, regulator references, locks, flags, and calculated layout parameters. The header also encodes persistent hardware ABI expectations such as bank numbering and bitfield widths.

## Dependencies And Integration Points
Depends on Linux pinctrl descriptors, spinlocks, regulators, irqdomains, gpiochips, and device/platform data. It is consumed by `pinctrl-sunxi.c` and many Allwinner SoC pin description files.

## Risks And Edge Cases
Changing constants or packed assumptions here affects every sunxi pinctrl implementation. `SUNXI_PINCTRL_MAX_BANKS` and the fixed `regulators[11]` array must stay aligned with supported bank counts. Variant mask bits share `flags` with layout-control bits, so new variants must not collide with `SUNXI_PINCTRL_NEW_REG_LAYOUT`, `PORTF_SWITCH`, or `ELEVEN_BANKS`.

## Test Signals
Compile all sunxi pinctrl users, probe controllers with legacy and new layouts, validate bank K and eleven-bank offsets, exercise IRQ bank maps, variant-only pins/functions, IO-bias variants, and generated DT-table initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/Kconfig

## Purpose
Declares Kconfig symbols for NVIDIA Tegra pinctrl support. It separates the shared Tegra pinctrl core from SoC-specific pinmux table drivers and the XUSB pad controller driver.

## Important APIs, Types, And Functions
`PINCTRL_TEGRA` is the common hidden boolean and selects `PINMUX` and `PINCONF`. SoC booleans `PINCTRL_TEGRA20`, `TEGRA30`, `TEGRA114`, `TEGRA124`, `TEGRA210`, `TEGRA186`, `TEGRA194`, and `TEGRA234` select the common symbol. `PINCTRL_TEGRA_XUSB` defaults to enabled on `ARCH_TEGRA` and selects `GENERIC_PHY`, `PINCONF`, and `PINMUX`.

## Control Flow
There is no runtime control flow. Kernel configuration enables these symbols through architecture or SoC selection, which controls which objects the Makefile builds.

## State And Persistence Behavior
State is build-time only: selected symbols persist in `.config` and drive object inclusion. No runtime data is stored here.

## Dependencies And Integration Points
Integrates with the top-level pinctrl Kconfig hierarchy, Tegra architecture symbols, the generic pinmux/pinconf framework, and the generic PHY subsystem for XUSB.

## Risks And Edge Cases
Missing `select PINCTRL_TEGRA` for a SoC table would compile a table without the common implementation. Enabling XUSB broadly via `def_bool y if ARCH_TEGRA` assumes the driver remains safe to build for all Tegra kernels. Dependency changes can affect early boot because Tegra pinctrl drivers register through `arch_initcall`.

## Test Signals
Configuration tests for each Tegra SoC symbol, allmodconfig/allyesconfig builds, `ARCH_TEGRA` builds including XUSB, and link checks that common and SoC-specific objects are selected together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/Makefile

## Purpose
Maps Tegra pinctrl Kconfig symbols to the object files built into the kernel. It is the build glue for the shared Tegra implementation, SoC pin tables, and XUSB pad controller.

## Important APIs, Types, And Functions
The Makefile emits `pinctrl-tegra.o` for `CONFIG_PINCTRL_TEGRA`, SoC objects from `pinctrl-tegra20.o` through `pinctrl-tegra234.o`, and `pinctrl-tegra-xusb.o` for `CONFIG_PINCTRL_TEGRA_XUSB`.

## Control Flow
There is no runtime flow. Kbuild expands each `obj-$(CONFIG_...)` assignment after Kconfig resolution and compiles/links the selected objects.

## State And Persistence Behavior
State is build-system state only: object selection follows `.config`, and normal build outputs are generated under the kernel build tree.

## Dependencies And Integration Points
Integrates with `drivers/pinctrl/Makefile`, the Tegra Kconfig file, platform driver module metadata in each C file, and the shared `pinctrl-tegra.h` interface.

## Risks And Edge Cases
The common object must be present whenever a SoC table calls `tegra_pinctrl_probe`; Kconfig currently enforces this through `select`. Object names must match source files exactly. Adding a new SoC requires coordinated Kconfig, Makefile, compatible string, and descriptor data changes.

## Test Signals
Incremental and clean builds for each symbol, allmodconfig link success, and runtime probe on DT nodes matching the selected SoC drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra-xusb.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra-xusb.c

## Purpose
Implements the legacy Tegra124 XUSB pad controller as both a pinctrl/pinmux/pinconf provider for XUSB lanes and a generic PHY provider for PCIe and SATA lanes. It controls lane muxing, IDDQ state, ELPG clamp sequencing, and PLL power-on/off sequences.

## Important APIs, Types, And Functions
Core types are `struct tegra_xusb_padctl`, `struct tegra_xusb_padctl_soc`, `struct tegra_xusb_padctl_function`, and `struct tegra_xusb_padctl_lane`. Pinctrl callbacks parse `nvidia,function`, `nvidia,lanes`, and `nvidia,iddq`; pinmux uses `tegra_xusb_padctl_pinmux_set`; pinconf uses `tegra_xusb_padctl_pinconf_group_get/set`. PHY operations are `pcie_phy_ops` and `sata_phy_ops`, backed by `tegra_xusb_padctl_enable/disable`, `pcie_phy_power_on/off`, and `sata_phy_power_on/off`. Exported legacy entry points are `tegra_xusb_padctl_legacy_probe` and `tegra_xusb_padctl_legacy_remove`.

## Control Flow
Probe allocates state, deasserts reset, maps registers, registers a pinctrl device, creates PCIe and SATA PHYs, and registers an OF PHY provider. DT pinctrl subnodes become mux and config maps per lane. Pinmux writes function indices into lane bitfields. PHY init increments a shared enable count and unclamps ELPG registers; exit decrements and reclamps. PHY power-on sequences program PLL/control bits and poll lock-detect with a 50 ms timeout.

## State And Persistence Behavior
Runtime state includes MMIO base, reset control, mutex, selected SoC lane tables, pinctrl descriptor/device, PHY provider, two PHY handles, and a reference-count-like `enable` counter. Hardware state persists in padctl lane mux/IDDQ fields, ELPG clamp bits, and PCIe/SATA PLL registers until reset or power-management code changes them.

## Dependencies And Integration Points
Depends on pinctrl core utilities, generic PHY, reset controller, device tree, Tegra XUSB binding constants, MMIO accessors, and legacy Tegra124 padctl matching. Consumers obtain PHYs by phandle index and pin states through the pinctrl framework.

## Risks And Edge Cases
Lane `iddq == 0` means unsupported, so lane metadata must not use bit zero for a real IDDQ field in this encoding. The SATA power-off path writes `value |= ~BIT` masks, which is unusually broad and should be treated carefully in behavior changes. PLL polling has fixed timeout/sleep intervals. The shared `enable` counter is mutex-protected but must remain balanced across PHY users.

## Test Signals
Tegra124 XUSB padctl probe/remove, reset assert/deassert, pinctrl DT lane muxing, IDDQ set/get, PCIe and SATA PHY init/exit/power-on/power-off, PLL lock timeout handling, multiple concurrent PHY users, and OF PHY xlate bounds checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra-xusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.c

## Purpose
Implements the shared NVIDIA Tegra pinctrl core used by Tegra SoC table files. It provides pinctrl group/function enumeration, DT map parsing, mux programming, group pinconf access, GPIO/SFIO switching, parked-bit cleanup, and suspend/resume register save/restore.

## Important APIs, Types, And Functions
Main exported API is `tegra_pinctrl_probe`; exported PM ops are `tegra_pinctrl_pm`. Internal callbacks include `tegra_pinctrl_dt_node_to_map`, `tegra_pinctrl_set_mux`, `tegra_pinctrl_gpio_request_enable`, `tegra_pinctrl_gpio_disable_free`, `tegra_pinconf_reg`, `tegra_pinconf_group_get/set`, `tegra_pinctrl_clear_parked_bits`, `tegra_pinctrl_suspend`, and `tegra_pinctrl_resume`. DT properties are mapped by `cfg_params`, including pull, tristate, input, open-drain, lock, IO reset, receiver select/IO HV, drive strengths, slew rates, drive type, and GPIO mode.

## Control Flow
SoC drivers call `tegra_pinctrl_probe` with static `tegra_pinctrl_soc_data`. Probe allocates `struct tegra_pmx`, builds reverse function-to-group lists from each pingroup's four mux slots, maps all MMIO banks, allocates register backup storage, registers pinctrl ops, clears parked bits, optionally adds a GPIO range, and stores driver data. DT subnodes emit mux/config maps for each `nvidia,pins` group. Mux writes select the matching function slot. Pinconf resolves a parameter to bank/register/bit/width metadata and performs range-checked read-modify-write.

## State And Persistence Behavior
Per-device state includes SoC descriptor data, generated function group lists, GPIO range, pinctrl descriptor, MMIO bank array, suspend backup register array, and per-pingroup cached SFIO state for GPIO requests. Suspend snapshots every mapped register word and forces pinctrl sleep; resume writes all saved words back, then flushes writes.

## Dependencies And Integration Points
Depends on Linux pinctrl core, pinctrl-utils, platform resources, DT parsing, debugfs seq output, gpiolib ranges, and SoC data from `pinctrl-tegra*.c`. GPIO cooperation depends on the companion Tegra GPIO DT node and `gpio-ranges`.

## Risks And Edge Cases
The generated function group array assumes each mux group appears in at most four function lists. `LOCK` bits cannot be cleared, so bad pinconf inputs can permanently change hardware state until reset. Some features are unsupported per group via negative register/bit fields. Suspend backup size is derived from resource bytes while loops treat it as 32-bit words, so resource sizing must be sane. GPIO/SFIO restoration depends on cached per-group state and correct group lookup by pin offset.

## Test Signals
Probe on each Tegra SoC table, DT pinctrl states with mux-only, config-only, and combined subnodes, unsupported property errors, lock-bit behavior, GPIO request/free with `sfsel_in_mux`, debugfs group dumps, parked-bit clearing, suspend/resume restoration, and builds with/without DT `gpio-ranges`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.h

## Purpose
Defines the shared data model and public interface for Tegra pinctrl SoC table drivers and the common implementation in `pinctrl-tegra.c`.

## Important APIs, Types, And Functions
Key types are `struct tegra_pmx`, `struct tegra_pingroup_config`, `struct tegra_function`, `struct tegra_pingroup`, and `struct tegra_pinctrl_soc_data`. Enumerations define Tegra-specific pinconf parameters and legal pull/tristate values. Macros `TEGRA_PINCONF_PACK`, `TEGRA_PINCONF_UNPACK_PARAM`, and `TEGRA_PINCONF_UNPACK_ARG` encode configs. The public symbols are `tegra_pinctrl_probe` and `tegra_pinctrl_pm`.

## Control Flow
The header itself has no execution. SoC files fill arrays of `pinctrl_pin_desc`, function names, and `tegra_pingroup` entries, then pass a `tegra_pinctrl_soc_data` instance to `tegra_pinctrl_probe`. The common implementation interprets per-group register offsets, banks, bit positions, and widths from this metadata.

## State And Persistence Behavior
`struct tegra_pmx` is mutable per-controller state: device, pinctrl device, SoC data, generated functions, group pin names, GPIO range, mapped register banks, suspend backup registers, and counted pingroup config cache. SoC data and pingroup arrays are static descriptors that encode hardware register layout.

## Dependencies And Integration Points
Integrates with platform devices, pinctrl descriptors, GPIO ranges, MMIO resources, and noirq PM. The SoC files depend on the documented meanings of negative `*_reg` and `*_bit` fields to mark unsupported features.

## Risks And Edge Cases
The bitfield widths in `struct tegra_pingroup` constrain register banks, bits, and widths; out-of-range metadata would truncate at compile/runtime. `funcs[4]` hardcodes four mux slots per group. Descriptor comments are part of the ABI between generated SoC tables and common code; changes must be coordinated across every Tegra table.

## Test Signals
Compile all Tegra SoC table files, validate pinconf packing/unpacking, exercise groups with unsupported fields, verify SoC data flags for `hsm_in_mux`, `schmitt_in_mux`, `drvtype_in_mux`, and `sfsel_in_mux`, and run suspend/resume with multiple MMIO banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra114.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra114.c

## Purpose
Provides the Tegra114-specific pin, function, group, drive-group, and platform-driver descriptors consumed by the shared Tegra pinctrl core.

## Important APIs, Types, And Functions
The file defines Tegra114 GPIO-numbered pins, non-GPIO pins, `tegra114_pins`, one-pin group arrays, multi-pin drive groups, `enum tegra_mux`, `tegra114_functions`, `PINGROUP` and `DRV_PINGROUP` descriptor macros, `tegra114_groups`, and `tegra114_pinctrl`. Runtime registration is through `tegra114_pinctrl_probe`, `tegra114_pinctrl_driver`, and `arch_initcall(tegra114_pinctrl_init)`.

## Control Flow
At arch init, the platform driver registers for compatible `nvidia,tegra114-pinmux`. Probe delegates to `tegra_pinctrl_probe`, which uses this file's static tables to register pins, groups, functions, and GPIO ranges. Each `PINGROUP` maps one logical pin group to a mux register in bank 1 and records pull, tristate, input, open-drain, lock, IO reset, and receiver-select bits. Each `DRV_PINGROUP` maps a drive group to bank 0 drive-strength/slew/schmitt/high-speed fields.

## State And Persistence Behavior
The file is static descriptor data only. Persistent runtime state is created by the common driver from these tables. Hardware state affected by the descriptors includes Tegra114 mux registers based at `0x3000` and drive registers based at `0x868`.

## Dependencies And Integration Points
Depends on `pinctrl-tegra.h`, Linux platform/OF matching, and a Tegra114 GPIO controller compatible string `nvidia,tegra114-gpio`. It integrates with DT pinctrl properties whose group and function names must match the static table names.

## Risks And Edge Cases
This file is table-heavy and correctness depends on exact GPIO numbering, register offsets, mux-slot ordering, and feature bits. Empty drive pin arrays still define configurable groups. Function enum ordering must match `tegra114_functions` and every `TEGRA_MUX_*` value used in group macros. A wrong compatible string or GPIO count breaks pinctrl/GPIO integration.

## Test Signals
Boot/probe on Tegra114 DT, pinctrl state application for UART/I2C/SDMMC/GMI/display groups, drive strength and slew config on drive groups, GPIO range mapping, debugfs group function dumps, and suspend/resume through the common Tegra PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra114.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra124.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra124.c

## Purpose
Provides Tegra124-specific pinctrl descriptor data and platform-driver registration for the common Tegra pinctrl core. It extends the Tegra114-style model with Tegra124 pin names, additional GPIOs, PCIe/DP/DSI-related pins, updated mux functions, drive groups, and a MIPI pad control group.

## Important APIs, Types, And Functions
The file defines GPIO/non-GPIO pin IDs, `tegra124_pins`, one-pin group arrays, drive-group arrays, `mipi_pad_ctrl_dsi_b_pins`, `enum tegra_mux`, `tegra124_functions`, descriptor macros `PINGROUP`, `DRV_PINGROUP`, and `MIPI_PAD_CTRL_PINGROUP`, `tegra124_groups`, and `tegra124_pinctrl`. Runtime registration is via `tegra124_pinctrl_probe`, OF match `nvidia,tegra124-pinmux`, and `arch_initcall(tegra124_pinctrl_init)`.

## Control Flow
At arch init the platform driver registers and later delegates matching devices to `tegra_pinctrl_probe`. The common driver consumes this file's tables to enumerate groups/functions, parse DT pinctrl states, and program mux/pinconf registers. Standard pingroups live in bank 1 relative to `0x3000`, drive groups live in bank 0 relative to `0x868`, and the DSI-B MIPI pad control group lives in bank 2 relative to `0x820`.

## State And Persistence Behavior
This file contributes static read-only hardware layout data. Runtime state and suspend backup are owned by `pinctrl-tegra.c`. Hardware configuration persists in the mux, pull, tristate, drive, and MIPI pad control registers described by the tables.

## Dependencies And Integration Points
Depends on the shared Tegra header/core, platform driver/OF infrastructure, the Tegra124 GPIO compatible `nvidia,tegra124-gpio`, and DT pinctrl group/function names. It also aligns with the separate Tegra124 XUSB padctl driver for related USB/PCIe/SATA pad functions, though that driver owns XUSB lane PHY control.

## Risks And Edge Cases
The large declarative tables are prone to off-by-one GPIO IDs, wrong function-slot ordering, bad register offsets, and mismatched group names. Tegra124 adds a third MMIO bank for MIPI pad control, so platform resources must match the bank indices used here. Some drive groups have unsupported fields encoded as `-1`, which common pinconf must reject cleanly.

## Test Signals
Tegra124 boot/probe, DT states for SDMMC, UART, I2C, display, PCIe, SATA, DP, and DSI-B groups, MIPI pad muxing, drive-group pinconf, GPIO range mapping through `nvidia,tegra124-gpio`, debugfs dumps, and suspend/resume across all three register banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra124.c -->
