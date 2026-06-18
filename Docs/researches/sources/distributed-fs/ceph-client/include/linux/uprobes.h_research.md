<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uprobes.h -->
# sources/distributed-fs/ceph-client/include/linux/uprobes.h

Purpose: declares the internal userspace probes interface for planting breakpoints in user mappings, single-stepping original instructions, and handling return probes.

Important APIs and types: `struct uprobe_consumer` defines handler, return-handler, and filter callbacks plus registration ID. Enabled builds define task states (`UTASK_*`), hybrid return-probe lifetime states (`HPROBE_*`), `struct hprobe`, `struct uprobe_task`, `struct return_instance`, `struct return_consumer`, `struct uprobes_state`, `uprobe_write_verify_t`, and many generic/arch hooks. Registration/control APIs include `uprobe_register()`, `uprobe_apply()`, `uprobe_unregister_nosync()`, `uprobe_unregister_sync()`, mmap/munmap/dup hooks, task copy/free hooks, pre/post single-step notifiers, resume notification, state clear/init, trampoline handling, and opcode write helpers. Disabled builds provide stubs returning `-ENOSYS` or no-ops.

Control flow: a consumer registers an inode/offset probe, mmap hooks install breakpoints into matching VMAs, a trap enters uprobe handling, the original instruction is executed out-of-line, and post-step handling restores user execution. Uretprobes hijack return addresses, track return instances on a task stack, and call return handlers through trampoline handling. Hybrid `hprobe` state allows return instances to transition from SRCU-protected to refcounted lifetime.

State and persistence: per-task uprobe state stores single-step status, return-instance stack/pool/timer/seqcount, active uprobe, XOL address, and signal-denial state. Per-mm state stores XOL area and optional trampolines. Probe definitions are in-memory registrations tied to inode offsets and consumers; breakpoint changes affect mapped process text while active.

Dependencies and integration points: depends on rbtrees, wait queues, timers, seqcounts, mutexes, `asm/uprobes.h`, VMAs, mm lifecycle hooks, task fork/exit, exception notifiers, instruction decoding, and tracing/perf consumers.

Risks and test signals: high-risk areas include instruction patching races, VMA lifetime during mmap/munmap/dup, XOL slot management, signal delivery during denied windows, uretprobe depth and lifetime transitions, stale consumer removal, and architecture decode mismatches. Test perf uprobes/uretprobes, concurrent mmap/unmap, fork/exec/exit, nested return probes to `MAX_URETPROBE_DEPTH`, signal-heavy workloads, disabled config builds, and architecture single-step fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uprobes.h -->
