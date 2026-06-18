# sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/process.c

## Purpose
Implements host-side SKAS process control: creating `uml-userspace` helpers, waiting for ptrace/seccomp stops, shuttling registers, running guest userspace, and switching UML kernel threads.

## Important APIs, Types, and Functions
`start_userspace()` clones a trampoline that execs the embedded stub executable. `init_stub_exe_fd()` materializes the embedded stub into a sealed memfd or executable temp file. `wait_stub_done()` and `wait_stub_done_seccomp()` synchronize stub completion. `userspace()` is the main loop that syncs TLBs, flushes stub syscalls, sets/restores registers, resumes ptrace or seccomp child execution, decodes host stop signals, and dispatches to page fault, syscall, or signal handlers. Thread switching uses `new_thread()`, `switch_threads()`, `start_idle_thread()`, callbacks, halt, and reboot longjmps.

## Control Flow, State, and Persistence
Persistent state includes `stub_exe_fd`, `using_seccomp`, initial jump buffer, thread-local callback slots, `noreboot`, and unscheduled userspace iteration counters. Per-mm state is protected by the turnstile while manipulating a shared child process.

## Dependencies and Integration Points
This is the hub between kernel UML execution, host ptrace/seccomp, stub executable, TLB sync, signal/trap/syscall handlers, time travel, SMP constraints, and reboot/halt paths.

## Risks and Test Signals
Risks are high: register corruption, lost SIGSYS/SIGALRM ordering, stub child death, insecure seccomp mode, turnstile deadlocks, unreaped temp stub files, and longjmp misuse. Test boot in ptrace/seccomp, `seccomp=on/auto/off`, SMP rejection in ptrace mode, syscall/page-fault stress, signal delivery, gdb/strace, panic/reboot/noreboot, and time-travel workloads.
