# sources/distributed-fs/ceph-client/drivers/clk/qcom/hfpll.c

## Purpose

This platform driver registers Qualcomm HFPLL clocks for QCS404 and MSM8976 CPU/CCI PLL variants. It provides a simple OF clock provider around the shared `clk-hfpll` implementation while preserving firmware-owned enable state.

## Important APIs, types, and functions

The main data is a set of `hfpll_data` instances: `qcs404`, `msm8976_a53`, `msm8976_a72`, and `msm8976_cci`. These describe register offsets, lock bit, config/user values, optional default `l_val`, VCO selection, and min/max rates. `qcom_hfpll_probe()` allocates `clk_hfpll`, maps MMIO, initializes a regmap, reads `clock-output-names`, sets parent index 0, installs `clk_ops_hfpll`, initializes the lock, registers the regmap clock, and adds an OF provider.

## Control flow, state, and persistence

Probe is linear and device-managed. The clock is registered with `CLK_IGNORE_UNUSED`, intentionally avoiding a Linux-driven disable because firmware remains responsible for enabling the PLL. State lives in HFPLL registers and in the CCF object; the driver has no remove path because devm cleans up registration resources.

## Dependencies and integration points

It depends on OF match data, `clk-regmap.h`, `clk-hfpll.h`, `clock-output-names`, and a single parent clock supplied by DT. It feeds CPU/CCI clock trees, especially Krait-style or QCS404 CPU clock consumers that use HFPLL rate changes.

## Risks and test signals

The largest risks are incorrect `hfpll_data` values, missing `clock-output-names`, parent-rate assumptions, and accidentally allowing unused-clock cleanup to disable a firmware-critical CPU PLL. Test with DT binding validation, successful CPU/CCI clock registration, cpufreq transitions across min/max rates, lock-bit polling behavior from `clk-hfpll`, and boot logs showing no missing provider or disable warnings.
