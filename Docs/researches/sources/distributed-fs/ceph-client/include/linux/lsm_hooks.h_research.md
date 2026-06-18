<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_hooks.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm_hooks.h

## Purpose
This header defines the LSM hook registration framework. It turns `lsm_hook_defs.h` into typed function-pointer storage, static-call tables, hook descriptors, blob size declarations, and LSM registration records.

## Important APIs, Types, and Functions
`union security_list_options` contains a function pointer for every LSM hook. `struct lsm_static_call`, `struct lsm_static_calls_table`, `struct lsm_id`, `struct security_hook_list`, `struct lsm_blob_sizes`, and `struct lsm_info` are central types. `LSM_HOOK_INIT` initializes hook descriptors. `security_add_hooks` registers callbacks. `DEFINE_LSM` and `DEFINE_EARLY_LSM` place LSM descriptors in init sections. `lsm_get_xattr_slot` allocates xattr output slots.

## Control Flow
An LSM defines `struct security_hook_list` entries and a `struct lsm_info`. During boot, the framework orders LSMs, allocates blob offsets, registers hooks, and fills static-call tables from last to first so dispatch can jump directly to the first active callback.

## State and Persistence Behavior
Runtime state includes `static_calls_table`, registered hook descriptors, blob size allocations, enable flags, and init ordering. The state is initialized at boot and is not persistent.

## Dependencies and Integration Points
It depends on UAPI LSM IDs, security core declarations, RCU lists, xattrs, static calls, jump labels, unroll helpers, and `lsm_count.h`. It integrates every in-kernel LSM with the common security hook dispatch layer.

## Risks and Test Signals
Risks include bad hook initialization, wrong LSM ordering or exclusivity flags, static-call table sizing errors, blob offset conflicts, and xattr slot overrun. Test signals are boot-time enabled LSM logs, LSM selftests, multi-LSM stacking tests, static-call coverage, and xattr allocation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_hooks.h -->
