# sources/distributed-fs/ceph-client/include/dt-bindings/clock/starfive,jh7110-crg.h

## Purpose

`starfive,jh7110-crg.h` is a Linux device-tree binding header for StarFive JH71xx clock-generator binding IDs. It separates JH7110 PLL, system, always-on, STG, ISP, video-in, and video-out clock ID spaces with `*_END` sentinels for each sub-controller. The file is part of the dt-bindings ABI: DTS and DT overlay sources compile these macro names into integer cells, and the corresponding kernel clock controller interprets those cells at runtime. It contains `301` lines and `274` exported binding macros after the include guard.

## Important APIs, Types, and Functions

This header exports preprocessor constants, not C functions or runtime types. The include guard is `__DT_BINDINGS_CLOCK_STARFIVE_JH7110_CRG_H__`. Representative early exports are `JH7110_PLLCLK_PLL0_OUT`, `JH7110_PLLCLK_PLL1_OUT`, `JH7110_PLLCLK_PLL2_OUT`, `JH7110_PLLCLK_END`, `JH7110_SYSCLK_CPU_ROOT`, `JH7110_SYSCLK_CPU_CORE`, `JH7110_SYSCLK_CPU_BUS`, `JH7110_SYSCLK_GPU_ROOT`; representative trailing exports are `JH7110_VOUTCLK_DSITX_SYS`, `JH7110_VOUTCLK_DSITX_DPI`, `JH7110_VOUTCLK_DSITX_TXESC`, `JH7110_VOUTCLK_MIPITX_DPHY_TXESC`, `JH7110_VOUTCLK_HDMI_TX_MCLK`, `JH7110_VOUTCLK_HDMI_TX_BCLK`, `JH7110_VOUTCLK_HDMI_TX_SYS`, `JH7110_VOUTCLK_END`. Numeric analysis shows plain decimal IDs span `0` (`JH7110_PLLCLK_PLL0_OUT`) through `190` (`JH7110_SYSCLK_END`). Sentinel or count-style macros are `JH7110_PLLCLK_END`, `JH7110_SYSCLK_END`, `JH7110_AONCLK_END`, `JH7110_STGCLK_END`, `JH7110_ISPCLK_END`, `JH7110_VOUTCLK_END`. The dominant macro prefixes are `JH7110`:274, which reflect the binding namespaces rather than runtime class names.

## Control Flow

There is no executable control flow. The only control behavior is C preprocessor inclusion through the guard, plus any explicit include chaining. The header has no direct include dependencies; its integration dependency is the StarFive clock/reset driver and device-tree sources that include this binding by path. At build time, DTS files include the header and the device-tree compiler substitutes macro values into `clocks`, `clock-names`, `assigned-clocks`, reset, or related phandle cells. At runtime, the platform clock driver receives those integer IDs through the common clock framework and maps them to fixed factors, gates, muxes, PLLs, dividers, or reset lines implemented elsewhere.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its values become persistent ABI once compiled into DTBs distributed with boards or firmware. Renumbering, deleting, or reusing an existing ID changes the meaning of already-built device trees. Gaps and non-contiguous values should therefore be treated as intentional layout, often mirroring hardware register indices, legacy ABI reservations, or driver array positions. End/count macros such as `JH7110_PLLCLK_END`, `JH7110_SYSCLK_END`, `JH7110_AONCLK_END`, `JH7110_STGCLK_END`, `JH7110_ISPCLK_END`, `JH7110_VOUTCLK_END` are especially important because drivers often size descriptor tables or validate upper bounds with them.

## Dependencies and Integration Points

The binding integrates with Linux OF/device-tree parsing, the common clock framework, and platform-specific clock controller drivers under the same vendor family. Consumers are board and SoC `.dts`/`.dtsi` files, peripheral drivers that request named clocks, reset-controller users when reset IDs are present, and YAML binding schemas that document acceptable `compatible`, `clocks`, and `resets` shapes. Include dependencies are: none.

## Risks and Maintenance Notes

The main risk is ABI drift: changing numeric assignments breaks DTBs even when the C compiler still succeeds. Other risks are duplicate IDs, stale max/end macros, adding new IDs in the middle of an existing range, losing include chaining for extension headers, or mixing clock and reset namespaces in a way the driver does not implement. Because these are macro-only headers, review should compare identifier order and values against the clock driver tables and the vendor reference manual rather than looking for local algorithmic bugs.

## Test Signals

Useful checks include compiling all affected DTBs, running `make dt_binding_check` for schemas that include this header, building the corresponding clock/reset drivers, and grepping in-tree DTS consumers for representative macros such as `JH7110_PLLCLK_PLL0_OUT`, `JH7110_PLLCLK_PLL1_OUT`, `JH7110_VOUTCLK_HDMI_TX_SYS`, `JH7110_VOUTCLK_END`. For changes, confirm old IDs are unchanged, new IDs are appended or intentionally placed in reserved gaps, max/end/count macros still match the driver table size, and extension headers still include their base namespace.
