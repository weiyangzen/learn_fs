# sources/distributed-fs/ceph-client/include/linux/ptdump.h

Purpose: declares generic page-table dump walking hooks used for debugfs/proc-style page table inspection and W+X permission checks.

Important APIs and types: `struct ptdump_range` describes address ranges. `struct ptdump_state` carries callbacks for each page table level, flush notification, effective protection aggregation, and a range list. APIs include `ptdump_walk_pgd_level_core()`, `ptdump_walk_pgd()`, `ptdump_check_wx()`, and inline `debug_checkwx()`.

Control flow: architecture or debug code initializes a `ptdump_state` and walks a PGD for an `mm_struct`; callbacks observe PTE/PMD/PUD/P4D/PGD entries and effective protections. `debug_checkwx()` conditionally checks for writable-executable mappings when `CONFIG_DEBUG_WX` is enabled.

State and persistence: no state is stored here; walkers inspect live page tables. Dump output and check results are transient diagnostics.

Dependencies and integration points: depends on MM page table types, seq_file users, architecture page table formats, and debug W+X checking.

Risks and test signals: risks include walking unstable page tables without proper locking, incorrect effective-protection aggregation, missing folded levels, and false W+X reports. Test kernel page table dumps across paging modes, DEBUG_WX boot checks, huge mappings, folded-level architectures, and user/kernel mm walks.
