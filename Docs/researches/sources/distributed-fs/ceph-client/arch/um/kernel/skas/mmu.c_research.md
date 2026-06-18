# sources/distributed-fs/ceph-client/arch/um/kernel/skas/mmu.c

## Purpose
Creates, tracks, and destroys UML SKAS memory contexts. Each Linux `mm_struct` receives a host userspace helper process plus shared stub-data pages used for register and memory-management coordination.

## Important APIs, Types, and Functions
`__get_turnstile()`, `enter_turnstile()`, and `exit_turnstile()` serialize operations on a memory context. `init_new_context()` allocates stub data pages, links the mm into `mm_list`, starts the host userspace process, and clears unwanted mappings. `destroy_context()` kills the host child, closes seccomp sockets, and frees pages. `mm_sigchld_irq()` reaps unexpected child exits and marks affected contexts dead.

## Control Flow, State, and Persistence
Persistent runtime state lives in `mm->context`: turnstile mutex, TLB sync lock, `mm_id` pid/socket/stack, and list linkage. A global `mm_list` protected by `mm_list_lock` lets SIGCHLD handling map dead host pids back to mm contexts.

## Dependencies and Integration Points
Depends on SKAS process startup, `map()`/`unmap()` syscall stubs, SIGCHLD IRQ, `stub_data`, futex waking, and host process kill/close helpers. It is the central lifecycle owner for user address-space backing processes.

## Risks and Test Signals
Risks include leaking child processes, dead contexts causing later faults, and turnstile deadlocks. Test fork/exec/exit storms, seccomp child crashes, OOM during context creation, and SMP page-fault/mmap concurrency.
