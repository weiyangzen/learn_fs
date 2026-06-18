<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us3-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us3-cpufreq.c

## Purpose

Implements UltraSPARC-III-family cpufreq by changing Safari config divider bits for divisors 1, 2, and 32.

## APIs, Types, And Functions

`struct us3_freq_percpu_info` holds a four-entry per-CPU table. `read_safari_cfg()` and `update_safari_cfg()` access `ASI_SAFARI_CONFIG`. `get_current_freq()` decodes divider bits. cpufreq callbacks are `us3_freq_get()`, `us3_freq_target()`, `us3_freq_cpu_init()`, and `us3_freq_cpu_exit()`.

## Control Flow

Module init verifies Cheetah/Cheetah+ TLB type and implementation ids, allocates per-CPU tables, and registers. CPU init fills rates from `sparc64_get_clock_tick()`. Targeting maps index to Safari divider bits and sends the update to the target CPU. Exit restores divisor 1.

## State And Persistence

State is limited to allocated per-CPU frequency tables. Hardware state persists in the Safari config divider field.

## Dependencies And Integration Points

Depends on SPARC CPU identification constants, ASI access, SMP single-CPU calls, and cpufreq generic table verification.

## Risks And Test Signals

The driver does no transition notification wrapping and assumes immediate divider changes. Test signals include table rates, Safari config readback, correct rejection on unsupported implementations, and full-speed restore on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us3-cpufreq.c -->
