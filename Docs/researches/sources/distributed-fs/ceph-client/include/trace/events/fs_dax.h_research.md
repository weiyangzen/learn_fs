<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fs_dax.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fs_dax.h

## Purpose
Defines filesystem DAX tracepoints for PMD/PTE faults, load-hole handling, PFN insertion, and DAX writeback ranges.

## APIs, Control Flow, and State
Event classes include `dax_pmd_fault_class`, `dax_pmd_load_hole_class`, `dax_pte_fault_class`, and `dax_writeback_range_class`. Instances are `dax_pmd_fault`, `dax_pmd_fault_done`, `dax_pmd_load_hole`, `dax_pmd_load_hole_fallback`, `dax_pte_fault`, `dax_pte_fault_done`, `dax_load_hole`, `dax_insert_pfn_mkwrite_no_entry`, `dax_insert_pfn_mkwrite`, `dax_writeback_range`, `dax_writeback_range_done`, and `dax_writeback_one`. Fault events record inode/device identity, VMA range, shared/private VMA mode, VM fault flags, fault address, page offset, max pgoff for PMD faults, and VM fault result flags. Load-hole events additionally record zero folio and radix entry pointers. Writeback events record pgoff ranges or a single pgoff/page length. The header owns no DAX radix or mapping state.

## Dependencies, Integration, Risks, and Tests
Depends on inode/VMA/vm_fault definitions, `FAULT_FLAG_TRACE`, `VM_FAULT_RESULT_TRACE`, device number helpers, and DAX implementation call sites. Integration points are fs-DAX mmap fault handling for PMD and PTE mappings, hole faults, PFN dirty/write faults, and writeback over persistent memory ranges. Risks include exposing DAX physical layout indirectly through pgoff ranges, tracing pointer values for zero folios/radix entries, interpreting result flags without fault retry context, and assuming PMD events fire on filesystems or hardware that only support PTE DAX. Test signals include DAX xfstests, mmap shared/private DAX faults, hole-fault fallback tests, pfn_mkwrite paths, writeback range tracing, and PMD-vs-PTE configuration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fs_dax.h -->
