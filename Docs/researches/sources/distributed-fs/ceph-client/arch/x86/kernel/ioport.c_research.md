# sources/distributed-fs/ceph-client/arch/x86/kernel/ioport.c

## Purpose
Implements x86 user I/O port permission syscalls `ioperm` and `iopl` using task I/O bitmaps rather than CPU IOPL interrupt-disable privileges.

## Important APIs And State
Under `CONFIG_X86_IOPL_IOPERM`, defines `io_bitmap_sequence`, `io_bitmap_share()`, `io_bitmap_exit()`, `ksys_ioperm()`, `SYSCALL_DEFINE3(ioperm)`, and `SYSCALL_DEFINE1(iopl)`. Without support, the syscalls return `-ENOSYS`.

## Control Flow And Persistence
`ioperm()` validates range, enforces `CAP_SYS_RAWIO` and lockdown for enabling access, lazily allocates an all-denied bitmap, copy-on-writes shared bitmaps inherited by fork, clears bits to permit ports or sets bits to deny, computes active max size, frees the bitmap when all permissions are denied, and increments a sequence to force TSS update on return to user mode. `iopl()` emulates only level 3 as all-ports permission and never grants CLI/STI behavior; it updates per-thread `iopl_emul` and TIF_IO_BITMAP/TSS state.

## Dependencies And Integration Points
Depends on task `thread_struct` I/O bitmap fields, TSS update code, fork/exit hooks, capabilities, lockdown LSM, bitmap helpers, and syscall ABI.

## Risks And Test Signals
Risks include stale TSS bitmap after permission changes, refcount/copy-on-write mistakes across fork, privilege bypass under lockdown, and semantic differences from hardware IOPL. Tests include `ioperm()` ranges and overflow, fork inheritance, permission drop/free, `iopl(3)` all-port behavior, lockdown denial, and context-switch/user-return TSS updates.
