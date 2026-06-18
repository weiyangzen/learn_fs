<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/inat.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/inat.h

## Purpose
Instruction attribute table interface used by the x86 instruction decoder to classify prefixes, opcodes, ModRM, immediates, and escape maps. The header is 266 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/inat_types.h> /* __ignore_sync_check__ */`

Notable constants/macros: `#define _ASM_X86_INAT_H`; `#define INAT_OPCODE_TABLE_SIZE 256`; `#define INAT_GROUP_TABLE_SIZE 8`; `#define INAT_PFX_OPNDSZ 1 /* 0x66 */ /* LPFX1 */`; `#define INAT_PFX_REPE 2 /* 0xF3 */ /* LPFX2 */`; `#define INAT_PFX_REPNE 3 /* 0xF2 */ /* LPFX3 */`; `#define INAT_PFX_LOCK 4 /* 0xF0 */`; `#define INAT_PFX_CS 5 /* 0x2E */`; `#define INAT_PFX_DS 6 /* 0x3E */`; `#define INAT_PFX_ES 7 /* 0x26 */`; `#define INAT_PFX_FS 8 /* 0x64 */`; `#define INAT_PFX_GS 9 /* 0x65 */`; `#define INAT_PFX_SS 10 /* 0x36 */`; `#define INAT_PFX_ADDRSZ 11 /* 0x67 */`; `#define INAT_PFX_REX 12 /* 0x4X */`; `#define INAT_PFX_VEX2 13 /* 2-bytes VEX prefix */`; `#define INAT_PFX_VEX3 14 /* 3-bytes VEX prefix */`; `#define INAT_PFX_EVEX 15 /* EVEX prefix */`

Notable declarations and inline helpers: `#define _ASM_X86_INAT_H`; `#define INAT_OPCODE_TABLE_SIZE 256`; `#define INAT_GROUP_TABLE_SIZE 8`; `#define INAT_PFX_OPNDSZ 1 /* 0x66 */ /* LPFX1 */`; `#define INAT_PFX_REPE 2 /* 0xF3 */ /* LPFX2 */`; `#define INAT_PFX_REPNE 3 /* 0xF2 */ /* LPFX3 */`; `#define INAT_PFX_LOCK 4 /* 0xF0 */`; `#define INAT_PFX_CS 5 /* 0x2E */`; `#define INAT_PFX_DS 6 /* 0x3E */`; `#define INAT_PFX_ES 7 /* 0x26 */`; `#define INAT_PFX_FS 8 /* 0x64 */`; `#define INAT_PFX_GS 9 /* 0x65 */`; `#define INAT_PFX_SS 10 /* 0x36 */`; `#define INAT_PFX_ADDRSZ 11 /* 0x67 */`; `#define INAT_PFX_REX 12 /* 0x4X */`; `#define INAT_PFX_VEX2 13 /* 2-bytes VEX prefix */`; `#define INAT_PFX_VEX3 14 /* 3-bytes VEX prefix */`; `#define INAT_PFX_EVEX 15 /* EVEX prefix */`; `#define INAT_PFX_REX2 16 /* 0xD5 */`; `#define INAT_PFX_XOP 17 /* 0x8F */`; `#define INAT_LSTPFX_MAX 3`; `#define INAT_LGCPFX_MAX 11`; `#define INAT_IMM_BYTE 1`; `#define INAT_IMM_WORD 2`

## Control Flow
Decoder code queries inat_get_* helpers to progress from prefixes to opcode attributes, group attributes, AVX/XOP/EVEX maps, and immediate/displacement sizing.

## State and Persistence
State is generated read-only inat tables and compact bitfields; the header itself only defines accessors and bit tests.

## Dependencies and Integration Points
Depends on inat_types.h, generated opcode attribute tables, insn.h, kprobes, uprobes, alternatives, and instruction emulation users.

## Risks
Risks include generated-table mismatch with decoder macros, incomplete new opcode coverage, and wrong group handling producing unsafe instruction lengths.

## Test Signals
Tests should run insn decoder selftests, kprobe/uprobes decode cases, alternatives patching, AVX/EVEX/APX opcodes, and malformed-byte fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/inat.h -->
