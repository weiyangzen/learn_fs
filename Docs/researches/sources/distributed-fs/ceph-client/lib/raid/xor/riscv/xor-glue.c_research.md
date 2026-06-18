# sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor-glue.c

Purpose: exposes RISC-V vector assembly XOR helpers as a safe XOR template.

Important APIs and flow: `DO_XOR_BLOCKS(vector_inner, xor_regs_2_, xor_regs_3_, xor_regs_4_, xor_regs_5_)` builds an inner generator. `xor_gen_vector()` wraps it with `kernel_vector_begin()` and `kernel_vector_end()`. `xor_block_rvv` registers template name `rvv`.

State and persistence: no persistent state; only vector context bracketing and destination mutation.

Dependencies and integration: depends on RISC-V vector switch helpers, assembly prototypes, `xor.S`, and `riscv/xor_arch.h`.

Risks and test signals: vector state handling and runtime feature gating are critical. Signals include RISC-V vector build coverage, KUnit XOR tests, and boot calibration choosing `rvv`.
