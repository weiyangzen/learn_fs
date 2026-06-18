# Research: subset-b-005113 STM32 pinctrl descriptor tables

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f429.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f429.c

## Purpose

`pinctrl-stm32f429.c` is the SoC-specific pin description table and platform-driver registration unit for the STM32F429 pin controller. It does not implement pinctrl algorithms itself; instead it supplies static metadata to the shared STM32 pinctrl core in `pinctrl-stm32.c` through `struct stm32_pinctrl_match_data`.

The file declares 168 pins, numbered 0 through 167, covering GPIO ports PA through PJ with 16 pins each and PK with 8 pins. Each pin entry maps a Linux pinctrl pin descriptor such as `PINCTRL_PIN(0, "PA0")` to the STM32 alternate-function selector slots used by the generic STM32 pinctrl driver. Function slot 0 is always the GPIO function, slot 16 is `EVENTOUT`, and slot 17 is `ANALOG`; intermediate slots describe hardware alternate functions such as timers, USART/UART, I2C, SPI/I2S, Ethernet MII/RMII, SDIO, DCMI, FMC, LCD, OTG FS/HS, SAI1, JTAG/SWD/trace, CAN, and RTC outputs.

## Important APIs, Types, and Data

- `static const struct stm32_desc_pin stm32f429_pins[]`: the authoritative static pin/function table for this compatible.
- `STM32_PIN(...)`, `PINCTRL_PIN(...)`, and `STM32_FUNCTION(...)`: descriptor macros from the pinctrl and STM32 local headers. Each `STM32_FUNCTION(n, name)` stores the alternate-function selector number and user-visible function name in the fixed `functions[STM32_CONFIG_NUM]` array.
- `static struct stm32_pinctrl_match_data stm32f429_match_data`: binds `.pins` to `stm32f429_pins` and `.npins` to `ARRAY_SIZE(stm32f429_pins)`. No secure-control, I/O-sync, RIF, or package flags are set in this SoC table.
- `static const struct of_device_id stm32f429_pctrl_match[]`: matches device-tree nodes with `.compatible = "st,stm32f429-pinctrl"` and exposes `stm32f429_match_data` via `.data`.
- `static struct platform_driver stm32f429_pinctrl_driver`: registers the shared `stm32_pctl_probe` callback with driver name `stm32f429-pinctrl`.
- `arch_initcall(stm32f429_pinctrl_init)`: registers the platform driver early during kernel boot.

The table is data-heavy. Representative patterns include PA0-PA15 for low-numbered GPIOs and common peripheral pins, PB/PC/PD/PE/PF/PG for dense timer, serial, SDIO, Ethernet, FMC, and DCMI routing, PH/PI/PJ/PK for oscillator, trace, LCD, camera, FMC, and high pin-count package functions. Pins retain numeric holes only where the SoC itself has package/function constraints; the F429 table covers the full 0-167 range.

## Control Flow

The runtime control flow is intentionally short:

1. The built-in initcall invokes `stm32f429_pinctrl_init()`.
2. `stm32f429_pinctrl_init()` calls `platform_driver_register(&stm32f429_pinctrl_driver)`.
3. When the platform bus finds a device-tree node compatible with `st,stm32f429-pinctrl`, the kernel binds it to this driver.
4. The shared `stm32_pctl_probe()` receives the `platform_device`, obtains the match data from the OF match table, and uses this file's pin table to register pins, groups, functions, GPIO ranges, and pin configuration support.
5. Later pinmux requests from device-tree states are resolved by the common driver against the `stm32_desc_pin` entries provided here.

There is no per-pin executable logic in this file after registration. The behavior comes from the data table and the shared STM32 core.

## State and Persistence

The pin table and OF match data are static kernel data. They are effectively immutable after boot. This file keeps no runtime state, owns no locks, allocates no memory directly, and persists nothing across boots. Hardware register programming, suspend/resume state, and pin configuration caching are delegated to the common STM32 pinctrl implementation.

Because this is built in via `arch_initcall`, the driver is intended to be present before dependent platform devices request their pin states. The absence of a module exit path is normal for this built-in pinctrl driver.

## Dependencies and Integration Points

- Linux headers: `<linux/init.h>`, `<linux/of.h>`, and `<linux/platform_device.h>`.
- Local integration: `pinctrl-stm32.h` defines descriptor structures, function-slot constants, and the shared `stm32_pctl_probe()` prototype.
- Device tree: board DTS files must use `compatible = "st,stm32f429-pinctrl"` and pinmux/function names that match this table.
- Generic pinctrl and gpiolib: the shared STM32 core converts this descriptor table into Linux pinctrl pins, functions, groups, and GPIO ranges.
- Peripheral drivers: Ethernet, LCD, DCMI, SDIO, USART/UART, SPI/I2S, I2C, timers, USB OTG, FMC, CAN, and debug/trace peripherals depend on these names and AF numbers when applying pinctrl states.

## Risks and Edge Cases

- A wrong alternate-function number silently programs incorrect hardware muxing even though the kernel data structures remain valid.
- Function-name drift between this table and device-tree bindings can break board pinctrl states at probe time.
- Multi-name function strings such as `TIM2_CH1 TIM2_ETR` or `ETH_MII_RX_CLK ETH_RMII_REF_CLK` intentionally represent shared AF selectors; consumers and reviewers must preserve those combined names rather than splitting them as independent selector slots.
- Debug pins (`JTMS SWDIO`, `JTCK SWCLK`, `JTDO TRACESWO`, `NJTRST`, trace data pins) can conflict with board debug access if selected by an alternate state.
- High-density peripheral groups such as FMC, LCD, DCMI, Ethernet, and SDIO require many pins to be consistent. A single descriptor typo can produce hard-to-diagnose board-level failures.
- This table has no package filtering (`pkg` remains unset), so package-specific absence of pins must be handled by board design and device-tree usage rather than this match data.

## Test Signals

- Build coverage: compile the STM32 pinctrl driver with this file enabled and check for descriptor macro or type regressions.
- Boot/probe coverage: a DTS node with `st,stm32f429-pinctrl` should bind to `stm32f429-pinctrl` and call the shared probe successfully.
- Device-tree validation: board pinctrl states should only reference pin/function names present in `stm32f429_pins`.
- Hardware smoke tests: exercise GPIO, USART, I2C, SPI/I2S, Ethernet MII/RMII, SDIO, LCD, DCMI, USB OTG, and FMC configurations on representative F429 boards.
- Regression checks: compare AF numbers against the STM32F429 datasheet/reference manual when adding or changing descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f429.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f469.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f469.c

## Purpose

`pinctrl-stm32f469.c` supplies the STM32F469-specific pin and alternate-function map to the shared STM32 pinctrl driver. Its role is parallel to the F429 file but with the F469/F46x function set, especially richer LCD, DSI host, QuadSPI, SAI, FMC, trace, and package-constrained high-port coverage.

The file declares 159 pins over numeric IDs 0 through 167. Ports PA through PI are fully represented with 16 pins each, while PJ contributes 10 pins and PK contributes 5 pins. Every listed pin has a GPIO function at slot 0, `EVENTOUT` at slot 16, and `ANALOG` at slot 17. The intervening alternate-function slots describe SoC mux choices for timers, serial buses, audio, camera/display, memory controller, Ethernet, USB OTG, SDIO, QuadSPI, DSI host, trace/debug, and CAN.

## Important APIs, Types, and Data

- `static const struct stm32_desc_pin stm32f469_pins[]`: complete F469 pin descriptor table.
- `STM32_PIN`, `PINCTRL_PIN`, and `STM32_FUNCTION`: macros that build `struct stm32_desc_pin` entries and fixed-position function descriptors.
- `static struct stm32_pinctrl_match_data stm32f469_match_data`: provides `.pins = stm32f469_pins` and `.npins = ARRAY_SIZE(stm32f469_pins)` to the common STM32 driver.
- `static const struct of_device_id stm32f469_pctrl_match[]`: matches `st,stm32f469-pinctrl`.
- `static struct platform_driver stm32f469_pinctrl_driver`: binds `stm32_pctl_probe` to the compatible-specific match table.
- `arch_initcall(stm32f469_pinctrl_init)`: registers this built-in platform driver during early boot.

Compared with the F429 descriptor table, the F469 data adds or emphasizes QuadSPI bank pins, DSI host pins, more LCD alternates, and F469-specific remaps on PA/PB/PC and high ports. The table also omits some PJ and PK entries that exist in full 168-pin maps, reflecting the F469 descriptor coverage in this source rather than providing a dense 0-167 array.

## Control Flow

Control flow is registration-oriented:

1. `stm32f469_pinctrl_init()` runs as an `arch_initcall`.
2. It registers `stm32f469_pinctrl_driver` with the platform bus.
3. OF platform matching binds nodes with `compatible = "st,stm32f469-pinctrl"` to the driver.
4. The shared `stm32_pctl_probe()` consumes `stm32f469_match_data`.
5. Runtime pinmux and pinconf operations are handled by the common STM32 implementation using this file's static descriptors.

The file has no callback beyond `probe`; no suspend, resume, remove, or runtime PM hooks are declared locally.

## State and Persistence

All data in this file is static descriptor state. It does not mutate after initialization and does not directly store hardware state. Persistence is limited to the lifetime of the running kernel image. Register programming and restoration, if any, are handled by shared STM32 pinctrl code and platform power-management paths outside this file.

Because the table is not package-filtered with `STM32_PIN_PKG`, package availability is implicit in board design and pin usage. The `.pkg`, `.secure_control`, `.io_sync_control`, and `.rif_control` match-data features are not used here.

## Dependencies and Integration Points

- Depends on `pinctrl-stm32.h` for descriptor structures and the shared probe entry point.
- Uses Linux platform-driver and OF matching infrastructure.
- Integrates with DTS pinctrl nodes using `st,stm32f469-pinctrl` and pin function names exactly as emitted in the descriptor table.
- Serves downstream peripheral drivers for LCD/DSI, DCMI, QuadSPI, FMC, Ethernet, SDIO, USB OTG, SAI/I2S/SPI, UART/USART, I2C, timers, CAN, and trace/debug by allowing their pinctrl states to resolve to numeric AF selectors.

## Risks and Edge Cases

- The F469 table has fewer descriptor entries than the full numeric range. Board DTS files that assume all PJ/PK pins from sibling SoCs exist can fail to resolve pin states.
- QuadSPI, LCD, DSI, and FMC signals occupy many alternate-function slots and often share physical pins with Ethernet, camera, or trace; mismatched board states may produce pin conflicts outside the pinctrl driver's static validation.
- Several names encode multiple signal aliases in one selector string, for example combined MII/RMII or timer channel/event labels. Renaming these can break existing DTS consumers.
- The data file has no dynamic validation against silicon revision or package, so descriptor correctness depends on maintaining the table against ST reference material.
- Since registration is built-in and early, a bad OF match-data pointer or malformed descriptor entry affects boot-time pinctrl availability for all dependent devices.

## Test Signals

- Compile with STM32 pinctrl enabled to validate macros and OF table references.
- Boot an F469 DTS and confirm the platform driver binds under `stm32f469-pinctrl`.
- Use `pinctrl` debugfs, if enabled, to inspect registered pins/functions and compare expected PA-PI plus partial PJ/PK coverage.
- Probe board peripherals that stress F469-specific routes: QuadSPI, LCD/DSI, FMC SDRAM/NOR, DCMI, Ethernet, SDIO, and SAI.
- Validate new pin changes against DTS consumers and ST alternate-function tables, paying close attention to the partial high-port coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f469.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f746.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f746.c

## Purpose

`pinctrl-stm32f746.c` provides the static pin descriptor table for STM32F746 devices and registers the compatible-specific platform driver shell that delegates to the common STM32 pinctrl core. The F746 table covers the full 168-pin range from PA0 through PK7 and adds F7-generation peripheral muxing compared with the F4 tables, including SDMMC1 naming, LPTIM1, I2C4, richer SAI2, SPDIFRX, HDMI CEC, and wider UART alternate mappings.

Each `STM32_PIN` entry names the Linux pin, then lists the hardware selector slots for GPIO, alternate functions 1-15 when available, `EVENTOUT`, and `ANALOG`. The descriptors are consumed by the shared driver to expose pin groups/functions and to program the SoC GPIO alternate-function registers.

## Important APIs, Types, and Data

- `static const struct stm32_desc_pin stm32f746_pins[]`: F746 pin/function metadata, 168 entries, ports PA-PJ complete and PK0-PK7.
- `STM32_FUNCTION(num, name)`: maps an STM32 AF slot to one or more signal names for a pin.
- `static struct stm32_pinctrl_match_data stm32f746_match_data`: passes the pin table and count into `stm32_pctl_probe`.
- `static const struct of_device_id stm32f746_pctrl_match[]`: contains the `st,stm32f746-pinctrl` compatible string.
- `static struct platform_driver stm32f746_pinctrl_driver`: names the driver `stm32f746-pinctrl` and uses the common probe.
- `stm32f746_pinctrl_init()` plus `arch_initcall`: performs early built-in registration.

The table contains common F7 peripheral families: `TIM*`, `USART*`, `UART*`, `I2C1` through `I2C4`, `SPI*`/`I2S*`, `SAI1`, `SAI2`, `ETH_*`, `OTG_*`, `FMC_*`, `LCD_*`, `DCMI_*`, `SDMMC1_*`, `QUADSPI_*`, `SPDIFRX_*`, `LPTIM1_*`, trace/debug, `CAN1`, `CAN2`, and RTC/MCO signals.

## Control Flow

1. During early init, the kernel calls `stm32f746_pinctrl_init()`.
2. The function registers `stm32f746_pinctrl_driver`.
3. The platform bus binds device-tree nodes compatible with `st,stm32f746-pinctrl`.
4. `stm32_pctl_probe()` receives the match data and creates the pinctrl device from `stm32f746_pins`.
5. Subsequent device pinctrl state selection is resolved by common code using the static AF numbers and names from this table.

No SoC-specific control decisions are implemented here; F746-specific behavior is fully encoded in data.

## State and Persistence

`stm32f746_pins`, match data, and match table are static kernel objects. The file does not allocate or persist runtime state. It does not implement resume or suspend itself, although the common driver has suspend/resume helpers declared in the shared header. Any hardware register state lives in the common STM32 pinctrl structures and the GPIO/pinctrl hardware, not in this descriptor file.

No match-data feature flags are enabled, so the file does not opt into secure control, I/O sync control, RIF control, or package filtering.

## Dependencies and Integration Points

- `pinctrl-stm32.h` defines `struct stm32_desc_pin`, `struct stm32_desc_function`, `struct stm32_pinctrl_match_data`, and the common probe.
- OF/platform infrastructure provides compatible-string matching and driver registration.
- Device-tree pinctrl states must use names and pins present in this table.
- Peripheral integration spans SDMMC1, Ethernet, LCD-TFT, camera DCMI, USB OTG FS/HS, FMC external memory, audio interfaces, SPDIFRX, HDMI CEC, timers, UART/USART, SPI/I2S, I2C, CAN, and debug/trace.

## Risks and Edge Cases

- F746 uses `SDMMC1_*` naming where older F4 tables use `SDIO_*`; DTS reuse between families must account for those names.
- The file includes dense high-port LCD/FMC/DCMI mappings. Pin conflicts can be legal at descriptor level while impossible in a board's simultaneous peripheral configuration.
- Several pins have additional F7-specific functions in AF4/AF5/AF9/AF10/AF11 compared with F4 relatives; copying entries between sibling SoCs can introduce silent hardware mux bugs.
- No package masks are used. Package-specific availability is not enforced here.
- Since there is no local validation logic, tests must catch typos in selector numbers and function strings through build, DTS, and hardware paths.

## Test Signals

- Kernel build with the F746 pinctrl object included.
- Device-tree boot with `st,stm32f746-pinctrl` and successful `stm32f746-pinctrl` binding.
- Pinctrl debugfs or boot logs showing 168 registered pins.
- Peripheral smoke tests for F7-specific routes such as SDMMC1, QUADSPI, SAI2, SPDIFRX, LPTIM1, HDMI CEC, and I2C4.
- Cross-check changed entries against the STM32F746 alternate-function tables and existing board DTS pin states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f746.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f769.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f769.c

## Purpose

`pinctrl-stm32f769.c` describes the STM32F769 pin multiplexing matrix and registers the corresponding built-in platform driver. It is a full 168-pin PA0-PK7 table like F746, but with expanded F769-specific alternate functions. Notable additions and increases include CAN3, MDIOS, DFSDM, SDMMC2, additional UART4/UART5/UART7 routes, SPI6, DSI, broader LCD mappings, and more QuadSPI/FMC coverage.

The file is data-driven. It gives the common STM32 pinctrl core enough information to translate device-tree pinctrl states into hardware alternate-function numbers for the F769 family.

## Important APIs, Types, and Data

- `static const struct stm32_desc_pin stm32f769_pins[]`: static F769 descriptor table with 168 pin entries.
- `STM32_PIN(PINCTRL_PIN(...), STM32_FUNCTION(...), ...)`: each entry binds a pin name/number to AF-slot names.
- `static struct stm32_pinctrl_match_data stm32f769_match_data`: references the descriptor table and array size.
- `static const struct of_device_id stm32f769_pctrl_match[]`: matches device-tree compatible `st,stm32f769-pinctrl`.
- `static struct platform_driver stm32f769_pinctrl_driver`: delegates probe to `stm32_pctl_probe`.
- `stm32f769_pinctrl_init()` and `arch_initcall`: early platform-driver registration.

Descriptor content includes common STM32 families and F769-oriented expansions: `DFSDM_*` appears widely, `SDMMC1_*` and `SDMMC2_*` coexist, `CAN3_*` appears in addition to CAN1/CAN2, `MDIOS_MDC/MDIO` is present, SPI6 mappings are broader, and display-related `LCD_*` and `DSI*` alternates are dense.

## Control Flow

The file follows the standard STM32 descriptor-driver sequence:

1. `arch_initcall` invokes `stm32f769_pinctrl_init()`.
2. The init function registers `stm32f769_pinctrl_driver`.
3. OF matching selects the driver for `st,stm32f769-pinctrl` nodes.
4. The common `stm32_pctl_probe()` reads `.data = &stm32f769_match_data`.
5. The common driver registers pinctrl entities and later programs pinmux state according to requests from board and peripheral drivers.

All device-specific branching is expressed through the descriptor table rather than local code.

## State and Persistence

This file contains immutable static metadata. It has no local dynamic state, no allocations, no refcounting, no locks, and no persistent storage. Hardware state and suspend/resume behavior are outside this file, in the common STM32 pinctrl core and platform power-management paths.

The match data does not enable package-specific filtering or newer security/I/O-control flags. All described pins are exposed to the common driver for this compatible.

## Dependencies and Integration Points

- Relies on Linux OF/platform driver infrastructure for binding.
- Relies on `pinctrl-stm32.h` for descriptor layout and `stm32_pctl_probe`.
- Integrates with DTS consumers through exact function strings such as `SDMMC2_D0`, `DFSDM_DATIN*`, `MDIOS_MDIO`, `CAN3_RX`, `QUADSPI_BK*`, `LCD_*`, and `FMC_*`.
- Feeds peripheral drivers for storage, audio, display/camera, memory, Ethernet/MDIO, USB, serial, timers, CAN, and debug/trace by making their pin states selectable.

## Risks and Edge Cases

- F769 has many more valid alternatives per pin than F746. Reviewers should avoid assuming sibling F7 AF numbers are interchangeable.
- DFSDM, SDMMC2, QuadSPI, FMC, DSI/LCD, and Ethernet/MDIOS share high-value pins; legal individual pin states can still conflict at board level.
- Combined labels for MII/RMII, timer channel/break, and serial signal variants are part of the ABI consumed by existing DTS files.
- Since the descriptor table is the only SoC-specific source of truth, typos in names or AF slots may not be caught until a specific peripheral route is tested on hardware.
- The lack of package masks can expose pins that are not bonded out on some package variants.

## Test Signals

- Build the kernel object and verify no macro/array issues.
- Boot an STM32F769 board DTS and confirm the `stm32f769-pinctrl` platform driver probes.
- Inspect pinctrl debugfs for 168 pins and expected F769-specific functions.
- Exercise routes for DFSDM, SDMMC2, CAN3, MDIOS, QuadSPI, DSI/LCD, FMC, Ethernet, and SPI6 on hardware or board tests.
- For descriptor edits, run DTS grep/build checks for affected function names and compare selector numbers against F769 reference documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f769.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32h743.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32h743.c

## Purpose

`pinctrl-stm32h743.c` is the STM32H743-specific pin descriptor and platform-driver registration file. It is structurally identical to the F4/F7 descriptor units, but its table represents the H7 mux matrix with many H7-only or H7-expanded peripherals. It covers 168 pins from PA0 through PK7 and provides the common STM32 pinctrl core with GPIO, AF1-AF15, event, and analog choices for each pin.

The H743 table adds substantially richer high-performance and mixed-signal routing than the F7 files, including HRTIM, LPTIM2-LPTIM5, TIM15/TIM16/TIM17, SDMMC1/2 expansions, SAI3/SAI4, LPUART1, SWPMI, comparator-triggered timer break functions, broader CAN1/CAN2, more Ethernet/MDIOS, DFSDM, and FMC coverage.

## Important APIs, Types, and Data

- `static const struct stm32_desc_pin stm32h743_pins[]`: complete H743 pin descriptor array with 168 entries.
- `STM32_PIN`, `PINCTRL_PIN`, `STM32_FUNCTION`: descriptor macros used throughout the table.
- `static struct stm32_pinctrl_match_data stm32h743_match_data`: exports `.pins` and `.npins` to shared probe logic.
- `static const struct of_device_id stm32h743_pctrl_match[]`: matches `st,stm32h743-pinctrl`.
- `static struct platform_driver stm32h743_pinctrl_driver`: names the driver `stm32h743-pinctrl` and delegates to `stm32_pctl_probe`.
- `static int __init stm32h743_pinctrl_init(void)` plus `arch_initcall`: registers the platform driver early.

The table is dense across most AF slots. It includes standard GPIO and `ANALOG` coverage for every pin, `EVENTOUT` on every pin, and H7-specific routing such as `HRTIM_CH*`, `HRTIM_EEV*`, `LPTIM*_IN/OUT/ETR`, `SAI4_*`, `LPUART1_*`, `SWPMI_*`, `TRGIN/TRGOUT/TRGIO`, `COMP*` interactions, and expanded SDMMC/FMC/LCD/ETH/DFSDM signals.

## Control Flow

1. `stm32h743_pinctrl_init()` is invoked through `arch_initcall`.
2. It calls `platform_driver_register(&stm32h743_pinctrl_driver)`.
3. The platform bus matches a device-tree node compatible with `st,stm32h743-pinctrl`.
4. `stm32_pctl_probe()` receives `stm32h743_match_data` from the OF match table.
5. Common STM32 pinctrl code uses `stm32h743_pins` to register pins/functions and service later pinmux/pinconf requests.

The file does not implement custom H743 mux programming; the only H743-specific behavior is the descriptor data selected by compatible string.

## State and Persistence

All SoC data here is static and immutable. No runtime state is owned by this file. It performs no direct register access and does not persist configuration across suspend or reboot. Power-management and hardware register state belong to the common STM32 pinctrl implementation and the underlying GPIO hardware.

The descriptor match data leaves optional feature flags unset. H743-specific security or package behavior, if needed by other H7/MP variants, is not represented in this file.

## Dependencies and Integration Points

- Depends on the local STM32 pinctrl header and the shared `stm32_pctl_probe()`.
- Uses Linux OF matching and platform-driver registration.
- Provides the function namespace consumed by H743 DTS pinctrl states and peripheral drivers.
- Integrates with storage (`SDMMC1`, `SDMMC2`, QuadSPI), display/camera (`LCD`, DCMI, DSI), memory (`FMC`), networking (`ETH`, `MDIOS`, CAN), audio (`SAI1`-`SAI4`, SPDIFRX, I2S), timers (`TIM*`, `HRTIM`, `LPTIM*`), serial (`USART`, `UART`, `LPUART1`, `SWPMI`), USB OTG, debug/trace, and analog/power-related board states.

## Risks and Edge Cases

- H743 has very high AF density. A descriptor copied from an F7 file can be wrong even when the signal name looks similar.
- HRTIM, comparator break, and trigger signals are safety/real-time-sensitive; an incorrect AF can produce subtle control-loop or power-stage failures.
- The table includes many shared pins across LCD/DCMI/FMC/SDMMC/ETH/DFSDM/SAI. Pinctrl can select a state, but board-level mutual exclusion remains the DTS and system-design responsibility.
- Function names form a de facto DTS ABI. Renaming `SAI2_MCK_B` versus sibling spellings like `SAI2_MCLK_B`, or changing combined names, can break existing board descriptions.
- No package masks are present, so package-specific pin availability is not enforced.
- Since the file is built in early and exposes 168 pins, a malformed descriptor can affect many dependent devices during boot.

## Test Signals

- Compile the H743 pinctrl object with the shared STM32 pinctrl core.
- Boot an H743 DTS and verify binding through `st,stm32h743-pinctrl`.
- Inspect debugfs for 168 pins and expected H7-specific functions such as HRTIM, LPUART1, SAI4, SDMMC2, and SWPMI.
- Run hardware smoke tests for storage, Ethernet/MDIOS, display/camera, FMC, USB, serial, timers, audio, and HRTIM-critical routes.
- For edits, validate against STM32H743 alternate-function tables and run DTS build checks for all affected pin state names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32h743.c -->
