# sources/distributed-fs/ceph-client/arch/um/os-Linux/process.c

## Purpose
Wraps host process, signal, memory-map, futex, and child-reaping operations for UML runtime code.

## Important APIs, Types, and Functions
Includes `os_alarm_process()`, `os_kill_process()`, `os_kill_ptraced_process()`, `os_reap_child()`, raw `os_getpid()`, `os_map_memory()`, `os_protect_memory()`, `os_unmap_memory()`, `os_drop_memory()`, `can_drop_memory()`, `init_new_thread_signals()`, `os_set_pdeathsig()`, `os_futex_wait()`, and `os_futex_wake()`.

## Control Flow, State, and Persistence
No long-lived state except host signal handlers installed by `init_new_thread_signals()`. Kill paths block UML signals while killing/reaping children. Mapping helpers create fixed shared host mappings for UML memory.

## Dependencies and Integration Points
Used by TLB sync, reboot cleanup, SKAS process management, SMP startup, memory discard, and signal initialization. It bridges kernel abstractions to host syscalls.

## Risks and Test Signals
Risks are killing wrong process groups/pids, ptrace kill races, `MADV_REMOVE` support detection, signal-handler installation mismatch with seccomp, and futex wait wakeups. Test child crash/reap, memory mapping/protection, discard support, and signal initialization in ptrace/seccomp modes.
