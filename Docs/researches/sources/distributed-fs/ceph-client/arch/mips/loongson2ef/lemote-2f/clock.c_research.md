<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/clock.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/clock.c

Purpose: Exposes Loongson2F CPU clock modulation states and implements frequency-rate programming.

Important APIs/types/functions: Exports `loongson2_clockmod_table` and `loongson2_cpu_set_rate(rate_khz)`.

Control flow: The setter searches valid cpufreq table entries for the requested frequency, then writes `(driver_data - 1)` into low 3 bits of `LOONGSON_CHIPCFG`.

State and persistence: CPU duty-cycle state is stored in `LOONGSON_CHIPCFG`.

Dependencies and integration: Used by Loongson2 cpufreq platform driver registered by common platform code.

Risks: Table entries with zero frequency must be filled by the cpufreq driver before use. Unsupported rates return `-ENOTSUPP`.

Test signals: Requested cpufreq levels should change low chipcfg bits and reject rates not present in the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/clock.c -->
