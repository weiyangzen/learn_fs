<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/io_bitmap.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/io_bitmap.h

## Purpose
Task I/O permission bitmap layout and helpers for x86 TSS-based port I/O access control. The header is 52 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/refcount.h>`; `#include <asm/processor.h>`; `#include <asm/paravirt.h>`

Notable constants/macros: `#define _ASM_X86_IOBITMAP_H`; `#define tss_update_io_bitmap native_tss_update_io_bitmap`; `#define tss_invalidate_io_bitmap native_tss_invalidate_io_bitmap`

Notable declarations and inline helpers: `#define _ASM_X86_IOBITMAP_H`; `struct io_bitmap {`; `u64 sequence;`; `unsigned int max;`; `unsigned long bitmap[IO_BITMAP_LONGS];`; `struct task_struct;`; `void io_bitmap_share(struct task_struct *tsk);`; `void io_bitmap_exit(struct task_struct *tsk);`; `static inline void native_tss_invalidate_io_bitmap(void)`; `void native_tss_update_io_bitmap(void);`; `#define tss_update_io_bitmap native_tss_update_io_bitmap`; `#define tss_invalidate_io_bitmap native_tss_invalidate_io_bitmap`; `static inline void io_bitmap_share(struct task_struct *tsk) { }`; `static inline void io_bitmap_exit(struct task_struct *tsk) { }`; `static inline void tss_update_io_bitmap(void) { }`

## Control Flow
Context switch and ioperm/iopl paths copy or invalidate per-task bitmaps and update the TSS I/O bitmap base so user port I/O traps or succeeds.

## State and Persistence
State is per-task io_bitmap data, TSS bitmap storage, and thread flags indicating bitmap validity.

## Dependencies and Integration Points
Depends on processor/TSS layout, thread_struct, syscall ioperm/iopl handling, and context switch code.

## Risks
Risks include stale bitmap permissions after exec/fork, bitmap overrun beyond TSS limit, and privilege escalation through incorrect invalidation.

## Test Signals
Tests should cover ioperm/iopl syscalls, fork/exec inheritance, context switch isolation, invalid port ranges, and 32-bit compat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/io_bitmap.h -->
