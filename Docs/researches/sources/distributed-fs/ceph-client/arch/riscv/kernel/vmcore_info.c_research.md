<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmcore_info.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vmcore_info.c

Purpose: Emits RISC-V architecture-specific vmcore metadata for crash dump tools.

Important APIs/types/functions: Defines `get_satp_value()` and `arch_crash_save_vmcoreinfo()`.

Control flow: Crash vmcore setup records the current SATP mode/value and architecture constants into VMCOREINFO notes.

State and persistence: Persists metadata in the crash kernel vmcoreinfo note for later dump analysis.

Dependencies and integration points: Used by kdump/crash tooling to interpret RISC-V page tables and memory layout.

Risks: Missing or wrong SATP/page-table metadata makes crash dumps hard or impossible to decode.

Test signals: kdump capture on Sv39/Sv48/Sv57 systems and crash utility page-table interpretation.

Source read size: 31 lines, 1056 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmcore_info.c -->
