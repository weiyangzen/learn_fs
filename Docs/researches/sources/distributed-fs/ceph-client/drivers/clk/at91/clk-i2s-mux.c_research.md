# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-i2s-mux.c

Purpose: simple SFR-backed mux provider selecting I2S bus clock source between the peripheral clock and generated clock on SAMA5D2-style hardware.

Important APIs and data: `at91_clk_i2s_mux_register()` allocates `struct clk_i2s_mux`, storing the SFR regmap and bus id. `clk_i2s_mux_ops` implements get_parent, set_parent, and mux determine-rate.

Control flow: get reads `AT91_SFR_I2SCLKSEL` and extracts the bit for `bus_id`. set updates that bit to the requested parent index. Registration accepts parent names and bus id from SoC setup or DT compat and registers a normal mux-like `clk_hw`.

State and persistence: the parent selection is persisted solely in SFR hardware. There are no save/restore hooks here, so retention depends on SFR state across suspend or reconfiguration by consumers after resume.

Dependencies and integration: uses `syscon_regmap_lookup_by_compatible("atmel,sama5d2-sfr")` in callers and `soc/at91/atmel-sfr.h` offsets. SAMA5D2 publishes `PMC_I2S0_MUX` and `PMC_I2S1_MUX` when SFR is available.

Risks: `set_parent` trusts common-clock parent index validation; a bad bus id would address an unintended bit. Test signals include I2S mux parent in clk_summary, SFR bit changes per bus, and audio playback/recording with both peripheral and GCK parents.
