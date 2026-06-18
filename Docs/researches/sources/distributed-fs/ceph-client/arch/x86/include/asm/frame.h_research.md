<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/frame.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/frame.h

## Purpose
Assembler/C macros for frame-pointer prologues and encoded pt_regs frame pointers used by unwinding. The header is 113 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/asm.h>`

Notable constants/macros: `#define _ASM_X86_FRAME_H`; `#define FRAME_BEGIN \`; `#define FRAME_END "pop %" _ASM_BP "\n"`; `#define ENCODE_FRAME_POINTER \`; `#define FRAME_OFFSET __ASM_SEL(4, 8)`; `#define ENCODE_FRAME_POINTER`; `#define FRAME_BEGIN`; `#define FRAME_END`; `#define FRAME_OFFSET 0`

Notable declarations and inline helpers: `#define _ASM_X86_FRAME_H`; `#define FRAME_BEGIN \`; `#define FRAME_END "pop %" _ASM_BP "\n"`; `#define ENCODE_FRAME_POINTER \`; `static inline unsigned long encode_frame_pointer(struct pt_regs *regs)`; `#define FRAME_OFFSET __ASM_SEL(4, 8)`; `#define ENCODE_FRAME_POINTER`; `#define FRAME_BEGIN`; `#define FRAME_END`; `#define FRAME_OFFSET 0`

## Control Flow
FRAME_BEGIN/END emit rbp/ebp setup when frame pointers are enabled; ENCODE_FRAME_POINTER stores a tagged pt_regs pointer for exception-entry unwinders.

## State and Persistence
No persistent state; correctness is encoded in stack layout conventions and FRAME_OFFSET constants.

## Dependencies and Integration Points
Integrates with entry assembly, objtool/unwinder, pt_regs layout, and callable non-leaf assembly routines.

## Risks
Risks include corrupting original bp before register save, architecture tag mismatch, and unreliable stack traces if assembly omits macros.

## Test Signals
Tests should include objtool validation, ORC/frame-pointer unwinds through exceptions/interrupts, and 32-bit/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/frame.h -->
