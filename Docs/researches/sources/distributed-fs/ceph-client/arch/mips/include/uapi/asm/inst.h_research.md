# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/inst.h

## Purpose

`inst.h` exposes MIPS instruction opcode enumerations and endian-aware bitfield overlays for instruction decoding in UAPI-visible tooling.

## Important APIs, Types, And Functions

Important APIs are opcode enums for classic MIPS, microMIPS, MIPS16e, MSA, DSP, COP0/COP1, Loongson, Octeon, and MXU encodings; format structs such as `j_format`, `i_format`, `r_format`, `c0r_format`, `msa_mi10_format`, microMIPS formats, and unions `mips_instruction`/`mips16e_instruction`. Includes: `asm/bitfield.h`. Macros/constants: `_UAPI_ASM_INST_H`, `MM_NOP16`. Types/enums/unions: `major_op`, `spec_op`, `spec2_op`, `spec3_op`, `mult_op`, `multu_op`, `div_op`, `divu_op`, `dmult_op`, `dmultu_op`, `ddiv_op`, `ddivu_op`, `rt_op`, `cop_op`, `bcop_op`, `cop0_coi_func`, `cop0_com_func`, `cop1_fmt`, `cop1_sdw_func`, `cop1x_func`, `mad_func`, `ptw_func`, `lx_func`, `mxu_func`, `lx_ingenic_func`, `bshfl_func`, and 76 more.

## Control Flow

There is no runtime flow locally; consumers overlay instruction words with endian-correct bitfields to decode or inspect opcodes.

## State And Persistence

State is user/kernel memory containing instruction words; no persistent state is modified.

## Dependencies And Integration Points

It integrates with uprobes, kprobes, instruction emulation, disassembly helpers, ptrace tooling, and user programs including kernel UAPI headers.

## Risks

Risks are UAPI ABI breakage, endian field-order mistakes, incorrect opcode values, and tooling misdecode across ISA revisions.

## Test Signals

Test signals are instruction decoder tests, kprobe/uprobe branch handling, microMIPS/MIPS16e coverage, and headers-install UAPI compilation.
Static review signal: this source currently has 1175 lines and 29923 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
