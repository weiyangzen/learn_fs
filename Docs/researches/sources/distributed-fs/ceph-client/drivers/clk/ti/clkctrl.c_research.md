# sources/distributed-fs/ceph-client/drivers/clk/ti/clkctrl.c

Purpose: OMAP4-style clkctrl provider implementation. It turns SoC-specific `omap_clkctrl_data[]` tables into CCF module clocks and optional subclocks, handles MODULEMODE enable/disable, waits for IDLEST transitions, and exposes two-cell clkctrl phandle translation.

Important APIs/types/functions: `CLK_OF_DECLARE(... "ti,clkctrl", _ti_omap4_clkctrl_setup)`, `_omap4_clkctrl_clk_enable()`, `_omap4_clkctrl_clk_disable()`, `_ti_omap4_clkctrl_xlate()`, `_ti_clkctrl_setup_gate/mux/div/subclks()`, `_ti_clkctrl_clk_register()`, and exported `ti_clk_is_in_standby()`. Internal state lives in `omap_clkctrl_provider` and `omap_clkctrl_clk`.

Control flow: setup maps node address, selects SoC data by machine compatible, applies SoC/security masks, derives a clockdomain name, maps MMIO, and iterates matching register entries. Each entry can create gate/mux/divider subclocks from bit data, then creates a primary module clock with SW or HW supervisor mode. The OF provider later resolves `<offset bit>` phandle arguments by scanning the provider list.

State and persistence: provider lists and allocated clocks persist. Runtime state is in PRCM MODULEMODE, IDLEST, and STBYST bits. `_early_timeout` switches from udelay loop counting to ktime-based timeout at `arch_initcall`, but timekeeping-suspended paths continue using delay loops.

Dependencies/integration: consumes SoC clkctrl tables from DRA7, OMAP, AM3/AM4, DM814, and DM816 files. Depends on `ti_clk_ll_ops`, clockdomain callbacks, CCF, OF address resources, and generated parent clock names.

Risks: offset/name generation must match DTS and alias tables. Incorrect `CLKF_NO_IDLEST` or supervisor flags cause hangs, false readiness, or modules left unmanaged. Timeout logic differs during early boot and suspend, which matters for clocks used by timers or PM.

Test signals: boot each supported SoC family, resolve clkctrl phandles, enable/disable modules, verify timeout logs are absent, test suspend/resume with clkctrl users, and inspect `ti_clk_is_in_standby()` behavior for OMAP clocks.
