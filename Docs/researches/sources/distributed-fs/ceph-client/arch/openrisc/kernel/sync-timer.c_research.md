<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/sync-timer.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/sync-timer.c

## Purpose
Synchronizes OpenRISC per-CPU tick timer counters during secondary CPU bring-up.

## Important APIs, Types, And Functions
Uses `initcount`, `count_count_start`, `count_count_stop`, `COUNTON`, and `NR_LOOPS`. Exports `synchronise_count_master()` and `synchronise_count_slave()`.

## Control Flow
Master and slave perform three atomic handshakes. The middle pass samples `initcount`; the final pass writes TTCR on both CPUs. Both schedule a near-future timer event before returning.

## State And Persistence
Temporarily uses atomic counters and persists synchronized TTCR values in hardware timers.

## Dependencies And Integration Points
Called from `__cpu_up()` and `secondary_start_kernel()`. Depends on timer APIs, barriers, atomics, and IRQ save/restore.

## Risks
Handshake assumes one secondary at a time. Broken barriers or missed atomic transitions can hang CPU bring-up. CPU0 can see a small time warp by design.

## Test Signals
SMP boot repeatedly, timer interrupt delivery soon after CPU online, and no hangs in counter synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/sync-timer.c -->
