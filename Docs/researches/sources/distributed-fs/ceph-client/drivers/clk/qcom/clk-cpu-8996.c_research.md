# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-cpu-8996.c

## Purpose
Implements the MSM8996 APCC CPU clock driver for power and performance Kryo clusters. Each cluster has a primary PLL, an alternate PLL, a secondary mux for PLL/2 operation, a primary mux for CPU selection, and ACD-related fixed factors used during normal high-rate operation and voltage-droop handling.

## Important APIs, Types, And Functions
Important static descriptors include primary and alternate PLL register tables, `hfpll_config`, `altpll_config`, primary and alternate `clk_alpha_pll` objects, postdiv and ACD fixed-factor clocks, `clk_regmap_mux` SMUXes, and `struct clk_cpu_8996_pmux` PMUXes. Main functions are `clk_cpu_8996_pmux_get_parent()`, `clk_cpu_8996_pmux_set_parent()`, `clk_cpu_8996_pmux_determine_rate()`, `qcom_cpu_clk_msm8996_register_clks()`, `qcom_cpu_clk_msm8996_acd_init()`, `cpu_clk_notifier_cb()`, and platform probe.

## Control Flow
Probe maps APCC registers, creates a two-clock onecell provider, and delegates clock registration. Registration parks both clusters on GPLL0, programs auto-clock selection, configures primary and alternate PLLs, enables auto-clock selection, initializes ACD registers through Kryo L2 indirect access, programs pulse-swallow/soft-start controls, switches clusters to the ACD path, registers fixed and regmap clocks, enables alternate PLLs, and installs PMUX notifiers. Rate determination chooses SMUX/PLL2 for 300-600 MHz and ACD/primary PLL above 600 MHz. Notifiers reinitialize ACD and manually switch to SMUX before downward crossings to prevent transient overclocking.

## State And Persistence
Hardware state persists in per-cluster PLL registers, mux registers, auto-clock-select fields, ACD L2 indirect registers, soft-start/pulse-swallow registers, and alternate PLL state. Software descriptors are global. A spinlock serializes ACD indirect register programming, and the current CPU MPIDR decides which cluster receives one ACD sideband write.

## Dependencies And Integration Points
Depends on alpha PLL ops, regmap mux helpers, platform/OF APIs, CCF notifiers, fixed-factor clocks, `soc/qcom/kryo-l2-accessors.h`, and ARM CPU ID access. The exported OF provider returns the power and performance PMUX clocks to cpufreq or OPP consumers.

## Risks And Edge Cases
CPU clocks are critical and cannot be gated. PMUX threshold logic must avoid rates below 300 MHz and avoid overclocking while the primary PLL is being reprogrammed. Alternate PLL enable failures are not checked in detail after `clk_prepare_enable()`. ACD init is architecture-specific and relies on indirect L2 accessors plus current cluster affinity. Global descriptors make multiple instances unsupported.

## Test Signals
Boot on MSM8996, cpufreq transitions below and above 600 MHz, abort notifier rollback, alternate PLL availability during primary PLL changes, ACD register programming on both clusters, onecell provider indices, and no CPU stalls during repeated rate changes are important signals.
