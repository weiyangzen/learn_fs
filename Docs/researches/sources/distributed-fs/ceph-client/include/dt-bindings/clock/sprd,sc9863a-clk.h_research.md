# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sprd,sc9863a-clk.h

## Purpose

`sprd,sc9863a-clk.h` is a Linux device-tree binding header for Spreadtrum/Unisoc SoC clock-controller binding IDs. It exposes Unisoc fixed-factor roots, PLL gates, composite selectors, peripheral clocks, and enable-gate IDs for PMU, analog, AON, AP, GPU, MM, and CPU-related clock domains. The file is part of the dt-bindings ABI: DTS and DT overlay sources compile these macro names into integer cells, and the corresponding kernel clock controller interprets those cells at runtime. It contains `339` lines and `316` exported binding macros after the include guard.

## Important APIs, Types, and Functions

This header exports preprocessor constants, not C functions or runtime types. The include guard is `_DT_BINDINGS_CLK_SC9863A_H_`. Representative early exports are `CLK_MPLL0_GATE`, `CLK_DPLL0_GATE`, `CLK_LPLL_GATE`, `CLK_GPLL_GATE`, `CLK_DPLL1_GATE`, `CLK_MPLL1_GATE`, `CLK_MPLL2_GATE`, `CLK_ISPPLL_GATE`; representative trailing exports are `CLK_UART2_EB`, `CLK_UART3_EB`, `CLK_UART4_EB`, `CLK_SIM0_32K_EB`, `CLK_SPI3_EB`, `CLK_I2C5_EB`, `CLK_I2C6_EB`, `CLK_AP_APB_GATE_NUM`. Numeric analysis shows plain decimal IDs span `0` (`CLK_MPLL0_GATE`) through `97` (`CLK_AON_AP_EMC_EB`). Sentinel or count-style macros are `CLK_PMU_APB_NUM`, `CLK_ANLG_PHY_G5_NUM`, `CLK_ANLG_PHY_G1_NUM`, `CLK_ANLG_PHY_G7_NUM`, `CLK_ANLG_PHY_G4_NUM`, `CLK_AP_CLK_NUM`, `CLK_AON_CLK_NUM`, `CLK_AP_AHB_GATE_NUM`, and 4 more. The dominant macro prefixes are `CLK`:316, which reflect the binding namespaces rather than runtime class names.

## Control Flow

There is no executable control flow. The only control behavior is C preprocessor inclusion through the guard, plus any explicit include chaining. The header has no direct include dependencies; its integration dependency is the Spreadtrum/Unisoc clock/reset driver and device-tree sources that include this binding by path. At build time, DTS files include the header and the device-tree compiler substitutes macro values into `clocks`, `clock-names`, `assigned-clocks`, reset, or related phandle cells. At runtime, the platform clock driver receives those integer IDs through the common clock framework and maps them to fixed factors, gates, muxes, PLLs, dividers, or reset lines implemented elsewhere.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its values become persistent ABI once compiled into DTBs distributed with boards or firmware. Renumbering, deleting, or reusing an existing ID changes the meaning of already-built device trees. Gaps and non-contiguous values should therefore be treated as intentional layout, often mirroring hardware register indices, legacy ABI reservations, or driver array positions. End/count macros such as `CLK_PMU_APB_NUM`, `CLK_ANLG_PHY_G5_NUM`, `CLK_ANLG_PHY_G1_NUM`, `CLK_ANLG_PHY_G7_NUM`, `CLK_ANLG_PHY_G4_NUM`, `CLK_AP_CLK_NUM`, `CLK_AON_CLK_NUM`, `CLK_AP_AHB_GATE_NUM`, and 4 more are especially important because drivers often size descriptor tables or validate upper bounds with them.

## Dependencies and Integration Points

The binding integrates with Linux OF/device-tree parsing, the common clock framework, and platform-specific clock controller drivers under the same vendor family. Consumers are board and SoC `.dts`/`.dtsi` files, peripheral drivers that request named clocks, reset-controller users when reset IDs are present, and YAML binding schemas that document acceptable `compatible`, `clocks`, and `resets` shapes. Include dependencies are: none.

## Risks and Maintenance Notes

The main risk is ABI drift: changing numeric assignments breaks DTBs even when the C compiler still succeeds. Other risks are duplicate IDs, stale max/end macros, adding new IDs in the middle of an existing range, losing include chaining for extension headers, or mixing clock and reset namespaces in a way the driver does not implement. Because these are macro-only headers, review should compare identifier order and values against the clock driver tables and the vendor reference manual rather than looking for local algorithmic bugs.

## Test Signals

Useful checks include compiling all affected DTBs, running `make dt_binding_check` for schemas that include this header, building the corresponding clock/reset drivers, and grepping in-tree DTS consumers for representative macros such as `CLK_MPLL0_GATE`, `CLK_DPLL0_GATE`, `CLK_I2C6_EB`, `CLK_AP_APB_GATE_NUM`. For changes, confirm old IDs are unchanged, new IDs are appended or intentionally placed in reserved gaps, max/end/count macros still match the driver table size, and extension headers still include their base namespace.
