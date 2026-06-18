# sources/distributed-fs/ceph-client/arch/riscv/kernel/perf_regs.c

Purpose: Maps perf register sampling ABI numbers to RISC-V `pt_regs` fields.

Important APIs/types/functions: Implements `perf_reg_value()` and register mask validation helpers for the RISC-V perf ABI.

Control flow: Perf asks for selected registers in a sample. The implementation validates the register id and returns the corresponding general register, PC, or status value from the trap frame.

State and persistence: No persistent state; it reads sample-time `pt_regs`.

Dependencies and integration points: Depends on perf event core, `pt_regs`, and RISC-V userspace perf register ABI.

Risks and test signals: ABI numbering errors break profiler register dumps. Test `perf record --intr-regs`, invalid masks, user/kernel samples, and 32/64-bit register width expectations.
