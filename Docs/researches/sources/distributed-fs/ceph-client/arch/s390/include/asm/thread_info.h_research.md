## sources/distributed-fs/ceph-client/arch/s390/include/asm/thread_info.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/thread_info.h` is a thread-info flags and
stack sizing in the s390 ceph-client Linux source snapshot. It has 84 lines and 2493 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
thread_info layout, thread/boot stack sizes, TIF flag numbers, and arch exec setup hooks
Important macros/constants: `_ASM_THREAD_INFO_H`, `THREAD_SIZE_ORDER`, `BOOT_STACK_SIZE`, `THREAD_SIZE`, `STACK_INIT_OFFSET`, `INIT_THREAD_INFO(tsk)`, `arch_setup_new_exec`, `HAVE_TIF_NEED_RESCHED_LAZY`, `HAVE_TIF_RESTORE_SIGMASK`, `TIF_ASCE_PRIMARY`, `TIF_GUARDED_STORAGE`, `TIF_ISOLATE_BP_GUEST`, `TIF_PER_TRAP`, `TIF_SINGLE_STEP`, `TIF_BLOCK_STEP`, `TIF_UPROBE_SINGLESTEP`, `_TIF_ASCE_PRIMARY`, `_TIF_GUARDED_STORAGE`, `_TIF_ISOLATE_BP_GUEST`, `_TIF_PER_TRAP`; plus 3 more.
Important types/layouts: `should`, `shares`, `thread_info`, `task_struct`.
Important declarations or inline helpers: `arch_setup_new_exec`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
scheduler, entry code, signal restore, guarded storage, and low-level stack assumptions. Direct
include dependencies detected here: `linux/bits.h`, `vdso/page.h`, `asm-generic/thread_info_tif.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for scheduler, entry code, signal restore,
guarded storage, and low-level stack assumptions. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
flag-number drift breaks entry assembly work checks and signal/exec cleanup

### Test Signals
entry-path tests, signal restore, guarded-storage state reset, and stack-size build checks
