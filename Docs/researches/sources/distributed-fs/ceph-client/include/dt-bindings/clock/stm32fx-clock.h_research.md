# sources/distributed-fs/ceph-client/include/dt-bindings/clock/stm32fx-clock.h

## Purpose

`stm32fx-clock.h` is a Linux device-tree binding header for STMicroelectronics STM32 RCC and clock-controller binding IDs. It provides compact STM32F4/F7 primary clock IDs for oscillator roots, PLL VCO outputs, LCD/I2S/SAI clocks, UART/I2C clocks, and end sentinels. The file is part of the dt-bindings ABI: DTS and DT overlay sources compile these macro names into integer cells, and the corresponding kernel clock controller interprets those cells at runtime. It contains `63` lines and `38` exported binding macros after the include guard.

## Important APIs, Types, and Functions

This header exports preprocessor constants, not C functions or runtime types. The include guard is `_DT_BINDINGS_CLK_STMFX_H`. Representative early exports are `SYSTICK`, `FCLK`, `CLK_LSI`, `CLK_LSE`, `CLK_HSE_RTC`, `CLK_RTC`, `PLL_VCO_I2S`, `PLL_VCO_SAI`; representative trailing exports are `CLK_I2C3`, `CLK_I2C4`, `CLK_LPTIMER`, `CLK_PLL_SRC`, `CLK_DFSDM1`, `CLK_ADFSDM1`, `CLK_F769_DSI`, `END_PRIMARY_CLK_F7`. Numeric analysis shows plain decimal IDs span `0` (`SYSTICK`) through `35` (`END_PRIMARY_CLK_F7`). Sentinel or count-style macros are `END_PRIMARY_CLK`, `END_PRIMARY_CLK_F7`. The dominant macro prefixes are `CLK`:32, `PLL`:2, `END`:2, `SYSTICK`:1, `FCLK`:1, which reflect the binding namespaces rather than runtime class names.

## Control Flow

There is no executable control flow. The only control behavior is C preprocessor inclusion through the guard, plus any explicit include chaining. The header has no direct include dependencies; its integration dependency is the STMicroelectronics STM32 clock/reset driver and device-tree sources that include this binding by path. At build time, DTS files include the header and the device-tree compiler substitutes macro values into `clocks`, `clock-names`, `assigned-clocks`, reset, or related phandle cells. At runtime, the platform clock driver receives those integer IDs through the common clock framework and maps them to fixed factors, gates, muxes, PLLs, dividers, or reset lines implemented elsewhere.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its values become persistent ABI once compiled into DTBs distributed with boards or firmware. Renumbering, deleting, or reusing an existing ID changes the meaning of already-built device trees. Gaps and non-contiguous values should therefore be treated as intentional layout, often mirroring hardware register indices, legacy ABI reservations, or driver array positions. End/count macros such as `END_PRIMARY_CLK`, `END_PRIMARY_CLK_F7` are especially important because drivers often size descriptor tables or validate upper bounds with them.

## Dependencies and Integration Points

The binding integrates with Linux OF/device-tree parsing, the common clock framework, and platform-specific clock controller drivers under the same vendor family. Consumers are board and SoC `.dts`/`.dtsi` files, peripheral drivers that request named clocks, reset-controller users when reset IDs are present, and YAML binding schemas that document acceptable `compatible`, `clocks`, and `resets` shapes. Include dependencies are: none.

## Risks and Maintenance Notes

The main risk is ABI drift: changing numeric assignments breaks DTBs even when the C compiler still succeeds. Other risks are duplicate IDs, stale max/end macros, adding new IDs in the middle of an existing range, losing include chaining for extension headers, or mixing clock and reset namespaces in a way the driver does not implement. Because these are macro-only headers, review should compare identifier order and values against the clock driver tables and the vendor reference manual rather than looking for local algorithmic bugs.

## Test Signals

Useful checks include compiling all affected DTBs, running `make dt_binding_check` for schemas that include this header, building the corresponding clock/reset drivers, and grepping in-tree DTS consumers for representative macros such as `SYSTICK`, `FCLK`, `CLK_F769_DSI`, `END_PRIMARY_CLK_F7`. For changes, confirm old IDs are unchanged, new IDs are appended or intentionally placed in reserved gaps, max/end/count macros still match the driver table size, and extension headers still include their base namespace.
