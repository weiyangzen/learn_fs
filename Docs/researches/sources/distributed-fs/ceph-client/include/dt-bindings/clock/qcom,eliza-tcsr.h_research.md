# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,eliza-tcsr.h

Purpose: declares Qualcomm Eliza-family clock-controller binding IDs for `qcom,eliza-tcsr.h`. It exports 6 macros for a generated-style provider namespace, including controller clocks plus reset or GDSC IDs where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 6 exported defines, numeric range 0..5, first numeric symbols `TCSR_HDMI_CLKREF_EN`=0, `TCSR_PCIE_0_CLKREF_EN`=1, `TCSR_PCIE_1_CLKREF_EN`=2, `TCSR_UFS_CLKREF_EN`=3, `TCSR_USB2_CLKREF_EN`=4, and last numeric symbols `TCSR_PCIE_0_CLKREF_EN`=1, `TCSR_PCIE_1_CLKREF_EN`=2, `TCSR_UFS_CLKREF_EN`=3, `TCSR_USB2_CLKREF_EN`=4, `TCSR_USB3_CLKREF_EN`=5. Dominant macro prefixes are `TCSR`(6); common suffix categories are `EN`(6). Source section markers include `TCSR_CC clocks`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The macros align with Eliza TCSR clock-reference provider data and DTS nodes that gate external clock references.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_TCSR_CC_ELIZA_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
