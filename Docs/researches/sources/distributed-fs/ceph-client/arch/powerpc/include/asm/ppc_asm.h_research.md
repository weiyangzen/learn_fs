# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc_asm.h

Purpose: This header provides PowerPC assembly macros for register save/restore, symbol declarations, stack frame construction, TOC/address loading, endian fixups, TLB/cache helpers, register names, soft-mask/restart tables, and ABI-specific constants.

Important APIs/types/functions: Major assembler macros include `OP_REGS`, `ZEROIZE_REGS`, `SAVE_GPRS`, `REST_GPRS`, `SAVE_NVGPRS`, FPR/VR/VSR/EVR save and restore groups, `SANITIZE_*` register clearing macros, HMT priority macros, `_GLOBAL`, `_GLOBAL_TOC`, `DOTSYM`, `_ASM_NOKPROBE_SYMBOL`, `LOAD_REG_IMMEDIATE`, `LOAD_REG_ADDR`, `LOAD_REG_ADDR_PIC`, `LOAD_PACA_TOC`, `PPC_CREATE_STACK_FRAME`, `MFTB`, `TLBSYNC`, `MTOCRF`, `tlbia`, `DCBT_*`, `toreal/fromreal/tophys/tovirt`, `MTMSRD`, `FIXUP_ENDIAN`, `FIXUP_ENDIAN_HV`, `SOFT_MASK_TABLE`, `RESTART_TABLE`, and `BTB_FLUSH`.

Control flow: The macros expand into low-level assembly sequences used by exception entry/exit, context switch, VDSO, boot, TLB invalidation, endian mode correction, feature alternatives, and ABI entry points. Some macros create table entries in named sections, while others use nested feature fixup sections to patch instructions by CPU feature.

State and persistence: Generated code saves/restores architectural register state to `pt_regs` or thread structures, updates stack frames, manipulates MSR/SRR/HSRR state for endian trampolines, writes SPRs for BTB/TLB/cache behavior, and emits metadata sections consumed by runtime fixup code.

Dependencies and integration points: It includes assembler compatibility, processor definitions, opcode macros, firmware flags, feature fixups, and exception-table support. It sits at the intersection of C-visible ABI definitions, assembly source files, kprobe blacklists, CPU feature patching, KVM/BookE/Book3S variants, and endian/TOC models.

Risks and test signals: Incorrect offsets or ABI variants corrupt saved registers, stack unwinding, or TOC setup. Endian fixup code is deliberately raw instruction data and must preserve exact encodings. Sanitization macros affect security hardening. Tests should include allmodconfig/defconfig builds for 32/64-bit, BE/LE, ELFv1/ELFv2, BookE/Book3S, boot tests, exception return tests, objdump checks, kprobe blacklist validation, and CPU feature alternative patch coverage.
