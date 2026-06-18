# Research Group: subset-b-005821

Grouped report for the exact subset-b-005821 source list. Each section is wrapped with reconciliation markers so the guard can split it into source-tree-aligned per-file research outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-dispcc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-dispcc.h

## Purpose
Qualcomm display clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 86 across 101 source lines.
- Dominant prefix: `DISP`; prefix distribution: DISP: 84, MDSS: 2.
- Export categories inferred from names: clock: 80, power-domain: 3, reset: 3.
- First exported ID: `DISP_CC_MDSS_ACCU_CLK=0`; last exported ID: `MDSS_INT2_GDSC=1`.
- Representative exported IDs: `DISP_CC_MDSS_ACCU_CLK=0`, `DISP_CC_MDSS_AHB1_CLK=1`, `DISP_CC_MDSS_AHB_CLK=2`, `DISP_CC_MDSS_AHB_CLK_SRC=3`, `DISP_CC_MDSS_BYTE0_CLK=4`, `...=...`, `DISP_CC_MDSS_RSCC_BCR=2`, `MDSS_GDSC=0`, `MDSS_INT2_GDSC=1`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-gcc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-gcc.h

## Purpose
Qualcomm global clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 238 across 254 source lines.
- Dominant prefix: `GCC`; prefix distribution: GCC: 230, PCIE: 4, UFS: 2, USB3: 1, USB30: 1.
- Export categories inferred from names: clock: 196, power-domain: 8, reset: 34.
- First exported ID: `GCC_AGGRE_NOC_PCIE_AXI_CLK=0`; last exported ID: `USB3_PHY_GDSC=7`.
- Representative exported IDs: `GCC_AGGRE_NOC_PCIE_AXI_CLK=0`, `GCC_AGGRE_UFS_PHY_AXI_CLK=1`, `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK=2`, `GCC_AGGRE_USB3_PRIM_AXI_CLK=3`, `GCC_BOOT_ROM_AHB_CLK=4`, `...=...`, `UFS_MEM_PHY_GDSC=5`, `USB30_PRIM_GDSC=6`, `USB3_PHY_GDSC=7`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-gpucc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-gpucc.h

## Purpose
Qualcomm GPU clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 29 across 43 source lines.
- Dominant prefix: `GPU`; prefix distribution: GPU: 29.
- Export categories inferred from names: clock: 26, power-domain: 3.
- First exported ID: `GPU_CC_AHB_CLK=0`; last exported ID: `GPU_CX_GDSC=1`.
- Representative exported IDs: `GPU_CC_AHB_CLK=0`, `GPU_CC_CRC_AHB_CLK=1`, `GPU_CC_CX_ACCU_SHIFT_CLK=2`, `GPU_CC_CX_FF_CLK=3`, `GPU_CC_CX_GMU_CLK=4`, `...=...`, `GPU_CC_SLEEP_CLK=26`, `GPU_GX_GDSC=0`, `GPU_CX_GDSC=1`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-tcsr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-tcsr.h

## Purpose
Qualcomm TCSR clock-reference binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 6 across 18 source lines.
- Dominant prefix: `TCSR`; prefix distribution: TCSR: 6.
- Export categories inferred from names: clock: 6.
- First exported ID: `TCSR_PCIE_0_CLKREF_EN=0`; last exported ID: `TCSR_USB3_CLKREF_EN=5`.
- Representative exported IDs: `TCSR_PCIE_0_CLKREF_EN=0`, `TCSR_PCIE_1_CLKREF_EN=1`, `TCSR_UFS_CLKREF_EN=2`, `TCSR_UFS_PAD_CLKREF_EN=3`, `TCSR_USB2_CLKREF_EN=4`, `TCSR_USB3_CLKREF_EN=5`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-tcsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-videocc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-videocc.h

## Purpose
Qualcomm video clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 6 across 23 source lines.
- Dominant prefix: `VIDEO`; prefix distribution: VIDEO: 6.
- Export categories inferred from names: clock: 6.
- First exported ID: `VIDEO_CC_MVS0_SHIFT_CLK=12`; last exported ID: `VIDEO_CC_XO_CLK_ARES=7`.
- Representative exported IDs: `VIDEO_CC_MVS0_SHIFT_CLK=12`, `VIDEO_CC_MVS0C_SHIFT_CLK=13`, `VIDEO_CC_MVS1_SHIFT_CLK=14`, `VIDEO_CC_MVS1C_SHIFT_CLK=15`, `VIDEO_CC_XO_CLK_SRC=16`, `VIDEO_CC_XO_CLK_ARES=7`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include "qcom,sm8450-videocc.h"`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-videocc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-cambistmclkcc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-cambistmclkcc.h

## Purpose
Qualcomm camera clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 19 across 30 source lines.
- Dominant prefix: `CAM`; prefix distribution: CAM: 19.
- Export categories inferred from names: clock: 19.
- First exported ID: `CAM_BIST_MCLK_CC_MCLK0_CLK=0`; last exported ID: `CAM_BIST_MCLK_CC_SLEEP_CLK_SRC=18`.
- Representative exported IDs: `CAM_BIST_MCLK_CC_MCLK0_CLK=0`, `CAM_BIST_MCLK_CC_MCLK0_CLK_SRC=1`, `CAM_BIST_MCLK_CC_MCLK1_CLK=2`, `CAM_BIST_MCLK_CC_MCLK1_CLK_SRC=3`, `CAM_BIST_MCLK_CC_MCLK2_CLK=4`, `...=...`, `CAM_BIST_MCLK_CC_PLL0=16`, `CAM_BIST_MCLK_CC_SLEEP_CLK=17`, `CAM_BIST_MCLK_CC_SLEEP_CLK_SRC=18`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-cambistmclkcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-camcc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-camcc.h

## Purpose
Qualcomm camera clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 136 across 151 source lines.
- Dominant prefix: `CAM`; prefix distribution: CAM: 136.
- Export categories inferred from names: clock: 121, power-domain: 7, reset: 8.
- First exported ID: `CAM_CC_CAM_TOP_AHB_CLK=0`; last exported ID: `CAM_CC_TFE_2_BCR=7`.
- Representative exported IDs: `CAM_CC_CAM_TOP_AHB_CLK=0`, `CAM_CC_CAM_TOP_FAST_AHB_CLK=1`, `CAM_CC_CAMNOC_DCD_XO_CLK=2`, `CAM_CC_CAMNOC_NRT_AXI_CLK=3`, `CAM_CC_CAMNOC_NRT_CRE_CLK=4`, `...=...`, `CAM_CC_TFE_0_BCR=5`, `CAM_CC_TFE_1_BCR=6`, `CAM_CC_TFE_2_BCR=7`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-dispcc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-dispcc.h

## Purpose
Qualcomm display clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 95 across 112 source lines.
- Dominant prefix: `DISP`; prefix distribution: DISP: 93, MDSS: 2.
- Export categories inferred from names: clock: 89, power-domain: 3, reset: 3.
- First exported ID: `DISP_CC_ESYNC0_CLK=0`; last exported ID: `MDSS_INT2_GDSC=1`.
- Representative exported IDs: `DISP_CC_ESYNC0_CLK=0`, `DISP_CC_ESYNC0_CLK_SRC=1`, `DISP_CC_ESYNC1_CLK=2`, `DISP_CC_ESYNC1_CLK_SRC=3`, `DISP_CC_MDSS_ACCU_SHIFT_CLK=4`, `...=...`, `DISP_CC_MDSS_RSCC_BCR=2`, `MDSS_GDSC=0`, `MDSS_INT2_GDSC=1`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-gcc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-gcc.h

## Purpose
Qualcomm global clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 211 across 226 source lines.
- Dominant prefix: `GCC`; prefix distribution: GCC: 211.
- Export categories inferred from names: clock: 175, power-domain: 6, reset: 30.
- First exported ID: `GCC_AGGRE_NOC_PCIE_AXI_CLK=0`; last exported ID: `GCC_EVA_AXI0C_CLK_ARES=33`.
- Representative exported IDs: `GCC_AGGRE_NOC_PCIE_AXI_CLK=0`, `GCC_AGGRE_UFS_PHY_AXI_CLK=1`, `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK=2`, `GCC_AGGRE_USB3_PRIM_AXI_CLK=3`, `GCC_BOOT_ROM_AHB_CLK=4`, `...=...`, `GCC_VIDEO_BCR=31`, `GCC_EVA_AXI0_CLK_ARES=32`, `GCC_EVA_AXI0C_CLK_ARES=33`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-gpucc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-gpucc.h

## Purpose
Qualcomm GPU clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 36 across 50 source lines.
- Dominant prefix: `GPU`; prefix distribution: GPU: 36.
- Export categories inferred from names: clock: 27, power-domain: 2, reset: 7.
- First exported ID: `GPU_CC_AHB_CLK=0`; last exported ID: `GPU_CC_GPU_CC_XO_BCR=6`.
- Representative exported IDs: `GPU_CC_AHB_CLK=0`, `GPU_CC_CB_CLK=1`, `GPU_CC_CX_ACCU_SHIFT_CLK=2`, `GPU_CC_CX_FF_CLK=3`, `GPU_CC_CX_GMU_CLK=4`, `...=...`, `GPU_CC_GPU_CC_GMU_BCR=4`, `GPU_CC_GPU_CC_GX_BCR=5`, `GPU_CC_GPU_CC_XO_BCR=6`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-tcsr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-tcsr.h

## Purpose
Qualcomm TCSR clock-reference binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 4 across 15 source lines.
- Dominant prefix: `TCSR`; prefix distribution: TCSR: 4.
- Export categories inferred from names: clock: 4.
- First exported ID: `TCSR_PCIE_0_CLKREF_EN=0`; last exported ID: `TCSR_USB3_CLKREF_EN=3`.
- Representative exported IDs: `TCSR_PCIE_0_CLKREF_EN=0`, `TCSR_UFS_CLKREF_EN=1`, `TCSR_USB2_CLKREF_EN=2`, `TCSR_USB3_CLKREF_EN=3`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-tcsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-videocc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-videocc.h

## Purpose
Qualcomm video clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 25 across 40 source lines.
- Dominant prefix: `VIDEO`; prefix distribution: VIDEO: 25.
- Export categories inferred from names: clock: 20, power-domain: 2, reset: 3.
- First exported ID: `VIDEO_CC_AHB_CLK=0`; last exported ID: `VIDEO_CC_XO_CLK_ARES=6`.
- Representative exported IDs: `VIDEO_CC_AHB_CLK=0`, `VIDEO_CC_AHB_CLK_SRC=1`, `VIDEO_CC_MVS0_CLK=2`, `VIDEO_CC_MVS0_CLK_SRC=3`, `VIDEO_CC_MVS0_DIV_CLK_SRC=4`, `...=...`, `VIDEO_CC_MVS0_FREERUN_CLK_ARES=4`, `VIDEO_CC_MVS0C_FREERUN_CLK_ARES=5`, `VIDEO_CC_XO_CLK_ARES=6`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8750-videocc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,turingcc-qcs404.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,turingcc-qcs404.h

## Purpose
Qualcomm global clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 5 across 15 source lines.
- Dominant prefix: `TURING`; prefix distribution: TURING: 5.
- Export categories inferred from names: clock: 5.
- First exported ID: `TURING_Q6SS_Q6_AXIM_CLK=0`; last exported ID: `TURING_WRAPPER_QOS_AHBS_AON_CLK=4`.
- Representative exported IDs: `TURING_Q6SS_Q6_AXIM_CLK=0`, `TURING_Q6SS_AHBM_AON_CLK=1`, `TURING_WRAPPER_AON_CLK=2`, `TURING_Q6SS_AHBS_AON_CLK=3`, `TURING_WRAPPER_QOS_AHBS_AON_CLK=4`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,turingcc-qcs404.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sc7180.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sc7180.h

## Purpose
Qualcomm video clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 10 across 23 source lines.
- Dominant prefix: `VIDEO`; prefix distribution: VCODEC0: 1, VENUS: 1, VIDEO: 8.
- Export categories inferred from names: clock: 8, power-domain: 2.
- First exported ID: `VIDEO_PLL0=0`; last exported ID: `VCODEC0_GDSC=1`.
- Representative exported IDs: `VIDEO_PLL0=0`, `VIDEO_CC_VCODEC0_AXI_CLK=1`, `VIDEO_CC_VCODEC0_CORE_CLK=2`, `VIDEO_CC_VENUS_AHB_CLK=3`, `VIDEO_CC_VENUS_CLK_SRC=4`, `...=...`, `VIDEO_CC_XO_CLK=7`, `VENUS_GDSC=0`, `VCODEC0_GDSC=1`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sc7180.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sc7280.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sc7280.h

## Purpose
Qualcomm video clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 14 across 27 source lines.
- Dominant prefix: `VIDEO`; prefix distribution: MVS0: 1, MVSC: 1, VIDEO: 12.
- Export categories inferred from names: clock: 12, power-domain: 2.
- First exported ID: `VIDEO_PLL0=0`; last exported ID: `MVSC_GDSC=1`.
- Representative exported IDs: `VIDEO_PLL0=0`, `VIDEO_CC_IRIS_AHB_CLK=1`, `VIDEO_CC_IRIS_CLK_SRC=2`, `VIDEO_CC_MVS0_AXI_CLK=3`, `VIDEO_CC_MVS0_CORE_CLK=4`, `...=...`, `VIDEO_CC_XO_CLK_SRC=11`, `MVS0_GDSC=0`, `MVSC_GDSC=1`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sc7280.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sdm845.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sdm845.h

## Purpose
Qualcomm video clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 20 across 35 source lines.
- Dominant prefix: `VIDEO`; prefix distribution: VCODEC0: 1, VCODEC1: 1, VENUS: 1, VIDEO: 17.
- Export categories inferred from names: clock: 13, power-domain: 3, reset: 4.
- First exported ID: `VIDEO_CC_APB_CLK=0`; last exported ID: `VCODEC1_GDSC=2`.
- Representative exported IDs: `VIDEO_CC_APB_CLK=0`, `VIDEO_CC_AT_CLK=1`, `VIDEO_CC_QDSS_TRIG_CLK=2`, `VIDEO_CC_QDSS_TSCTR_DIV8_CLK=3`, `VIDEO_CC_VCODEC0_AXI_CLK=4`, `...=...`, `VENUS_GDSC=0`, `VCODEC0_GDSC=1`, `VCODEC1_GDSC=2`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sdm845.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sm8150.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sm8150.h

## Purpose
Qualcomm video clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 14 across 29 source lines.
- Dominant prefix: `VIDEO`; prefix distribution: VCODEC0: 1, VCODEC1: 1, VENUS: 1, VIDEO: 11.
- Export categories inferred from names: clock: 6, power-domain: 3, reset: 5.
- First exported ID: `VIDEO_CC_IRIS_AHB_CLK=0`; last exported ID: `VCODEC1_GDSC=2`.
- Representative exported IDs: `VIDEO_CC_IRIS_AHB_CLK=0`, `VIDEO_CC_IRIS_CLK_SRC=1`, `VIDEO_CC_MVS0_CORE_CLK=2`, `VIDEO_CC_MVS1_CORE_CLK=3`, `VIDEO_CC_MVSC_CORE_CLK=4`, `...=...`, `VENUS_GDSC=0`, `VCODEC0_GDSC=1`, `VCODEC1_GDSC=2`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sm8150.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sm8250.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sm8250.h

## Purpose
Qualcomm video clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 22 across 36 source lines.
- Dominant prefix: `VIDEO`; prefix distribution: MVS0: 1, MVS0C: 1, MVS1: 1, MVS1C: 1, VIDEO: 18.
- Export categories inferred from names: clock: 13, power-domain: 4, reset: 5.
- First exported ID: `VIDEO_CC_MVS0_CLK_SRC=0`; last exported ID: `MVS1_GDSC=3`.
- Representative exported IDs: `VIDEO_CC_MVS0_CLK_SRC=0`, `VIDEO_CC_MVS0C_CLK=1`, `VIDEO_CC_MVS0C_DIV2_DIV_CLK_SRC=2`, `VIDEO_CC_MVS1_CLK_SRC=3`, `VIDEO_CC_MVS1_DIV2_CLK=4`, `...=...`, `MVS1C_GDSC=1`, `MVS0_GDSC=2`, `MVS1_GDSC=3`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,videocc-sm8250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-camcc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-camcc.h

## Purpose
Qualcomm camera clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 120 across 135 source lines.
- Dominant prefix: `CAM`; prefix distribution: CAM: 120.
- Export categories inferred from names: clock: 107, power-domain: 7, reset: 6.
- First exported ID: `CAM_CC_BPS_AHB_CLK=0`; last exported ID: `CAM_CC_SFE_0_BCR=5`.
- Representative exported IDs: `CAM_CC_BPS_AHB_CLK=0`, `CAM_CC_BPS_CLK=1`, `CAM_CC_BPS_CLK_SRC=2`, `CAM_CC_BPS_FAST_AHB_CLK=3`, `CAM_CC_CAMNOC_AXI_NRT_CLK=4`, `...=...`, `CAM_CC_IFE_1_BCR=3`, `CAM_CC_IPE_0_BCR=4`, `CAM_CC_SFE_0_BCR=5`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-dispcc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-dispcc.h

## Purpose
Qualcomm display clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 86 across 101 source lines.
- Dominant prefix: `DISP`; prefix distribution: DISP: 84, MDSS: 2.
- Export categories inferred from names: clock: 80, power-domain: 3, reset: 3.
- First exported ID: `DISP_CC_MDSS_ACCU_CLK=0`; last exported ID: `MDSS_INT2_GDSC=1`.
- Representative exported IDs: `DISP_CC_MDSS_ACCU_CLK=0`, `DISP_CC_MDSS_AHB1_CLK=1`, `DISP_CC_MDSS_AHB_CLK=2`, `DISP_CC_MDSS_AHB_CLK_SRC=3`, `DISP_CC_MDSS_BYTE0_CLK=4`, `...=...`, `DISP_CC_MDSS_DPTX2_USB_ROUTER_LINK_INTF_CLK_ARES=5`, `MDSS_GDSC=0`, `MDSS_INT2_GDSC=1`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-gcc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-gcc.h

## Purpose
Qualcomm global clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 536 across 551 source lines.
- Dominant prefix: `GCC`; prefix distribution: GCC: 536.
- Export categories inferred from names: clock: 385, power-domain: 27, reset: 124.
- First exported ID: `GCC_AGGRE_NOC_USB_NORTH_AXI_CLK=0`; last exported ID: `GCC_USB4PHY_PHY_TERT_BCR=125`.
- Representative exported IDs: `GCC_AGGRE_NOC_USB_NORTH_AXI_CLK=0`, `GCC_AGGRE_NOC_USB_SOUTH_AXI_CLK=1`, `GCC_AGGRE_UFS_PHY_AXI_CLK=2`, `GCC_AGGRE_USB2_PRIM_AXI_CLK=3`, `GCC_AGGRE_USB3_MP_AXI_CLK=4`, `...=...`, `GCC_USB4PHY_PHY_PRIM_BCR=123`, `GCC_USB4PHY_PHY_SEC_BCR=124`, `GCC_USB4PHY_PHY_TERT_BCR=125`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-gpucc.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-gpucc.h

## Purpose
Qualcomm GPU clock controller binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 39 across 54 source lines.
- Dominant prefix: `GPU`; prefix distribution: GPU: 39.
- Export categories inferred from names: clock: 27, power-domain: 3, reset: 9.
- First exported ID: `GPU_CC_AHB_CLK=0`; last exported ID: `GPU_CC_XO_BCR=8`.
- Representative exported IDs: `GPU_CC_AHB_CLK=0`, `GPU_CC_CB_CLK=1`, `GPU_CC_CRC_AHB_CLK=2`, `GPU_CC_CX_FF_CLK=3`, `GPU_CC_CX_GMU_CLK=4`, `...=...`, `GPU_CC_GMU_BCR=6`, `GPU_CC_GX_BCR=7`, `GPU_CC_XO_BCR=8`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-tcsr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-tcsr.h

## Purpose
Qualcomm TCSR clock-reference binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Qualcomm binding is consumed by SoC-specific clock-controller drivers and device-tree nodes using `#clock-cells`, `#reset-cells`, and, where present, GDSC/power-domain cells. The numeric values must match the provider driver descriptor arrays for the same controller block.

## Important APIs, Types, and Exports
- Exported macro count: 12 across 23 source lines.
- Dominant prefix: `TCSR`; prefix distribution: TCSR: 12.
- Export categories inferred from names: clock: 12.
- First exported ID: `TCSR_PCIE_2L_4_CLKREF_EN=0`; last exported ID: `TCSR_EDP_CLKREF_EN=11`.
- Representative exported IDs: `TCSR_PCIE_2L_4_CLKREF_EN=0`, `TCSR_PCIE_2L_5_CLKREF_EN=1`, `TCSR_PCIE_8L_CLKREF_EN=2`, `TCSR_USB3_MP0_CLKREF_EN=3`, `TCSR_USB3_MP1_CLKREF_EN=4`, `...=...`, `TCSR_USB2_2_CLKREF_EN=9`, `TCSR_PCIE_4L_CLKREF_EN=10`, `TCSR_EDP_CLKREF_EN=11`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,x1e80100-tcsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r7s72100-clock.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r7s72100-clock.h

## Purpose
Renesas legacy SoC clock binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This legacy Renesas clock binding provides SoC-specific clock or MSTP bit identifiers without a dependency on the shared CPG/MSSR selector header. The values map directly to device-tree clock cells and older Renesas clock provider tables.

## Important APIs, Types, and Exports
- Exported macro count: 77 across 112 source lines.
- Dominant prefix: `R7S72100`; prefix distribution: R7S72100: 77.
- Export categories inferred from names: clock: 76, power-domain: 1.
- First exported ID: `R7S72100_CLK_PLL=0`; last exported ID: `R7S72100_CLK_PIX0=1`.
- Representative exported IDs: `R7S72100_CLK_PLL=0`, `R7S72100_CLK_I=1`, `R7S72100_CLK_G=2`, `R7S72100_CLK_CORESIGHT=0`, `R7S72100_CLK_IEBUS=7`, `...=...`, `R7S72100_CLK_SDHI11=0`, `R7S72100_CLK_PIX1=2`, `R7S72100_CLK_PIX0=1`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r7s72100-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r7s9210-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r7s9210-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 6 across 20 source lines.
- Dominant prefix: `R7S9210`; prefix distribution: R7S9210: 6.
- Export categories inferred from names: clock: 6.
- First exported ID: `R7S9210_CLK_I=0`; last exported ID: `R7S9210_CLK_P0=5`.
- Representative exported IDs: `R7S9210_CLK_I=0`, `R7S9210_CLK_G=1`, `R7S9210_CLK_B=2`, `R7S9210_CLK_P1=3`, `R7S9210_CLK_P1C=4`, `R7S9210_CLK_P0=5`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r7s9210-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a73a4-clock.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a73a4-clock.h

## Purpose
Renesas legacy SoC clock binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This legacy Renesas clock binding provides SoC-specific clock or MSTP bit identifiers without a dependency on the shared CPG/MSSR selector header. The values map directly to device-tree clock cells and older Renesas clock provider tables.

## Important APIs, Types, and Exports
- Exported macro count: 43 across 64 source lines.
- Dominant prefix: `R8A73A4`; prefix distribution: R8A73A4: 43.
- Export categories inferred from names: clock: 43.
- First exported ID: `R8A73A4_CLK_MAIN=0`; last exported ID: `R8A73A4_CLK_IIC8=15`.
- Representative exported IDs: `R8A73A4_CLK_MAIN=0`, `R8A73A4_CLK_PLL0=1`, `R8A73A4_CLK_PLL1=2`, `R8A73A4_CLK_PLL2=3`, `R8A73A4_CLK_PLL2S=4`, `...=...`, `R8A73A4_CLK_IRQC=7`, `R8A73A4_CLK_THERMAL=22`, `R8A73A4_CLK_IIC8=15`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a73a4-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7740-clock.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7740-clock.h

## Purpose
Renesas legacy SoC clock binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This legacy Renesas clock binding provides SoC-specific clock or MSTP bit identifiers without a dependency on the shared CPG/MSSR selector header. The values map directly to device-tree clock cells and older Renesas clock provider tables.

## Important APIs, Types, and Exports
- Exported macro count: 53 across 74 source lines.
- Dominant prefix: `R8A7740`; prefix distribution: R8A7740: 53.
- Export categories inferred from names: clock: 53.
- First exported ID: `R8A7740_CLK_SYSTEM=0`; last exported ID: `R8A7740_CLK_SUBCK2=10`.
- Representative exported IDs: `R8A7740_CLK_SYSTEM=0`, `R8A7740_CLK_PLLC0=1`, `R8A7740_CLK_PLLC1=2`, `R8A7740_CLK_PLLC2=3`, `R8A7740_CLK_R=4`, `...=...`, `R8A7740_CLK_USBPHY=6`, `R8A7740_CLK_SUBCK=9`, `R8A7740_CLK_SUBCK2=10`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7740-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7742-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7742-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 30 across 42 source lines.
- Dominant prefix: `R8A7742`; prefix distribution: R8A7742: 30.
- Export categories inferred from names: clock: 30.
- First exported ID: `R8A7742_CLK_Z=0`; last exported ID: `R8A7742_CLK_OSC=29`.
- Representative exported IDs: `R8A7742_CLK_Z=0`, `R8A7742_CLK_Z2=1`, `R8A7742_CLK_ZG=2`, `R8A7742_CLK_ZTR=3`, `R8A7742_CLK_ZTRD2=4`, `...=...`, `R8A7742_CLK_RCAN=27`, `R8A7742_CLK_R=28`, `R8A7742_CLK_OSC=29`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7742-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7743-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7743-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 27 across 39 source lines.
- Dominant prefix: `R8A7743`; prefix distribution: R8A7743: 27.
- Export categories inferred from names: clock: 27.
- First exported ID: `R8A7743_CLK_Z=0`; last exported ID: `R8A7743_CLK_OSC=30`.
- Representative exported IDs: `R8A7743_CLK_Z=0`, `R8A7743_CLK_ZG=1`, `R8A7743_CLK_ZTR=2`, `R8A7743_CLK_ZTRD2=3`, `R8A7743_CLK_ZT=4`, `...=...`, `R8A7743_CLK_RCAN=28`, `R8A7743_CLK_R=29`, `R8A7743_CLK_OSC=30`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7743-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7744-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7744-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 27 across 39 source lines.
- Dominant prefix: `R8A7744`; prefix distribution: R8A7744: 27.
- Export categories inferred from names: clock: 27.
- First exported ID: `R8A7744_CLK_Z=0`; last exported ID: `R8A7744_CLK_OSC=30`.
- Representative exported IDs: `R8A7744_CLK_Z=0`, `R8A7744_CLK_ZG=1`, `R8A7744_CLK_ZTR=2`, `R8A7744_CLK_ZTRD2=3`, `R8A7744_CLK_ZT=4`, `...=...`, `R8A7744_CLK_RCAN=28`, `R8A7744_CLK_R=29`, `R8A7744_CLK_OSC=30`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7744-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7745-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7745-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 28 across 40 source lines.
- Dominant prefix: `R8A7745`; prefix distribution: R8A7745: 28.
- Export categories inferred from names: clock: 28.
- First exported ID: `R8A7745_CLK_Z2=0`; last exported ID: `R8A7745_CLK_OSC=29`.
- Representative exported IDs: `R8A7745_CLK_Z2=0`, `R8A7745_CLK_ZG=1`, `R8A7745_CLK_ZTR=2`, `R8A7745_CLK_ZTRD2=3`, `R8A7745_CLK_ZT=4`, `...=...`, `R8A7745_CLK_RCAN=27`, `R8A7745_CLK_R=28`, `R8A7745_CLK_OSC=29`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7745-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77470-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77470-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 24 across 36 source lines.
- Dominant prefix: `R8A77470`; prefix distribution: R8A77470: 24.
- Export categories inferred from names: clock: 24.
- First exported ID: `R8A77470_CLK_Z2=0`; last exported ID: `R8A77470_CLK_OSC=23`.
- Representative exported IDs: `R8A77470_CLK_Z2=0`, `R8A77470_CLK_ZTR=1`, `R8A77470_CLK_ZTRD2=2`, `R8A77470_CLK_ZT=3`, `R8A77470_CLK_ZX=4`, `...=...`, `R8A77470_CLK_RCAN=21`, `R8A77470_CLK_R=22`, `R8A77470_CLK_OSC=23`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77470-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774a1-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774a1-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 47 across 59 source lines.
- Dominant prefix: `R8A774A1`; prefix distribution: R8A774A1: 47.
- Export categories inferred from names: clock: 47.
- First exported ID: `R8A774A1_CLK_Z=0`; last exported ID: `R8A774A1_CLK_CANFD=46`.
- Representative exported IDs: `R8A774A1_CLK_Z=0`, `R8A774A1_CLK_Z2=1`, `R8A774A1_CLK_ZG=2`, `R8A774A1_CLK_ZTR=3`, `R8A774A1_CLK_ZTRD2=4`, `...=...`, `R8A774A1_CLK_R=44`, `R8A774A1_CLK_OSC=45`, `R8A774A1_CLK_CANFD=46`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774a1-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774b1-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774b1-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 45 across 57 source lines.
- Dominant prefix: `R8A774B1`; prefix distribution: R8A774B1: 45.
- Export categories inferred from names: clock: 45.
- First exported ID: `R8A774B1_CLK_Z=0`; last exported ID: `R8A774B1_CLK_CANFD=44`.
- Representative exported IDs: `R8A774B1_CLK_Z=0`, `R8A774B1_CLK_ZG=1`, `R8A774B1_CLK_ZTR=2`, `R8A774B1_CLK_ZTRD2=3`, `R8A774B1_CLK_ZT=4`, `...=...`, `R8A774B1_CLK_R=42`, `R8A774B1_CLK_OSC=43`, `R8A774B1_CLK_CANFD=44`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774b1-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774c0-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774c0-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 49 across 61 source lines.
- Dominant prefix: `R8A774C0`; prefix distribution: R8A774C0: 49.
- Export categories inferred from names: clock: 49.
- First exported ID: `R8A774C0_CLK_Z2=0`; last exported ID: `R8A774C0_CLK_CANFD=48`.
- Representative exported IDs: `R8A774C0_CLK_Z2=0`, `R8A774C0_CLK_ZG=1`, `R8A774C0_CLK_ZTR=2`, `R8A774C0_CLK_ZT=3`, `R8A774C0_CLK_ZX=4`, `...=...`, `R8A774C0_CLK_CP=46`, `R8A774C0_CLK_CPEX=47`, `R8A774C0_CLK_CANFD=48`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774c0-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774e1-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774e1-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 47 across 59 source lines.
- Dominant prefix: `R8A774E1`; prefix distribution: R8A774E1: 47.
- Export categories inferred from names: clock: 47.
- First exported ID: `R8A774E1_CLK_Z=0`; last exported ID: `R8A774E1_CLK_CANFD=46`.
- Representative exported IDs: `R8A774E1_CLK_Z=0`, `R8A774E1_CLK_Z2=1`, `R8A774E1_CLK_ZG=2`, `R8A774E1_CLK_ZTR=3`, `R8A774E1_CLK_ZTRD2=4`, `...=...`, `R8A774E1_CLK_R=44`, `R8A774E1_CLK_OSC=45`, `R8A774E1_CLK_CANFD=46`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a774e1-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7778-clock.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7778-clock.h

## Purpose
Renesas legacy SoC clock binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This legacy Renesas clock binding provides SoC-specific clock or MSTP bit identifiers without a dependency on the shared CPG/MSSR selector header. The values map directly to device-tree clock cells and older Renesas clock provider tables.

## Important APIs, Types, and Exports
- Exported macro count: 50 across 69 source lines.
- Dominant prefix: `R8A7778`; prefix distribution: R8A7778: 50.
- Export categories inferred from names: clock: 50.
- First exported ID: `R8A7778_CLK_PLLA=0`; last exported ID: `R8A7778_CLK_SRU_SRC8=23`.
- Representative exported IDs: `R8A7778_CLK_PLLA=0`, `R8A7778_CLK_PLLB=1`, `R8A7778_CLK_B=2`, `R8A7778_CLK_OUT=3`, `R8A7778_CLK_P=4`, `...=...`, `R8A7778_CLK_SRU_SRC6=25`, `R8A7778_CLK_SRU_SRC7=24`, `R8A7778_CLK_SRU_SRC8=23`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7778-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7779-clock.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7779-clock.h

## Purpose
Renesas legacy SoC clock binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This legacy Renesas clock binding provides SoC-specific clock or MSTP bit identifiers without a dependency on the shared CPG/MSSR selector header. The values map directly to device-tree clock cells and older Renesas clock provider tables.

## Important APIs, Types, and Exports
- Exported macro count: 41 across 60 source lines.
- Dominant prefix: `R8A7779`; prefix distribution: R8A7779: 41.
- Export categories inferred from names: clock: 41.
- First exported ID: `R8A7779_CLK_PLLA=0`; last exported ID: `R8A7779_CLK_MMC0=31`.
- Representative exported IDs: `R8A7779_CLK_PLLA=0`, `R8A7779_CLK_Z=1`, `R8A7779_CLK_ZS=2`, `R8A7779_CLK_S=3`, `R8A7779_CLK_S1=4`, `...=...`, `R8A7779_CLK_SDHI0=23`, `R8A7779_CLK_MMC1=30`, `R8A7779_CLK_MMC0=31`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7779-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7790-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7790-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 35 across 48 source lines.
- Dominant prefix: `R8A7790`; prefix distribution: R8A7790: 35.
- Export categories inferred from names: clock: 35.
- First exported ID: `R8A7790_CLK_Z=0`; last exported ID: `R8A7790_CLK_OSC=34`.
- Representative exported IDs: `R8A7790_CLK_Z=0`, `R8A7790_CLK_Z2=1`, `R8A7790_CLK_ZG=2`, `R8A7790_CLK_ZTR=3`, `R8A7790_CLK_ZTRD2=4`, `...=...`, `R8A7790_CLK_RCAN=32`, `R8A7790_CLK_R=33`, `R8A7790_CLK_OSC=34`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7790-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7791-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7791-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 31 across 44 source lines.
- Dominant prefix: `R8A7791`; prefix distribution: R8A7791: 31.
- Export categories inferred from names: clock: 31.
- First exported ID: `R8A7791_CLK_Z=0`; last exported ID: `R8A7791_CLK_OSC=30`.
- Representative exported IDs: `R8A7791_CLK_Z=0`, `R8A7791_CLK_ZG=1`, `R8A7791_CLK_ZTR=2`, `R8A7791_CLK_ZTRD2=3`, `R8A7791_CLK_ZT=4`, `...=...`, `R8A7791_CLK_RCAN=28`, `R8A7791_CLK_R=29`, `R8A7791_CLK_OSC=30`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7791-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7792-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7792-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 26 across 39 source lines.
- Dominant prefix: `R8A7792`; prefix distribution: R8A7792: 26.
- Export categories inferred from names: clock: 26.
- First exported ID: `R8A7792_CLK_Z=0`; last exported ID: `R8A7792_CLK_OSC=25`.
- Representative exported IDs: `R8A7792_CLK_Z=0`, `R8A7792_CLK_ZG=1`, `R8A7792_CLK_ZTR=2`, `R8A7792_CLK_ZTRD2=3`, `R8A7792_CLK_ZT=4`, `...=...`, `R8A7792_CLK_RCAN=23`, `R8A7792_CLK_R=24`, `R8A7792_CLK_OSC=25`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7792-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7793-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7793-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 31 across 44 source lines.
- Dominant prefix: `R8A7793`; prefix distribution: R8A7793: 31.
- Export categories inferred from names: clock: 31.
- First exported ID: `R8A7793_CLK_Z=0`; last exported ID: `R8A7793_CLK_OSC=30`.
- Representative exported IDs: `R8A7793_CLK_Z=0`, `R8A7793_CLK_ZG=1`, `R8A7793_CLK_ZTR=2`, `R8A7793_CLK_ZTRD2=3`, `R8A7793_CLK_ZT=4`, `...=...`, `R8A7793_CLK_RCAN=28`, `R8A7793_CLK_R=29`, `R8A7793_CLK_OSC=30`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7793-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7794-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7794-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 30 across 43 source lines.
- Dominant prefix: `R8A7794`; prefix distribution: R8A7794: 30.
- Export categories inferred from names: clock: 30.
- First exported ID: `R8A7794_CLK_Z2=0`; last exported ID: `R8A7794_CLK_OSC=29`.
- Representative exported IDs: `R8A7794_CLK_Z2=0`, `R8A7794_CLK_ZG=1`, `R8A7794_CLK_ZTR=2`, `R8A7794_CLK_ZTRD2=3`, `R8A7794_CLK_ZT=4`, `...=...`, `R8A7794_CLK_RCAN=27`, `R8A7794_CLK_R=28`, `R8A7794_CLK_OSC=29`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7794-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7795-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7795-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 51 across 66 source lines.
- Dominant prefix: `R8A7795`; prefix distribution: R8A7795: 51.
- Export categories inferred from names: clock: 51.
- First exported ID: `R8A7795_CLK_Z=0`; last exported ID: `R8A7795_CLK_S0D12=51`.
- Representative exported IDs: `R8A7795_CLK_Z=0`, `R8A7795_CLK_Z2=1`, `R8A7795_CLK_ZR=2`, `R8A7795_CLK_ZG=3`, `R8A7795_CLK_ZTR=4`, `...=...`, `R8A7795_CLK_S0D6=49`, `R8A7795_CLK_S0D8=50`, `R8A7795_CLK_S0D12=51`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7795-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7796-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7796-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 52 across 65 source lines.
- Dominant prefix: `R8A7796`; prefix distribution: R8A7796: 52.
- Export categories inferred from names: clock: 52.
- First exported ID: `R8A7796_CLK_Z=0`; last exported ID: `R8A7796_CLK_OSC=52`.
- Representative exported IDs: `R8A7796_CLK_Z=0`, `R8A7796_CLK_Z2=1`, `R8A7796_CLK_ZR=2`, `R8A7796_CLK_ZG=3`, `R8A7796_CLK_ZTR=4`, `...=...`, `R8A7796_CLK_CPEX=50`, `R8A7796_CLK_R=51`, `R8A7796_CLK_OSC=52`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a7796-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77961-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77961-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 52 across 65 source lines.
- Dominant prefix: `R8A77961`; prefix distribution: R8A77961: 52.
- Export categories inferred from names: clock: 52.
- First exported ID: `R8A77961_CLK_Z=0`; last exported ID: `R8A77961_CLK_OSC=52`.
- Representative exported IDs: `R8A77961_CLK_Z=0`, `R8A77961_CLK_Z2=1`, `R8A77961_CLK_ZR=2`, `R8A77961_CLK_ZG=3`, `R8A77961_CLK_ZTR=4`, `...=...`, `R8A77961_CLK_CPEX=50`, `R8A77961_CLK_R=51`, `R8A77961_CLK_OSC=52`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77961-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77965-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77965-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 50 across 62 source lines.
- Dominant prefix: `R8A77965`; prefix distribution: R8A77965: 50.
- Export categories inferred from names: clock: 50.
- First exported ID: `R8A77965_CLK_Z=0`; last exported ID: `R8A77965_CLK_OSC=49`.
- Representative exported IDs: `R8A77965_CLK_Z=0`, `R8A77965_CLK_ZR=1`, `R8A77965_CLK_ZG=2`, `R8A77965_CLK_ZTR=3`, `R8A77965_CLK_ZTRD2=4`, `...=...`, `R8A77965_CLK_CPEX=47`, `R8A77965_CLK_R=48`, `R8A77965_CLK_OSC=49`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77965-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77970-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77970-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 31 across 44 source lines.
- Dominant prefix: `R8A77970`; prefix distribution: R8A77970: 31.
- Export categories inferred from names: clock: 31.
- First exported ID: `R8A77970_CLK_Z2=0`; last exported ID: `R8A77970_CLK_OSC=30`.
- Representative exported IDs: `R8A77970_CLK_Z2=0`, `R8A77970_CLK_ZR=1`, `R8A77970_CLK_ZTR=2`, `R8A77970_CLK_ZTRD2=3`, `R8A77970_CLK_ZT=4`, `...=...`, `R8A77970_CLK_CPEX=28`, `R8A77970_CLK_R=29`, `R8A77970_CLK_OSC=30`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77970-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77980-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77980-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 38 across 51 source lines.
- Dominant prefix: `R8A77980`; prefix distribution: R8A77980: 38.
- Export categories inferred from names: clock: 38.
- First exported ID: `R8A77980_CLK_Z2=0`; last exported ID: `R8A77980_CLK_OSC=37`.
- Representative exported IDs: `R8A77980_CLK_Z2=0`, `R8A77980_CLK_ZR=1`, `R8A77980_CLK_ZTR=2`, `R8A77980_CLK_ZTRD2=3`, `R8A77980_CLK_ZT=4`, `...=...`, `R8A77980_CLK_CPEX=35`, `R8A77980_CLK_R=36`, `R8A77980_CLK_OSC=37`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77980-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77990-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77990-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 50 across 62 source lines.
- Dominant prefix: `R8A77990`; prefix distribution: R8A77990: 50.
- Export categories inferred from names: clock: 50.
- First exported ID: `R8A77990_CLK_Z2=0`; last exported ID: `R8A77990_CLK_CPEX=49`.
- Representative exported IDs: `R8A77990_CLK_Z2=0`, `R8A77990_CLK_ZR=1`, `R8A77990_CLK_ZG=2`, `R8A77990_CLK_ZTR=3`, `R8A77990_CLK_ZT=4`, `...=...`, `R8A77990_CLK_CSI0=47`, `R8A77990_CLK_CP=48`, `R8A77990_CLK_CPEX=49`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77990-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77995-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77995-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 40 across 54 source lines.
- Dominant prefix: `R8A77995`; prefix distribution: R8A77995: 40.
- Export categories inferred from names: clock: 40.
- First exported ID: `R8A77995_CLK_Z2=0`; last exported ID: `R8A77995_CLK_CPEX=41`.
- Representative exported IDs: `R8A77995_CLK_Z2=0`, `R8A77995_CLK_ZG=1`, `R8A77995_CLK_ZTR=2`, `R8A77995_CLK_ZT=3`, `R8A77995_CLK_ZX=4`, `...=...`, `R8A77995_CLK_LV1=39`, `R8A77995_CLK_CP=40`, `R8A77995_CLK_CPEX=41`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a77995-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a779a0-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a779a0-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 44 across 56 source lines.
- Dominant prefix: `R8A779A0`; prefix distribution: R8A779A0: 44.
- Export categories inferred from names: clock: 44.
- First exported ID: `R8A779A0_CLK_Z0=0`; last exported ID: `R8A779A0_CLK_ZG=43`.
- Representative exported IDs: `R8A779A0_CLK_Z0=0`, `R8A779A0_CLK_ZX=1`, `R8A779A0_CLK_Z1=2`, `R8A779A0_CLK_ZR=3`, `R8A779A0_CLK_ZS=4`, `...=...`, `R8A779A0_CLK_R=41`, `R8A779A0_CLK_OSC=42`, `R8A779A0_CLK_ZG=43`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a779a0-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a779f0-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a779f0-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 51 across 64 source lines.
- Dominant prefix: `R8A779F0`; prefix distribution: R8A779F0: 51.
- Export categories inferred from names: clock: 51.
- First exported ID: `R8A779F0_CLK_ZX=0`; last exported ID: `R8A779F0_CLK_R=50`.
- Representative exported IDs: `R8A779F0_CLK_ZX=0`, `R8A779F0_CLK_ZS=1`, `R8A779F0_CLK_ZT=2`, `R8A779F0_CLK_ZTR=3`, `R8A779F0_CLK_S0D2=4`, `...=...`, `R8A779F0_CLK_CPEX=48`, `R8A779F0_CLK_CBFUSA=49`, `R8A779F0_CLK_R=50`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a779f0-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a779g0-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a779g0-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 78 across 91 source lines.
- Dominant prefix: `R8A779G0`; prefix distribution: R8A779G0: 78.
- Export categories inferred from names: clock: 78.
- First exported ID: `R8A779G0_CLK_ZX=0`; last exported ID: `R8A779G0_CLK_CP=77`.
- Representative exported IDs: `R8A779G0_CLK_ZX=0`, `R8A779G0_CLK_ZS=1`, `R8A779G0_CLK_ZT=2`, `R8A779G0_CLK_ZTR=3`, `R8A779G0_CLK_S0D2=4`, `...=...`, `R8A779G0_CLK_CBFUSA=75`, `R8A779G0_CLK_R=76`, `R8A779G0_CLK_CP=77`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r8a779g0-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a06g032-sysctrl.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a06g032-sysctrl.h

## Purpose
Renesas system-controller clock binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This legacy Renesas clock binding provides SoC-specific clock or MSTP bit identifiers without a dependency on the shared CPG/MSSR selector header. The values map directly to device-tree clock cells and older Renesas clock provider tables.

## Important APIs, Types, and Exports
- Exported macro count: 135 across 149 source lines.
- Dominant prefix: `R9A06G032`; prefix distribution: R9A06G032: 135.
- Export categories inferred from names: clock: 134, selector: 1.
- First exported ID: `R9A06G032_CLK_PLL_USB=1`; last exported ID: `R9A06G032_CLK_UART7=153`.
- Representative exported IDs: `R9A06G032_CLK_PLL_USB=1`, `R9A06G032_CLK_48=1`, `R9A06G032_MSEBIS_CLK=3`, `R9A06G032_MSEBIM_CLK=3`, `R9A06G032_CLK_DDRPHY_PLLCLK=5`, `...=...`, `R9A06G032_CLK_UART5=151`, `R9A06G032_CLK_UART6=152`, `R9A06G032_CLK_UART7=153`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a06g032-sysctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a07g043-cpg.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a07g043-cpg.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 187 across 203 source lines.
- Dominant prefix: `R9A07G043`; prefix distribution: R9A07G043: 187.
- Export categories inferred from names: clock: 105, reset: 80, selector: 2.
- First exported ID: `R9A07G043_CLK_I=0`; last exported ID: `R9A07G043_IAX45_RESETN=79`.
- Representative exported IDs: `R9A07G043_CLK_I=0`, `R9A07G043_CLK_I2=1`, `R9A07G043_CLK_S0=2`, `R9A07G043_CLK_SPI0=3`, `R9A07G043_CLK_SPI1=4`, `...=...`, `R9A07G043_AX45MP_L2_RESETN=77`, `R9A07G043_AX45MP_CORE0_RESETN=78`, `R9A07G043_IAX45_RESETN=79`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a07g043-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a07g044-cpg.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a07g044-cpg.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 204 across 220 source lines.
- Dominant prefix: `R9A07G044`; prefix distribution: R9A07G044: 204.
- Export categories inferred from names: clock: 119, reset: 84, selector: 1.
- First exported ID: `R9A07G044_CLK_I=0`; last exported ID: `R9A07G044_TSU_PRESETN=83`.
- Representative exported IDs: `R9A07G044_CLK_I=0`, `R9A07G044_CLK_I2=1`, `R9A07G044_CLK_G=2`, `R9A07G044_CLK_S0=3`, `R9A07G044_CLK_S1=4`, `...=...`, `R9A07G044_ADC_PRESETN=81`, `R9A07G044_ADC_ADRST_N=82`, `R9A07G044_TSU_PRESETN=83`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a07g044-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a07g054-cpg.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a07g054-cpg.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 213 across 229 source lines.
- Dominant prefix: `R9A07G054`; prefix distribution: R9A07G054: 213.
- Export categories inferred from names: clock: 127, reset: 85, selector: 1.
- First exported ID: `R9A07G054_CLK_I=0`; last exported ID: `R9A07G054_STPAI_ARESETN=84`.
- Representative exported IDs: `R9A07G054_CLK_I=0`, `R9A07G054_CLK_I2=1`, `R9A07G054_CLK_G=2`, `R9A07G054_CLK_S0=3`, `R9A07G054_CLK_S1=4`, `...=...`, `R9A07G054_ADC_ADRST_N=82`, `R9A07G054_TSU_PRESETN=83`, `R9A07G054_STPAI_ARESETN=84`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a07g054-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a08g045-cpg.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a08g045-cpg.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 226 across 242 source lines.
- Dominant prefix: `R9A08G045`; prefix distribution: R9A08G045: 226.
- Export categories inferred from names: clock: 130, reset: 94, selector: 2.
- First exported ID: `R9A08G045_CLK_I=0`; last exported ID: `R9A08G045_VBAT_BRESETN=93`.
- Representative exported IDs: `R9A08G045_CLK_I=0`, `R9A08G045_CLK_I2=1`, `R9A08G045_CLK_I3=2`, `R9A08G045_CLK_S0=3`, `R9A08G045_CLK_SPI0=4`, `...=...`, `R9A08G045_I3C_TRESETN=91`, `R9A08G045_I3C_PRESETN=92`, `R9A08G045_VBAT_BRESETN=93`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a08g045-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a09g011-cpg.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a09g011-cpg.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 302 across 352 source lines.
- Dominant prefix: `R9A09G011`; prefix distribution: R9A09G011: 302.
- Export categories inferred from names: clock: 205, power-domain: 1, reset: 94, selector: 2.
- First exported ID: `R9A09G011_SYS_CLK=0`; last exported ID: `R9A09G011_DDI_RESETN_APB=94`.
- Representative exported IDs: `R9A09G011_SYS_CLK=0`, `R9A09G011_PFC_PCLK=1`, `R9A09G011_PMC_CORE_CLOCK=2`, `R9A09G011_GIC_CLK=3`, `R9A09G011_RAMA_ACLK=4`, `...=...`, `R9A09G011_DDI_PWROK=92`, `R9A09G011_DDI_RESET=93`, `R9A09G011_DDI_RESETN_APB=94`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/r9a09g011-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/raspberrypi,rp1-clocks.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/raspberrypi,rp1-clocks.h

## Purpose
Raspberry Pi RP1 clock binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This RP1 binding enumerates PLL cores, PLL output channels, peripheral clocks, and DSI byte clocks for the Raspberry Pi RP1 clock provider. It is intentionally a flat numeric table used by RP1 device-tree clock references.

## Important APIs, Types, and Exports
- Exported macro count: 47 across 65 source lines.
- Dominant prefix: `RP1`; prefix distribution: RP1: 47.
- Export categories inferred from names: clock: 47.
- First exported ID: `RP1_PLL_SYS_CORE=0`; last exported ID: `RP1_CLK_MIPI1_DSI_BYTECLOCK=46`.
- Representative exported IDs: `RP1_PLL_SYS_CORE=0`, `RP1_PLL_AUDIO_CORE=1`, `RP1_PLL_VIDEO_CORE=2`, `RP1_PLL_SYS=3`, `RP1_PLL_AUDIO=4`, `...=...`, `RP1_PLL_AUDIO_TERN=44`, `RP1_CLK_MIPI0_DSI_BYTECLOCK=45`, `RP1_CLK_MIPI1_DSI_BYTECLOCK=46`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/raspberrypi,rp1-clocks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r8a779h0-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r8a779h0-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 83 across 96 source lines.
- Dominant prefix: `R8A779H0`; prefix distribution: R8A779H0: 83.
- Export categories inferred from names: clock: 83.
- First exported ID: `R8A779H0_CLK_ZX=0`; last exported ID: `R8A779H0_CLK_R=82`.
- Representative exported IDs: `R8A779H0_CLK_ZX=0`, `R8A779H0_CLK_ZD=1`, `R8A779H0_CLK_ZS=2`, `R8A779H0_CLK_ZT=3`, `R8A779H0_CLK_ZTR=4`, `...=...`, `R8A779H0_CLK_CP=80`, `R8A779H0_CLK_CBFUSA=81`, `R8A779H0_CLK_R=82`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r8a779h0-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a08g045-vbattb.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a08g045-vbattb.h

## Purpose
Renesas VBATTB clock binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This legacy Renesas clock binding provides SoC-specific clock or MSTP bit identifiers without a dependency on the shared CPG/MSSR selector header. The values map directly to device-tree clock cells and older Renesas clock provider tables.

## Important APIs, Types, and Exports
- Exported macro count: 4 across 13 source lines.
- Dominant prefix: `VBATTB`; prefix distribution: VBATTB: 4.
- Export categories inferred from names: clock: 1, selector: 3.
- First exported ID: `VBATTB_XC=0`; last exported ID: `VBATTB_VBATTCLK=3`.
- Representative exported IDs: `VBATTB_XC=0`, `VBATTB_XBYP=1`, `VBATTB_MUX=2`, `VBATTB_VBATTCLK=3`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a08g045-vbattb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a08g046-cpg.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a08g046-cpg.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 326 across 342 source lines.
- Dominant prefix: `R9A08G046`; prefix distribution: R9A08G046: 326.
- Export categories inferred from names: clock: 206, reset: 118, selector: 2.
- First exported ID: `R9A08G046_CLK_I=0`; last exported ID: `R9A08G046_BSC_X_PRESET_BSC=117`.
- Representative exported IDs: `R9A08G046_CLK_I=0`, `R9A08G046_CLK_IC0=1`, `R9A08G046_CLK_IC1=2`, `R9A08G046_CLK_IC2=3`, `R9A08G046_CLK_IC3=4`, `...=...`, `R9A08G046_RSCI3_TRESETN=115`, `R9A08G046_LVDS_RESET_N=116`, `R9A08G046_BSC_X_PRESET_BSC=117`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a08g046-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g047-cpg.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g047-cpg.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 16 across 28 source lines.
- Dominant prefix: `R9A09G047`; prefix distribution: R9A09G047: 16.
- Export categories inferred from names: clock: 16.
- First exported ID: `R9A09G047_SYS_0_PCLK=0`; last exported ID: `R9A09G047_USB2_0_CLK_CORE1=15`.
- Representative exported IDs: `R9A09G047_SYS_0_PCLK=0`, `R9A09G047_CA55_0_CORECLK0=1`, `R9A09G047_CA55_0_CORECLK1=2`, `R9A09G047_CA55_0_CORECLK2=3`, `R9A09G047_CA55_0_CORECLK3=4`, `...=...`, `R9A09G047_USB3_0_CLKCORE=13`, `R9A09G047_USB2_0_CLK_CORE0=14`, `R9A09G047_USB2_0_CLK_CORE1=15`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g047-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g056-cpg.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g056-cpg.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 15 across 27 source lines.
- Dominant prefix: `R9A09G056`; prefix distribution: R9A09G056: 15.
- Export categories inferred from names: clock: 15.
- First exported ID: `R9A09G056_SYS_0_PCLK=0`; last exported ID: `R9A09G056_USB3_0_CLKCORE=14`.
- Representative exported IDs: `R9A09G056_SYS_0_PCLK=0`, `R9A09G056_CA55_0_CORE_CLK0=1`, `R9A09G056_CA55_0_CORE_CLK1=2`, `R9A09G056_CA55_0_CORE_CLK2=3`, `R9A09G056_CA55_0_CORE_CLK3=4`, `...=...`, `R9A09G056_SPI_CLK_SPI=12`, `R9A09G056_USB3_0_REF_ALT_CLK_P=13`, `R9A09G056_USB3_0_CLKCORE=14`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g056-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g057-cpg.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g057-cpg.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 18 across 30 source lines.
- Dominant prefix: `R9A09G057`; prefix distribution: R9A09G057: 18.
- Export categories inferred from names: clock: 18.
- First exported ID: `R9A09G057_SYS_0_PCLK=0`; last exported ID: `R9A09G057_USB3_1_CLKCORE=17`.
- Representative exported IDs: `R9A09G057_SYS_0_PCLK=0`, `R9A09G057_CA55_0_CORE_CLK0=1`, `R9A09G057_CA55_0_CORE_CLK1=2`, `R9A09G057_CA55_0_CORE_CLK2=3`, `R9A09G057_CA55_0_CORE_CLK3=4`, `...=...`, `R9A09G057_USB3_0_CLKCORE=15`, `R9A09G057_USB3_1_REF_ALT_CLK_P=16`, `R9A09G057_USB3_1_CLKCORE=17`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g057-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g077-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g077-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 25 across 38 source lines.
- Dominant prefix: `R9A09G077`; prefix distribution: R9A09G077: 25.
- Export categories inferred from names: clock: 25.
- First exported ID: `R9A09G077_CLK_CA55C0=0`; last exported ID: `R9A09G077_PCLKCAN=24`.
- Representative exported IDs: `R9A09G077_CLK_CA55C0=0`, `R9A09G077_CLK_CA55C1=1`, `R9A09G077_CLK_CA55C2=2`, `R9A09G077_CLK_CA55C3=3`, `R9A09G077_CLK_CA55S=4`, `...=...`, `R9A09G077_XSPI_CLK0=22`, `R9A09G077_XSPI_CLK1=23`, `R9A09G077_PCLKCAN=24`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g077-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g087-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g087-cpg-mssr.h

## Purpose
Renesas CPG/MSSR clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Renesas CPG/MSSR binding lists SoC core clock IDs and, on newer families, reset/module IDs that pair with `renesas-cpg-mssr.h` selectors. The IDs are used by DTS clock/reset specifiers and by the matching CPG/MSSR driver tables.

## Important APIs, Types, and Exports
- Exported macro count: 25 across 38 source lines.
- Dominant prefix: `R9A09G087`; prefix distribution: R9A09G087: 25.
- Export categories inferred from names: clock: 25.
- First exported ID: `R9A09G087_CLK_CA55C0=0`; last exported ID: `R9A09G087_PCLKCAN=24`.
- Representative exported IDs: `R9A09G087_CLK_CA55C0=0`, `R9A09G087_CLK_CA55C1=1`, `R9A09G087_CLK_CA55C2=2`, `R9A09G087_CLK_CA55C3=3`, `R9A09G087_CLK_CA55S=4`, `...=...`, `R9A09G087_XSPI_CLK0=22`, `R9A09G087_XSPI_CLK1=23`, `R9A09G087_PCLKCAN=24`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/renesas-cpg-mssr.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas,r9a09g087-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas-cpg-mssr.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas-cpg-mssr.h

## Purpose
Renesas CPG/MSSR shared binding selector header. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This shared Renesas header defines the clock-specifier type selector used by SoC CPG/MSSR bindings. `CPG_CORE` and `CPG_MOD` identify whether a device-tree clock specifier names a core clock or a module clock.

## Important APIs, Types, and Exports
- Exported macro count: 2 across 11 source lines.
- Dominant prefix: `CPG`; prefix distribution: CPG: 2.
- Export categories inferred from names: clock: 2.
- First exported ID: `CPG_CORE=0`; last exported ID: `CPG_MOD=1`.
- Representative exported IDs: `CPG_CORE=0`, `CPG_MOD=1`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/renesas-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3036-cru.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3036-cru.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 156 across 186 source lines.
- Dominant prefix: `SRST`; prefix distribution: ACLK: 6, ARMCLK: 1, HCLK: 15, PCLK: 19, PLL: 3, SCLK: 34, SRST: 78.
- Export categories inferred from names: clock: 78, reset: 78.
- First exported ID: `PLL_APLL=1`; last exported ID: `SRST_DBG_P=131`.
- Representative exported IDs: `PLL_APLL=1`, `PLL_DPLL=2`, `PLL_GPLL=3`, `ARMCLK=4`, `SCLK_GPU=64`, `...=...`, `SRST_GPU=120`, `SRST_GPU_NIU_A=122`, `SRST_DBG_P=131`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3036-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3066a-cru.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3066a-cru.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 13 across 31 source lines.
- Dominant prefix: `SRST`; prefix distribution: SRST: 13.
- Export categories inferred from names: reset: 13.
- First exported ID: `SRST_SRST1=0`; last exported ID: `SRST_CIF1=111`.
- Representative exported IDs: `SRST_SRST1=0`, `SRST_SRST2=1`, `SRST_L2MEM=18`, `SRST_I2S0=23`, `SRST_I2S1=24`, `...=...`, `SRST_HDMI=96`, `SRST_HDMI_APB=97`, `SRST_CIF1=111`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/rk3188-cru-common.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3066a-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3128-cru.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3128-cru.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 241 across 273 source lines.
- Dominant prefix: `SRST`; prefix distribution: ACLK: 14, ARMCLK: 1, DCLK: 2, HCLK: 26, PCLK: 29, PLL: 6, SCLK: 49, SRST: 114.
- Export categories inferred from names: clock: 127, reset: 114.
- First exported ID: `PLL_APLL=1`; last exported ID: `SRST_VIO_MIPI_DSI=137`.
- Representative exported IDs: `PLL_APLL=1`, `PLL_DPLL=2`, `PLL_CPLL=3`, `PLL_GPLL=4`, `ARMCLK=5`, `...=...`, `SRST_TIMER5=135`, `SRST_VIO_H2P=136`, `SRST_VIO_MIPI_DSI=137`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3128-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3188-cru-common.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3188-cru-common.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 229 across 261 source lines.
- Dominant prefix: `SRST`; prefix distribution: ACLK: 15, ARMCLK: 1, CORE: 2, DCLK: 2, HCLK: 26, PCLK: 36, PLL: 4, SCLK: 30, SRST: 113.
- Export categories inferred from names: clock: 114, reset: 113, selector: 2.
- First exported ID: `PLL_APLL=1`; last exported ID: `SRST_TS=143`.
- Representative exported IDs: `PLL_APLL=1`, `PLL_DPLL=2`, `PLL_CPLL=3`, `PLL_GPLL=4`, `CORE_PERI=5`, `...=...`, `SRST_PTM1_ATB=141`, `SRST_CTM=142`, `SRST_TS=143`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3188-cru-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3188-cru.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3188-cru.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 27 across 47 source lines.
- Dominant prefix: `SRST`; prefix distribution: SRST: 27.
- Export categories inferred from names: reset: 27.
- First exported ID: `SRST_PTM_CORE2=0`; last exported ID: `SRST_CTI3_APB=124`.
- Representative exported IDs: `SRST_PTM_CORE2=0`, `SRST_PTM_CORE3=1`, `SRST_CORE2=5`, `SRST_CORE3=6`, `SRST_CORE2_DBG=10`, `...=...`, `SRST_GPU_BRIDGE=121`, `SRST_CTI3=123`, `SRST_CTI3_APB=124`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: `#include <dt-bindings/clock/rk3188-cru-common.h>`
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3188-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3228-cru.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3228-cru.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 253 across 285 source lines.
- Dominant prefix: `SRST`; prefix distribution: ACLK: 17, ARMCLK: 1, DCLK: 2, HCLK: 28, PCLK: 25, PLL: 4, SCLK: 50, SRST: 126.
- Export categories inferred from names: clock: 127, reset: 126.
- First exported ID: `PLL_APLL=1`; last exported ID: `SRST_TIMER_6CH_P=141`.
- Representative exported IDs: `PLL_APLL=1`, `PLL_DPLL=2`, `PLL_CPLL=3`, `PLL_GPLL=4`, `ARMCLK=5`, `...=...`, `SRST_HDMIPHY=139`, `SRST_VDAC=140`, `SRST_TIMER_6CH_P=141`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3228-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3288-cru.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3288-cru.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 343 across 378 source lines.
- Dominant prefix: `SRST`; prefix distribution: ACLK: 19, ARMCLK: 1, DCLK: 2, HCLK: 31, PCLK: 52, PLL: 5, SCLK: 66, SRST: 167.
- Export categories inferred from names: clock: 176, reset: 167.
- First exported ID: `PLL_APLL=1`; last exported ID: `SRST_TSP_27M=191`.
- Representative exported IDs: `PLL_APLL=1`, `PLL_DPLL=2`, `PLL_CPLL=3`, `PLL_GPLL=4`, `PLL_NPLL=5`, `...=...`, `SRST_TSP_CLKIN0=189`, `SRST_TSP_CLKIN1=190`, `SRST_TSP_27M=191`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3288-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3308-cru.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3308-cru.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 341 across 385 source lines.
- Dominant prefix: `SRST`; prefix distribution: ACLK: 10, ARMCLK: 1, DCLK: 1, HCLK: 23, PCLK: 45, PLL: 4, SCLK: 108, SRST: 148, USB480M: 1.
- Export categories inferred from names: clock: 192, reset: 148, selector: 1.
- First exported ID: `PLL_APLL=1`; last exported ID: `SRST_ACODEC_P=153`.
- Representative exported IDs: `PLL_APLL=1`, `PLL_DPLL=2`, `PLL_VPLL0=3`, `PLL_VPLL1=4`, `ARMCLK=5`, `...=...`, `SRST_I2S1_2CH_M=151`, `SRST_VAD_H=152`, `SRST_ACODEC_P=153`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3308-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3328-cru.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3328-cru.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 356 across 391 source lines.
- Dominant prefix: `SRST`; prefix distribution: ACLK: 28, ARMCLK: 1, DCLK: 3, HCLK: 33, HDMIPHY: 1, PCLK: 37, PLL: 5, SCLK: 73, SRST: 174, USB480M: 1.
- Export categories inferred from names: clock: 180, reset: 174, selector: 2.
- First exported ID: `PLL_APLL=1`; last exported ID: `SRST_RKVENC_INTMEM=184`.
- Representative exported IDs: `PLL_APLL=1`, `PLL_DPLL=2`, `PLL_CPLL=3`, `PLL_GPLL=4`, `PLL_NPLL=5`, `...=...`, `SRST_RKVENC_H264_A=182`, `SRST_RKVENC_H264_H=183`, `SRST_RKVENC_INTMEM=184`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3328-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3368-cru.h -->
# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3368-cru.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 347 across 383 source lines.
- Dominant prefix: `SRST`; prefix distribution: ACLK: 18, ARMCLKB: 1, ARMCLKL: 1, DCLK: 1, HCLK: 28, MCLK: 1, PCLK: 47, PLL: 6, SCLK: 63, SRST: 181.
- Export categories inferred from names: clock: 166, reset: 181.
- First exported ID: `PLL_APLLB=1`; last exported ID: `SRST_TIMER1_APB=237`.
- Representative exported IDs: `PLL_APLLB=1`, `PLL_APLLL=2`, `PLL_DPLL=3`, `PLL_CPLL=4`, `PLL_GPLL=5`, `...=...`, `SRST_TIMER15=235`, `SRST_TIMER0_APB=236`, `SRST_TIMER1_APB=237`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3368-cru.h -->
