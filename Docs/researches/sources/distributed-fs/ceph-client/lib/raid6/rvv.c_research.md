## sources/distributed-fs/ceph-client/lib/raid6/rvv.c

Purpose: provides RISC-V Vector Extension RAID-6 syndrome generation and incremental xor-syndrome implementations. The file deliberately errors if compiled with compiler vector support enabled, because it emits vector instructions explicitly in inline assembly under `.option arch,+v`.

Important APIs/functions: real worker functions are `raid6_rvv{1,2,4,8}_gen_syndrome_real()` and `raid6_rvv{1,2,4,8}_xor_syndrome_real()`. `RAID6_RVV_WRAPPER(1/2/4/8)` from `rvv.h` registers `raid6_calls` objects named `rvvx1`, `rvvx2`, `rvvx4`, and `rvvx8`.

Control flow: each function obtains runtime vector length with `vsetvli e8,m1`, uses that as `nsize`, and loops over `bytes` in unroll factors of 1, 2, 4, or 8 vector chunks. Syndrome generation initializes P and Q from the highest data disk and walks lower data disks, applying GF multiply-by-two using sign-mask, left-shift, and XOR with `0x1d`, then XORing input data into P/Q. Xor-syndrome first computes the affected range, advances Q over unaffected lower disks, then XORs computed P/Q deltas into existing parity.

State and persistence: no heap/global state is maintained. All state is vector registers and caller buffers; writes land in parity buffers or update existing parity in place. Kernel vector state is handled by wrapper functions, not the `_real()` bodies.

Dependencies/integration: depends on `rvv.h`, `linux/raid/pq.h`, RISC-V vector availability, and assembler support for vector mnemonics. Integrated through the RAID-6 algorithm list when `CONFIG_RISCV_ISA_V`/userspace RVV detection is active.

Risks/test signals: repeated inline assembly blocks make register/address mistakes easy, especially in the x8 path. The loops assume `bytes` is compatible with the chosen vector chunking; RAID page-sized callers normally satisfy this. Test coverage comes from `raid6/test` on RISC-V vector-capable systems and algorithm self-selection benchmarks.
