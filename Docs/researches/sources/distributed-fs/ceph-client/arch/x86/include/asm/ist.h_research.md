<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ist.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/ist.h

## Purpose
Interrupt Stack Table information declaration and UAPI include for x86 special exception stacks. The header is 14 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <uapi/asm/ist.h>`

Notable constants/macros: `#define _ASM_X86_IST_H`

Notable declarations and inline helpers: `#define _ASM_X86_IST_H`; `extern struct ist_info ist_info;`

## Control Flow
No local control flow; it exposes global ist_info for code that reports or configures IST stack layout.

## State and Persistence
State is the global IST layout metadata and TSS IST pointers managed by CPU init/entry code.

## Dependencies and Integration Points
Depends on uapi/asm/ist.h and x86_64 exception stack setup.

## Risks
Risks include stale IST metadata relative to actual TSS stacks and config-only compile gaps.

## Test Signals
Tests should cover NMI/DB/MCE/DF stack setup, debugfs/proc reporting if present, and x86_64 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ist.h -->
