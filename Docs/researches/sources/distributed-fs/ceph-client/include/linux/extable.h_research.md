# sources/distributed-fs/ceph-client/include/linux/extable.h

Purpose: exception table search/sort API for recovering from faulting kernel instruction ranges.

Important APIs/types/functions: `search_extable()`, `sort_extable()`, `sort_main_extable()`, `trim_init_extable()`, `search_exception_tables()`, `search_kernel_exception_table()`, optional `search_module_extables()`, and optional `search_bpf_extables()`.

Control flow: boot/module load sorts exception tables; fault handlers call search helpers by instruction address; module and BPF JIT tables are included conditionally; init tables can be trimmed after init.

State/persistence: exception table entries are linked into kernel/modules/BPF JIT metadata and persist for code lifetime.

Dependencies/integration: architecture exception table entry format, modules, BPF JIT, fault handlers, linker sections.

Risks/test signals: risks are unsorted tables causing failed lookup, stale module/BPF entries after unload, trimming too aggressively, and address comparison bugs. Test uaccess fault fixups, module load/unload exception fixups, BPF JIT fault recovery, and boot-time sort validation.
