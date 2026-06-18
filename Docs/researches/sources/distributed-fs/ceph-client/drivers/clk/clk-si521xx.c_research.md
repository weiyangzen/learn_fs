<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si521xx.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-si521xx.c

### Purpose
`clk-si521xx.c` supports Skyworks Si52144/Si52146/Si52147 PCIe clock generators. It registers each differential output as a CCF clock, controls output-enable bits, and optionally configures output amplitude.

### Important APIs, Types, And Functions
`struct si521xx` holds client, regmap, up to nine `struct si_clk`, chip info bit map, and amplitude setting. `struct si_clk` stores the per-output `clk_hw`, backpointer, OE register, and OE bit. Important functions include custom I2C regmap read/write helpers, `si521xx_diff_recalc_rate()`, `si521xx_diff_determine_rate()`, `si521xx_diff_prepare()`, `si521xx_diff_unprepare()`, `si521xx_get_common_config()`, `si521xx_update_config()`, `si521xx_diff_idx_to_reg_bit()`, `si521xx_probe()`, `si521xx_suspend()`, and `si521xx_resume()`.

### Control Flow, State, And Persistence
Probe decodes model match data into an OE bit map, parses optional `skyworks,out-amplitude-microvolt`, initializes a flat custom regmap, programs BCP for one-byte reads, registers one `DIFF%d` clock for every populated OE bit, maps logical output indexes to OE registers using bit reversal, publishes an OF provider, and writes non-default amplitude. Prepare/unprepare sets or clears the mapped OE bit. Suspend switches regmap to cache-only and marks dirty; resume syncs settings.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C, regmap cache, parent clock index 0, Skyworks DT compatibles, and PCIe reference-clock consumers. Risks include no phandle bounds check, OF match data for `skyworks,si52147` differing from I2C ID data, ignored regmap errors in prepare/unprepare, no hardware ID verification, and rate modeling as parent multiplied by four. Test signals include output count per model, OE bit mapping for all DIFF outputs, amplitude validation from 300000 to 1000000 uV in 100000 uV steps, suspend/resume cache restore, parent-rate propagation, and measured differential outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si521xx.c -->
