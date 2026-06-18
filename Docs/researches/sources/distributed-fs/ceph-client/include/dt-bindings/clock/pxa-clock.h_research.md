# sources/distributed-fs/ceph-client/include/dt-bindings/clock/pxa-clock.h

Purpose: defines legacy PXA2xx/PXA3xx clock IDs consumed by PXA clock providers and device-tree users. It exports 63 contiguous `CLK_*` IDs from `CLK_NONE` through `CLK_MAX`, covering UARTs, SSP/I2C/I2S, LCD, memory, GPIO, USB, MMC, camera, timers, and board-specific functional clocks.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 63 exported defines, numeric range 0..62, first numeric symbols `CLK_NONE`=0, `CLK_1WIRE`=1, `CLK_AC97`=2, `CLK_AC97CONF`=3, `CLK_ASSP`=4, and last numeric symbols `CLK_USIM`=58, `CLK_USIM1`=59, `CLK_USMI0`=60, `CLK_OSC32k768`=61, `CLK_MAX`=62. Dominant macro prefixes are `CLK`(63); common suffix categories are `GCU`(2), `IM`(2), `LCD`(2), `1WIRE`(1), `AC97`(1), `AC97CONF`(1), `ASSP`(1), `BOOT`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs are shared by PXA DTS users and the PXA clock drivers in `drivers/clk/pxa/`, preserving compatibility with older board and SoC clock naming.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `__DT_BINDINGS_CLOCK_PXA2XX_H__` should remain unique enough to avoid accidental include suppression. Since the file has no executable validation, errors usually appear as boot-time probe failures, missing clocks, or devices stuck in reset.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include provider probe success and expected entries in common-clock debugfs output.
