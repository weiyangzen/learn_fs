<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/insn.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/insn.h

## Purpose
Core x86 instruction decoder data structures and APIs for incremental decoding of prefixes, REX/REX2, VEX/XOP/EVEX, opcode, ModRM/SIB, displacement, immediates, and length. The header is 344 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/byteorder.h>`; `#include <asm/inat.h> /* __ignore_sync_check__ */`

Notable constants/macros: `#define _ASM_X86_INSN_H`; `#define MAX_INSN_SIZE 15`; `#define X86_MODRM_MOD(modrm) (((modrm) & 0xc0) >> 6)`; `#define X86_MODRM_REG(modrm) (((modrm) & 0x38) >> 3)`; `#define X86_MODRM_RM(modrm) ((modrm) & 0x07)`; `#define X86_SIB_SCALE(sib) (((sib) & 0xc0) >> 6)`; `#define X86_SIB_INDEX(sib) (((sib) & 0x38) >> 3)`; `#define X86_SIB_BASE(sib) ((sib) & 0x07)`; `#define X86_REX2_M(rex) ((rex) & 0x80) /* REX2 M0 */`; `#define X86_REX2_R(rex) ((rex) & 0x40) /* REX2 R4 */`; `#define X86_REX2_X(rex) ((rex) & 0x20) /* REX2 X4 */`; `#define X86_REX2_B(rex) ((rex) & 0x10) /* REX2 B4 */`; `#define X86_REX_W(rex) ((rex) & 8) /* REX or REX2 W */`; `#define X86_REX_R(rex) ((rex) & 4) /* REX or REX2 R3 */`; `#define X86_REX_X(rex) ((rex) & 2) /* REX or REX2 X3 */`; `#define X86_REX_B(rex) ((rex) & 1) /* REX or REX2 B3 */`; `#define X86_VEX_W(vex) ((vex) & 0x80) /* VEX3 Byte2 */`; `#define X86_VEX_R(vex) ((vex) & 0x80) /* VEX2/3 Byte1 */`

Notable declarations and inline helpers: `#define _ASM_X86_INSN_H`; `struct insn_field {`; `union {`; `unsigned char got;`; `unsigned char nbytes;`; `static inline void insn_field_set(struct insn_field *p, insn_value_t v,`; `unsigned char n)`; `static inline void insn_set_byte(struct insn_field *p, unsigned char n,`; `struct insn {`; `struct insn_field prefixes; /*`; `struct insn_field rex_prefix; /* REX prefix */`; `struct insn_field vex_prefix; /* VEX prefix */`; `struct insn_field xop_prefix; /* XOP prefix */`; `struct insn_field opcode; /*`; `struct insn_field modrm;`; `struct insn_field sib;`; `struct insn_field displacement;`; `struct insn_field immediate;`; `struct insn_field moffset1; /* for 64bit MOV */`; `struct insn_field immediate1; /* for 64bit imm or off16/32 */`; `struct insn_field moffset2; /* for 64bit MOV */`; `struct insn_field immediate2; /* for 64bit imm or seg16 */`; `int emulate_prefix_size;`; `unsigned char opnd_bytes;`

## Control Flow
Callers initialize struct insn with a byte buffer, lazily request fields, and the decoder advances next_byte until length/attributes are known; helper accessors expose prefix-map bits and addressing flags.

## State and Persistence
State is per-decode struct insn and read-only inat tables; no global persistence.

## Dependencies and Integration Points
Depends on byte order, inat.h generated attributes, MAX_INSN_SIZE rules, and kernel/32/64-bit decode mode selection.

## Risks
Risks include length miscalculation, endian handling errors, new opcode prefix gaps, and unsafe consumers trusting partially decoded fields.

## Test Signals
Tests should include decoder selftests, random-byte fuzzing, EVEX/VEX/XOP/REX2/APX cases, RIP-relative detection, and kprobe/alternative patch users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/insn.h -->
