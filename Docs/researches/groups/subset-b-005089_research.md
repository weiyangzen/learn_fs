# Research: subset-b-005089

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1625.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1625.c

## Purpose
This file is the Realtek RTD1625 SoC-specific pin controller description. It does not implement generic pinctrl algorithms itself; instead it builds static tables that describe four RTD1625 pin-control register banks and hands the matching descriptor to the shared Realtek pinctrl core in `pinctrl-rtd.h`/the companion core implementation. The supported banks are `iso`, `isom`, `ve4`, and `main2`, each exposed by its own device-tree compatible string.

## Important APIs, Types, And Data
- `enum rtd1625_*_pins_enum` assigns dense pin IDs for each bank. These enum values are used as indexes into pin, mux, and config arrays, so ordering is a behavioral contract.
- `struct pinctrl_pin_desc rtd1625_*_pins[]` publishes pin names to the Linux pinctrl core.
- `DECLARE_RTD1625_PIN()` creates one-pin arrays used by group descriptors.
- `struct rtd_pin_group_desc rtd1625_*_pin_groups[]` maps named groups to pin arrays.
- `struct rtd_pin_func_desc rtd1625_*_pin_functions[]` maps function names to group-name lists via `RTD1625_FUNC()`.
- `struct rtd_pin_desc rtd1625_*_muxes[]` is the core mux data: each `RTK_PIN_MUX()` entry names the affected pin, register offset, bit mask, and legal `RTK_PIN_FUNC()` encoded values.
- `struct rtd_pin_config_desc rtd1625_*_configs[]` and `struct rtd_pin_sconfig_desc rtd1625_*_sconfigs[]` describe pin configuration register fields, including pull, drive, and special drive-strength data.
- `struct rtd_reg_range`/`struct rtd_pin_range` constrain the register windows that the generic Realtek core may access for each bank.
- `struct rtd_pinctrl_desc rtd1625_*_pinctrl_desc` is the final per-bank descriptor consumed by `rtd_pinctrl_probe()`.

## Control Flow And Integration
The runtime path is deliberately short. The platform driver matches one of:
`realtek,rtd1625-iso-pinctrl`, `realtek,rtd1625-isom-pinctrl`, `realtek,rtd1625-ve4-pinctrl`, or `realtek,rtd1625-main2-pinctrl`. `rtd1625_pinctrl_probe()` calls `device_get_match_data()` to fetch the selected `rtd_pinctrl_desc`, then delegates to `rtd_pinctrl_probe(pdev, desc)`. The shared Realtek driver is responsible for registering the pinctrl device, decoding device-tree pin states, applying mux values, applying pin config, and using `realtek_pinctrl_pm_ops` for suspend/resume behavior.

The descriptor tables define the SoC surface:
- `iso` covers low-power/isolated pins, USB-CC pins, SDIO, many audio and video functions, EJTAG location selectors, RGMII/CSI voltage selectors, SPDIF mode/location selectors, and register ranges at offsets `0x0..0x58`, `0x120..0x130`, `0x180..0x18c`, and `0x1a0..0x1ac`.
- `isom` covers a small isolated management bank with GPIO0/1/28/29, IR receive location, UART10, pctrl, debug output, and tristate.
- `ve4` covers a broad media/peripheral bank: UART, GSPI, I2C, SD, TS, CSI, PCIe indicators, SPDIF, Ethernet LED/PHY alternate locations, PWM, and a `ve4_uart_loc` selector.
- `main2` covers eMMC, NAND, SD/HIF, Ethernet RGMII/RMII/LED/PHY, I2C1, SPI, debug, PLL test, and legacy EJTAG/HI function choices.

## State And Persistence
This file declares only immutable `static const` tables plus the platform driver object. Persistent hardware state lives in RTD1625 pinmux/config registers after the shared Realtek core writes encoded mux/config values. The file's own state is limited to module registration through `module_platform_driver()`. Suspend/resume persistence is delegated through `.pm = &realtek_pinctrl_pm_ops`; the register ranges included in each descriptor are the likely save/restore boundaries for the common core.

## Dependencies
It depends on Linux platform-driver, OF matching, module, and pinctrl headers, and on local Realtek abstractions from `pinctrl-rtd.h`: `rtd_pinctrl_desc`, `rtd_pin_desc`, `rtd_pin_config_desc`, `RTK_PIN_MUX`, `RTK_PIN_FUNC`, `RTK_PIN_CONFIG*`, `RTK_PIN_SCONFIG`, `SHIFT_LEFT`, `PADDRI_4_8`, and `realtek_pinctrl_pm_ops`.

## Risks And Review Notes
- The dense enum indexes must match all sparse designated initializer arrays. Adding/removing pins without updating mux/config arrays can silently leave pins without mux/config support.
- Function group lists are string-based. A typo is not caught by the C type system. One notable review signal is `rtd1625_iso_spdif_in_coaxial_groups`, which references `"spdif_sel"` while the visible selector pins are named `spdif_loc` and `spdif_in_mode`; this should be checked against the shared Realtek group lookup behavior and binding expectations.
- Several mux fields accept wide or unusual encoded values, such as `RTD1625_ISO_GPIO_112` using `GENMASK(4, 0)` and values beyond `0xf`. Mask/value alignment is critical.
- Register range declarations must include every offset referenced by mux/config/sconfig tables. Missing a range can break PM save/restore or access validation in the common core.
- Many pins share the same physical groups across mutually exclusive functions. Bad DT pin states can disrupt boot-critical busses such as eMMC, SDIO, RGMII/RMII, I2C, or UART.

## Test Signals
Useful validation includes `dtbs_check` for RTD1625 pinctrl compatibles and pin-state names, `make W=1`/`COMPILE_TEST` builds for array/type issues, boot logs showing `rtd1625-pinctrl` probe for all instantiated banks, debugfs pinctrl inspection to verify registered pins/groups/functions, and hardware tests that switch representative muxes for eMMC, SDIO, UART, I2C, Ethernet, audio, and video pins. Suspend/resume tests should verify that mux and config registers are restored for all listed register ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1625.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/Kconfig

## Purpose
This Kconfig file defines the selectable build matrix for Renesas pinctrl drivers. It gates the common SuperH/Renesas PFC core, optional GPIO support, legacy function-GPIO support, many SoC-specific PFC table files, and newer RZ-family pinctrl drivers.

## Important Symbols
- `PINCTRL_RENESAS` is the top-level Renesas pinctrl switch. It defaults to `y` for `ARCH_RENESAS` or `SUPERH`, is visible for `COMPILE_TEST` on other architectures, and selects SoC-specific symbols based on architecture/subtype symbols.
- `PINCTRL_SH_PFC` enables common PFC functionality and selects `GENERIC_PINCONF`, `PINMUX`, and `PINCONF`.
- `PINCTRL_SH_PFC_GPIO` adds GPIO support and selects `GPIOLIB` plus the common PFC core.
- `PINCTRL_SH_FUNC_GPIO` enables legacy function GPIOs and depends indirectly on GPIO support.
- `PINCTRL_PFC_*` entries select the common PFC core or GPIO-enabled PFC core for individual EMMA Mobile, R-Car, R-Mobile, SH-Mobile, and SuperH SoCs.
- `PINCTRL_RZA1`, `PINCTRL_RZA2`, `PINCTRL_RZG2L`, `PINCTRL_RZN1`, `PINCTRL_RZT2H`, and `PINCTRL_RZV2M` describe newer OF-based Renesas pinctrl families with their own dependencies and selected framework helpers.

## Control Flow And Integration
Kconfig has no runtime control flow, but it determines which objects from the sibling `Makefile` are built and which `#ifdef CONFIG_*` blocks in `core.c` are compiled. For example, `PINCTRL_PFC_EMEV2` selects `PINCTRL_SH_PFC`, which builds `core.o`, `pinctrl.o`, and `pfc-emev2.o`; it does not select `PINCTRL_SH_PFC_GPIO`, so `gpio.o` is not required for EMEV2. SuperH CPU subtype symbols select legacy PFC files and usually select `PINCTRL_SH_FUNC_GPIO`, enabling the deprecated function GPIO path.

## State And Persistence
The file contributes build-time configuration state only. Its choices persist in the generated kernel `.config` and determine compiled features, available compatible matches, and whether GPIO/pinconf support is present.

## Dependencies
It depends on architecture symbols (`ARCH_RENESAS`, `SUPERH`, many `ARCH_R8A*`/`CPU_SUBTYPE_*` symbols), `OF`, `64BIT`, and kernel subsystems such as `GPIOLIB`, `GENERIC_PINCONF`, `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `IRQ_DOMAIN_HIERARCHY`, `REGULATOR`, `PINMUX`, and `PINCONF`.

## Risks And Review Notes
- The `select` graph is the main risk. A SoC entry selecting `PINCTRL_SH_PFC` instead of `PINCTRL_SH_PFC_GPIO` changes whether GPIO registration is available.
- Top-level auto-selection must stay aligned with architecture symbols; otherwise a platform can boot without its pinctrl driver.
- COMPILE_TEST visibility is useful, but missing dependencies can cause build failures on non-native architectures.
- New SoCs require coordinated Kconfig, Makefile, OF match table, and table-file changes.

## Test Signals
Use `make olddefconfig` or targeted defconfigs to verify expected symbols. Run `make drivers/pinctrl/renesas/` under native and `COMPILE_TEST` configurations. Inspect `.config` to confirm that `PINCTRL_RENESAS` selects the intended `PINCTRL_PFC_*` symbol and that GPIO helper symbols are present only where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/Makefile

## Purpose
This Makefile maps Renesas pinctrl Kconfig symbols to object files. It wires the shared SH/Renesas PFC core, optional GPIO support, SoC-specific PFC data tables, and newer RZ-family drivers into the kernel build.

## Important Build Rules
- `obj-$(CONFIG_PINCTRL_SH_PFC) += core.o pinctrl.o` builds the common PFC runtime and pinctrl glue.
- `obj-$(CONFIG_PINCTRL_SH_PFC_GPIO) += gpio.o` adds the PFC GPIO bridge.
- Each `CONFIG_PINCTRL_PFC_*` symbol adds one SoC table object. Some RZ/G aliases intentionally reuse an R-Car table object, such as `R8A7742 -> pfc-r8a7790.o`, `R8A7743/R8A7744/R8A7793 -> pfc-r8a7791.o`, `R8A774A1/R8A77960/R8A77961 -> pfc-r8a7796.o`, and `R8A774E1 -> pfc-r8a77951.o`.
- RZ-family standalone drivers map to `pinctrl-rza1.o`, `pinctrl-rza2.o`, `pinctrl-rzg2l.o`, `pinctrl-rzn1.o`, `pinctrl-rzt2h.o`, and `pinctrl-rzv2m.o`.
- Under `CONFIG_COMPILE_TEST=y`, SuperH PFC objects receive CPU include paths through `CFLAGS_pfc-*.o`.

## Control Flow And Integration
The Makefile is build-time control flow. It must remain synchronized with `Kconfig` and with symbols referenced by `core.c`'s platform ID and OF match tables. If a Kconfig symbol selects `PINCTRL_SH_PFC`, the common core and pinctrl glue become available; if the symbol also selects `PINCTRL_SH_PFC_GPIO`, `gpio.o` is linked and `sh_pfc_register_gpiochip()` becomes available to the core.

## State And Persistence
It has no runtime state. Its outputs are linked object files determined by `.config`. Alias mappings persist as build rules and are important ABI assumptions for compatible SoCs sharing pin tables.

## Dependencies
It depends on Kconfig symbol names, object filenames in this directory, and architecture header paths under `arch/sh/include/cpu-*` for compile-testing legacy SuperH table files.

## Risks And Review Notes
- Mismatched Kconfig and object names cause missing drivers at link/build time.
- Alias mappings are compact but easy to break when a derivative SoC diverges from the reused table.
- The compile-test include path list must be updated when adding legacy SuperH PFC objects that require CPU-local headers.
- Duplicate object inclusion via multiple enabled alias symbols can compile the same object more than once into built-in code depending on Kbuild de-duplication behavior; this should be considered when expanding aliases.

## Test Signals
Run targeted builds for representative configs: common PFC only, PFC with GPIO, EMEV2, one R-Car alias, one SuperH legacy COMPILE_TEST, and each standalone RZ driver. `make V=1 drivers/pinctrl/renesas/` should show the expected object list and SuperH include flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/core.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/core.c

## Purpose
`core.c` is the common runtime for the SuperH/Renesas Pin Function Controller. It maps platform resources, translates physical register addresses to MMIO windows, programs mux/config registers, initializes pin ranges, registers the pinctrl and optional GPIO layers, supports PSCI suspend/resume register save/restore, and contains a DEBUG-only validator for SoC pinmux tables.

## Important APIs And Functions
- `sh_pfc_map_resources()` counts MEM/IRQ resources, maps MMIO windows with `devm_platform_get_and_ioremap_resource()`, and stores IRQs.
- `sh_pfc_phys_to_virt()` resolves SoC physical register addresses in table data to mapped virtual addresses.
- `sh_pfc_get_pin_index()` translates an external pin number into the dense index used by `info->pins`.
- `sh_pfc_read_raw_reg()`/`sh_pfc_write_raw_reg()` support 8/16/32-bit MMIO accesses; `sh_pfc_read()`/`sh_pfc_write()` wrap 32-bit access and unlock handling.
- `sh_pfc_unlock_reg()` supports SoCs that require writing the inverse of the target data to an unlock register or mask-derived unlock address.
- `sh_pfc_config_mux()` walks `pinmux_data` for a mark, resolves enum IDs to register fields with `sh_pfc_get_config_reg()`, filters by pinmux type, and writes matching config fields.
- `sh_pfc_init_ranges()` builds contiguous pin ranges and determines `nr_gpio_pins`.
- `sh_pfc_suspend_init()`, `sh_pfc_suspend_noirq()`, and `sh_pfc_resume_noirq()` save and restore mux/config-related registers when PSCI CPU suspend is available.
- `sh_pfc_check_driver()` and helper validators run only under `DEBUG` to check pins, groups, functions, enum conflicts, register bit conflicts, drive/bias/ioctrl metadata, data registers, and optional function GPIOs.
- `sh_pfc_probe()` is the platform probe entry that ties resource mapping, optional SoC init, PM setup, pinctrl registration, optional GPIO registration, and driver data storage together.

## Control Flow
At init time `postcore_initcall(sh_pfc_init)` optionally validates built-in tables and registers the platform driver. During probe, the driver obtains `sh_pfc_soc_info` from OF match data or platform ID data, allocates `struct sh_pfc`, maps resources, initializes the spinlock, runs optional SoC-specific `.init()`, initializes suspend storage, provides dummy pinctrl states for non-DT systems, derives pin ranges, registers pinctrl, optionally registers GPIO support, stores driver data, and logs the registered SoC name.

Mux changes flow from the pinctrl layer into `sh_pfc_config_mux()`. The function maps a requested mark to one or more enum IDs in `pinmux_data`, decides whether each enum belongs to function/input/output ranges, locates the corresponding config register field, and updates only that field with read-modify-write plus optional unlock.

## State And Persistence
Runtime state lives in `struct sh_pfc`: device pointer, SoC info pointer, mapped windows, IRQs, spinlock, computed pin ranges, `nr_gpio_pins`, optional GPIO object, and optional `saved_regs`. Hardware mux and pin configuration persist in MMIO registers. With `CONFIG_ARM_PSCI_FW`, selected registers from `cfg_regs`, `drive_regs`, `bias_regs`, and `ioctrl_regs` are saved at noirq suspend and restored at noirq resume.

DEBUG validation uses init-only globals (`sh_pfc_errors`, `sh_pfc_warnings`, register and enum scratch arrays). They are freed after init and do not affect runtime operation.

## Dependencies
The file depends on Linux platform, OF, pinctrl, PM, PSCI, MMIO, sys_soc, slab, and device-managed resource APIs. It consumes local data structures from `sh_pfc.h` and prototypes from `core.h`. It also depends on sibling `pinctrl.c` for `sh_pfc_register_pinctrl()` and, when enabled, `gpio.c` for `sh_pfc_register_gpiochip()`. SoC table symbols such as `emev2_pinmux_info` are pulled into OF/platform match tables behind `CONFIG_PINCTRL_PFC_*`.

## Risks And Review Notes
- `sh_pfc_phys_to_virt()` calls `BUG()` if a table register address is outside mapped resources. Bad SoC tables or device-tree resources can crash the kernel.
- Mux correctness depends on consistent `pinmux_data`, enum ranges, and config register descriptions. A single wrong enum can program the wrong register field.
- `sh_pfc_config_reg_helper()` uses shift/mask arithmetic; field widths must not overflow the target type.
- GPIO registration failure is intentionally ignored after pinctrl registration, which preserves existing pinctrl users but can hide missing GPIO functionality.
- PSCI save/restore covers only table categories known to `sh_pfc_walk_regs()`. Registers omitted from SoC metadata may lose state across suspend.
- DEBUG validation has fixed `SH_PFC_MAX_REGS` and `SH_PFC_MAX_ENUMS`; very large SoC tables can exceed these scratch limits and reduce check coverage.

## Test Signals
Test by building with representative SoC symbols and `CONFIG_DEBUG` to exercise table validation logs. Boot tests should confirm probe success, pinctrl registration, optional GPIO registration, and correct OF compatible matching. Runtime tests should apply several pin states and verify register fields. Suspend/resume tests are important on PSCI systems. Fault-oriented tests should check behavior when MEM or IRQ resource counts do not match expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/core.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/core.h

## Purpose
`core.h` is the internal interface for the Renesas/SuperH PFC core. It shares the small set of common data structures and functions needed by `core.c`, `pinctrl.c`, and `gpio.c`.

## Important APIs And Types
- `struct sh_pfc_pin_range { u16 start; u16 end; }` represents contiguous ranges of externally visible pin numbers. `core.c` computes these ranges and both pinctrl/GPIO paths use them for pin-to-index and pin-range registration.
- `sh_pfc_register_gpiochip()` is implemented in `gpio.c` when GPIO support is built.
- `sh_pfc_register_pinctrl()` is implemented in the pinctrl glue file and registers the PFC with the Linux pinctrl subsystem.
- `sh_pfc_read_raw_reg()`/`sh_pfc_write_raw_reg()` expose width-aware MMIO helpers for common and GPIO code.
- `sh_pfc_read()`/`sh_pfc_write()` expose 32-bit register access with physical-address translation and unlock handling.
- `sh_pfc_get_pin_index()` maps a hardware pin number into `info->pins[]` index space.
- `sh_pfc_config_mux()` programs mux fields for a mark and pinmux type.

## Control Flow And Integration
This header is included by the core implementation and helper layers. It creates the internal contract: `core.c` owns MMIO mapping, mux programming, and register helpers; `pinctrl.c` uses `sh_pfc_config_mux()` to apply mux states; `gpio.c` uses pin indexing and raw register helpers to implement GPIO get/set/direction integration.

## State And Persistence
The header owns no storage. It defines the shape of pin range state embedded in `struct sh_pfc` and exposes functions that mutate hardware registers or use the `struct sh_pfc` runtime object.

## Dependencies
It includes `<linux/types.h>` for integer types and local `sh_pfc.h` for `struct sh_pfc` and SoC metadata definitions.

## Risks And Review Notes
- Because this is an internal cross-file API, signature changes require synchronized updates in `core.c`, `gpio.c`, and pinctrl glue.
- `struct sh_pfc_pin_range` uses `u16`; SoCs with pin numbers beyond 65535 would need a type expansion.
- Callers must ensure `struct sh_pfc` has been initialized by the core before using helpers; the header does not encode lifecycle constraints.

## Test Signals
Build tests with `CONFIG_PINCTRL_SH_PFC` and `CONFIG_PINCTRL_SH_PFC_GPIO` catch prototype drift. Runtime pinmux and GPIO tests indirectly validate that the shared helpers operate with the expected `struct sh_pfc` state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/gpio.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/gpio.c

## Purpose
`gpio.c` adapts Renesas/SuperH PFC pin tables into Linux `gpio_chip` instances. It supports real pin GPIOs backed by PFC data registers and, when `CONFIG_PINCTRL_SH_FUNC_GPIO` is enabled, a deprecated legacy function-GPIO interface for old SH platforms.

## Important APIs, Types, And Functions
- `struct sh_pfc_gpio_data_reg` stores a `pinmux_data_reg` pointer and a `shadow` copy of the output register value.
- `struct sh_pfc_gpio_pin` stores the data-register index and bit number for one PFC pin.
- `struct sh_pfc_chip` combines a `struct sh_pfc *`, a `struct gpio_chip`, the memory window containing GPIO data registers, and the derived per-register/per-pin lookup tables.
- `gpio_setup_data_regs()` counts data registers, snapshots initial hardware values into shadows, and maps each PFC pin to a data register bit using `gpio_setup_data_reg()`.
- GPIO callbacks include request/free, direction input/output, get, set, and `to_irq`.
- `sh_pfc_register_gpiochip()` is the exported entry used by `core.c` after pinctrl registration.

## Control Flow
`sh_pfc_register_gpiochip()` first exits successfully if the SoC has no `data_regs`. It finds the MMIO window containing the first data register, exits successfully if no such window exists, validates IRQ resource count against `gpio_irq_size`, and registers a real GPIO chip through `sh_pfc_add_gpiochip()`. For non-DT legacy builds, it adds pin ranges and optionally registers a second function-GPIO chip.

For real GPIOs, `gpio_pin_request()` checks that the pin maps to a valid PFC pin with a nonzero enum ID, then delegates reservation to `pinctrl_gpio_request()`. Output direction sets the desired value in the shadow and writes the data register before asking pinctrl to switch direction. Input reads the hardware data register directly. `to_irq` scans the SoC `gpio_irq` tables and returns the platform IRQ associated with a GPIO.

For function GPIOs, `gpio_function_request()` warns once that the API is deprecated, then programs a function mux mark under `pfc->lock` by calling `sh_pfc_config_mux(mark, PINMUX_TYPE_FUNCTION)`.

## State And Persistence
The driver keeps a software shadow per data register to preserve unrelated output bits during GPIO writes. Initial shadow state is read from hardware at registration time. Direction and mux state persists in PFC hardware registers through the core pinctrl path. GPIO chip instances are device-managed and are cleaned up with the parent PFC device.

## Dependencies
It depends on Linux GPIO, pinctrl consumer, spinlock, device, slab, and module APIs. It relies on `core.h` for raw register access and pin-index/mux helpers, and on SoC data in `struct sh_pfc_soc_info`: `pins`, `data_regs`, `gpio_irq`, `func_gpios`, and range metadata initialized by `core.c`.

## Risks And Review Notes
- `gpio_get_data_reg()` indexes `chip->pins[idx]` after `sh_pfc_get_pin_index()`; normal request paths validate the index, but misuse from future paths could produce invalid indexing.
- `gpio_pin_set_value()` updates `shadow` without its own lock. Correctness relies on GPIO core serialization or external constraints; concurrent writes to different pins in the same register should be reviewed.
- `gpio_setup_data_reg()` calls `BUG()` if no data register bit matches a pin enum, so inconsistent SoC tables can crash during GPIO registration.
- If the GPIO data registers are not in the supplied memory resources, GPIO support silently stays disabled. This supports boards with separate GPIO devices but can hide resource mistakes.
- `gpio_pin_to_irq()` returns `0` on no match. Since IRQ 0 handling is architecture-dependent, callers should be checked for expectations; many modern GPIO drivers return negative errors for missing IRQs.

## Test Signals
Build with and without `CONFIG_PINCTRL_SH_PFC_GPIO` and `CONFIG_PINCTRL_SH_FUNC_GPIO`. Boot logs should show GPIO chip ranges when data registers and IRQ counts match. Use gpiolib tools or in-kernel consumers to request pins, toggle outputs, read inputs, and verify pinctrl direction transitions. IRQ mappings need board tests for every `gpio_irq` table entry. Legacy function-GPIO use should emit the deprecation notice once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-emev2.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-emev2.c

## Purpose
`pfc-emev2.c` is the SoC-specific pinmux data table for the Renesas Emma Mobile EV2 PFC. It describes pins, data marks, mux groups, functions, and PFC configuration registers, then exports `emev2_pinmux_info` for the common `sh-pfc` core.

## Important Data And Macros
- `CPU_ALL_PORT()` and `CPU_ALL_NOGP()` expand repeated GPIO-capable and no-GPIO pin lists.
- The large enum defines `PINMUX_DATA_*`, `PINMUX_FUNCTION_*`, and `PINMUX_MARK_*` IDs for data, function selector, and mux mark spaces.
- `pinmux_pins[]` lists GPIO-capable `PORT#` pins plus no-GPIO LCD pins.
- `pinmux_data[]` maps marks to one or more enum IDs used by `sh_pfc_config_mux()`.
- `EMEV_MUX_PIN()` creates single-pin group arrays.
- Many `*_pins[]` and `*_mux[]` arrays describe peripheral groups for external bus, camera, CompactFlash, DTV, IIC, JTAG, LCD/YUV, NTSC, PWM, SD/SDIO, TP33, UART, USB, and USI.
- `pinmux_groups[]` collects groups, including bus-width variants created by `BUS_DATA_PIN_GROUP()`.
- `pinmux_functions[]` maps user-visible function names to group lists.
- `pinmux_config_regs[]` describes GPSR and CHG_PINSEL registers at physical addresses around `0xe0140200` to `0xe01402a8`.
- `emev2_pinmux_info` publishes all data to the common PFC core.

## Control Flow And Integration
This file has no probe function. It is linked when `CONFIG_PINCTRL_PFC_EMEV2` is enabled. `core.c` includes `emev2_pinmux_info` in its OF match table for `renesas,pfc-emev2`. At runtime the common core receives this static table, registers pins/groups/functions, and uses `pinmux_data[]` plus `pinmux_config_regs[]` to program register fields when a pinctrl state requests one of the groups/functions.

Mux application uses the common flow: a pinctrl group chooses marks from a `*_mux[]` array, the core resolves each mark in `pinmux_data[]`, and then writes the corresponding GPSR/CHG_PINSEL fields from `pinmux_config_regs[]`.

## State And Persistence
All file-local data is immutable. Hardware state persists in EMEV2 PFC registers. The exported `sh_pfc_soc_info` does not include GPIO `data_regs`, drive, bias, or custom ops in this file, so this table primarily drives mux selection and pin/group/function enumeration.

## Dependencies
The file depends on local `sh_pfc.h` macros and types such as `SH_PFC_PIN_CFG`, `PINMUX_DATA`, `PINMUX_SINGLE`, `PINMUX_IPSR_NOFN`, `PINMUX_CFG_REG`, `PINMUX_CFG_REG_VAR`, `SH_PFC_PIN_GROUP`, `SH_PFC_FUNCTION`, and bus-data group helpers. It integrates with `core.c`, `pinctrl.c`, and the Kconfig/Makefile entries for `PINCTRL_PFC_EMEV2`.

## Risks And Review Notes
- This is dense hand-maintained SoC metadata. A wrong pin number, mark, enum selector, or register bit can route a peripheral to the wrong pad.
- Some no-GPIO LCD pins are represented by synthetic `PIN_NOGP` entries and mixed into LCD/YUV/TP33 groups. Group definitions must preserve the intended order and mux correspondence.
- `pinmux_data[]` contains multi-step mappings for alternate functions that combine GPSR function selection with CHG_PINSEL selector values. Missing either side causes partial mux programming.
- Register descriptions use both fixed-width and variable-width fields. The common DEBUG validator can catch some enum/register conflicts but not board-level electrical mistakes.
- EMEV2 selects `PINCTRL_SH_PFC` but not GPIO support in Kconfig, so consumers expecting GPIO chips from this table would be disappointed unless configuration changes add data-register support.

## Test Signals
Build with `CONFIG_PINCTRL_PFC_EMEV2` and, preferably, `DEBUG` to run the common PFC table checker. Boot on an EMEV2 DT with `renesas,pfc-emev2` and inspect pinctrl debugfs for the expected groups/functions. Hardware validation should apply representative states for LCD/YUV, SDIO, IIC, UART, external bus/CF, USI, and camera paths and confirm both GPSR and CHG_PINSEL fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-emev2.c -->
