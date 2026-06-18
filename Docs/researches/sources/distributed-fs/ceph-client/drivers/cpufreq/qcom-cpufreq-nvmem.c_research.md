<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-nvmem.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-nvmem.c

## Purpose

Configures Qualcomm CPU OPP selection from NVMEM speed-bin fuses, SMEM SoC ids, PVS names, and optional power domains, then instantiates the generic `cpufreq-dt` platform device.

## APIs, Types, And Functions

`struct qcom_cpufreq_match_data` describes SoC-specific version decoding and power-domain names. `struct qcom_cpufreq_drv` stores the selected `supported_hw` bitmask and per-CPU OPP/power-domain tokens. Version helpers cover simple speedbin, Kryo, Krait formats A/B, IPQ8064, IPQ6018, and IPQ8074. Probe/remove manage OPP config and `cpufreq-dt` registration.

## Control Flow

Module init matches the machine compatible, registers the platform driver, and creates a data-bearing platform device. Probe validates the CPU0 OPP descriptor compatible, allocates per-CPU state, reads NVMEM if required, computes `drv->versions` and optional `pvs_name`, then for each present CPU applies OPP config and attaches required performance domains. Finally it registers `cpufreq-dt`; remove unregisters it and clears OPP/domain state.

## State And Persistence

Global platform-device pointers track the wrapper and delegated `cpufreq-dt` device. Per-CPU state retains OPP config tokens and attached PM domain lists. Persistent hardware input is fuse/NVMEM and SMEM SoC identity; this driver does not change clocks directly.

## Dependencies And Integration Points

Depends on NVMEM cells, Qualcomm SMEM ids, DT OPP v2 compatible strings, OPP `supported_hw`/property-name selection, generic PM domains with required OPP links, and the `cpufreq-dt` driver.

## Risks And Test Signals

Wrong fuse decoding hides valid OPPs or exposes unsafe ones. Several fallbacks intentionally limit frequency for unknown SoC ids. Test signals include selected version bitmask, PVS property name, successful `dev_pm_opp_set_config()` on every CPU, attached performance domains, `cpufreq-dt` platform creation, and correct OPP availability under `/sys/devices/system/cpu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-nvmem.c -->
