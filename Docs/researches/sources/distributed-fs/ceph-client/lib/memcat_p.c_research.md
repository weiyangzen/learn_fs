# sources/distributed-fs/ceph-client/lib/memcat_p.c

Purpose: Concatenates two NULL-terminated pointer arrays into a newly allocated NULL-terminated array.

Important APIs/types/functions: Exports GPL-only `__memcat_p(void **a, void **b)`.

Control flow: Counts entries in both arrays, allocates `nr + 1` pointer slots, then copies backward from the end of `b` and then `a`, preserving order and the final NULL terminator.

State and persistence: Returns caller-owned heap allocation from `kmalloc_array`; no global state.

Dependencies/integration: Depends on slab allocation and kernel export infrastructure.

Risks: Assumes both inputs are valid NULL-terminated arrays; returns NULL on allocation failure; callers must free the new array.

Test signals: No local tests; good tests would cover empty arrays, allocation failure, and order preservation.
