# sources/distributed-fs/ceph-client/include/linux/kprobes.h

## Purpose

`kprobes.h` defines the generic kernel dynamic instrumentation interface for kprobes, kretprobes, optimized probes, ftrace-backed probes, instruction slots, blacklists, and page-fault handling. The source was read as a complete 594-line file.

## Important APIs, Types, and Functions

Core types include `struct kprobe`, `struct kretprobe`, `struct kretprobe_instance`, `struct kprobe_blacklist_entry`, `struct kprobe_insn_cache`, and `struct optimized_kprobe`. Important APIs include `register_kprobe()`, `unregister_kprobe()`, `register_kprobes()`, `register_kretprobe()`, `disable_kprobe()`, `enable_kprobe()`, `get_kprobe()`, `kprobe_running()`, `kprobe_lookup_name()`, `arch_adjust_kprobe_addr()`, `within_kprobe_blacklist()`, `kprobe_add_ksym_blacklist()`, `kprobe_add_area_blacklist()`, `kprobe_ftrace_handler()`, `kprobe_ftrace_kill()`, `kretprobe_trampoline_handler()`, `kretprobe_find_ret_addr()`, and `kprobe_page_fault()`.

## Control Flow

A registered kprobe replaces or routes execution at an address through architecture breakpoint/ftrace machinery, invokes pre/post handlers, and tracks per-CPU current probe state. Kretprobes install return trampolines or rethooks and call handlers on function return. Optimized probes may replace breakpoints with direct jumps after safety checks. Fault handling only claims kernel-mode, non-preemptible faults while a kprobe is running.

## State and Persistence Behavior

Registered probes persist in global hash/list structures until unregistered. Per-CPU `current_kprobe` and `kprobe_ctlblk` track active execution. Instruction slot caches allocate executable pages. Kretprobe instances come from pools and carry per-instance data.

## Dependencies and Integration Points

It depends on architecture kprobe support, notifier paths, percpu data, ftrace, objpool, rethook, RCU, mutexes, and exception/page-fault handling. KGDB shares blacklist concepts with kprobes.

## Risks and Edge Cases

Instrumentation can recurse, hit blacklisted text, race with module unload, or fault in probe handlers. Disabled configs return `-EOPNOTSUPP` and treat blacklist as closed. Optimized/ftrace paths must be killed safely when ftrace is disabled.

## Test Signals

Kprobes selftests, kretprobe maxactive/nmissed tests, optimized probe tests, ftrace-backed probe tests, blacklist rejection tests, module unload tests, fault-in-handler tests, and disabled-config build coverage are important.
