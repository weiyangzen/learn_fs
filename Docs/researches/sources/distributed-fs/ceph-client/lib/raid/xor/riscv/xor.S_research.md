# sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor.S

Purpose: implements raw RISC-V vector XOR loops for 2 through 5 operand cases.

Important APIs and flow: exports `xor_regs_2_`, `xor_regs_3_`, `xor_regs_4_`, and `xor_regs_5_`. Each loop uses `vsetvli` with byte elements, vector-loads destination and sources, performs chained `vxor.vv`, vector-stores the destination, advances pointers by the selected vector length, and repeats until all bytes are consumed.

State and persistence: no persistence; destination buffer is updated in place. Vector context ownership is handled by the C glue.

Dependencies and integration: called by `riscv/xor-glue.c` and declared through architecture assembly prototypes.

Risks and test signals: risks include incorrect ABI register usage, varying vector length handling, and missing vector feature gating. Signals include assembly build coverage, KUnit randomized XOR tests, and hardware parity stress on RVV systems.
