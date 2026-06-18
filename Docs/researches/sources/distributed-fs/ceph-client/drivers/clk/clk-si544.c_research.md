# sources/distributed-fs/ceph-client/drivers/clk/clk-si544.c

Purpose: I2C CCF driver for Silicon Labs Si544 programmable oscillators. It exposes the oscillator as a zero-parent programmable clock with output enable control and rate programming across Si544A/B/C speed grades.

Important APIs/types/functions: `struct clk_si544` stores `clk_hw`, regmap, I2C client, and max frequency. `struct clk_si544_muldiv` stores feedback divider, high-speed divider, low-speed divider, and delta adjustment. Key helpers are `si544_get_muldiv()`, `si544_set_delta_m()`, `si544_set_muldiv()`, `si544_calc_muldiv()`, `si544_calc_center_rate()`, `si544_calc_rate()`, `si544_max_delta()`, `si544_calc_delta()`, and `si544_enable_output()`. CCF ops are `si544_prepare`, `si544_unprepare`, `si544_is_prepared`, `si544_recalc_rate`, `si544_determine_rate`, and `si544_set_rate`.

Control flow: probe chooses the max frequency from I2C/OF match data, names the clock from `clock-output-names` or the DT node, creates an 8-bit cached regmap, selects page 0, registers the clock, and adds a simple OF provider. Runtime rate changes first validate range. If the requested rate is within the Si544 delta-M fine-adjustment range of the current center frequency, only ADPLL delta registers are changed. Larger changes compute new dividers, read output-enable state, disable the output, allow FCAL, reset delta, write divider registers with feedback MSB last to trigger the change, start calibration, wait 10-12 ms, and restore output state if it was enabled.

State and persistence: hardware registers hold dividers, fine frequency offset, calibration state, page selection, and output enable. Regmap uses MAPLE cache with volatile control/FCAL registers. The driver persists no software rate cache beyond max frequency; recalc reads hardware each time.

Dependencies and integration: depends on I2C, regmap, CCF, 64-bit division helpers, DT compatible strings `silabs,si544a/b/c`, and optional `clock-output-names`. Consumers obtain the single clock through `of_clk_hw_simple_get`.

Risks: many writes after disabling output return immediately on error and can leave output disabled or hardware partially programmed. Fine-adjustment arithmetic relies on signed 24-bit delta decoding and ppm constants. `determine_rate()` accepts any valid rate because expected accuracy is sub-Hz, so hardware behavior is only proven at set-time. No locking protects concurrent set_rate/prepare operations beyond CCF serialization assumptions.

Test signals: validate each speed grade max range, small delta-M-only changes, large divider/calibration changes, output enable preservation on success/failure, recalc against known register values, page selection, and OF provider registration. No direct unit tests are present.
