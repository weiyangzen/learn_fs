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
