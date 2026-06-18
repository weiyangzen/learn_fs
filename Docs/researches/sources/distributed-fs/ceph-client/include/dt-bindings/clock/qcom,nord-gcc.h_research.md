# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,nord-gcc.h` / `nord`. The source was read completely for this report (147 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_NORD_H`. This header defines 91 clock IDs, 32 reset IDs, and 9 power-domain/GDSC IDs, for 132 numeric binding macros total.

Clock ID range: `GCC_BOOT_ROM_AHB_CLK`=0 through `GCC_SMMU_PCIE_QTC_VOTE_CLK`=90. Representative clocks: `GCC_BOOT_ROM_AHB_CLK`, `GCC_GP1_CLK`, `GCC_GP1_CLK_SRC`, `GCC_GP2_CLK`, `GCC_GP2_CLK_SRC`, `GCC_GPLL0`, ... `GCC_QUPV3_WRAP3_QSPI_REF_CLK`, `GCC_QUPV3_WRAP3_QSPI_REF_CLK_SRC`, `GCC_QUPV3_WRAP3_S0_CLK`, `GCC_QUPV3_WRAP3_S0_CLK_SRC`, `GCC_QUPV3_WRAP3_S_AHB_CLK`, `GCC_SMMU_PCIE_QTC_VOTE_CLK`.

Reset ID range: `GCC_PCIE_A_BCR`=0 through `GCC_TCSR_PCIE_BCR`=31. Representative resets: `GCC_PCIE_A_BCR`, `GCC_PCIE_A_LINK_DOWN_BCR`, `GCC_PCIE_A_NOCSR_COM_PHY_BCR`, `GCC_PCIE_A_PHY_BCR`, `GCC_PCIE_A_PHY_CFG_AHB_BCR`, `GCC_PCIE_A_PHY_COM_BCR`, ... `GCC_PCIE_D_PHY_COM_BCR`, `GCC_PCIE_D_PHY_NOCSR_COM_PHY_BCR`, `GCC_PCIE_NOC_BCR`, `GCC_PDM_BCR`, `GCC_QUPV3_WRAPPER_3_BCR`, `GCC_TCSR_PCIE_BCR`.

Power-domain/GDSC range: `GCC_PCIE_A_GDSC`=0 through `GCC_PCIE_NOC_GDSC`=8. Representative domains: `GCC_PCIE_A_GDSC`, `GCC_PCIE_A_PHY_GDSC`, `GCC_PCIE_B_GDSC`, `GCC_PCIE_B_PHY_GDSC`, `GCC_PCIE_C_GDSC`, `GCC_PCIE_C_PHY_GDSC`, `GCC_PCIE_D_GDSC`, `GCC_PCIE_D_PHY_GDSC`, `GCC_PCIE_NOC_GDSC`.

Macro inventory begins with:
- `GCC_BOOT_ROM_AHB_CLK` = 0 (clock, line 10)
- `GCC_GP1_CLK` = 1 (clock, line 11)
- `GCC_GP1_CLK_SRC` = 2 (clock, line 12)
- `GCC_GP2_CLK` = 3 (clock, line 13)
- `GCC_GP2_CLK_SRC` = 4 (clock, line 14)
- `GCC_GPLL0` = 5 (clock, line 15)
- `GCC_GPLL0_OUT_EVEN` = 6 (clock, line 16)
- `GCC_MMU_0_TCU_VOTE_CLK` = 7 (clock, line 17)
- `GCC_PCIE_A_AUX_CLK` = 8 (clock, line 18)
- `GCC_PCIE_A_AUX_CLK_SRC` = 9 (clock, line 19)
- ... 122 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-nord.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,nord-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_PCIE_A_BCR`=0 through `GCC_TCSR_PCIE_BCR`=31). Power-domain/GDSC IDs are exported as `GCC_PCIE_A_GDSC`=0 through `GCC_PCIE_NOC_GDSC`=8. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,nord-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
