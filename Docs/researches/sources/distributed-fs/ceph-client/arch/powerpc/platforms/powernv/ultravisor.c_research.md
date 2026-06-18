## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/ultravisor.c

### Purpose
`ultravisor.c` detects IBM Ultravisor firmware and exposes its memory console through sysfs.

### Important APIs, Types, And Functions
`early_init_dt_scan_ultravisor()` sets `FW_FEATURE_ULTRAVISOR` when an `ibm,ultravisor` flat-DT node appears. `uv_init()` finds `ibm,uv-firmware`, initializes `uv_memcons`, creates `/sys/firmware/ultravisor`, and publishes a read-only `msglog` binary attribute. `uv_msglog_read()` copies from the memconsole.

### Control Flow
Early DT scanning marks the firmware feature. A PowerNV machine subsystem initcall returns immediately without the feature, otherwise locates the UV firmware node, initializes memcons, sizes the bin attribute, creates the kobject, and registers the sysfs file.

### State, Persistence, And Dependencies
State is `ultravisor_kobj`, `uv_memcons`, and the initialized bin attribute size. The exposed persistence is the firmware-backed memconsole content.

### Integration Points
This integrates with firmware feature detection, `firmware_kobj`, sysfs binary attributes, and the generic `memcons` helper.

### Risks
Missing or malformed DT nodes disable exposure. Kobject creation or sysfs file creation can fail after memcons initialization without explicit cleanup. Access permissions intentionally restrict the log to root-readable.

### Test Signals
Boot with and without Ultravisor nodes, sysfs `msglog` reads at offsets, and error paths for missing `ibm,uv-firmware` validate behavior.
