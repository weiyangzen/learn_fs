<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/internal.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/internal.h

Purpose: private regulator framework header defining internal consumer state, logging helpers, OF lookup hooks, and common get/bulk-get entry points.

Important APIs/types/functions: `struct regulator` represents one consumer handle with voltage requests per suspend state, load, enable count, deferred disables, supply name, device link flag, and debugfs/sysfs fields. `struct regulator_voltage`, `enum regulator_get_type`, `dev_to_rdev()`, `rdev_*()` logging macros, and OF helper prototypes form the main interface.

Control flow: this header has no runtime control flow. It controls compile-time contracts between regulator core source files and provides stub OF functions when `CONFIG_OF` is disabled.

State and persistence: documents the in-memory per-consumer state used by the core; persistence is runtime only and tied to consumer handles, not hardware NVM.

Dependencies and integration: includes suspend state constants and relies on public regulator consumer/driver types included by users. It bridges core lookup paths, OF parsing, coupled regulators, and common regulator acquisition semantics.

Risks and test signals: layout changes affect regulator core internals broadly. OF stubs must preserve error semantics for non-DT builds. Test signals are compile coverage with `CONFIG_OF=y/n`, optional/exclusive get paths, coupled regulator parsing, and suspend-state voltage arrays sized by `PM_SUSPEND_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/internal.h -->
