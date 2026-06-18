<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/jailhouse_para.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/jailhouse_para.h

## Purpose
Jailhouse hypervisor paravirtualization detection helper. The header is 26 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/types.h>`

Notable constants/macros: `#define _ASM_X86_JAILHOUSE_PARA_H`

Notable declarations and inline helpers: `#define _ASM_X86_JAILHOUSE_PARA_H`; `bool jailhouse_paravirt(void);`; `static inline bool jailhouse_paravirt(void)`

## Control Flow
jailhouse_paravirt() reports true only when Jailhouse guest support is configured and detected; otherwise it compiles to false.

## State and Persistence
State is global hypervisor detection state in the Jailhouse implementation.

## Dependencies and Integration Points
Depends on CONFIG_JAILHOUSE_GUEST and x86 hypervisor detection.

## Risks
Risks are minimal, but false positives can install wrong paravirt behavior and false negatives skip required guest quirks.

## Test Signals
Tests should boot Jailhouse and non-Jailhouse guests and compile disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/jailhouse_para.h -->
