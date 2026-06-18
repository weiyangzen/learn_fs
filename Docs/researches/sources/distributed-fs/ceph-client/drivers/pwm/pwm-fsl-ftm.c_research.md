<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-fsl-ftm.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-fsl-ftm.c

Purpose: implements the Freescale/NXP FlexTimer Module PWM provider for VF610, i.MX8QM, and S32G2-style FTM blocks. It exposes up to eight PWM channels, but the controller has one shared period source, so the driver arbitrates period-clock and prescaler changes across all enabled outputs.

Important APIs/types/functions: `struct fsl_pwm_chip` holds the regmap, clocks, SoC data, and current shared `struct fsl_pwm_periodcfg`. `fsl_pwm_request()` and `fsl_pwm_free()` manage the interface clock and optional channel enable bits. `fsl_pwm_calculate_period()`, `fsl_pwm_apply_config()`, and `fsl_pwm_apply()` implement period selection, duty programming, polarity, output masking, and counter-clock enable/disable. Probe uses `devm_regmap_init_mmio_clk()`, named clocks `ftm_sys`, `ftm_fix`, `ftm_ext`, `ftm_cnt_clk_en`, optional `ipg`, and SoC match data.

Control flow: probe maps registers, builds a regmap with volatile/readable/writeable filters, gets clocks, registers the PWM chip, and initializes counter start, output init, and output masks. Applying an enabled state computes the best source clock and prescaler, rejects shared-period changes while other PWMs are enabled, clears FTM write protection, updates `FTM_SC`, `FTM_MOD`, channel status/value registers, and polarity, then unmasks the output after enabling the selected period clock and counter-enable clock. Disabling masks the channel and drops enabled clocks.

State and persistence: hardware registers and clock enables hold runtime state. The driver caches only the active shared period config; it is valid when at least one PWM is running. Suspend moves regmap into cache-only dirty mode and disables requested/enabled clocks; resume reenables clocks for requested/enabled channels and syncs the cached register image. No state is persisted outside hardware/kernel memory.

Dependencies and integration: depends on Linux PWM core, platform/OF binding, clk framework, regmap MMIO cache, PM sleep hooks, and `linux/fsl/ftm.h` register definitions. It integrates with consumers through standard `pwm_ops` and with SoC variants through `struct fsl_ftm_soc`.

Risks and test signals: the shared period is the main behavioral constraint; tests should cover two channels with conflicting periods, period source changes, enable/disable clock reference balance, and SoC variants with/without enable bits and filter registers. The duplicated `if (!fsl_pwm_is_any_pwm_enabled(...))` in `fsl_pwm_apply_config()` is suspicious style and should be reviewed for intended control flow. Test suspend/resume with enabled outputs and regcache sync failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-fsl-ftm.c -->
