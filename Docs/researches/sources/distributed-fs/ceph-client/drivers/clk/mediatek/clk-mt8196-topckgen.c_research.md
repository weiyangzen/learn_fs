# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-topckgen.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-topckgen.c

### Purpose
`clk-mt8196-topckgen.c` is the primary MT8196 top clock generator. It defines fixed factors, muxes, mux gates, fenced muxes, hardware-voter mux gates, and audio divider/composite clocks for CPU/peripheral/storage/audio/security/interconnect clock roots.

### Important APIs, Types, And Functions
Important tables are `top_divs`, many parent arrays, `top_muxes`, `top_aud_divs`, and `topck_desc`. It uses macros from `clk-mux.h` including `MUX_CLR_SET_UPD`, `MUX_GATE_CLR_SET_UPD`, `MUX_GATE_FENC_CLR_SET_UPD`, `MUX_GATE_HWV_FENC_CLR_SET_UPD`, `MUX_DIV_GATE`, and `DIV_GATE`. The descriptor is registered via `mtk_clk_simple_probe()`.

### Control Flow, State, And Persistence
Probe is fully table driven: the common helper registers factors, muxes, and composites, then exposes the OF provider for `mediatek,mt8196-topckgen`. Mux state is persisted in hardware `CLK_CFG_*` registers with set/clear/update writes. Fenced muxes check `CLK_FENC_STATUS_MON_*`; HWV muxes use HW voter set/clear/done registers. Audio dividers store divider fields in `CLK_AUDDIV_*`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include APMIXED PLL names, VLP audio PLLs, ULP oscillator parents, HWV support, and nearly every MT8196 peripheral driver. Risks are parent-list ordering, update-bit mapping, fencing status bits, missing separators in parent strings, and critical clocks accidentally gated. Test signals include full boot provider resolution, clk tree dumps, peripheral probes, mux rate switching, audio I2S divider tests, and HWV/fence timeout instrumentation.
