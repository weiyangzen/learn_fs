# sources/distributed-fs/ceph-client/arch/mips/kernel/r4k_fpu.S

## Purpose
Provides R4K/newer FPU and MSA context save/restore assembly, including signal-frame FP copy helpers and MSA upper-lane user-copy helpers.

## Important APIs, Types, and Functions
- `_save_fp`, `_restore_fp`, `_save_msa`, `_restore_msa`, and `_init_msa_upper` move task FP/MSA state to/from hardware.
- `_save_fp_context()` and `_restore_fp_context()` copy FPU state between hardware and user signal context with exception fixups.
- `read_msa_wr_*` and `write_msa_wr_*` generated leaf routines read/write one MSA vector register element width.
- `_save_msa_all_upper()` and `_restore_msa_all_upper()` copy upper 64-bit MSA lanes for signal context.
- `fault` returns `-EFAULT` for protected user-memory faults.

## Control Flow
Thread FP helpers read CP0 status when needed and invoke double-precision FPU macros. MSA helpers call MSA save/restore/init macros. Signal save reads FCSR, conditionally stores odd double registers only when FR=1 on relevant CPUs, stores even registers, stores FCSR, and returns zero. Restore loads FCSR and registers in the inverse order and writes FCSR. MSA indexed helpers jump through an inline table of 32 register-specific operations. Upper-lane helpers unroll all 32 vector registers, with endian and 32/64-bit-specific lane extraction/insertion.

## State and Persistence
Moves state among hardware FPU/MSA registers, task `thread.fpu`, and user signal buffers. No disk persistence.

## Dependencies and Integration Points
Used by FPU ownership/context switch code, ptrace/MSA regsets, and signal code through `signal-common.h`. Depends on hardfloat/MSA assembler support, `__ex_table`, CP0 status FR mode, endian configuration, and FPU/MSA macros.

## Risks
FR mode handling is critical: saving odd registers when FR=0 or failing to save them when FR=1 corrupts FP state. MSA upper-lane endian handling must match user ABI. All user stores/loads must have exception-table fixups. Indexed MSA helpers rely on exact table stride and register ordering.

## Test Signals
FP and MSA context-switch stress, signal delivery/return, ptrace MSA regset get/set, and invalid signal-frame fault injection should preserve registers or return `-EFAULT` correctly across endian and FR modes.
