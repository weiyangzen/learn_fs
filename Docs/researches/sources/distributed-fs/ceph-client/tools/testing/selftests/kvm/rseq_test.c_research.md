# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/rseq_test.c

## Purpose
This generic KVM selftest stresses restartable sequences during repeated task migration while a vCPU enters and exits KVM. It targets bugs where KVM handles migration or resume-notification paths without updating the task's rseq CPU ID consistently.

## Important APIs, Types, And Functions
The file includes `../rseq/rseq.c` directly under its own feature configuration and uses `rseq_register_current_thread()`, `rseq_current_cpu_raw()`, and `rseq_unregister_current_thread()`. It uses pthreads, `sched_getaffinity()`, `sched_setaffinity()`, `sys_getcpu()`, atomic sequence counters, and optional `/dev/cpu_dma_latency`. KVM integration is minimal: `vm_create_with_one_vcpu()`, `vcpu_run()`, and `GUEST_SYNC()` exits from `guest_code()`.

## Control Flow
`main()` records the current affinity mask, requires at least two usable CPUs, registers rseq, creates a dummy one-vCPU VM, and starts `migration_worker()`. The worker repeatedly pins the process to the next allowed CPU, bracketing each affinity change with `seq_cnt` increments and memory barriers. The main thread repeatedly enters KVM, consumes the sync exit, and samples `getcpu()` plus raw rseq CPU inside a stable sequence-counter window. It asserts that both CPU IDs match until the migration worker completes.

## State, Dependencies, And Integration
Shared process state includes `possible_mask`, `min_cpu`, `max_cpu`, `done`, `seq_cnt`, and the migration thread. `/dev/cpu_dma_latency` is held open only if `-l` is requested. There is no persistent repository state. The test depends on Linux rseq support, at least two schedulable CPUs, KVM_RUN progress, and timing sufficient to exercise migration during KVM entry/exit.

## Risks And Test Signals
The workload is intentionally timing-sensitive. False negatives are possible if migrations do not overlap KVM resume paths; false positives are mitigated by the sequence counter and barriers. The final sanity check requires enough KVM_RUN iterations relative to migrations unless `-u` is given. A failure is a direct mismatch between rseq and scheduler CPU IDs or an unexpectedly low KVM_RUN count.
