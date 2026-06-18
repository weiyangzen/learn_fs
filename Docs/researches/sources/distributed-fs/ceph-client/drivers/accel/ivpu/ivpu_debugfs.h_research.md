## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_debugfs.h

### Purpose
`ivpu_debugfs.h` declares debugfs initialization and provides a no-op stub when debugfs is disabled.

### Important APIs, Types, And Functions
The only API is `ivpu_debugfs_init(struct ivpu_device *vdev)`, either declared for `CONFIG_DEBUG_FS` or defined inline as an empty function.

### Control Flow
Driver probe calls `ivpu_debugfs_init()` unconditionally. Compile-time configuration decides whether files are registered.

### State, Persistence, And Dependencies
The header stores no state. When enabled, state is created in debugfs by the implementation; when disabled, no state is created. It depends only on a forward declaration of `struct ivpu_device`.

### Integration Points
It decouples `ivpu_drv.c` from debugfs configuration and matches the Makefile conditional object.

### Risks
The stub must remain signature-compatible with the real function so disabled-debugfs builds continue to compile.

### Test Signals
Build with and without `CONFIG_DEBUG_FS`; probe should succeed in both cases, with debugfs files present only in the enabled build.
