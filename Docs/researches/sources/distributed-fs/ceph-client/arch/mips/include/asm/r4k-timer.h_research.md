# sources/distributed-fs/ceph-client/arch/mips/include/asm/r4k-timer.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/r4k-timer.h

### Purpose
`r4k-timer.h` declares or stubs synchronization of MIPS R4K CP0 count timers across CPUs.

### Important APIs, Types, And Functions
The single API is `synchronise_count_slave(int cpu)`, declared externally under `CONFIG_SYNC_R4K` and otherwise defined as an empty inline.

### Control Flow
SMP timer bring-up calls `synchronise_count_slave` for secondary CPUs. On configurations that do not require synchronization, the call compiles away.

### State, Persistence, Dependencies, And Integration
State is CP0 Count/Compare timing state and per-CPU timer skew; there is no persistence. Integration is with SMP CPU bring-up, clockevents, and scheduler tick correctness.

### Risks
Wrongly disabling synchronization can produce skewed timer interrupts. Calling synchronization too late or without matching master-side code can make secondary CPU timekeeping unstable.

### Test Signals
Boot SMP R4K-style systems with `CONFIG_SYNC_R4K`, compare per-CPU clockevent skew, run timer migration and scheduler tick tests, and build the stub branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/r4k-timer.h -->
