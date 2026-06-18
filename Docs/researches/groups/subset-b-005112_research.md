# subset-b-005112 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd-sc9860.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd-sc9860.c

## Purpose
This file is the Spreadtrum SC9860 SoC-specific pin table and platform-driver wrapper for the common Spreadtrum pinctrl core. It enumerates the SC9860 global-control, common-pin, and misc-pin register entries, builds a `struct sprd_pins_info` array from that encoded metadata, and binds the common probe/remove/shutdown routines to the `sprd,sc9860-pinctrl` device-tree compatible.

## Important APIs, types, and functions
The key data is `enum sprd_sc9860_pins`, whose entries are packed with `SPRD_PIN_INFO(num, type, offset, width, reg)`, and `sprd_sc9860_pins_info[]`, whose entries are expanded with `SPRD_PINCTRL_PIN()`. `sprd_pinctrl_probe()` calls `sprd_pinctrl_core_probe(pdev, sprd_sc9860_pins_info, ARRAY_SIZE(...))`. `sprd_pinctrl_of_match[]` declares the compatible string, and `sprd_pinctrl_driver` wires `.probe`, `.remove = sprd_pinctrl_remove`, and `.shutdown = sprd_pinctrl_shutdown`.

## Control flow
Module initialization registers a platform driver. On probe, no local register access is performed; the SoC table is passed to the core. The core later interprets the packed metadata to derive MMIO addresses for global control registers, common pin registers, and misc pin registers. Device-tree child groups are parsed by the core, so the SC9860 file only supplies the universe of legal pin names and their encoded register layout.

## State and persistence behavior
This file owns no runtime state. Its static arrays are read-only metadata after initialization. Hardware state persists through the common driver's writes to the controller MMIO registers. Shutdown persistence is delegated to the common `sprd_pinctrl_shutdown()` path, which selects a pinctrl state named `shutdown` if present.

## Dependencies and integration points
It depends on `pinctrl-sprd.h`, `linux/platform_device.h`, and module/of matching infrastructure. It integrates with Linux pinctrl through `sprd_pinctrl_core_probe()` exported by `pinctrl-sprd.c`. It also depends on the SC9860 device tree using pin names identical to the generated enum-token strings such as `SC9860_U0TXD` or `SC9860_SD0_CLK`, because the common parser resolves group pin names by string match.

## Risks
The table is large and manually ordered. Common pins and misc pins are assigned register offsets by the core using the array order minus counts of earlier global/common pins, so reordering entries can silently change hardware addresses. Reserved common/misc pairs are present in the enum but omitted from `sprd_sc9860_pins_info[]`; adding them without checking numbering may expose nonexistent pins. Any typo in a generated pin name breaks device-tree group parsing. The table also has sparse pin numbers, so code must not assume array index equals pin number.

## Test signals
Build coverage should include `CONFIG_PINCTRL_SPRD_SC9860=m/y`. Runtime signals include successful probe for `sprd,sc9860-pinctrl`, correct pin count in debugfs, successful DT group parsing for representative UART/I2C/SD/eMMC/RF pins, and mux/pinconf writes landing at expected SC9860 register offsets. Shutdown state testing should confirm the common driver applies a `shutdown` state when one is declared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd-sc9860.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd.c

## Purpose
This is the common Spreadtrum pinctrl implementation. It converts SoC-provided `sprd_pins_info` metadata into pinctrl pin descriptors, parses device-tree pin groups, implements four-function mux selection, implements generic and Spreadtrum-specific pin configuration, and exports probe/remove/shutdown helpers for SoC wrapper drivers.

## Important APIs, types, and functions
Core runtime types are local `struct sprd_pin`, `struct sprd_pin_group`, `struct sprd_pinctrl_soc_info`, and `struct sprd_pinctrl`. Public entry points are `sprd_pinctrl_core_probe()`, `sprd_pinctrl_remove()`, and `sprd_pinctrl_shutdown()`. Pinctrl callbacks are `sprd_pctrl_group_count()`, `sprd_pctrl_group_name()`, `sprd_pctrl_group_pins()`, and `sprd_dt_node_to_map()`. Pinmux callbacks expose `func1` through `func4` and write `PIN_FUNC_MASK` in `sprd_pmx_set_mux()`. Pinconf callbacks are `sprd_pinconf_get()`, `sprd_pinconf_set()`, group variants, and debug display helpers. Custom DT params are `sprd,control` and `sprd,sleep-mode`.

## Control flow
Probe allocates controller state, ioremaps resource 0, converts SoC metadata with `sprd_pinctrl_add_pins()`, parses DT groups with `sprd_pinctrl_parse_dt()`, creates `pinctrl_pin_desc` entries, fills the static `sprd_pinctrl_desc`, and registers the pinctrl device. DT parsing counts direct children and grandchildren as groups. Each group is named after its DT node and resolves its `pins` strings to SoC pin numbers. `sprd_dt_node_to_map()` looks up the group by node name, optionally adds a mux map from the `function` property, and adds pin or group config maps depending on whether the node has one or multiple pins. Mux selection writes two function bits on every common pin in the group; global-control and misc pins are skipped for muxing. Pinconf set loops over packed configs, computes a mask/shift/value, and performs read-modify-write on either a global-control bitfield or a full common/misc pin register.

## State and persistence behavior
Persistent driver state is devm-allocated and stored in platform drvdata. Hardware state is direct MMIO in the pin controller. `sprd_pinconf_set()` updates registers immediately and has no rollback across a multi-config sequence or group operation. Some sleep-related configs only take effect when the config list also contains `PIN_CONFIG_SLEEP_HARDWARE_STATE`; otherwise input/output/high-impedance and sleep pull settings can be ignored by falling through with zero mask. `sprd_pinctrl_shutdown()` obtains the pinctrl handle and selects a state named `shutdown`, so board DT can define last-minute pin state before poweroff/reboot.

## Dependencies and integration points
The file depends on Linux pinctrl, pinmux, generic pinconf parsing, `pinctrl-utils`, platform MMIO resources, and SoC wrapper metadata from `pinctrl-sprd.h`. Integration with consumers is entirely through pinctrl state nodes and generic pinconf properties plus `sprd,control` and `sprd,sleep-mode`. Debugfs integration prints raw register values for pins and groups when enabled.

## Risks
`sprd_pinctrl_desc` is static and mutated during probe, which is common for singleton SoC drivers but risky if multiple Spreadtrum pinctrl instances coexist. `sprd_pinconf_group_dbg_show()` increments `config` in the loop header despite assigning it each iteration, which is harmless but suspicious. Drive-strength validation accepts 2 through 60 mA, while `sprd_pinconf_drive()` only maps discrete values and silently maps unsupported in-range values to 2 mA encoding. Pull-up set accepts only 20000 and 4700 ohms but silently writes zero for other arguments. Group parsing does not fail if a pin name is not found; it leaves the default zero entry in the group array, which can misconfigure pin 0. RMW operations are not locked, so concurrent pinconf/mux updates may race.

## Test signals
Useful tests include DT parsing with direct child groups and nested groups, invalid pin names, one-pin versus multi-pin config maps, all four mux functions, sleep-state config combinations, global-control `sprd,control`, pull-up/down/bias-disable, and shutdown state selection. Runtime observability comes from pinctrl debugfs raw register dumps and dev_dbg group/pin logs. Static tests should check sparse pin numbers and that SoC table order matches hardware register order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd.h

## Purpose
This header defines the packed metadata contract between Spreadtrum SoC pin tables and the common Spreadtrum pinctrl core. It also declares the exported lifecycle helpers used by SoC-specific platform drivers.

## Important APIs, types, and functions
`SPRD_PIN_INFO()` packs pin number, pin type, global-control bit offset, bit width, and global-control register index into one integer. `SPRD_PINCTRL_PIN()` and `SPRD_PINCTRL_PIN_DATA()` unpack that value into `struct sprd_pins_info`. `enum pin_type` classifies entries as `GLOBAL_CTRL_PIN`, `COMMON_PIN`, or `MISC_PIN`. `struct sprd_pins_info` is the SoC table element consumed by `sprd_pinctrl_core_probe()`. The exported functions are `sprd_pinctrl_core_probe()`, `sprd_pinctrl_remove()`, and `sprd_pinctrl_shutdown()`.

## Control flow
SoC files define enum constants with `SPRD_PIN_INFO()` and then instantiate a `sprd_pins_info[]` table using `SPRD_PINCTRL_PIN()`. The common core reads the unpacked fields and computes register addresses differently for global-control versus common/misc pins. The header itself has no runtime control flow.

## State and persistence behavior
There is no runtime state in this header. Its bitfield layout is persistent ABI within this driver family: changing offsets, masks, or type values would change how all Spreadtrum SoC tables decode.

## Dependencies and integration points
The header forward-declares `struct platform_device` and is included by both the common core and SC9860 wrapper. It integrates with Linux module symbol exports indirectly by declaring the common functions.

## Risks
The packed format allocates 12 bits for pin number, 4 bits for type, 8 bits for bit offset, 4 bits for width, and 4 bits for register index. Larger future register indices or widths would be truncated. The macro uses token stringification for pin names, so renaming enum tokens changes the DT-visible name expected by the common parser. Because common/misc register offsets are inferred from array order, the header's compact representation does not encode enough information to protect against table-order mistakes.

## Test signals
Compile tests for all Spreadtrum SoC tables validate macro expansion. A useful review check is to decode a few enum entries manually and confirm `.num`, `.type`, `.bit_offset`, `.bit_width`, and `.reg` match hardware documentation. DT parsing tests should use the stringified names emitted by `SPRD_PINCTRL_PIN()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/Kconfig

## Purpose
This Kconfig fragment exposes StarFive JH7100 and JH7110 pinctrl/GPIO drivers and their shared feature dependencies.

## Important APIs, types, and functions
The visible symbols are `PINCTRL_STARFIVE_JH7100`, `PINCTRL_STARFIVE_JH7110_SYS`, and `PINCTRL_STARFIVE_JH7110_AON`. `PINCTRL_STARFIVE_JH7110` is an internal bool selected by both JH7110 instance drivers to build the common helper. All drivers select `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `GENERIC_PINCONF`, `GPIOLIB`, and `GPIOLIB_IRQCHIP`.

## Control flow
Kconfig dependency resolution controls which object files are built by the Makefile. JH7100 is a standalone tristate. The JH7110 SYS and AON drivers are separate tristates that each select the common bool, ensuring `pinctrl-starfive-jh7110.o` is built when either instance is enabled.

## State and persistence behavior
There is no runtime state. Build-time selections determine whether module or built-in platform drivers are present in the kernel image.

## Dependencies and integration points
All visible symbols depend on `SOC_STARFIVE || COMPILE_TEST` and `OF`, default to `SOC_STARFIVE`, and integrate with DT-based platform probing. The selected generic pinctrl and gpiolib symbols reflect the implementation's use of generic group/function registration, generic pinconf parsing, and GPIO IRQ chips.

## Risks
Because `PINCTRL_STARFIVE_JH7110` is bool, enabling either JH7110 instance as a module can still force the shared helper according to Kconfig's tristate/bool semantics; this should be checked against expected module linkage. The visible drivers have no explicit `HAS_IOMEM` dependency even though they ioremap MMIO resources, relying on the StarFive/compile-test context.

## Test signals
Build matrix should cover `JH7100=y/m`, `JH7110_SYS=y/m`, `JH7110_AON=y/m`, both JH7110 instances enabled together, and `COMPILE_TEST` on non-StarFive architectures. Module dependency checks should confirm the common JH7110 object is linked whenever SYS or AON is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/Makefile

## Purpose
This Makefile maps StarFive pinctrl Kconfig symbols to the object files that implement each SoC/controller variant.

## Important APIs, types, and functions
`obj-$(CONFIG_PINCTRL_STARFIVE_JH7100)` builds `pinctrl-starfive-jh7100.o`. `obj-$(CONFIG_PINCTRL_STARFIVE_JH7110)` builds the common `pinctrl-starfive-jh7110.o`. `obj-$(CONFIG_PINCTRL_STARFIVE_JH7110_SYS)` and `obj-$(CONFIG_PINCTRL_STARFIVE_JH7110_AON)` build the SYS and always-on wrappers.

## Control flow
Kbuild evaluates each `obj-*` line from Kconfig state. The common JH7110 object is separate from the two platform-driver wrappers, so SYS/AON share probe, GPIO, pinmux, pinconf, IRQ, and PM logic while supplying different `jh7110_pinctrl_soc_info` tables.

## State and persistence behavior
There is no runtime state. The file controls which translation units exist in the final kernel/module build.

## Dependencies and integration points
It integrates directly with the StarFive Kconfig fragment. The split mirrors the source design: JH7100 is self-contained, while JH7110 has common code plus SYS/AON instance files.

## Risks
If a visible JH7110 driver is enabled without selecting `PINCTRL_STARFIVE_JH7110`, unresolved symbols such as `jh7110_pinctrl_probe()` would result; Kconfig currently handles this. Duplicate symbol or module-loading issues should be watched when common code is built-in but instance drivers are modules.

## Test signals
Build tests should confirm object inclusion for each symbol combination and no unresolved exports between `pinctrl-starfive-jh7110.o` and the SYS/AON objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7100.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7100.c

## Purpose
This is the complete pinctrl, pinmux, pinconf, GPIO, and GPIO-IRQ driver for the StarFive JH7100 SoC. It handles 64 GPIO-capable pads plus function-share pads, parses packed DT pinmux values, controls pad configuration, exposes a gpiochip, and services chained GPIO interrupts.

## Important APIs, types, and functions
`struct starfive_pinctrl` stores the gpiochip, pinctrl range, locks, MMIO bases, pinctrl device, and DT-registration mutex. `starfive_dt_node_to_map()` dynamically creates generic groups/functions from DT. `starfive_set_mux()` writes `GPON_DOUT_CFG`, `GPON_DOEN_CFG`, and optional GPI input selector registers from packed pinmux values. Pinconf is implemented by `starfive_pinconf_get()`, `starfive_pinconf_group_set()`, `starfive_padctl_get()`, and `starfive_padctl_rmw()`, with custom `starfive,strong-pull-up`. GPIO callbacks include direction, get/set, set_config, and pin-range registration. IRQ callbacks are `starfive_irq_ack/mask/mask_ack/unmask/set_type()` plus `starfive_gpio_irq_handler()`. `starfive_probe()` wires clocks, reset, pinctrl, optional signal group, gpiochip, and IRQ parent.

## Control flow
Probe maps `"gpio"` and `"padctl"` resources, enables the clock, deasserts reset, registers pinctrl, optionally writes `starfive,signal-group` to `IO_PADSHARE_SEL`, derives the GPIO-to-pin range from the selected signal group, then registers a gpiochip with one parent IRQ. DT pinctrl parsing requires each child to contain either `pinmux` or `pins` but not both. `pinmux` children create a mux map plus optional configs; `pins` children create config-only groups. Mux application writes per-GPIO output data/enable selectors and routes input selectors when `din != GPI_NONE`. GPIO direction operations program both mux registers and pad input/bias bits. IRQ set-type programs edge/level, both-edge, and polarity registers, and the chained handler dispatches set bits from the two masked-status registers.

## State and persistence behavior
Runtime state is devm-managed; hardware state lives in GPIO, padctl, and padshare registers. Raw spinlocks serialize low-level register RMW paths, while a mutex serializes dynamic group/function creation. The clock is disabled via devm action on detach. No explicit suspend/resume state save exists in this file, so persistence across low-power states depends on platform retention or pinctrl core state reapplication.

## Dependencies and integration points
The driver depends on StarFive JH7100 DT bindings for `PAD_GPIO()`, `PAD_FUNC_SHARE()`, `GPI_NONE`, `GPO_ENABLE`, and packed pinmux values. It integrates with generic pinctrl groups/functions, generic pinconf parsing, gpiolib, gpiolib IRQ helpers, clocks, resets, and DT resources named `gpio` and `padctl`.

## Risks
The selected `IO_PADSHARE_SEL` changes which 64 pads are GPIO-capable; value 0 disables GPIO registration entirely. Packed pinmux encoding must match DT bindings exactly, or mux writes will route wrong signals. `starfive_pinconf_group_set()` combines all configs into a single mask/value before applying to all pins; conflicting configs in one node are resolved by order in that local computation. Drive strength is clamped from 14 to 63 mA and quantized. The chained IRQ handler reads status into `unsigned long`, which is fine for 32-bit chunks but should stay aligned with register width assumptions.

## Test signals
Tests should cover probe with and without `starfive,signal-group`, invalid signal groups, dynamic DT groups with `pinmux` and `pins`, GPIO direction transitions, input selector routing, custom strong pull-up, bias/drive/slew configs, IRQ edge/level/both-edge handling, and debugfs pin output showing `dout/doen`. Hardware tests should validate GPIO registration disappears for signal group 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110-aon.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110-aon.c

## Purpose
This file supplies the JH7110 always-on pinctrl instance: its pin list, MMIO register layout, GPIO IRQ register bases, pad-config range, and platform-driver binding. It delegates common pinctrl/GPIO/IRQ/PM behavior to `pinctrl-starfive-jh7110.c`.

## Important APIs, types, and functions
Constants define four always-on GPIOs, 37 saved registers, and AON register offsets. `jh7110_aon_pins[]` lists TESTEN, RGPIO0-3, RSTN, and GMAC0 pins. `jh7110_aon_set_one_pin_mux()` only calls `jh7110_set_gpiomux()` when the pin is one of the AON GPIOs and function is GPIO. `jh7110_aon_get_padcfg_base()` exposes pad config only for pins before `PAD_GMAC0_MDC`. `jh7110_aon_irq_handler()` dispatches masked status bits across the four GPIOs. `jh7110_aon_init_hw()` masks, clears, and enables AON GPIO interrupts. `jh7110_aon_pinctrl_info` is the `jh7110_pinctrl_soc_info` consumed by the common probe.

## Control flow
The platform driver matches `starfive,jh7110-aon-pinctrl` and passes `jh7110_aon_pinctrl_info` through `of_device_get_match_data()` to the common probe. During mux operations, only GPIO-function requests for the first four pins update generic GPIO mux registers; non-GPIO functions are represented by the pinmux encoding but require no extra AON function-select register in this file. IRQ handling reads `JH7110_AON_GPIOMIS` and forwards active pins to the gpiochip IRQ domain.

## State and persistence behavior
The file itself has no mutable software state. The common driver allocates `saved_regs[37]` when sleep PM is enabled and restores the AON register prefix on resume. Hardware state includes AON DOEN/DOUT/GPI/GPIOIN, IRQ registers, and the pad config register block starting at `0x30`.

## Dependencies and integration points
It depends on JH7110 DT binding pin numbers, the common JH7110 header, and the common exported `jh7110_pinctrl_probe()`, `jh7110_set_gpiomux()`, `jh7110_from_irq_desc()`, and PM ops. It integrates as a separate platform driver from the SYS controller and provides only four gpiochip lines even though the pinctrl pin list includes more non-GPIO pads.

## Risks
`JH7110_AON_GPIORIS` and `JH7110_AON_GPIOMIS` share offset `0x28`, so assumptions about raw versus masked status should be checked against hardware documentation. AON interrupt clear uses a two-write sequence through common ack/mask_ack and init paths; missed or sticky interrupts are possible if clear polarity is wrong. Pad configuration is unavailable for GMAC0 pins by design, so pinconf get may return success with no data via common fallback behavior.

## Test signals
Probe tests should verify four GPIOs register for `starfive,jh7110-aon-pinctrl`, pinctrl lists all AON pins, and suspend/resume restores the first 37 registers. Runtime tests should cover RGPIO input/output, bias/input-enable pinconf on RGPIO pins, IRQ dispatch for all four GPIOs, and no padconf writes for GMAC0 pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110-aon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110-sys.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110-sys.c

## Purpose
This file supplies the JH7110 system pinctrl instance. It provides the SYS pin table, function-select and VIN-group sideband programming tables, register layout, IRQ handlers, pad-config ranges, and platform-driver binding for the common JH7110 driver.

## Important APIs, types, and functions
`jh7110_sys_pins[]` lists 64 GPIO pins plus SD0, GMAC1, and QSPI pads. `struct jh7110_func_sel` and `jh7110_sys_func_sel[]` describe per-pin function select bitfields. `struct jh7110_vin_group_sel` and `jh7110_sys_vin_group_sel[]` map VIN-related GPIO groups. `jh7110_sys_set_one_pin_mux()` combines generic GPIO mux writes, function selection, and VIN group selection. `jh7110_sys_get_padcfg_base()` maps pins to one of two pad-config register regions. `jh7110_sys_irq_handler()` dispatches the two 32-bit masked IRQ status registers. `jh7110_sys_pinctrl_info` supplies masks, register bases, saved-register count, callbacks, and pin metadata to the common probe.

## Control flow
The platform driver matches `starfive,jh7110-sys-pinctrl` and delegates probe to `jh7110_pinctrl_probe()`. For each pinmux entry, the common driver decodes pin/din/dout/doen/function and calls `jh7110_sys_set_one_pin_mux()`. If the selected pin is a GPIO and function is 0, `jh7110_set_gpiomux()` updates DOUT/DOEN/GPI selectors. It then writes any defined function-select bitfield if the requested function is within that pin's max. For GPIO pins with function 2, it also writes VIN group selection. IRQ init masks both banks, clears both edge-clear registers, and enables the global GPIO interrupt.

## State and persistence behavior
All mutable state is in common driver allocations and SYS MMIO. The common PM ops save and restore 174 32-bit registers for this instance. Function-select and VIN-group sideband registers are included in that saved range, so suspend/resume should preserve mux state even beyond the common GPIO selector registers.

## Dependencies and integration points
The file depends on JH7110 DT binding pin IDs and mux encoding, the common JH7110 header, and the exported common helper symbols. It integrates with the common gpiochip as a 64-line GPIO controller and with the pinctrl core as a larger pin controller for GPIO, SD0, GMAC1, and QSPI pads.

## Risks
Function-select table entries use fixed offsets, shifts, and `max` values; bad entries silently skip writes or ignore over-range function values, which can make DT pinmux failures hard to diagnose. `jh7110_set_function()` uses a fixed `0x3U` mask even when some entries declare max 3 and shifts are not uniformly spaced; table correctness is critical. Pad configuration is intentionally unavailable for the GMAC1 range between `PAD_GMAC1_MDC` and `PAD_GMAC1_TXC`, so common pinconf may no-op for those pins. VIN group selection is tied to function value 2 and only for tabled GPIO pins.

## Test signals
Tests should cover GPIO mux function 0, alternate function selection for tabled GPIOs, over-range function requests, VIN group setup for function 2, SD0/QSPI padconf ranges, GMAC1 no-padconf behavior, interrupt dispatch across GPIO0-31 and GPIO32-63, and suspend/resume restoring the 174-register window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110-sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110.c

## Purpose
This is the common JH7110 pinctrl/GPIO/IRQ implementation shared by the SYS and AON controller instances. SoC-instance files provide pin tables, register bases, masks, IRQ handlers, and per-pin mux callbacks; this file implements the generic pinctrl, pinmux, pinconf, gpiochip, interrupt-chip, probe, and suspend/resume behavior.

## Important APIs, types, and functions
Packed DT pinmux decoding is handled by `jh7110_pinmux_pin/din/dout/doen/function()`. Exported helpers are `jh7110_set_gpiomux()`, `jh7110_pinctrl_probe()`, `jh7110_from_irq_desc()`, and `jh7110_pinctrl_pm_ops`. DT parsing is `jh7110_dt_node_to_map()`. Mux application is `jh7110_set_mux()` through the SoC callback `jh7110_set_one_pin_mux`. Pinconf uses `jh7110_padcfg_rmw()`, `jh7110_pinconf_get()`, and `jh7110_pinconf_group_set()`. GPIO callbacks include direction/get/set/set_config/add_pin_ranges. IRQ callbacks include ack, mask, mask_ack, unmask, set_type, and a shared `jh7110_irq_chip`.

## Control flow
Probe obtains `jh7110_pinctrl_soc_info` from the OF match, allocates state and optional saved registers, maps the MMIO resource, deasserts reset, optionally enables a clock, creates a pinctrl descriptor from instance pin data, registers pinctrl, registers a gpiochip with instance GPIO count, installs the instance chained IRQ handler and hardware-init callback, and enables pinctrl. DT parsing creates one group per child node under a pinctrl state, requiring a `pinmux` array, then adds a mux map and optional config map. Mux setting decodes each packed value and calls the instance callback. Generic GPIO mux writes update per-four-pin packed DOUT/DOEN registers and optional GPI selector registers. IRQ set-type maps requested edge/level semantics onto instance IRQ register bases and parent handler selection.

## State and persistence behavior
Software state is devm-managed `struct jh7110_pinctrl`. Raw spinlocks serialize register RMW; a mutex serializes dynamic group/function creation. With sleep PM enabled, suspend copies `info->nsaved_regs` 32-bit registers from the MMIO base into `saved_regs`, and resume writes them back. Pinconf and mux state otherwise persists in hardware registers until reset or later writes.

## Dependencies and integration points
The file depends on Linux pinctrl generic group/function helpers, generic pinconf, gpiolib IRQ helpers, platform reset/clock APIs, and JH7110 DT bindings. It integrates with instance files through `struct jh7110_pinctrl_soc_info`, which supplies pin descriptors, masks, register bases, callbacks, and saved-register count. It integrates with DT consumers via packed `pinmux` arrays and generic pinconf properties.

## Risks
`jh7110_pinconf_get()` returns 0 when padcfg callbacks are missing or a pin has no padcfg base, which can look like success without packing a result. The shared `jh7110_irq_chip` is a mutable static whose `.name` is assigned during probe, so multiple instances can overwrite the displayed name. IRQ polarity for level high/low is opposite-looking compared with JH7100 comments and must match JH7110 hardware. Suspend/resume blindly saves a register prefix; if future instances have sparse or side-effect registers in that range, restore may be unsafe.

## Test signals
Build and runtime tests should enable SYS and AON together, verify both gpiochips register with separate line counts, parse DT pinmux groups, apply generic pinconf, exercise GPIO input/output/set, dispatch IRQs through each instance handler, and suspend/resume while preserving mux and pad configuration. Debugfs pin output should show decoded `dout`, `doen`, and `din` for GPIO pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110.h

## Purpose
This header defines the contract between the common JH7110 pinctrl driver and the SYS/AON instance files. It contains shared runtime state, per-instance register descriptions, callback hooks, and exported helper declarations.

## Important APIs, types, and functions
`struct jh7110_pinctrl` stores device, gpiochip, pin range, raw spinlock, MMIO base, pinctrl device, group-registration mutex, SoC info, and optional saved register buffer. `struct jh7110_gpio_irq_reg` describes IRQ register offsets. `struct jh7110_pinctrl_soc_info` supplies pins, GPIO count, DOUT/DOEN/GPI/GPIOIN register bases and masks, IRQ registers, saved-register count, and callbacks for one-pin muxing, padcfg base lookup, chained IRQ handling, and IRQ hardware init. Declared exports are `jh7110_set_gpiomux()`, `jh7110_pinctrl_probe()`, `jh7110_from_irq_desc()`, and `jh7110_pinctrl_pm_ops`.

## Control flow
Instance files instantiate `jh7110_pinctrl_soc_info` and attach it to OF match data. The common probe consumes that structure, and later calls the function pointers while serving pinmux, GPIO, IRQ, and PM operations.

## State and persistence behavior
The header defines but does not allocate state. The presence of `saved_regs` and `nsaved_regs` establishes the suspend/resume persistence model used by the common implementation.

## Dependencies and integration points
The header includes Linux pinconf and pinmux definitions and is included by all JH7110 source files. It is the integration point that lets SYS and AON vary register layout without duplicating common pinctrl/gpio/irq logic.

## Risks
The callback contract allows NULL callbacks, and the common implementation sometimes treats missing callbacks as no-op success. Register masks and bases are trusted, so a bad `jh7110_pinctrl_soc_info` can corrupt unrelated registers. `saved_regs` is a flat prefix copy, so instance files must choose `nsaved_regs` carefully.

## Test signals
Compile tests should include both instance files and the common file. Review checks should verify every `jh7110_pinctrl_soc_info` fills all fields required by enabled features, especially IRQ register bases, GPIO masks, saved register count, and padcfg callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/Kconfig

## Purpose
This Kconfig fragment defines the STM32 pinctrl family build options, including the common STM32 pinctrl core, multiple SoC pin table drivers, and the separate Hardware Debug Port pinctrl/GPIO driver.

## Important APIs, types, and functions
`PINCTRL_STM32` is the common tristate selected by SoC-specific symbols and selects `PINMUX`, `GENERIC_PINCONF`, `GPIOLIB`, `IRQ_DOMAIN_HIERARCHY`, and `MFD_SYSCON`. SoC symbols include STM32F429/F469/F746/F769/H743/MP135/MP157/MP257 and select the common core. `PINCTRL_STM32_HDP` is a separate tristate selecting `PINMUX`, `GENERIC_PINCONF`, `GPIOLIB`, and `GPIO_GENERIC`.

## Control flow
The whole fragment is gated by `ARCH_STM32 || COMPILE_TEST`. Kconfig selection controls Makefile object inclusion. Many MCU/MPU symbols default to their platform machine symbols; MP257 can be tristate and defaults on STM32MP25 or STM32 ARM64. HDP defaults on most STM32 architectures except ARM single-core ARMv7-M.

## State and persistence behavior
There is no runtime state. The selected symbols decide whether core probe helpers, SoC pin tables, PM ops, GPIO IRQ hierarchy support, and HDP support are built.

## Dependencies and integration points
The core depends on OF and syscon/IRQ-domain infrastructure because `pinctrl-stm32.c` parses DT GPIO-bank nodes and may configure a syscfg IRQ mux. HDP depends on OF/HAS_IOMEM and GPIO_GENERIC because it registers an output-only generic gpiochip.

## Risks
Most SoC symbols are bool, while MP257 and HDP are tristate; mixed built-in/module combinations should be checked for exported-symbol availability. HDP has no explicit `STM32_FIREWALL` dependency but uses guarded firewall calls under `IS_ENABLED(CONFIG_STM32_FIREWALL)`. The outer `ARCH_STM32 || COMPILE_TEST` block limits visibility, so cross-architecture build coverage relies on `COMPILE_TEST`.

## Test signals
Build matrix should cover each SoC symbol, HDP enabled alone, common core as built-in and module where possible, and `COMPILE_TEST`. Dependency tests should confirm `PINCTRL_STM32` pulls in IRQ hierarchy and syscon support needed by the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/Makefile

## Purpose
This Makefile maps STM32 pinctrl Kconfig symbols to the common core, SoC-specific pin table drivers, and the HDP driver.

## Important APIs, types, and functions
`obj-$(CONFIG_PINCTRL_STM32)` builds `pinctrl-stm32.o`. The STM32F/MP SoC symbols build their corresponding pin table objects, such as `pinctrl-stm32mp257.o`. `obj-$(CONFIG_PINCTRL_STM32_HDP)` builds `pinctrl-stm32-hdp.o`.

## Control flow
Kbuild includes object files according to Kconfig values. SoC drivers depend on the common core for exported `stm32_pctl_probe()` and PM helpers; HDP is independent and does not link against the common STM32 pinctrl core.

## State and persistence behavior
There is no runtime state. Build output determines which platform drivers can bind at runtime.

## Dependencies and integration points
This file integrates with `drivers/pinctrl/stm32/Kconfig`. Its layout mirrors the code structure: common core plus generated/static SoC pin description files, with HDP as a standalone driver.

## Risks
If a SoC symbol is enabled without the common core selection, unresolved references to `stm32_pctl_probe()` or PM helpers would occur; Kconfig selections guard this. Adding new SoC files requires both a Kconfig symbol and an object line.

## Test signals
Build tests should inspect object inclusion for all STM32 pinctrl symbols and verify module linking for MP257 and HDP. Static checks should ensure every SoC object selected here has matching OF compatible data and Kconfig entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32-hdp.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32-hdp.c

## Purpose
This driver controls the STM32 Hardware Debug Port, a small pinctrl/GPIO device that routes internal debug/observation signals to up to eight HDP pins and exposes output-only GPIO control for the HDP GPO value bits.

## Important APIs, types, and functions
`struct stm32_hdp` stores device state, MMIO base, clock, pinctrl device, optional firewall grants, generic gpiochip, cached mux/GPO state, function-name table, and firewall count. `stm32_hdp_pins[]` defines HDP0-7. `func_name_mp13`, `func_name_mp15`, and `func_name_mp25` provide 16 function names per HDP pin. Pinctrl callbacks expose one group per pin and use generic DT map/free helpers. Pinmux callbacks report `HDP_FUNC_TOTAL`, return function names, map each function to one HDP group, and write `HDP_MUX`. `stm32_hdp_probe()` maps resources, obtains firewall access, enables the clock, registers pinctrl, initializes a generic output-only gpiochip, and enables the HDP block. PM callbacks save/restore GPO and mux state.

## Control flow
Probe allocates state, optionally requests firewall access for all entries, maps resource 0, selects the function-name table from OF match data, enables the clock, registers and enables pinctrl, configures the generic gpiochip with data/set/clear registers, registers the gpiochip, writes `HDP_CTRL_ENABLE`, and logs hardware version. Pinmux `set_mux` computes the selected HDP line from `group_selector`, reduces the function selector modulo 16, updates that line's 4-bit field in `HDP_MUX`, and caches the full mux register. Suspend saves `HDP_GPOSET`, selects pinctrl sleep state, and disables the clock. Resume re-enables the clock, enables HDP, restores GPO set and mux state, and selects default state. Remove disables HDP and releases firewall grants.

## State and persistence behavior
The driver caches `mux_conf` on each mux update and `gposet_conf` on suspend. Hardware state lives in HDP control, mux, GPO set/clear/value, and version registers. The generic gpiochip is output-only (`GPIO_GENERIC_NO_INPUT`) and `get_direction` always reports output. Firewall grants are acquired at probe and explicitly released at remove.

## Dependencies and integration points
It depends on platform MMIO, clocks, pinctrl core, generic pinconf DT mapping, generic GPIO helpers, optional STM32 firewall APIs, and OF compatibles `st,stm32mp131-hdp`, `st,stm32mp151-hdp`, and `st,stm32mp251-hdp`. It does not use the common STM32 pinctrl core.

## Risks
Function selector space is flattened as 8*16 entries; wrong DT function indexes can select a valid but unintended signal. `set_mux` uses `func_selector %= HDP_FUNC`, so out-of-group function selectors wrap rather than fail. `gposet_conf` saves only the set register, not the clear/value register, so restored GPIO output state depends on hardware semantics. Firewall release is manual in remove; errors after partial firewall acquisition before drvdata lifetime ends need review against firewall helper semantics.

## Test signals
Tests should cover all three compatible function tables, pinmux selection on each HDP line, wrap behavior for selector values, output-only GPIO set/clear/value behavior, suspend/resume restoration of mux and GPO state, firewall-enabled and firewall-disabled builds, and removal disabling `HDP_CTRL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32-hdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32.c

## Purpose
This is the common STM32 pinctrl core. It registers one pin group per available pin, parses STM32 DT pinmux/config nodes, controls GPIO banks, implements pinmux and pinconf register programming, integrates GPIO lines with hierarchical IRQ domains and syscfg IRQ muxing, enforces secure/RIF access rules, and restores active pin state across suspend/resume.

## Important APIs, types, and functions
Major state types are `struct stm32_pinctrl_group`, `struct stm32_pin_backup`, `struct stm32_gpio_bank`, and `struct stm32_pinctrl`. Public exports are `stm32_pctl_probe()`, `stm32_pinctrl_suspend()`, and `stm32_pinctrl_resume()`. GPIO callbacks include request/free/get/set/direction/to_irq/valid-mask logic. IRQ-domain callbacks are `stm32_gpio_domain_translate/alloc/free/activate()`, with IRQ chip callbacks for set_type, resource lock, unmask/eoi retrigger, wake, and parent delegation. Pinctrl parsing is handled by `stm32_pctrl_dt_node_to_map()` and `stm32_pctrl_dt_subnode_to_map()`. Pinmux is `stm32_pmx_set_mux()`, `stm32_pmx_set_mode()`, and GPIO direction glue. Pinconf is implemented by helpers for drive, speed, bias, IO sync, skew delay, and `stm32_pconf_parse_conf()`.

## Control flow
Probe gets SoC match data, detects the parent IRQ domain, optionally requests a hwspinlock, filters pins by package, builds one group per pin, configures syscfg IRQ mux fields if interrupt support exists, registers the pinctrl device, counts GPIO bank child nodes, obtains each bank clock/reset, enables clocks, then registers each bank as a gpiochip and optional hierarchical IRQ domain. DT pinctrl states contain child nodes with `pinmux` arrays; each pinmux entry encodes pin number and function. The parser validates the function against the SoC pin descriptor, creates a mux map for the one-pin group, and attaches any generic pinconf configs. Runtime muxing finds the GPIO bank for the pin and writes AFR and MODER. Pinconf request paths validate line access, optionally acquire RIF semaphores, and RMW TYPER/SPEEDR/PUPDR/BSRR/ADVCFGR/DELAY registers. GPIO IRQ allocation reserves one shared IRQ-mux line per hardware IRQ number, sets parent fwspec, and writes syscfg mux fields on activation.

## State and persistence behavior
Per-bank `pin_backup[]` records output value, mode/alt, drive, speed, bias, advanced config, and skew delay whenever the driver writes those settings. Suspend disables bank clocks. Resume re-enables clocks and walks all groups, restoring only pins that are GPIO-owned or IRQ lines. IRQ mux selections are restored for IRQ pins. RIF semaphores may be acquired during request/config/restore and released on GPIO free. Hardware changes are immediate MMIO writes, guarded by per-bank spinlocks and optional hardware spinlock where cross-processor arbitration is needed.

## Dependencies and integration points
The driver depends on SoC pin tables using `struct stm32_pinctrl_match_data`, DT GPIO-bank child nodes, optional `st,syscfg` for IRQ mux regmap fields, optional hwspinlock phandle, clocks, resets, gpiolib, hierarchical IRQ domains, pinctrl-utils, and generic pinconf. It integrates with package filtering via `st,package`, secure pin invalidation through `STM32_GPIO_SECCFGR`, and RIF semaphore ownership through CID/SEM registers.

## Risks
The driver has many access-control paths: secure-control valid masks, RIF validity, and semaphore acquisition must agree or pins can be exposed incorrectly. `stm32_pmx_request()` acquires a RIF semaphore but has no matching release in pinmux ops, relying on GPIO free paths for GPIO users; non-GPIO pinctrl ownership deserves scrutiny. IRQ mux allocation allows only one bank per line, so consumers requesting the same line number on different banks get `-EBUSY`. Level IRQs are emulated through edge parent IRQs plus retrigger in EOI/unmask; missed level changes are a risk area. Resume restores only owned or IRQ pins, so bootloader/default pins not claimed by Linux are not preserved by this code. IO-sync/skew delay support is conditional and returns `-ENOTSUPP` when absent.

## Test signals
Coverage should include DT pinmux validation for valid/invalid functions, package-filtered pins, GPIO bank registration with and without `gpio-ranges`, secure and RIF-controlled lines, GPIO direction/value, pinconf drive/open-drain/slew/bias/level/skew/io-sync, IRQ allocation conflict across banks, level IRQ retrigger behavior, hwspinlock failure paths, syscfg deferred probe, and suspend/resume restoration of GPIO-owned and IRQ pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32.h

## Purpose
This header defines the common STM32 SoC pin-description format and the public common-core entry points used by STM32 pin table drivers.

## Important APIs, types, and functions
Macros encode and decode DT pinmux values: `STM32_PIN_NO(x)`, `STM32_GET_PIN_NO(x)`, and `STM32_GET_PIN_FUNC(x)`. Function constants define GPIO, alternate functions AF0-AF15, analog, reserved, and `STM32_CONFIG_NUM`. Package masks such as `STM32MP_PKG_AA` and `STM32MP_PKG_AL` allow SoC tables to filter pins by package. `struct stm32_desc_function` names one function slot. `struct stm32_desc_pin` combines a `pinctrl_pin_desc`, function table, and package mask. Macros `STM32_PIN`, `STM32_PIN_PKG`, and `STM32_FUNCTION` help build SoC pin arrays. `struct stm32_pinctrl_match_data` passes pin tables and feature flags to the common core. Exported declarations are `stm32_pctl_probe()`, `stm32_pinctrl_suspend()`, and `stm32_pinctrl_resume()`.

## Control flow
SoC files instantiate arrays of `stm32_desc_pin` and match-data records, then call the common probe from their platform-driver probe. The common core reads function tables, package masks, and feature flags to build runtime pin groups and register operations.

## State and persistence behavior
The header itself holds no state. Its structures define persistent contracts for SoC pin tables and PM helper usage. Package masks and function numbering must remain compatible with DT bindings.

## Dependencies and integration points
It depends on Linux pinctrl descriptors and generic pinconf definitions. It is included by the common STM32 core and all STM32 SoC-specific pin table drivers.

## Risks
DT pinmux encoding uses high bits for pin number and low 8 bits for function; mismatched bindings or macros will misroute pins. `STM32_CONFIG_NUM` sizes every function array, so adding new function constants changes table layout. Package filtering treats a zero package mask as generally available unless SoC tables and common code interpret it carefully.

## Test signals
Compile tests should cover all SoC tables using these macros. DT binding tests should verify encoded pinmux values decode to expected pin/function pairs. Package-specific boards should confirm unavailable pins are filtered from the runtime descriptor table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32.h -->
