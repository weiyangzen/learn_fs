# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,apss-ipq.h

Purpose: declares Qualcomm IPQ APSS/L3 clock IDs for CPU alias/core and L3 clock providers. It exports 8 contiguous constants used by `apss-ipq6018` style providers and CPU/NOC consumers.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 8 exported defines, numeric range 0..7, first numeric symbols `APCS_ALIAS0_CLK_SRC`=0, `APCS_ALIAS0_CORE_CLK`=1, `APSS_PLL_EARLY`=2, `APSS_SILVER_CLK_SRC`=3, `APSS_SILVER_CORE_CLK`=4, and last numeric symbols `APSS_SILVER_CLK_SRC`=3, `APSS_SILVER_CORE_CLK`=4, `L3_PLL`=5, `L3_CLK_SRC`=6, `L3_CORE_CLK`=7. Dominant macro prefixes are `APSS`(3), `L3`(3), `APCS`(2); common suffix categories are `CLK`(3), `SRC`(3), `EARLY`(1), `PLL`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs match Qualcomm APSS clock providers such as `drivers/clk/qcom/apss-ipq6018.c` and CPU/L3 consumers in IPQ DTS files.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLOCK_QCA_APSS_IPQ6018_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
