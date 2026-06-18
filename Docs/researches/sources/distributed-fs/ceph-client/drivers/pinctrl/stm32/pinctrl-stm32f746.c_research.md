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
