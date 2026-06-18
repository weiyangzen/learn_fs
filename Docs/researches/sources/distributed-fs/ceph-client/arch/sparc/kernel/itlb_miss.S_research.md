# sources/distributed-fs/ceph-client/arch/sparc/kernel/itlb_miss.S

## Purpose
`itlb_miss.S` is the sparc64 instruction TLB miss trap-table fragment. It performs a fast TSB lookup and loads the ITLB when the entry matches and is executable.

## Important APIs, Types, and Functions
There are no callable functions. The fragment uses `ASI_IMMU_TSB_8KB_PTR`, `ASI_IMMU`, `ASI_ITLB_DATA_IN`, `TSB_LOAD_QUAD()`, `_PAGE_EXEC_4U`, and external labels `kvmap_itlb`, `tsb_miss_itlb`, and `tsb_do_fault`.

## Control Flow and State
The code reads the IMMU TSB pointer and tag target, branches context-zero misses to kernel-vmap handling, loads a TSB quad, compares tags, routes misses to `tsb_miss_itlb` with `FAULT_CODE_ITLB`, checks the executable bit, routes non-executable translations to the fault path, writes a valid executable TTE to the ITLB, and retries.

## Persistence and Dependencies
It mutates only ITLB hardware state. Dependencies include TSB layout, executable bit encoding, trap-table register conventions, and sparc64 TLB/fault handlers.

## Integration Points, Risks, and Test Signals
Integration is with instruction fetch fault handling and kernel/user execution permissions. Risks include executing from non-executable mappings if `_PAGE_EXEC_4U` handling is wrong, excessive full miss handling due to tag mismatch bugs, and icache-line layout sensitivity. Test signals include NX permission faults, execution after ITLB eviction, module/text execution, and stable boot under instruction TLB pressure.
