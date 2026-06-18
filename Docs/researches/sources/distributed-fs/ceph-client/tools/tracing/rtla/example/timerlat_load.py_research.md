# sources/distributed-fs/ceph-client/tools/tracing/rtla/example/timerlat_load.py

## Purpose
`timerlat_load.py` is a sample userspace workload for timerlat's userspace timer interface. It pins itself to a CPU, optionally sets FIFO priority, waits on the per-CPU `timerlat_fd`, and performs a large read from `/dev/full` on each activation so RTLA can measure response time and auto-analysis data.

## Important APIs, Types, and Functions
The script uses `argparse` for CPU and optional priority, `os.sched_setaffinity()`, `os.sched_setscheduler()`, and opens `/sys/kernel/tracing/osnoise/per_cpu/cpuN/timerlat_fd`. It also opens `/dev/full` as an artificial data source.

## Control Flow
After parsing arguments, the script sets affinity and optional scheduler priority, opens the timerlat fd, opens `/dev/full`, then loops forever. Each iteration blocks on `timerlat_fd.read(1)` and then reads 20 MiB from `/dev/full`. It exits cleanly on Ctrl-C or I/O errors and closes both descriptors.

## State and Persistence
Runtime state is only open descriptors and process scheduling/affinity settings. It writes no files.

## Dependencies and Integration Points
It requires Python 3, sufficient privileges for scheduling and tracing file access, mounted tracefs, and a running `rtla timerlat -U` session that exposes the userspace fd.

## Risks and Edge Cases
The script assumes tracefs at `/sys/kernel/tracing`; systems using only debugfs tracing paths may need adaptation. Reading 20 MiB from `/dev/full` is a synthetic workload and may not represent application behavior. Scheduler and affinity setup failures terminate the script.

## Test Signals
Run with RTLA timerlat userspace mode active, pinned to a monitored CPU, and verify timerlat records user latency. Test permission errors, invalid CPU IDs, and optional FIFO priority failures.
