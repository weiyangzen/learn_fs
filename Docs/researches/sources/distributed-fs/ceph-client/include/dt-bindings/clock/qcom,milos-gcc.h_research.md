# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,milos-gcc.h` / `milos`. The source was read completely for this report (210 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_MILOS_H`. This header defines 158 clock IDs, 28 reset IDs, and 8 power-domain/GDSC IDs, for 194 numeric binding macros total.

Clock ID range: `GCC_GPLL0`=0 through `GCC_VIDEO_XO_CLK`=157. Representative clocks: `GCC_GPLL0`, `GCC_GPLL0_OUT_EVEN`, `GCC_GPLL2`, `GCC_GPLL4`, `GCC_GPLL6`, `GCC_GPLL7`, ... `GCC_USB3_PRIM_PHY_COM_AUX_CLK`, `GCC_USB3_PRIM_PHY_PIPE_CLK`, `GCC_USB3_PRIM_PHY_PIPE_CLK_SRC`, `GCC_VIDEO_AHB_CLK`, `GCC_VIDEO_AXI0_CLK`, `GCC_VIDEO_XO_CLK`.

Reset ID range: `GCC_CAMERA_BCR`=0 through `GCC_VIDEO_BCR`=27. Representative resets: `GCC_CAMERA_BCR`, `GCC_DISPLAY_BCR`, `GCC_GPU_BCR`, `GCC_PCIE_0_BCR`, `GCC_PCIE_0_LINK_DOWN_BCR`, `GCC_PCIE_0_NOCSR_COM_PHY_BCR`, ... `GCC_USB30_PRIM_BCR`, `GCC_USB3_DP_PHY_PRIM_BCR`, `GCC_USB3_PHY_PRIM_BCR`, `GCC_USB3PHY_PHY_PRIM_BCR`, `GCC_VIDEO_AXI0_CLK_ARES`, `GCC_VIDEO_BCR`.

Power-domain/GDSC range: `PCIE_0_GDSC`=0 through `USB3_PHY_GDSC`=7. Representative domains: `PCIE_0_GDSC`, `PCIE_0_PHY_GDSC`, `PCIE_1_GDSC`, `PCIE_1_PHY_GDSC`, `UFS_PHY_GDSC`, `UFS_MEM_PHY_GDSC`, `USB30_PRIM_GDSC`, `USB3_PHY_GDSC`.

Macro inventory begins with:
- `GCC_GPLL0` = 0 (clock, line 11)
- `GCC_GPLL0_OUT_EVEN` = 1 (clock, line 12)
- `GCC_GPLL2` = 2 (clock, line 13)
- `GCC_GPLL4` = 3 (clock, line 14)
- `GCC_GPLL6` = 4 (clock, line 15)
- `GCC_GPLL7` = 5 (clock, line 16)
- `GCC_GPLL9` = 6 (clock, line 17)
- `GCC_AGGRE_NOC_PCIE_AXI_CLK` = 7 (clock, line 18)
- `GCC_AGGRE_UFS_PHY_AXI_CLK` = 8 (clock, line 19)
- `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK` = 9 (clock, line 20)
- ... 184 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-milos.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/milos.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,milos-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_CAMERA_BCR`=0 through `GCC_VIDEO_BCR`=27). Power-domain/GDSC IDs are exported as `PCIE_0_GDSC`=0 through `USB3_PHY_GDSC`=7. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,milos-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
