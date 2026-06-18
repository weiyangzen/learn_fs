<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/alternative.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/alternative.c

Purpose: Implements RISC-V runtime alternative instruction patching for CPU features, vendor errata, modules, and the vDSO.

Important APIs/types/functions: Key functions are `riscv_fill_cpu_mfr_info()`, `riscv_alternative_fix_offsets()`, `apply_boot_alternatives()`, `apply_early_boot_alternatives()`, `apply_module_alternatives()`, and internal JAL/AUIPC+JALR fixup helpers.

Control flow: The code reads vendor/arch/implementation IDs from CSRs or SBI, runs generic cpufeature patching, dispatches vendor errata patch functions, adjusts PC-relative call/jump immediates when alternative blocks move, and applies alternatives at early boot, normal boot, module load, and vDSO setup.

State and persistence: Persistent effects are patched kernel/module/vDSO instruction bytes; manufacturer info is transient.

Dependencies and integration points: Depends on alternative section symbols, cpufeature patching, vendor errata, SBI/CSR IDs, instruction decoder/encoder, text patching, module loader, and vDSO ELF sections.

Risks: Incorrect immediate fixups or vendor selection can patch invalid code very early in boot. Early path has MMU-off and no-instrumentation constraints.

Test signals: Boot with feature/errata alternatives, module alternative tests, vDSO alternative checks, objdump validation of call fixups, vendor CPU matrix, and ftrace/KASAN instrumentation builds.

Source read size: 241 lines, 6244 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/alternative.c -->
