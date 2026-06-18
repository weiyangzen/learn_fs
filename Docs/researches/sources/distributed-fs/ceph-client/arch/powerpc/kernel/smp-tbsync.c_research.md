# sources/distributed-fs/ceph-client/arch/powerpc/kernel/smp-tbsync.c

## Purpose
Provides a generic software timebase synchronization algorithm for SMP PowerPC systems whose platform code supplies `take_timebase` and `give_timebase` operations. It aligns a secondary CPU timebase against the boot CPU by repeated timed contests.

## Important APIs, Types, and Functions
- `tbsync` is a shared cacheline-spaced control block with `tb`, `mark`, `cmd`, `handshake`, `ack`, and `race_result`.
- `smp_generic_take_timebase()` runs on the secondary CPU with interrupts disabled, waiting for commands, optionally setting the timebase, and entering contests.
- `smp_generic_give_timebase()` allocates state, starts the secondary, binary-searches an offset, validates it, sends exit, then frees state.
- `start_contest()` coordinates one batch of contests and scores which CPU crossed the mark first.

## Control Flow and State
The primary sets `running`, waits for secondary `ack`, then repeats `kSetAndTest` contests with varying offsets. Each contest posts target timebase and mark, opens `handshake`, waits until the local timebase reaches the start point, clears handshake, and records a race result. The secondary mirrors the handshake, sets its timebase for `kSetAndTest`, and races to write `race_result`. The chosen offset minimizes absolute score, with a guard loop to handle inaccurate `mttb`.

## State and Persistence Behavior
State is transient and global. Interrupts are disabled on both sides during contests. The only persistent effect is the secondary CPU's hardware timebase being set closer to the primary.

## Dependencies and Integration Points
Uses `get_tb()`, `set_tb()`, SMP bring-up hooks, barriers, and early CPU startup sequencing. It is called from platform `smp_ops` during secondary CPU bring-up.

## Risks
Busy waits can hang boot if the secondary never acknowledges. The volatile protocol depends on precise memory barriers and interrupt-disabled execution. Timebase writes are platform-sensitive, and poor firmware/hardware behavior can leave skew.

## Test Signals
Boot SMP systems requiring generic sync, stress CPU hotplug where platform reuses the hooks, check monotonic timebase deltas across CPUs, and instrument debug scores for convergence rather than oscillation.
