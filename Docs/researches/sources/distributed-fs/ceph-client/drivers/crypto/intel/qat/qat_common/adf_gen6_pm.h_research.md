## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_pm.h

Purpose: Defines Gen6 PM register offsets, masks, defaults, and debugfs data initialization hook.

Important APIs/types: Defines PM poll timing, `PM_STATUS`, `PM_INTERRUPT`, PM source bit, `DRV_ACTIVE`, default idle filter, init-state and CPM state masks, fuse PM enable masks, firmware idle masks, SSM PM enable/domain powered-up masks, and `adf_gen6_init_dev_pm_data()` under `CONFIG_DEBUG_FS` with an inline no-op fallback.

Control flow/state: No state is stored. Gen6 PM debugfs and product power-up code use these masks to decode status and expose PM data.

Dependencies/integration: Included by Gen6 PM debugfs and Gen6 hardware data paths. It is intentionally smaller than Gen4 PM because Gen6 debug status exposes fewer fields and no host message protocol in this file set.

Risks and test signals: Register mask drift affects PM status decoding. Build tests should cover debugfs on/off, and runtime tests should verify PM debug output for init state, CPM state, idle enable/filter, and SSM powered-up status.
