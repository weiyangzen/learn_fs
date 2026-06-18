# sources/distributed-fs/ceph-client/arch/csky/abiv2/fpu.c

## Purpose

implements C-SKY ABI v2 FPU exception support, libc compatibility handling for FPU control-register
instructions, and save/restore helpers for user floating-point state

## Important APIs, Types, and Functions

Source read size: 270 lines, 5431 bytes. Includes: `linux/ptrace.h`, `linux/uaccess.h`,
`abi/reg_ops.h`. Functions: `fpu_libc_helper`, `fpu_fpe`, `save_to_user_fp`, `restore_from_user_fp`.
Key macros/defines: `MTCR_MASK`, `MFCR_MASK`, `MTCR_DIST`, `MFCR_DIST`, `FMFVR_FPU_REGS(vrx, vry)`,
`FMTVR_FPU_REGS(vrx, vry)`, `STW_FPU_REGS(a, b, c, d)`, `LDW_FPU_REGS(a, b, c, d)`.

## Control Flow and Behavior

fpu_libc_helper() emulates selected mfcr/mtcr encodings, fpu_fpe() maps FESR bits to SIGILL/SIGFPE
codes, and save_to_user_fp()/restore_from_user_fp() move FCR/FESR and VR registers with
CPU_HAS_FPUV2/VDSP-specific assembly

## State and Persistence

persistent effects are updates to pt_regs pc/general registers during emulation and saved user_fp
images used by signal/core/ptrace-style paths

## Dependencies and Integration Points

depends on ABI register layout, FPU control registers cr<1,2>/cr<2,2>, CONFIG_CPU_HAS_FPUV2,
CONFIG_CPU_HAS_VDSP, interrupt masking, and signal delivery

## Risks and Test Signals

instruction decode, register count, and interrupt-disabled FPU transfer sequences are fragile; FPU
exception, signal frame, ptrace, and libc compatibility tests are the useful signals
