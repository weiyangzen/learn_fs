# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-imp_iic_wrap.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-imp_iic_wrap.c

### Purpose
`clk-mt8196-imp_iic_wrap.c` supplies MT8196 I2C wrapper clocks for central, east, north, and west I2C domains. It exposes gates for I2C0 through I2C14 using regional parent clocks.

### Important APIs, Types, And Functions
The file defines shared direct gate registers `imp_cg_regs`, one north HWV register block, `GATE_IMP`, `GATE_HWV_IMPN`, four clock arrays, and four descriptors. `of_match_clk_mt8196_imp_iic_wrap` maps each regional compatible to the correct descriptor. Probe/remove are `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

### Control Flow, State, And Persistence
OF matching chooses central/east/north/west tables. The common helper registers the selected gate clocks and provider. Most gates directly write set/clear/status offsets around 0xe00; `impn_i2c7` uses hardware voter registers. The driver keeps no persistent state outside clock registration data.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `i2c_p`, `i2c_east`, `i2c_north`, and `i2c_west`, I2C controller consumers, and HWV support. Risks include regional compatible mismatches, one HWV-only north clock path, and I2C probe failures when parent topckgen clocks are absent. Test signals include all I2C bus probes, runtime clock gating during transfers, north I2C7 HWV completion, and DT binding coverage.
