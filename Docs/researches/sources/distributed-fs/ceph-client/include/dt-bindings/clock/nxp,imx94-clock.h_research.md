# sources/distributed-fs/ceph-client/include/dt-bindings/clock/nxp,imx94-clock.h

Purpose: declares i.MX9 block-controller clock selector/gate IDs for `nxp,imx94-clock.h`. It is intentionally compact, exporting 2 macros in local block namespaces such as VPUBLK, CAMBLK, DISPMIX, or NETCMIX; values span 0..0 and are reused per block because each provider interprets the index in its own clock domain.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 2 exported defines, numeric range 0..0, first numeric symbols `IMX94_CLK_DISPMIX_CLK_SEL`=0, `IMX94_CLK_DISPMIX_LVDS_CLK_GATE`=0, and last numeric symbols `IMX94_CLK_DISPMIX_CLK_SEL`=0, `IMX94_CLK_DISPMIX_LVDS_CLK_GATE`=0. Dominant macro prefixes are `IMX94`(2); common suffix categories are `GATE`(1), `SEL`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs integrate with i.MX block-control clock drivers, especially `drivers/clk/imx/clk-imx95-blk-ctl.c`, and with NETC/display/camera block-controller device-tree bindings.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `__DT_BINDINGS_CLOCK_IMX94_H` should remain unique enough to avoid accidental include suppression. Repeated numeric values are intentional across separate block-local namespaces, so tests and reviews must validate provider domain selection rather than global uniqueness.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include i.MX9 block-control provider probe, display/camera/NETC clock consumers resolving block-local indexes, and no accidental reliance on global uniqueness of small integer IDs.
