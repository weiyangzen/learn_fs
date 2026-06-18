# sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor_arch.h

Purpose: registers RISC-V XOR templates.

Important APIs and flow: `arch_xor_init()` registers generic `8regs` and `32regs`. With `CONFIG_RISCV_ISA_V` and `has_vector()`, it also registers `xor_block_rvv`.

State and persistence: only init-time template registration and later selected template speed.

Dependencies and integration: depends on `<asm/vector.h>` and `xor-glue.c`.

Risks and test signals: feature probing determines whether RVV participates in calibration. Signals include boot logs, KUnit, and RISC-V vector enable/disable config tests.
