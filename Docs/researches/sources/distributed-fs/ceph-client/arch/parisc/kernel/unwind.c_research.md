<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unwind.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/unwind.c

### Purpose
`unwind.c` implements PA-RISC kernel stack unwinding using `.PARISC.unwind` tables, module unwind tables, and special frame handling.

### Important APIs, Types, And Functions
Core APIs are `unwind_table_add()`, `unwind_table_remove()`, `unwind_init()`, `unwind_frame_init()`, `unwind_frame_init_from_blocked_task()`, `unwind_frame_init_task()`, `unwind_once()`, `unwind_to_user()`, and `return_address()`.

### Control Flow
Unwind tables are sorted and initialized with relocated region bounds. Lookup binary-searches the kernel table or scans module tables under a spinlock, moving hits to the front. Frame unwinding uses unwind entries to scan function prologues for frame growth and return-pointer saves, handles special frames such as interruption, syscall exit, interrupt return, context switch, and IRQ stack calls, and falls back to conservative stack scanning when no unwind entry exists.

### State, Persistence, And Dependencies
The kernel unwind table is static `__ro_after_init`; module tables are dynamically allocated in a locked list. Dependencies include linker-provided unwind sections, PA-RISC function descriptors, stack/task layout, ftrace, switch code symbols, and exception frame layouts.

### Integration Points
Used by stacktrace, oops printing, `__get_wchan()`, return-address helpers, and module load/unload unwind registration.

### Risks
Forced unwinding without metadata can miss modules or produce unreliable frames. Prologue instruction recognition must match compiler output. Blocked-task initialization allocates a temporary `pt_regs` with `GFP_ATOMIC`.

### Test Signals
Backtraces through interrupts, syscalls, context switches, modules, ftrace, and functions without unwind data should be compared against expected call chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unwind.c -->
