## sources/distributed-fs/ceph-client/arch/mips/kernel/sync-r4k.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/sync-r4k.c` synchronizes CP0 Count registers between CPUs during secondary CPU bring-up. It detects counter time warps between CPUs and compensates a newly booted CPU when possible.

### Important APIs, Types, And Functions
Important state includes atomic `start_count`, `stop_count`, `test_runs`, raw `sync_lock`, `last_counter`, `max_warp`, `nr_warps`, and `random_warps`. Runtime functions are `check_counter_warp()`, `check_counter_sync_source()`, and `synchronise_count_slave()`.

### Control Flow
The newly booted CPU calls `synchronise_count_slave()`, which asks the first online CPU to run `check_counter_sync_source()`. Both CPUs enter synchronized loops, alternate reading Count under `sync_lock`, and detect backward movement relative to the previous CPU's read. If no warp is observed, the source reports pass. If a deterministic warp is found and retries remain, the slave adjusts its Count register by the measured warp and repeats. Finally the slave schedules a near-future compare interrupt.

### State, Persistence, And Dependencies
State is temporary synchronization counters and CP0 Count/Compare registers. The only persistent effect is a corrected Count register for the secondary CPU during boot. Dependencies include `read_c0_count()`, `write_c0_count()`, `write_c0_compare()`, `mips_hpt_frequency`, SMP function calls, raw arch spinlocks, and NMI watchdog touch calls.

### Integration Points
Generic `start_secondary()` in `smp.c` calls `synchronise_count_slave()` before marking the CPU online. Time initialization provides `mips_hpt_frequency`; clockevent code consumes the synchronized Count/Compare state.

### Risks
The code busy-waits with interrupts disabled-sensitive timing and assumes exactly two participants per sync run. Random warps cannot be compensated and only produce warnings. Incorrect frequency or broken Count registers can cause long loops, but the measurement loop has safety exits and watchdog touches.

### Test Signals
Boot SMP R4k-style systems, inspect counter synchronization logs, test CPUs with known Count skew, verify compare interrupts after secondary boot, and run hotplug cycles if Count sync occurs on re-online paths.
