<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/inat_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/inat_types.h

## Purpose
Primitive integer typedefs for instruction attribute and byte/value fields shared by inat and insn decoder headers. The header is 15 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INAT_TYPES_H`

Notable declarations and inline helpers: `#define _ASM_X86_INAT_TYPES_H`; `typedef unsigned int insn_attr_t;`; `typedef unsigned char insn_byte_t;`; `typedef signed int insn_value_t;`

## Control Flow
No control flow; it fixes the width of insn_attr_t, insn_byte_t, and insn_value_t.

## State and Persistence
State is absent; ABI is compile-time type size and signedness.

## Dependencies and Integration Points
Depends on linux/types.h and consumers in inat.h and insn.h.

## Risks
Risks are type-width changes breaking generated tables or instruction field packing.

## Test Signals
Test signal is build coverage and decoder selftests across 32-bit and 64-bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/inat_types.h -->
