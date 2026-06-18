<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us2e-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us2e-cpufreq.c

## Purpose

Implements UltraSPARC-IIe cpufreq using Hummingbird ESTAR divider modes and memory refresh/self-refresh sequencing.

## APIs, Types, And Functions

`struct us2e_freq_percpu_info` stores per-CPU tables. `read_hbreg()` and `write_hbreg()` access physical bypass ASI registers. `frob_mem_refresh()` and `self_refresh_ctl()` manage memory refresh state. `us2e_transition()` encodes the hardware state machine for dividers 1, 2, 4, 6, and 8. cpufreq callbacks include `us2e_freq_get()`, `us2e_freq_target()`, init, and exit.

## Control Flow

Module init verifies spitfire TLB type plus manufacturer/implementation ids, allocates per-CPU tables, and registers cpufreq. CPU init builds rates from `sparc64_get_clock_tick()` divided by supported divisors. Targeting executes on the target CPU, reads current ESTAR, converts target index to divider bits, and calls `us2e_transition()` if the divisor changes. Exit forces divisor 1.

## State And Persistence

Software state is the allocated per-CPU frequency table array. Hardware state persists in ESTAR mode and Hummingbird memory control registers. Memory refresh counters are recomputed around divider changes.

## Dependencies And Integration Points

Depends on SPARC ASI physical bypass access, clock tick helpers, CPU implementation ids, and SMP single-CPU calls.

## Risks And Test Signals

There appears to be a table-construction bug in `us2e_freq_cpu_init()`: entries after index 2 repeatedly overwrite `table[2]`, then set `table[3]` as the end marker, making divisor 6/8 entries inaccessible. Test signals should include available frequency table inspection, ESTAR readback, memory refresh register values, self-refresh behavior for 1<->2 transitions, and forced full-speed exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us2e-cpufreq.c -->
