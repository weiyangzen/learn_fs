<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/riscv_ksyms.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/riscv_ksyms.c

Purpose: Exports RISC-V memory helper symbols for modules.

Important APIs/types/functions: Exports `memset`, `memcpy`, `memmove`, `__memset`, `__memcpy`, and `__memmove`.

Control flow: No runtime control flow beyond symbol export table generation.

State and persistence: No state. The file affects module link-time symbol visibility.

Dependencies and integration points: Integrates architecture-provided optimized memory routines with loadable modules and module relocation/linking.

Risks: Exporting the wrong symbol variant can break module resolution or bypass intended optimized implementations.

Test signals: Build/load modules that call standard memory routines and verify kallsyms/module symbol resolution.

Source read size: 17 lines, 362 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/riscv_ksyms.c -->
