# sources/distributed-fs/ceph-client/drivers/clk/qcom/krait-cc.c

## Purpose

This driver builds the Krait CPU and L2 clock tree from HFPLL dividers, secondary muxes, and primary muxes. It supports up to four CPUs plus L2 and coordinates safe reparenting while HFPLLs are reprogrammed.

## Important APIs, types, and functions

Important functions are `krait_notifier_cb()`, `krait_notifier_register()`, `krait_add_div()`, `krait_add_sec_mux()`, `krait_add_pri_mux()`, `krait_add_clks()`, `krait_of_get()`, and `krait_cc_probe()`. The driver uses `krait_div2_clk`, `krait_mux_clk`, `krait_div2_clk_ops`, `krait_mux_clk_ops`, notifier blocks, fixed-rate/fixed-factor helper clocks, and an OF provider returning `struct clk *` entries by index.

## Control flow, state, and persistence

Probe registers a dummy-rate `qsb` safe source and, for v2/non-unique auxiliary mode, an `acpu_aux` fixed factor from `gpll0_vote`. It allocates a clock array, creates per-possible-CPU clocks and an L2 clock, prepares/enables online CPU and L2 clocks to prevent late disable, then forces each clock through auxiliary and dummy low-rate transitions before restoring the detected rate. Notifiers switch muxes to a safe parent on `PRE_RATE_CHANGE` and restore after `POST_RATE_CHANGE` if the framework did not intentionally reparent.

## Dependencies and integration points

The file depends on `clk-krait.h`, HFPLL providers named `hfpll*`, auxiliary clocks from `kpss-xcc` or `gpll0_vote`, CPU topology, machine compatibles for APQ/IPQ8064 errata, and cpufreq/hotplug users.

## Risks and test signals

CPU clock drivers are high risk: wrong mux maps can hang CPUs, notifier failures can reprogram HFPLLs while sourced from them, and prepare-count assumptions affect hotplug/cpufreq. Test on Krait v1/v2 hardware with all CPUs online/offline, cpufreq rate changes, L2 rate changes, debugfs parent checks, bootloader-misconfigured clock recovery, and suspend/resume.
