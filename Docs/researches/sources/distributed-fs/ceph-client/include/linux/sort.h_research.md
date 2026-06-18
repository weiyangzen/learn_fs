<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sort.h -->
# sources/distributed-fs/ceph-client/include/linux/sort.h

Purpose: This header declares generic in-kernel array sorting helpers, including variants that periodically reschedule for non-atomic contexts.

Important APIs/types/functions: `cmp_int(l, r)` performs a safe three-way comparison without subtraction overflow. `sort()` and `sort_r()` sort arrays using caller-provided compare/swap callbacks, with `sort_r()` carrying private context. `sort_nonatomic()` and `sort_r_nonatomic()` are variants that may call `cond_resched()`.

Control flow: Callers provide base pointer, element count, element size, comparator, optional swap routine, and optional private context. The implementation lives elsewhere and invokes callbacks while rearranging the array.

State and persistence: No global state. The only persistent effect is mutation of the caller-provided array.

Dependencies/integration: Depends on kernel type definitions and callback typedefs from included headers. Used by subsystems needing deterministic in-place ordering without open-coding sort algorithms.

Risks and test signals: Risks include comparators with inconsistent ordering, using nonatomic variants in atomic context, invalid element sizes, and swap callbacks that corrupt data. Test with duplicate keys, large arrays, custom swap callbacks, resched-enabled paths, and sanitizers for bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sort.h -->
