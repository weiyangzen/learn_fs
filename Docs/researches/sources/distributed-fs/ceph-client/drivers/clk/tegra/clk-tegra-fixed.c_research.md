<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-fixed.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-fixed.c

Purpose: initializes fixed root clocks common to Tegra SoCs: oscillator-derived roots (`osc`, `osc_div2`, `osc_div4`, `clk_m`, `pll_ref`) and the always-32768 Hz `clk_32k`. It also snapshots oscillator control bits for resume.

Important APIs, types, and functions: `tegra_osc_clk_init()` reads `OSC_CTRL`, maps the hardware oscillator index to a supplied frequency table, registers fixed-rate/fixed-factor roots into the SoC `struct tegra_clk` table, and optionally returns oscillator and PLL reference rates. `tegra_fixed_clk_init()` registers `clk_32k`. `tegra_clk_osc_resume()` restores saved oscillator control fields.

Control flow: `tegra_osc_clk_init()` saves `OSC_CTRL_MASK` bits in `osc_ctrl_ctx`, extracts `OSC_FREQ`, validates the index against `input_freqs`, registers `osc`, optional divided oscillator clocks, `clk_m` using the caller-provided divider, and `pll_ref` using `OSC_CTRL_PLL_REF_DIV_SHIFT`. Early returns are used when a clock ID is absent from the SoC table.

State and persistence: `osc_ctrl_ctx` is module-global saved state used by resume. Hardware state lives in `OSC_CTRL`; restored fields include oscillator frequency selection and PLL reference divider bits while preserving unrelated register bits. Registered fixed clocks are static roots with no rate changes.

Dependencies and integration: SoC init files call this before PLL registration so PLLs can parent to `pll_ref` and peripheral clocks can parent to `clk_m`. It relies on `tegra_lookup_dt_id()` and standard CCF fixed-rate/fixed-factor constructors.

Risks and test signals: risks are wrong oscillator frequency table indexing, returning success when a required root ID is absent, and restoring stale oscillator bits across suspend if firmware changed them. Test with each supported oscillator strap, verify `osc_freq` and `pll_ref_freq`, inspect `/sys/kernel/debug/clk/clk_summary`, and suspend/resume while checking PLL lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-fixed.c -->
