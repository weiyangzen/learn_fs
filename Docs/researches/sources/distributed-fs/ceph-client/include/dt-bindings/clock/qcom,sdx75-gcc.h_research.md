# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sdx75-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sdx75-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,sdx75-gcc.h` / `sdx75`. The source was read completely for this report (193 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_SDX75_H`. This header defines 143 clock IDs, 25 reset IDs, and 10 power-domain/GDSC IDs, for 178 numeric binding macros total.

Clock ID range: `GPLL0`=0 through `GCC_XO_PCIE_LINK_CLK`=142. Representative clocks: `GPLL0`, `GPLL0_OUT_EVEN`, `GPLL4`, `GPLL5`, `GPLL6`, `GPLL8`, ... `GCC_USB3_PHY_AUX_CLK_SRC`, `GCC_USB3_PHY_PIPE_CLK`, `GCC_USB3_PHY_PIPE_CLK_SRC`, `GCC_USB3_PRIM_CLKREF_EN`, `GCC_USB_PHY_CFG_AHB2PHY_CLK`, `GCC_XO_PCIE_LINK_CLK`.

Reset ID range: `GCC_EMAC0_BCR`=0 through `GCC_EMAC0_RGMII_CLK_ARES`=24. Representative resets: `GCC_EMAC0_BCR`, `GCC_EMAC1_BCR`, `GCC_EMMC_BCR`, `GCC_PCIE_1_BCR`, `GCC_PCIE_1_LINK_DOWN_BCR`, `GCC_PCIE_1_NOCSR_COM_PHY_BCR`, ... `GCC_TCSR_PCIE_BCR`, `GCC_USB30_BCR`, `GCC_USB3_PHY_BCR`, `GCC_USB3PHY_PHY_BCR`, `GCC_USB_PHY_CFG_AHB2PHY_BCR`, `GCC_EMAC0_RGMII_CLK_ARES`.

Power-domain/GDSC range: `GCC_EMAC0_GDSC`=0 through `GCC_USB3_PHY_GDSC`=9. Representative domains: `GCC_EMAC0_GDSC`, `GCC_EMAC1_GDSC`, `GCC_PCIE_1_GDSC`, `GCC_PCIE_1_PHY_GDSC`, `GCC_PCIE_2_GDSC`, `GCC_PCIE_2_PHY_GDSC`, `GCC_PCIE_GDSC`, `GCC_PCIE_PHY_GDSC`, `GCC_USB30_GDSC`, `GCC_USB3_PHY_GDSC`.

Macro inventory begins with:
- `GPLL0` = 0 (clock, line 10)
- `GPLL0_OUT_EVEN` = 1 (clock, line 11)
- `GPLL4` = 2 (clock, line 12)
- `GPLL5` = 3 (clock, line 13)
- `GPLL6` = 4 (clock, line 14)
- `GPLL8` = 5 (clock, line 15)
- `GCC_AHB_PCIE_LINK_CLK` = 6 (clock, line 16)
- `GCC_BOOT_ROM_AHB_CLK` = 7 (clock, line 17)
- `GCC_EEE_EMAC0_CLK` = 8 (clock, line 18)
- `GCC_EEE_EMAC0_CLK_SRC` = 9 (clock, line 19)
- ... 168 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sdx75.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sdx75.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sdx75-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_EMAC0_BCR`=0 through `GCC_EMAC0_RGMII_CLK_ARES`=24). Power-domain/GDSC IDs are exported as `GCC_EMAC0_GDSC`=0 through `GCC_USB3_PHY_GDSC`=9. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sdx75-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
