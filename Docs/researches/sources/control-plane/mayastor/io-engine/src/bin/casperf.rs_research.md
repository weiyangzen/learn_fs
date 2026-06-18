## sources/control-plane/mayastor/io-engine/src/bin/casperf.rs

### Purpose
`bin/casperf.rs` is a simple Mayastor/SPDK performance tool that creates bdevs from URIs and drives random read or write I/O at a configured queue depth, printing per-second throughput.

### Important APIs, Types, And Functions
`IoType` selects random read or write. `Job` owns the bdev, descriptor, I/O channel, queue depth, block sizing, I/O queue, counters, RNG, drain flag, and run period. `Io` owns a DMA buffer, operation type, offset, and raw job pointer. `sig_override()`, `perf_tick()`, and `main()` control lifecycle.

### Control Flow
`main()` disables NVMf target services, enables all-thread nexus channels, initializes Mayastor, registers nexus module, and on the master reactor creates one job per URI. Each job creates the bdev, opens it, computes I/O geometry, allocates `qd + 1` DMA buffers, starts on an `Mthread`, and submits initial I/O. Completion callbacks update counters, free SPDK bdev I/O, submit the next random operation unless draining, and stop the environment when all drained jobs finish. A poller prints average IO/s and MB/s once per second. Signal handlers unregister the perf poller and set all jobs to drain.

### State, Persistence, And Dependencies
State is thread-local `JOBLIST` and `PERF_TICK`, plus SPDK bdev/channel resources. Data written by random write persists only according to backing device semantics; the tool does not verify contents. Dependencies include Clap, random number generation, Mayastor environment/reactors/threads, `bdev_create`, SPDK bdev read/write APIs, `DmaBuf`, and signal-hook.

### Integration Points
The tool is a developer benchmark harness for any URI-supported bdev, including nexus and null/uring/nvme paths. It disables target services so it behaves as an initiator/workload generator.

### Risks
The queue is sized `0..=qd`, producing `qd + 1` I/O slots, so actual outstanding depth may exceed the user-specified queue depth. `io_size` is stored inconsistently: comments imply blocks, but later it is set to bytes after `io_blocks` calculation; SPDK offsets are byte offsets, so naming can confuse maintenance. `io_blocks = num_blocks / io_size` mixes blocks and bytes if `io_size` is bytes, which may produce bad ranges. Raw job pointers require jobs to outlive all queued I/O.

### Test Signals
Exercise CLI parsing, zero/large qd, io_size smaller/larger than block size, random offset bounds, read/write submission failure, drain on SIGINT/SIGTERM, poller unregister, all jobs complete stopping environment, and throughput calculation with controlled counters.
