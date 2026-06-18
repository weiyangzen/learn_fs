<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/mtk-cci-devfreq.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/mtk-cci-devfreq.c

Purpose: MediaTek CCI devfreq driver that follows CPUFreq through the passive governor and changes CCI PLL frequency with coordinated processor/SRAM regulator voltage tracking.

Important APIs and control flow: probe obtains CCI and intermediate clocks, optional `proc` and `sram` regulators, enables supplies and CCI clock, loads OPPs, determines intermediate voltage, raises to the highest OPP voltage, registers a passive devfreq device with `CPUFREQ_PARENT_DEV`, and registers an OPP voltage-change notifier. `mtk_ccifreq_target()` resolves an OPP, computes target voltage, scales voltage up before frequency increases, reparents CCI to the intermediate clock, changes the original PLL rate, reparents back, and scales voltage down when safe. `mtk_ccifreq_set_voltage()` enforces proc/SRAM voltage delta constraints iteratively according to SoC data. The OPP notifier adjusts voltage immediately when the current OPP voltage changes.

State and persistence behavior: per-device state includes devfreq pointer, regulators, CCI/intermediate clocks, intermediate voltage, previous frequency, regulator mutex, OPP notifier, SoC voltage constraints, and retry limit. Resources are manually disabled/removed in remove and probe-error paths.

Dependencies and integration points: depends on passive governor, CPUFreq parent support, OPP/regulator/clock frameworks, MediaTek DT compatibles `mediatek,mt8183-cci` and `mediatek,mt8186-cci`, and SoC-specific voltage tracking constants.

Risks and test signals: no profile `get_cur_freq` means core state relies on target history. Error paths before `devm_devfreq_add_device()` must disable regulators/clocks exactly once. Voltage rollback cannot recover all partial hardware states if reparenting back fails. Passive CPUFreq interpolation depends on CPU OPP/topology. Test signals include regulator delta tracking in both scale directions, reparenting to/from intermediate clock, current-voltage OPP notifier behavior, CPUFreq-driven passive updates, optional SRAM regulator absence on MT8183, and remove cleanup with supplies disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/mtk-cci-devfreq.c -->
