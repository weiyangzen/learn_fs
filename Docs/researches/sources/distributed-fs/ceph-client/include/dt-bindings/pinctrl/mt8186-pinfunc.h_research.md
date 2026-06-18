# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8186-pinfunc.h

## Purpose

This header is the MediaTek MT8186 pin-function binding table for Device Tree pinctrl nodes. It names the legal mux functions for GPIO0 through GPIO184 and encodes each one as `MTK_PIN_NO(pin) | selector`. MT8186 exposes a broad set of application-processor, subsystem, display, audio, storage, connectivity, and debug routes, and this file turns those routes into stable DTS symbols.

The file contains 976 pinmux macros over 185 pins. Selector 0 is the GPIO function for every pin. Selectors 1 through 7 cover alternate hardware routes such as I2S, TDM, PCM, SPI instances, SCP and SSPM interfaces, ADSP and SPM JTAG, DPI display signals, camera clock/reference pins, MSDC, SPINOR, UDI/DFD debug, GPS and antenna control, connectivity control pins, and SPMI.

## Important APIs, Types, and Macros

The API is a generated-style macro set rather than executable C:

- `PINMUX_GPIO<N>__FUNC_GPIO<N>` is the selector-0 GPIO value.
- `PINMUX_GPIO<N>__FUNC_<SIGNAL>` is a board-usable mux token for a concrete MT8186 pad function.
- The header includes `"mt65xx.h"`, which supplies the MediaTek pin encoding helpers.
- `MTK_PIN_NO(x)` shifts the pin number left by eight bits; `MTK_GET_PIN_FUNC(x)` later extracts the low nibble.

The full table is dense but not uniform. Early pins are audio and SPI heavy, for example I2S0/I2S2 and SPI0/SCP_SPI0 around GPIO0-GPIO3, I2S3/I2S1 and SPI1 around GPIO6-GPIO9, and SPM/SCP/ADSP/CONN JTAG selections around GPIO10-GPIO14. Mid-file regions include TDM receive, PCM, DPI, I2C-style `SCL`/`SDA`, PWM, camera clocks and resets, keypad rows/columns, GPS, antenna selects, and multiple SCP SPI/I2C/UART/JTAG choices. Late pins include audio data lanes, connectivity top/BT/Wi-Fi controls, UDI/DFD debug, and SPMI pins at GPIO183-GPIO184. The most common families are `SCP`, `DBG`, `TP`, `CONN`, `I2S2`, `DPI`, `I2S1`, `ANT`, `PGD`, `ADSP`, `UDI`, `DFD`, `I2S3`, `I2S0`, `SSPM`, and `AUD`.

## Control Flow

There is no runtime branch or call graph in this header. The control path is preprocessing and pinctrl data consumption:

1. MT8186 board DTS files include this binding.
2. Pinctrl states use the macro constants in `pinmux` arrays.
3. Device Tree preprocessing resolves macros to integer cells.
4. The MediaTek pinctrl driver decodes the pin number and selector and writes the matching mux registers when the state is selected.

Any apparent ordering in the file is a hardware-description ordering by GPIO number, not an execution order.

## State and Persistence Behavior

The header has no mutable state, no static storage, and no persistence logic. The persistent artifact is the compiled Device Tree containing the encoded constants. Runtime state is maintained by the kernel pinctrl subsystem and MT8186 pinctrl driver, which may switch between default, sleep, idle, or peripheral-specific pin states. Because DTS files can be built outside this repository, the macro names and numeric values form a binding ABI; stability matters even when no local C callers exist.

## Dependencies and Integration Points

This file depends on the common `mt65xx.h` binding and on the convention that MediaTek pin mux selectors fit in the low nibble. It integrates with the Linux Device Tree build, MT8186 board DTS/DTSI files, the generic pinctrl bindings, and MT8186 driver data that maps each pin/selector pair to actual register fields. It also indirectly integrates with peripheral drivers that request named pinctrl states, such as audio, SPI, I2C, display, storage, camera, connectivity, and low-power subsystem drivers.

This snapshot did not expose direct DTS references to the MT8186 header, but the file is still an exported hardware binding. Consumers need the matching SoC pinctrl driver and electrical configuration data; the pin-function macro only chooses the mux path and does not configure pull-up, pull-down, drive strength, input enable, or power domain requirements.

## Risks and Test Signals

The risk profile is mostly hardware routing correctness. A wrong selector can silently move a bus line to a different function, especially where related signals appear on repeated pins or alternate instance suffixes such as `_A`, `_B`, SCP variants, ADSP variants, or debug-monitor variants. Debug and DFD/UDI/JTAG functions can collide with production peripherals. SPM, SCP, SSPM, SPMI, and connectivity pins can affect suspend/resume and power-management behavior. Display DPI and audio/TDM/I2S groups must be complete and ordered consistently to avoid partial bus bring-up failures.

Test signals include DTC preprocessing with the intended macro names, `dtbs_check` coverage for pinctrl nodes, successful probe of the MT8186 pinctrl driver, and targeted hardware tests for each group referenced by board DTS. For display, verify DPI output and panel timing. For audio, verify clock, bit-clock, frame-sync, and data pins together. For storage and SPI/SPINOR, verify enumeration and transfer integrity. For low-power and subsystem pins, verify suspend/resume, wake, and SCP/SPM communication paths.
