# sources/distributed-fs/ceph-client/arch/parisc/include/asm/current.h

Purpose: provides PA-RISC access to the current task pointer.

Important APIs/types/functions: defines `get_current()` and `current` plumbing around `current_thread_info()`/thread-info storage.

Control flow: kernel code expands `current` to find the running task from low-level per-thread state without a function call.

State and persistence: does not store state; it exposes the scheduler-maintained current task. Dependencies and integration: used nearly everywhere in kernel code, including syscall, scheduler, and fault paths.

Risks and test signals: an incorrect current-task derivation corrupts scheduler and security decisions globally. Test through context-switch stress, syscall tracing, and stack/thread-info layout checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
