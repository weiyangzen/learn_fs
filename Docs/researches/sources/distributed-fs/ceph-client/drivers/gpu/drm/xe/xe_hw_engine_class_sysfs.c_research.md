# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_class_sysfs.c

Purpose: exposes per-hardware-engine-class scheduler properties through sysfs, with writable live values and read-only `.defaults`.

Important functions: `xe_hw_engine_class_sysfs_init`, `xe_hw_engine_timeout_in_range`, kobject creation/cleanup helpers, show/store wrappers that hold PM runtime, and store/show methods for job timeout, timeslice duration, and preempt timeout current/min/max/defaults.

Control flow: init creates an `engines` kobject under GT sysfs, walks hardware engines, skips OTHER/MAX, creates one child per engine class (`rcs`, `bcs`, `vcs`, `vecs`, `ccs`), attaches the class scheduling interface, creates `.defaults`, then creates live writable files. Managed cleanup removes files and puts kobjects.

State/persistence: sysfs writes update `hwe->eclass->sched_props` using `WRITE_ONCE`; default values remain in `eclass->defaults`. No locking beyond atomic-style writes is used for these 32-bit properties.

Dependencies/integration: integrates Linux kobject/sysfs APIs, DRM managed cleanup, Xe PM runtime, hardware engine class names, and scheduler property storage in `struct xe_hw_engine_class_intf`.

Risks/test signals: min/max stores must preserve valid ordering; live values are only range-checked against current min/max. Kobject release frees allocated objects, so cleanup ordering must match created files. Test valid/invalid writes, min > max rejection, max < min rejection, PM runtime around reads/writes, one sysfs directory per class despite multiple instances, and error-injected default directory creation.
