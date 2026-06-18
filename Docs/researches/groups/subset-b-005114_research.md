# subset-b-005114 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp135.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp135.c

## Purpose
This file is the SoC-specific pin description and platform-driver registration unit for the STM32MP135 pin controller. It does not implement generic pinctrl mechanics itself; instead it provides the STM32 pinctrl core with a static `stm32_desc_pin` table for the MP135 package and binds that data to the `st,stm32mp135-pinctrl` devicetree compatible.

The table enumerates 135 physical/logical pins from banks PA through PI, using GPIO numbers 0-126 and 128-135. Each `STM32_PIN(...)` entry supplies a `PINCTRL_PIN(number, name)` plus supported alternate functions such as timers, USART/UART, SPI/I2S, I2C, SAI, SDMMC, FMC, LCD, DCMIPP, ETH1/ETH2, boot strap pins, and analog mode. GPIO function 0 and analog function 17 are common anchors across the entries.

## Important APIs, Types, And Data
- `stm32mp135_pins[]`: the authoritative MP135 pin/function matrix consumed by the STM32 pinctrl core. The array uses macros from `pinctrl-stm32.h` and includes the SoC-specific alternate-function numbers expected by hardware and devicetree pinmux encodings.
- `stm32mp135_match_data`: a `struct stm32_pinctrl_match_data` with `.pins`, `.npins`, and `.secure_control = true`. This tells the generic STM32 probe path that MP135 participates in secure pin configuration handling.
- `stm32mp135_pctrl_match[]`: OF match table with `compatible = "st,stm32mp135-pinctrl"` and `.data = &stm32mp135_match_data`.
- `stm32_pinctrl_dev_pm_ops`: wires late system sleep callbacks to shared `stm32_pinctrl_suspend` and `stm32_pinctrl_resume`.
- `stm32mp135_pinctrl_driver`: platform driver whose `.probe` is the shared `stm32_pctl_probe`.
- `stm32mp135_pinctrl_init()` plus `arch_initcall(...)`: registers the driver early during boot rather than through a module helper.

## Control Flow
At boot, `arch_initcall(stm32mp135_pinctrl_init)` calls `platform_driver_register`. When a devicetree node with `st,stm32mp135-pinctrl` appears, the platform bus invokes `stm32_pctl_probe`. The shared probe reads the OF match data, takes the static pin table and count, maps/registers GPIO/pinctrl state using common STM32 code, and later routes pin configuration, mux selection, GPIO, and suspend/resume calls through the common implementation.

There are no runtime branches in this file apart from platform registration. All pin selection behavior is declarative: the generic driver interprets the table entries and the board devicetree decides which alternate functions to activate.

## State And Persistence
The file defines immutable static data. Runtime state such as selected muxes, GPIO ownership, saved suspend state, and secure-control access decisions is owned by the shared STM32 pinctrl driver and hardware registers. Persistence across suspend is integrated by exposing the common late suspend/resume callbacks; this file only opts the MP135 instance into those callbacks.

## Dependencies And Integration Points
- Depends on Linux platform driver, OF matching, initcall, and the common STM32 pinctrl header.
- Integrates with `drivers/pinctrl/stm32/pinctrl-stm32.c` through `stm32_pctl_probe`, `stm32_pinctrl_suspend`, `stm32_pinctrl_resume`, and `struct stm32_pinctrl_match_data`.
- Integrates with devicetree bindings through `st,stm32mp135-pinctrl`; board DTS pinctrl nodes must use function numbers and pin names compatible with this table.
- The secure-control flag makes this file sensitive to the common driver's secure register access and firmware/SoC privilege model.

## Risks
- Table correctness is the main risk. A wrong alternate-function number or pin name silently routes a peripheral to the wrong pad, which usually appears as peripheral bring-up failure rather than a compile error.
- GPIO numbering gap before PI0 is intentional in the table; consumers must not assume the array index equals the hardware pin number.
- Secure-control behavior can expose integration failures only on systems where secure firmware denies or mediates pin register access.
- `arch_initcall` means the driver is built-in style here; if Kconfig or build rules ever allow modular use, registration style must be reviewed.

## Test Signals
- Build coverage for the STM32 pinctrl driver catches macro/type breakage.
- Devicetree binding validation and board DTS compilation catch compatible and pinctrl-property shape errors, but not every alternate-function mismatch.
- Runtime signals include successful probe of `stm32mp135-pinctrl`, GPIO bank registration, absence of secure-control access errors, correct pin state application for UART/I2C/SPI/ETH/LCD/SDMMC consumers, and successful suspend/resume with pins restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp135.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp157.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp157.c

## Purpose
This file supplies STM32MP157-specific pin data and platform-driver registration for the common STM32 pinctrl core. It covers both the main MP157 pin controller and the separate Z-bank controller used by the `st,stm32mp157-z-pinctrl` compatible.

The main `stm32mp157_pins[]` table describes banks PA through PK, 168 entries using GPIO numbers 0-167. The `stm32mp157_z_pins[]` table describes PZ0 through PZ7 using GPIO numbers 400-407. Entries use `STM32_PIN_PKG(...)`, so each pin is annotated with package availability bits such as `STM32MP_PKG_AA`, `STM32MP_PKG_AB`, `STM32MP_PKG_AC`, and `STM32MP_PKG_AD`. Alternate functions include the MP157 peripheral surface: timers, I2C, SPI/I2S, USART/UART, SAI, SDMMC, ETH1 GMII/MII/RGMII/RMII, DCMI, LCD, FMC, trace/HDP, eventout, and analog.

## Important APIs, Types, And Data
- `stm32mp157_pins[]`: main pin/function/package matrix for GPIO banks A-K.
- `stm32mp157_z_pins[]`: separate Z-bank matrix for secure/auxiliary PZ pins. It has its own match data so the common driver can register it independently from the main controller.
- `stm32mp157_match_data` and `stm32mp157_z_match_data`: both provide `.pins` and `.npins`; neither sets MP135/MP257-style secure, RIF, or IO sync flags in this file.
- `stm32mp157_pctrl_match[]`: maps `st,stm32mp157-pinctrl` to the main table and `st,stm32mp157-z-pinctrl` to the Z table.
- `stm32_pinctrl_dev_pm_ops`: delegates late system sleep handling to the shared STM32 suspend/resume operations.
- `stm32mp157_pinctrl_driver`: platform driver with shared `.probe = stm32_pctl_probe`.
- `stm32mp157_pinctrl_init()` and `arch_initcall(...)`: early built-in registration path.

## Control Flow
During architecture init, the driver registers with the platform bus. OF matching selects either the main match data or the Z-bank match data, and `stm32_pctl_probe` consumes the selected table to create the pinctrl device. All pin lookup, mux setting, GPIO range registration, pin configuration, and sleep-state handling are performed by the common STM32 pinctrl implementation.

The file's own control flow is deliberately minimal: its job is to bind static SoC data to the generic driver. Runtime behavior is a function of table contents plus board devicetree pin states.

## State And Persistence
The pin arrays and match data are read-only static configuration. Runtime state is persisted in hardware registers and common-driver software state. The PM ops hook ensures the MP157 instance participates in common late suspend/resume save and restore.

## Dependencies And Integration Points
- Depends on `pinctrl-stm32.h` macros/types and Linux OF/platform driver infrastructure.
- Integrates with board DTS through `st,stm32mp157-pinctrl` and `st,stm32mp157-z-pinctrl`; package metadata matters for validating or filtering pins on package variants.
- The Z-bank split is an important integration point because boards may have separate register regions and security domains for those pins.
- Peripheral drivers depend indirectly on this table when their `pinctrl-0` states request SDMMC, Ethernet, display, camera, UART, or other functions.

## Risks
- Package mask mistakes can expose pins not present on a package or hide valid ones.
- Main-bank and Z-bank numbering are disjoint; consumers must respect the 400-series PZ numbering used by the common STM32 binding.
- Alternate-function table drift against reference manuals or board schematics can create hard-to-debug peripheral failures.
- Because the file has no `MODULE_DEVICE_TABLE` or module helper and uses `arch_initcall`, registration assumes built-in kernel usage.

## Test Signals
- Compile-test and allmodconfig-style coverage catch macro/API drift in the common STM32 pinctrl interface.
- DTS validation and board boot on MP157 variants are the strongest behavioral tests, especially for package-specific pins and the Z-bank compatible.
- Runtime checks include successful pinctrl probe for both compatible strings, correct pin state application for SDMMC/Ethernet/display/camera/serial devices, visible GPIO lines, and clean suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp157.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp257.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp257.c

## Purpose
This file provides STM32MP257 pin and package data plus platform-driver registration for the common STM32 pinctrl implementation. It covers the main MP257 pin controller and a Z-bank controller, and unlike the older MP135/MP157 units it is module-friendly through `module_platform_driver` and an OF module device table.

The main `stm32mp257_pins[]` table covers 162 main-bank entries over PA-PK with GPIO numbers 0-45, 48-125, and 128-167. The `stm32mp257_z_pins[]` table covers PZ0-PZ9 with GPIO numbers 400-409. Entries use `STM32_PIN_PKG(...)` with MP257 package masks `STM32MP_PKG_AI`, `STM32MP_PKG_AK`, and `STM32MP_PKG_AL`. Alternate functions reflect newer MP257 peripherals such as SPI5-SPI8, USART/LPUART, I2C/I3C, MDF/ADF, ETH1/ETH2/ETH3, DCMI/PSSI/DCMIPP, LCD, FMC, FDCAN, timers, eventout, debug triggers, MCO, and analog.

## Important APIs, Types, And Data
- `stm32mp257_pins[]`: main MP257 pin/function/package matrix.
- `stm32mp257_z_pins[]`: Z-bank pin/function/package matrix for PZ0-PZ9.
- `stm32mp257_match_data` and `stm32mp257_z_match_data`: both set `.io_sync_control = true`, `.secure_control = true`, and `.rif_control = true` in addition to `.pins` and `.npins`. Those flags opt the common STM32 driver into MP257-specific synchronization, security, and resource isolation handling.
- `stm32mp257_pctrl_match[]`: OF table for `st,stm32mp257-pinctrl` and `st,stm32mp257-z-pinctrl`; exported via `MODULE_DEVICE_TABLE(of, ...)`.
- `stm32_pinctrl_dev_pm_ops`: uses common late sleep callbacks.
- `stm32mp257_pinctrl_driver`: shared-probe platform driver registered by `module_platform_driver`.

## Control Flow
Module or built-in initialization registers the platform driver. Matching a devicetree pinctrl node selects either main or Z-bank match data. `stm32_pctl_probe` then initializes the common STM32 pinctrl device with the selected table and feature flags. The common driver interprets flags to handle IO synchronization, secure-control, and RIF policy around register access.

This file contains no custom mux logic. The pin matrix and match flags are the control inputs consumed by shared STM32 code and by board DTS pin state declarations.

## State And Persistence
Static arrays and match data are immutable. Runtime mux, GPIO, IO sync, secure, and RIF state lives in the common driver and SoC registers. The PM ops hook opts the MP257 driver into common late suspend/resume state preservation.

## Dependencies And Integration Points
- Depends on `pinctrl-stm32.h`, Linux module/platform/OF infrastructure, and the common STM32 pinctrl implementation.
- Integrates with devicetree through `st,stm32mp257-pinctrl` and `st,stm32mp257-z-pinctrl`.
- Package masks control availability across AI/AK/AL packages.
- The `.io_sync_control`, `.secure_control`, and `.rif_control` flags integrate this static data with common-driver support for MP257 isolation and synchronization features.
- Peripheral integration spans Ethernet, camera/display, serial buses, memory bus, audio, timers, and GPIO consumers.

## Risks
- MP257 has several dense alternate-function rows; duplicate or mistaken alternate-function numbers can create ambiguous or wrong mux selection. For example, adjacent high-speed camera/display/Ethernet functions share many banks.
- Feature flags mean this table is coupled to firmware/security configuration. A board may fail to apply pin states if secure/RIF ownership does not match Linux expectations.
- Main-bank numbering skips PC14/PC15 and PH0/PH1-style holes relative to a simple contiguous package assumption; users must follow the explicit table.
- Module support adds aliasing expectations: the OF module table must stay in sync with compatible strings.

## Test Signals
- Compile and module alias generation should validate the module-platform registration path.
- DT binding validation should cover compatible strings, package-visible pins, and pinmux references.
- Runtime signals include successful probe as built-in or module, no secure/RIF access denials, correct pin state activation for I3C/I2C/SPI/UART/Ethernet/display/camera/FMC consumers, GPIO visibility, and suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp257.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/Kconfig

## Purpose
This Kconfig file exposes the Sunplus SP7021 pinmux/GPIO controller driver as `CONFIG_PINCTRL_SPPCTL`. It controls whether the SP7021 pinctrl implementation in this directory is built and declares the framework dependencies required by the driver.

## Important APIs, Types, And Symbols
- `config PINCTRL_SPPCTL`: tristate option labeled "Sunplus SP7021 PinMux and GPIO driver".
- `depends on SOC_SP7021`: restricts visibility/building to SP7021 SoC configurations.
- `depends on OF && HAS_IOMEM`: requires devicetree and MMIO access, both mandatory for `sppctl.c`.
- `select GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `GENERIC_PINCONF`, `PINCONF`, `PINMUX`, and `GPIOLIB`: ensures pinctrl, pinmux, pinconf, and GPIO subsystems are present.
- Help text states the driver provides both pin control and GPIO and that the module name is `sppinctrl`.

## Control Flow
Kconfig resolution runs before build. If selected as built-in or module, the Makefile compiles `sppinctrl` from `sppctl.o` and `sppctl_sp7021.o`. If dependencies are unmet, the option is unavailable and no runtime driver registration occurs.

## State And Persistence
The file has no runtime state. It persists build-time policy in the kernel configuration. The selected tristate value controls whether the driver is absent, built into the kernel, or built as a module according to the Kconfig model, although the C file uses `builtin_platform_driver`, so modular expectations deserve review with the current tree.

## Dependencies And Integration Points
- Integrates with the top-level pinctrl Kconfig through inclusion by the parent driver menu.
- Directly coordinates with `drivers/pinctrl/sunplus/Makefile`.
- The selected generic pinctrl symbols are prerequisites for the operations structures used in `sppctl.c`.
- Devicetree binding `sunplus,sp7021-pctl` is meaningful only when this option is enabled.

## Risks
- The help text says `M` builds module `sppinctrl`, but `sppctl.c` uses `builtin_platform_driver`; if the broader kernel tree still permits `m`, module build semantics should be verified.
- `select` can force dependencies without exposing their own prompts; changes in generic pinctrl APIs may require revisiting selected symbols.
- Overly narrow `SOC_SP7021` dependency can prevent compile coverage on non-SP7021 test configs unless explicitly enabled by build infrastructure.

## Test Signals
- `make menuconfig`/`olddefconfig` should expose `PINCTRL_SPPCTL` only when dependencies are satisfied.
- Built-in and module build tests should confirm that the declared tristate behavior matches the C registration macro.
- Runtime boot on SP7021 with `sunplus,sp7021-pctl` should probe only when the option is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/Makefile

## Purpose
This Makefile connects `CONFIG_PINCTRL_SPPCTL` to the Sunplus SP7021 pinctrl build products. It builds a composite object named `sppinctrl` from the generic driver logic and the SP7021 data table.

## Important APIs, Types, And Targets
- `obj-$(CONFIG_PINCTRL_SPPCTL) += sppinctrl.o`: includes the composite object when the Kconfig option is built-in or module.
- `sppinctrl-objs := sppctl.o sppctl_sp7021.o`: links the framework-facing implementation (`sppctl.c`) with the SoC data definitions (`sppctl_sp7021.c`).

## Control Flow
During kbuild, the tristate expansion of `CONFIG_PINCTRL_SPPCTL` determines whether `sppinctrl.o` is omitted, built into `vmlinux`, or prepared as a module object. The composite object layout means exported arrays declared in `sppctl.h` and defined in `sppctl_sp7021.c` are linked with the driver operations in `sppctl.c`.

## State And Persistence
There is no runtime state. The file persists build topology: driver logic and SoC tables must be compiled together.

## Dependencies And Integration Points
- Depends on Kconfig symbol `PINCTRL_SPPCTL`.
- Integrates `sppctl.c`, `sppctl.h`, and `sppctl_sp7021.c`.
- Module naming is aligned with the Kconfig help text's `sppinctrl`.

## Risks
- If new SoC data files are added, this Makefile must be extended or the driver will compile without the needed table definitions.
- If `sppctl.c` remains built-in-only via `builtin_platform_driver`, module builds of `sppinctrl` should be checked carefully.
- Missing object linkage would surface as unresolved externals for `sppctl_list_funcs`, `sppctl_pins_all`, and related size symbols declared in `sppctl.h`.

## Test Signals
- `make drivers/pinctrl/sunplus/` or full kernel builds should produce `sppinctrl.o` when `CONFIG_PINCTRL_SPPCTL=y/m`.
- Link tests catch missing SP7021 table definitions.
- `modinfo`/module alias checks are useful if the option is built as a module in this tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl.c

## Purpose
This file implements the Sunplus SP7021 pin controller and GPIO driver. It bridges the Linux pinctrl, pinmux, pinconf, and gpiolib APIs to SP7021 MMIO registers, while `sppctl_sp7021.c` supplies the SoC-specific pin/function/group tables declared in `sppctl.h`.

The driver supports three logical pin modes: fully-pinmux pins routed through MOON2 function control fields, group-pinmux functions routed through MOON1 group fields, and GPIO/IOP pins controlled by FIRST and MASTER registers plus GPIOXT direction/value/inversion/open-drain registers.

## Important APIs, Types, And Functions
- `struct sppctl_gpio_chip`: private GPIO wrapper containing GPIOXT and FIRST base addresses, embedded `gpio_chip`, and a spinlock for OE/direction-related register access.
- MMIO helpers such as `sppctl_first_readl`, `sppctl_gpio_master_readl`, `sppctl_gpio_oe_readl`, `sppctl_gpio_out_writel`, `sppctl_gpio_in_readl`, and inversion/open-drain helpers centralize register block offsets.
- Offset helpers `sppctl_get_reg_and_bit_offset`, `sppctl_get_moon_reg_and_bit_offset`, and `sppctl_prep_moon_reg_and_offset` translate GPIO offsets into register offsets and mask-protected MOON/GPIOXT write values.
- `sppctl_func_set`: configures fully-pinmux routing in MOON2. It subtracts `MUXF_L2SW_CLK_OUT`, packs mask and control fields, handles odd/even function placement, and writes the computed control word.
- `sppctl_gmx_set`: configures group pinmux fields in MOON1 using mask-protected writes.
- GPIO callbacks: `sppctl_gpio_get_direction`, `sppctl_gpio_direction_input`, `sppctl_gpio_direction_output`, `sppctl_gpio_get`, `sppctl_gpio_set`, `sppctl_gpio_set_config`, and optional `sppctl_gpio_dbg_show`.
- Pinconf callbacks: `sppctl_pin_config_get` and `sppctl_pin_config_set` support open-drain, level, IOP pseudo-config, inversion, output-low/output-high, and output-open-drain flags.
- Pinmux callbacks: `sppctl_get_functions_count`, `sppctl_get_function_name`, `sppctl_get_function_groups`, `sppctl_set_mux`, and `sppctl_gpio_request_enable`.
- Pinctrl callbacks: `sppctl_get_groups_count`, `sppctl_get_group_name`, `sppctl_get_group_pins`, optional `sppctl_pin_dbg_show`, `sppctl_dt_node_to_map`, and `pinctrl_utils_free_map`.
- Probe helpers: `sppctl_gpio_new`, `sppctl_group_groups`, `sppctl_pinctrl_init`, `sppctl_resource_map`, and `sppctl_probe`.

## Control Flow
`builtin_platform_driver(sppctl_pinctrl_driver)` registers a platform driver named `sppctl_sp7021`. A devicetree node with `compatible = "sunplus,sp7021-pctl"` invokes `sppctl_probe`. Probe allocates `struct sppctl_pdata`, maps four named MMIO resources (`moon2`, `gpioxt`, `first`, `moon1`), registers a `gpio_chip`, initializes and registers the pinctrl device, enables pinctrl, then adds the GPIO range to the pinctrl device.

GPIO requests enter through pinctrl's `.gpio_request_enable`. The driver reads FIRST and MASTER bits; if the pin is not already digital GPIO, it writes FIRST=GPIO and MASTER=GPIO using `sppctl_first_master_set`. Direction changes write mask-protected OE fields; output direction optionally writes an initial output value. Reads use GPIOXT IN registers; writes use GPIOXT OUT mask-protected fields.

Pinmux requests enter `sppctl_set_mux`. For fully-pinmux functions, the group selector is treated as a GPIO pin offset, FIRST is switched to mux mode, and MOON2 function routing is updated. For group-pinmux functions, every pin in the selected group is switched to mux mode and the MOON1 group field is updated. `sppctl_group_groups` builds a flattened group namespace: all GPIO pin names first, then every group-pinmux group, with `g2fp_maps` preserving function/group table indices.

Devicetree mapping accepts two styles. `sunplus,pins` is an array of packed 32-bit values: pin number in bits 31-24, pin type in bits 23-16, function in bits 15-8, and flags in bits 7-0. GPIO and IOP entries become `PIN_MAP_TYPE_CONFIGS_PIN`; fully-pinmux entries become `PIN_MAP_TYPE_MUX_GROUP`. Standard `function` plus `groups` properties add additional mux maps. `sunplus,zerofunc` immediately clears selected fully-pinmux or group-pinmux routes to "No map" during mapping.

## State And Persistence
Persistent hardware state lives in the SP7021 MOON1, MOON2, FIRST, and GPIOXT registers. The driver writes mask fields together with control fields to avoid unintended bit changes. Software state is devm-managed and tied to the platform device: MMIO bases, GPIO chip, pinctrl descriptor/device, GPIO range, flattened group names, and `g2fp_maps`.

The spinlock protects direction/OE-sensitive sequences and debug reads that depend on direction. Value writes and pinmux writes are direct MMIO operations without a global pinmux lock in this file, relying on subsystem serialization and mask-protected registers. There is no explicit suspend/resume save/restore; pin state persistence depends on hardware retention or normal pinctrl state reapplication by consumers.

## Dependencies And Integration Points
- Depends on gpiolib, pinctrl core, pinmux, generic pinconf, OF helpers, platform MMIO resource mapping, bitfield helpers, managed allocation, and debugfs seq output.
- Includes `<dt-bindings/pinctrl/sppctl-sp7021.h>` for packed devicetree constants such as `SPPCTL_PCTL_G_GPIO`, `SPPCTL_PCTL_G_IOPP`, `SPPCTL_PCTL_L_OUT`, and `MUXF_L2SW_CLK_OUT`.
- Includes `../core.h` and `../pinctrl-utils.h` for pinctrl internals and map freeing utilities.
- Consumes SoC data arrays from `sppctl_sp7021.c`: `sppctl_list_funcs`, `sppctl_pmux_list_s`, `sppctl_gpio_list_s`, `sppctl_pins_all`, `sppctl_pins_gpio`, and their size symbols.
- Integrates with the devicetree binding `sunplus,sp7021-pinctrl.yaml`, especially named resources and packed `SPPCTL_IOPAD(...)` values.

## Risks
- `sppctl_get_function_groups` searches `g2fp_maps` for the first group matching a function selector and then returns `&pctl->unq_grps[i]` with `*num_groups = f->gnum`. If the function has no mapped groups or index accounting drifts, this can point past the intended group range.
- `sppctl_dt_node_to_map` validates pin numbers for `sunplus,pins`, but fully-pinmux entries index `sppctl_list_funcs[pin_func]` without an explicit `pin_func < sppctl_list_funcs_sz` check in that branch.
- `sunplus,zerofunc` performs hardware writes during DT map creation, so parsing a pin state has side effects beyond returning maps.
- FIRST register updates are read-modify-write without a dedicated lock in `sppctl_first_master_set`, so concurrent mux/GPIO transitions could race if subsystem-level serialization is insufficient.
- There is no explicit remove path or suspend/resume callback; this is acceptable for built-in platform use but should be revisited for real module unload or low-power retention requirements.
- The Kconfig help mentions module builds, while this file uses `builtin_platform_driver`; build and unload behavior should be tested if `CONFIG_PINCTRL_SPPCTL=m`.

## Test Signals
- Build/link tests must include both `sppctl.o` and `sppctl_sp7021.o` to satisfy all extern data symbols.
- Devicetree schema tests should cover `compatible`, named resources, `sunplus,pins`, `function`/`groups`, and `sunplus,zerofunc`.
- Runtime probe should map all four resources and register both gpiochip and pinctrl successfully.
- GPIO tests should verify request-enable changes FIRST/MASTER, input/output direction, initial output level, get/set value, open-drain, input/output inversion flags, and debugfs output.
- Pinmux tests should exercise fully-pinmux functions, group-pinmux functions, zerofunc clearing, invalid pin numbers, invalid function numbers, and mixed GPIO/IOP/pinmux states.
- Power-management tests should check whether register state survives suspend or is reapplied by consumer pinctrl states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl.h

## Purpose
This header defines the shared register constants, helper macros, enums, data structures, and extern SoC table declarations used by the Sunplus SP7021 pinctrl driver. It is the contract between the generic implementation in `sppctl.c` and the SP7021 data file `sppctl_sp7021.c`.

## Important APIs, Types, And Data
- `SPPCTL_MODULE_NAME`: shared driver/gpiochip name `sppctl_sp7021`.
- GPIOXT/FIRST register offsets: `SPPCTL_GPIO_OFF_FIRST`, `SPPCTL_GPIO_OFF_MASTER`, `SPPCTL_GPIO_OFF_OE`, `SPPCTL_GPIO_OFF_OUT`, `SPPCTL_GPIO_OFF_IN`, `SPPCTL_GPIO_OFF_IINV`, `SPPCTL_GPIO_OFF_OINV`, and `SPPCTL_GPIO_OFF_OD`.
- Fully-pinmux field masks: `SPPCTL_FULLY_PINMUX_MASK_MASK`, `SPPCTL_FULLY_PINMUX_SEL_MASK`, and `SPPCTL_FULLY_PINMUX_UPPER_SHIFT`.
- MOON mask helpers: `SPPCTL_MOON_REG_MASK_SHIFT`, `SPPCTL_SET_MOON_REG_BIT(bit)`, and `SPPCTL_CLR_MOON_REG_BIT(bit)`.
- `SPPCTL_IOP_CONFIGS`: sentinel config value used by `sppctl_pin_config_set` to switch a pin to IOP mode.
- Table-construction macros `FNCE`, `FNCN`, and `EGRP`: concise initializers for functions with explicit groups, functions without groups, and group descriptors.
- `enum mux_first_reg`: requested FIRST register action (`mux_f_mux`, `mux_f_gpio`, `mux_f_keep`).
- `enum mux_master_reg`: requested MASTER register action (`mux_m_iop`, `mux_m_gpio`, `mux_m_keep`).
- `enum pinmux_type`: distinguishes fully-pinmux functions from group-pinmux functions.
- `struct grp2fp_map`: maps flattened group selectors back to function and group indices.
- `struct sppctl_pdata`: per-device driver state shared across pinctrl/gpio operations, including four MMIO bases, pinctrl descriptor/device, GPIO range, GPIO chip pointer, flattened group names, and selector maps.
- `struct sppctl_grp`: named group value and pin list.
- `struct sppctl_func`: function name, pinmux type, register offset, bit offset/length, group list, and group count.
- Extern declarations for SP7021 data arrays and sizes: `sppctl_list_funcs`, `sppctl_pmux_list_s`, `sppctl_gpio_list_s`, `sppctl_pins_all`, `sppctl_pins_gpio`, and their size symbols.

## Control Flow
The header has no executable control flow. Its definitions drive compile-time layout and runtime interpretation in `sppctl.c`. The macros create static function/group records in `sppctl_sp7021.c`; the enums select behavior in `sppctl_first_master_set` and `sppctl_set_mux`; the extern arrays are consumed during probe, group construction, pinctrl operations, and GPIO registration.

## State And Persistence
`struct sppctl_pdata` describes all software state kept for a probed SP7021 pinctrl device. Because allocation in the implementation is device-managed, the lifetime is tied to the platform device. Hardware state represented by offsets and masks persists in MMIO registers outside the header.

## Dependencies And Integration Points
- Depends on Linux bit, gpio, pinctrl, spinlock, kernel, and type headers.
- The register layout constants must match SP7021 hardware and the named MMIO resources mapped in `sppctl.c`.
- The table macros are used by `sppctl_sp7021.c`; field order must remain consistent with `struct sppctl_func` and `struct sppctl_grp`.
- Devicetree constants from `include/dt-bindings/pinctrl/sppctl*.h` must remain aligned with `sppctl_func` ordering and function IDs.

## Risks
- `SPPCTL_IOP_CONFIGS` is a magic config sentinel (`0xff`); collisions with future packed pinconf values or flag combinations would alter behavior.
- The extern arrays and size symbols rely on exact linkage with the data object. Missing Makefile entries cause link failures, while mismatched ordering can cause wrong function selection at runtime.
- Register masks encode hardware write-protection semantics; an incorrect mask shift or field width can write the wrong control bits.
- `struct sppctl_pdata` exposes implementation details across the driver and data code, so adding another SoC may require careful separation of SP7021-specific assumptions.

## Test Signals
- Compile tests catch struct/macro initializer mismatches between this header and `sppctl_sp7021.c`.
- Link tests catch missing extern data definitions.
- Runtime GPIO/pinmux tests validate that offsets, masks, and enum values produce expected FIRST, MASTER, MOON1, MOON2, and GPIOXT register changes.
- DT binding tests should confirm that function IDs and packed pin constants remain aligned with `sppctl_list_funcs` ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl.h -->
