# sources/distributed-fs/ceph-client/drivers/clk/qcom/gxclkctl-kaanapali.c

## Purpose

This is a minimal GX clock-control/power-domain driver for Kaanapali-family Qualcomm SoCs. It exposes a single GX GDSC and no ordinary clocks, allowing GPU GX power-domain control through the common Qualcomm CC/GDSC infrastructure.

## Important APIs, types, and functions

The file defines `gx_clkctl_gx_gdsc`, `gx_clkctl_gdscs`, `gx_clkctl_regmap_config`, `gx_clkctl_kaanapali_desc`, and `gx_clkctl_kaanapali_probe()`. The GDSC uses `gdsc_gx_do_nothing_enable()` as its `power_on` callback, `PWRSTS_OFF_ON`, and flags `POLL_CFG_GDSCR | RETAIN_FF_ENABLE`. The descriptor sets `.use_rpm = true`.

## Control flow, state, and persistence

Probe is a single call to `qcom_cc_probe()`, which maps the controller, applies runtime PM-aware registration, and publishes the GDSC. The only persistent state is the GX GDSCR hardware state and the genpd registration.

## Dependencies and integration points

The driver depends on the `qcom,kaanapali-gxclkctl.h` binding, Qualcomm `common.h`, and `gdsc.h`. It matches `"qcom,glymur-gxclkctl"`, `"qcom,kaanapali-gxclkctl"`, and `"qcom,sm8750-gxclkctl"`, integrating with GPU power-domain consumers on those platforms.

## Risks and test signals

Because there are no clocks to sanity-check, the register range, compatible match, and GDSC flags are the critical surface. An incorrect `gdscr` offset or power-on callback would appear as GPU GX power-domain failures. Test by binding each compatible, validating genpd attach/detach, confirming GX domain transitions in debugfs, and exercising GPU runtime PM and suspend/resume.
