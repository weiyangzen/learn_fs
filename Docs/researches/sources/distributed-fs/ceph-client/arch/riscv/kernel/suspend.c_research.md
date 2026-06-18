<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend.c

Purpose: Implements RISC-V CPU and system suspend support, including CSR save/restore, non-local suspend entry, SBI system suspend, SBI hart suspend, and HSM capability checks.

Important APIs/types/functions: Provides `suspend_save_csrs()`, `suspend_restore_csrs()`, `cpu_suspend()`, SBI system suspend platform ops, `riscv_sbi_hart_suspend()`, `riscv_sbi_suspend_state_is_valid()`, and `riscv_sbi_hsm_is_supported()`.

Control flow: `cpu_suspend()` saves live CPU context, executes a finisher such as SBI hart/system suspend with physical resume address, and restores CSRs/context when firmware returns. System suspend registers platform suspend ops when SBI SUSP is available. Hart suspend validates state IDs and invokes HSM suspend.

State and persistence: Suspend context stores CSRs such as status, envcfg, tvec, ie, scratch, epc, cause, tval, counteren, and sscratch. Global platform ops persist after init.

Dependencies and integration points: Depends on `suspend_entry.S`, SBI HSM/SUSP extensions, CPU context save helpers, PM core, MMU physical address translation, and per-CPU CSR state.

Risks: Missing CSR save/restore can corrupt resumed execution or user feature state. Firmware may not preserve memory/cache state as expected. Resume address must be physical and correctly aligned.

Test signals: CPU idle/suspend-to-RAM on SBI SUSP systems, per-hart suspend states, vector/CFI/envcfg state across suspend, CPU hotplug with HSM, and negative tests for invalid suspend state IDs.

Source read size: 198 lines, 4865 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend.c -->
