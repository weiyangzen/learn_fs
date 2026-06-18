# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra124-car-common.h

## Purpose

`tegra124-car-common.h` is a Linux device-tree binding header for NVIDIA Tegra CAR clock binding IDs. It defines the Tegra124 common CAR namespace shared by Tegra124 variants, covering peripheral clocks, PLLs, display/audio muxes, SOR, XUSB, and unstable/divided PLL IDs. The file is part of the dt-bindings ABI: DTS and DT overlay sources compile these macro names into integer cells, and the corresponding kernel clock controller interprets those cells at runtime. It contains `349` lines and `194` exported binding macros after the include guard.

## Important APIs, Types, and Functions

This header exports preprocessor constants, not C functions or runtime types. The include guard is `_DT_BINDINGS_CLOCK_TEGRA124_CAR_COMMON_H`. Representative early exports are `TEGRA124_CLK_ISPB`, `TEGRA124_CLK_RTC`, `TEGRA124_CLK_TIMER`, `TEGRA124_CLK_UARTA`, `TEGRA124_CLK_SDMMC2`, `TEGRA124_CLK_I2S1`, `TEGRA124_CLK_I2C1`, `TEGRA124_CLK_SDMMC1`; representative trailing exports are `TEGRA124_CLK_AUDIO3_MUX`, `TEGRA124_CLK_AUDIO4_MUX`, `TEGRA124_CLK_SPDIF_MUX`, `TEGRA124_CLK_SOR0_LVDS`, `TEGRA124_CLK_SOR0_OUT`, `TEGRA124_CLK_XUSB_SS_DIV2`, `TEGRA124_CLK_PLL_M_UD`, `TEGRA124_CLK_PLL_C_UD`. Numeric analysis shows plain decimal IDs span `3` (`TEGRA124_CLK_ISPB`) through `314` (`TEGRA124_CLK_PLL_C_UD`). Sentinel or count-style macros are none observed. The dominant macro prefixes are `TEGRA124`:194, which reflect the binding namespaces rather than runtime class names.

## Control Flow

There is no executable control flow. The only control behavior is C preprocessor inclusion through the guard, plus any explicit include chaining. The header has no direct include dependencies; its integration dependency is the NVIDIA Tegra clock/reset driver and device-tree sources that include this binding by path. At build time, DTS files include the header and the device-tree compiler substitutes macro values into `clocks`, `clock-names`, `assigned-clocks`, reset, or related phandle cells. At runtime, the platform clock driver receives those integer IDs through the common clock framework and maps them to fixed factors, gates, muxes, PLLs, dividers, or reset lines implemented elsewhere.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its values become persistent ABI once compiled into DTBs distributed with boards or firmware. Renumbering, deleting, or reusing an existing ID changes the meaning of already-built device trees. Gaps and non-contiguous values should therefore be treated as intentional layout, often mirroring hardware register indices, legacy ABI reservations, or driver array positions. End/count macros such as none observed are especially important because drivers often size descriptor tables or validate upper bounds with them.

## Dependencies and Integration Points

The binding integrates with Linux OF/device-tree parsing, the common clock framework, and platform-specific clock controller drivers under the same vendor family. Consumers are board and SoC `.dts`/`.dtsi` files, peripheral drivers that request named clocks, reset-controller users when reset IDs are present, and YAML binding schemas that document acceptable `compatible`, `clocks`, and `resets` shapes. Include dependencies are: none.

## Risks and Maintenance Notes

The main risk is ABI drift: changing numeric assignments breaks DTBs even when the C compiler still succeeds. Other risks are duplicate IDs, stale max/end macros, adding new IDs in the middle of an existing range, losing include chaining for extension headers, or mixing clock and reset namespaces in a way the driver does not implement. Because these are macro-only headers, review should compare identifier order and values against the clock driver tables and the vendor reference manual rather than looking for local algorithmic bugs.

## Test Signals

Useful checks include compiling all affected DTBs, running `make dt_binding_check` for schemas that include this header, building the corresponding clock/reset drivers, and grepping in-tree DTS consumers for representative macros such as `TEGRA124_CLK_ISPB`, `TEGRA124_CLK_RTC`, `TEGRA124_CLK_PLL_M_UD`, `TEGRA124_CLK_PLL_C_UD`. For changes, confirm old IDs are unchanged, new IDs are appended or intentionally placed in reserved gaps, max/end/count macros still match the driver table size, and extension headers still include their base namespace.
