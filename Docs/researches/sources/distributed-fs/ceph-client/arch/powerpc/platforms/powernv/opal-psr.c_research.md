## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-psr.c

### Purpose
`opal-psr.c` exposes OPAL power-shift-ratio controls under `/sys/firmware/opal/psr`, with one read/write sysfs file per firmware-described ratio handle.

### Important APIs, Types, And Functions
The main type is `struct psr_attr`. Important functions are `psr_show()`, `psr_store()`, and `opal_psr_init()`.

### Control Flow
Initialization finds `ibm,opal-power-shift-ratio`, allocates per-child attributes, creates a `psr` kobject, reads each child `handle` and `label`, and creates 0664 sysfs files. Reads and writes allocate an async token, take `psr_mutex`, call OPAL get/set functions, wait for async completion when required, translate OPAL return codes, and release the token.

### State, Persistence, And Dependencies
State is the sysfs kobject, attribute array, handles, and mutex. The PSR value is firmware/platform state. Dependencies include OPAL async calls, `opal_error_code()`, device tree child metadata, and sysfs.

### Integration Points
`opal_init()` invokes this after OPAL sysfs setup. User space can inspect and change platform PSR settings through the generated sysfs files.

### Risks
Partial initialization failures rely on `kobject_put()` and array free but do not remove already created sysfs files explicitly. All attributes use labels from DT directly. Concurrency is globally serialized; interrupted locks or tokens return to user space.

### Test Signals
Test missing node, missing handle/label, async and immediate OPAL get/set paths, invalid writes, interrupted lock/token acquisition, sysfs permissions, and cleanup after mid-loop sysfs creation failure.
