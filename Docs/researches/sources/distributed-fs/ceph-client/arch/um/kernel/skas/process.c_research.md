# sources/distributed-fs/ceph-client/arch/um/kernel/skas/process.c

## Purpose
Starts the UML kernel on the initial SKAS thread, manages idle-thread longjmp setup, exposes current mm helpers, and synchronizes current TLB state before entering host userspace.

## Important APIs, Types, and Functions
`start_uml()` installs the boot CPU signal stack, initializes signal handlers, and starts the idle thread. `start_kernel_proc()` blocks signals and calls `start_kernel()`. `current_stub_stack()`, `current_mm_id()`, and `current_mm_sync()` expose active memory-context state. `initial_jmpbuf_lock()` and `initial_jmpbuf_unlock()` serialize jumps through the initial thread buffer.

## Control Flow, State, and Persistence
State includes per-CPU IRQ stacks and a spinlock around the initial jump buffer. Boot control transitions from host `linux_main()` into `start_idle_thread()`, then into `start_kernel()`. Current-mm helpers are read-only except `current_mm_sync()`, which flushes pending TLB updates.

## Dependencies and Integration Points
Integrates with host SKAS thread switching in `os-Linux/skas/process.c`, TLB sync in `kernel/tlb.c`, signal-stack setup in `os-Linux/signal.c`, and generic kernel boot.

## Risks and Test Signals
Risks are signal delivery on wrong stacks, unsynchronized initial jump-buffer use, and missing TLB sync before userspace. Test boot, reboot, panic paths, nested callbacks from initial thread, and page-table changes before userspace resumes.
