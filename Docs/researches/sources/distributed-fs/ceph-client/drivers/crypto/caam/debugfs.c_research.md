<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.c

Purpose: provides controller and QI debugfs visibility for CAAM performance counters, fault registers, optional key registers, and QI congestion counts.

Important APIs and control flow: `caam_debugfs_u32_get()` and `caam_debugfs_u64_get()` convert CAAM-endian register-backed values to CPU `u64` for read-only debugfs attributes. `caam_debugfs_init()` creates a `ctl` directory, publishes performance counters and fault registers from `struct caam_perfmon`, and, unless OP-TEE owns page0, exposes KEK/TKEK/TDSK register blobs. Under QI crypto API config, `caam_debugfs_qi_congested()` increments a static counter and `caam_debugfs_qi_init()` publishes it.

State and persistence behavior: debugfs dentries are stored in `ctrlpriv->ctl`; key blob wrappers live in controller private data. `times_congested` is a static process-wide counter. Removal is handled by `ctrl.c` with `debugfs_remove_recursive()` via devm action.

Dependencies and integration points: depends on debugfs, CAAM register endian helpers, `intern.h` private state, and QI congestion callback in `qi.c`. It is initialized from controller probe and QI init.

Risks and test signals: exposing internal keys in debugfs is intentionally skipped under OP-TEE but remains sensitive in non-secure debug builds; reads are raw register snapshots without locking; `times_congested` is not atomic. Test signals include expected files under `/sys/kernel/debug/<dev>/ctl`, monotonically increasing performance counters, fault register visibility after error injection, no key blobs with OP-TEE, and QI congestion count increments under congestion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.c -->
