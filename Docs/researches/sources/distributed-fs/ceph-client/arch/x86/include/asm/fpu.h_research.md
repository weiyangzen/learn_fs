<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu.h

## Purpose
Top-level x86 FPU include that exposes the public FPU API and declares kernel FPU availability. The header is 13 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/fpu/api.h>`

Notable constants/macros: `#define _ASM_X86_FPU_H`; `#define kernel_fpu_available() true`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_H`; `#define kernel_fpu_available() true`

## Control Flow
No independent control flow; it includes asm/fpu/api.h and maps kernel_fpu_available() to true on x86.

## State and Persistence
No state is stored here; state lives in task fpu/fpstate structures and per-CPU ownership variables declared below the API layer.

## Dependencies and Integration Points
Integrated by generic kernel code that checks kernel_fpu_available() before using kernel_fpu_begin()/end().

## Risks
Risk is mainly semantic: consumers may treat availability as permission, but context rules still require irq_fpu_usable() and locking discipline.

## Test Signals
Compile coverage should include generic FPU users and configurations with/without extended xstate support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu.h -->
