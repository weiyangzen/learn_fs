# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_stats.c

## Purpose

`qcom_stats.c` exposes Qualcomm RPM/RPMh sleep and DDR low-power statistics through debugfs. It reads SoC sleep stats from MSG RAM/MMIO, subsystem sleep stats from SMEM items, and optional DDR stats after synchronizing newer platforms through AOSS QMP.

## Important APIs, Types, and Functions

`struct stats_config` captures per-compatible offsets, record counts, appended-vote availability, dynamic RPM offset behavior, and whether subsystem stats live in SMEM. `struct sleep_stats`, `struct appended_stats`, and `struct ddr_stats_entry` mirror firmware data. Show paths are `qcom_soc_sleep_stats_show()`, `qcom_subsystem_sleep_stats_show()`, and `qcom_ddr_stats_show()`. Creation helpers build debugfs files for subsystem, SoC sleep, and DDR stats. `qcom_stats_probe()` maps the resource, gets optional QMP, creates `qcom_stats`, and marks PM not required.

## Control Flow

Probe selects config from OF match data, maps resource 0, allocates one `stats_data` per record, optionally resolves QMP, creates the debugfs directory, creates subsystem files if enabled, creates one file per low-power mode by reading each record's stat-type name from MMIO, and creates `ddr_stats` only when the DDR magic key matches. Reads copy the relevant shared record each time; DDR reads may first send `{class: ddr, action: freqsync}` over QMP.

## State and Persistence Behavior

Kernel state is limited to debugfs dentries, per-record MMIO pointers, and the global optional `qcom_stats_qmp`. Statistics are firmware-maintained counters in MSG RAM or SMEM and persist across driver reads. Accumulated duration is adjusted at read time if a subsystem is currently sleeping by adding the current arch timer delta.

## Dependencies and Integration Points

Dependencies include platform MMIO, debugfs, SMEM, AOSS QMP, arm arch timer, device tree compatibles, and bitfield helpers. It integrates with `qcom_aoss.c` for DDR stats sync and `smem.c` for subsystem statistics.

## Risks and Edge Cases

`qcom_stats_qmp` is global, so multiple instances would overwrite one another. `qcom_stats_remove()` removes debugfs but does not call `qmp_put()`, despite `qmp_get()` taking a device reference. Dynamic offsets are read from firmware and used without checking that computed records fit in the mapped resource. Debugfs file names are derived from raw four-byte stat types; unexpected bytes can create odd names. `devm_platform_get_and_ioremap_resource()` errors are collapsed to `-ENOMEM`, losing probe diagnostics.

## Test Signals

Validate each compatible config, dynamic RPM offset parsing, fixed RPM offsets, subsystem SMEM item absence, DDR magic mismatch, QMP absent/present/deferred/error paths, active sleep duration adjustment, malformed DDR entry count greater than 20, debugfs teardown, and repeated DDR reads that require QMP sync.
