## sources/distributed-fs/ceph-client/lib/rcuref.c

Purpose: implements slow paths for `rcuref`, a scalable reference count for RCU-managed objects. The design optimizes fast get/put paths with unconditional atomic add/subtract and uses value zones to detect valid, saturated, released, dead, and no-reference states.

Important APIs/functions: `rcuref_get_slowpath()` handles increments that land outside the valid reference zone. `rcuref_put_slowpath()` handles decrements that may drop the last reference, encounter imbalanced puts, or operate on saturated counts. Both are GPL exports.

Control flow: get slow path reads the counter; values in or beyond the released/dead zone are reset to `RCUREF_DEAD` and fail. Saturated values warn once, reset to `RCUREF_SATURATED`, and succeed so the object leaks rather than wraps. Put slow path marks `RCUREF_NOREF` as `RCUREF_DEAD` with release cmpxchg and acquire-after-control dependency; races simply return false. Imbalanced dead-zone puts warn and restore dead state; saturated puts restore saturation.

State and persistence: state is the atomic integer inside caller-owned `rcuref_t`. No global state is held.

Dependencies/integration: depends on `linux/rcuref.h`, atomics, warning macros, and RCU lifetime discipline. Callers must prevent grace-period completion across put slow paths, as described in the file comments.

Risks/test signals: misuse on non-RCU-managed objects can produce use-after-free. Saturation intentionally leaks. The code relies on large zones to absorb races and on exact memory-ordering contracts.
