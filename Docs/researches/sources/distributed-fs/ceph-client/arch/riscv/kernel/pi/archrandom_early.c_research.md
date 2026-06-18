# sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/archrandom_early.c

Purpose: Provides an early RISC-V architectural random seed path for KASLR before normal drivers initialize.

Important APIs/types/functions: Implements `get_kaslr_seed_zkr()` and uses the Zkr entropy CSR path when available.

Control flow: Early boot checks whether the CPU/FDT indicates the Zkr extension and then samples architectural random values to contribute a KASLR seed.

State and persistence: No long-lived state; returns seed material to early KASLR logic.

Dependencies and integration points: Depends on early ISA extension detection, CSR access, and `fdt_early.c` KASLR seed selection.

Risks and test signals: Early CSR access must only occur when supported, and weak entropy should not be over-trusted. Test Zkr-present and absent systems, traps on unsupported CSR access, and KASLR seed variation.
