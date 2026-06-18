# sources/distributed-fs/ceph-client/drivers/cpufreq/loongson3_cpufreq.c

## Purpose

`loongson3_cpufreq.c` is a LoongArch Loongson-3 cpufreq driver that delegates DVFS control to platform firmware through an IOCSR SMC mailbox. It discovers firmware-provided frequency levels per CPU/core, marks boost levels, and exposes them as cpufreq tables shared across topology siblings.

## Important APIs, types, and functions

- `union smc_message` defines the packed mailbox protocol fields: ID, info, value, command, extra flag, and completion bit.
- Command macros cover feature negotiation, sensor/fan commands, and DVFS commands such as `CMD_GET_FREQ_LEVEL_NUM`, `CMD_GET_FREQ_LEVEL_INFO`, and `CMD_SET_FREQ_INFO`.
- `struct loongson3_freq_data` stores the default frequency level and a flexible cpufreq table.
- `do_service_request()` serializes per-package mailbox access, writes `LOONGARCH_IOCSR_SMCMBX`, raises the soft interrupt bit, polls for completion, checks `CMD_OK`, and returns `msg.val`.
- `configure_freq_table()` queries level count, first boost level, and per-level frequencies, then allocates and caches per-CPU frequency data.
- `loongson3_cpufreq_target()` sets a frequency level for the target CPU core via firmware.

## Control flow

The platform driver matches `loongson3_cpufreq`. Probe initializes one mutex per package, validates firmware version, enables DVFS and boost features, stores the platform device in driver data, and registers cpufreq. CPU init lazily builds the table for the policy CPU, sets transition latency to 10 us, sets `suspend_freq` to the default non-boost level, and copies sibling CPUs into the same policy mask while sharing the same `freq_data` pointer.

Targets are level indexes, not raw frequencies. The driver sends `CMD_SET_FREQ_INFO` with `FREQ_INFO_TYPE_LEVEL` and the requested table index. `.get` asks firmware for current frequency and converts MHz-like values to kHz with `KILO`. Exit restores the default level.

## State and persistence behavior

State is split between firmware mailbox state, per-package mutexes, and per-CPU cached `loongson3_freq_data` allocations managed by device-managed memory. Sibling CPUs share the same table pointer. The driver does not free per-CPU pointers on policy exit because allocations are tied to platform device lifetime. Hardware DVFS enable/boost settings persist in firmware after probe until platform reset or firmware changes.

## Dependencies

Dependencies include LoongArch IOCSR accessors, `LOONGARCH_IOCSR_SMCMBX`, `LOONGARCH_IOCSR_MISC_FUNC`, CPU package/core topology in `cpu_data`, `MAX_PACKAGES`, cpufreq boost helpers, platform device binding, and firmware support for the documented SMC command set.

## Risks and edge cases

- `do_service_request()` uses `raw_smp_processor_id()` for package locking, while callers may request data for another CPU ID; mailbox affinity assumptions must match firmware routing.
- Completion polling waits up to 10000 short sleeps and collapses all timeout/non-OK statuses to `-EPERM`, reducing diagnosability.
- `def_freq_level = boost_level - 1` assumes firmware reports boost level greater than zero.
- Tables are capped at `FREQ_MAX_LEVEL`; firmware levels beyond 16 are ignored.
- `.get` returns `ret * KILO` even if `ret` is negative, so firmware errors can appear as large unsigned values.

## Test signals

Probe should successfully read interface version, enable DVFS/boost, and build cpufreq tables with boost flags at and above the firmware boost level. Runtime tests should switch every level, confirm current frequency from firmware, verify sibling policy masks, test suspend frequency selection, and exercise multi-package concurrent transitions for mailbox serialization.
