## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_coredump.h

### Purpose
`ivpu_coredump.h` declares the ivpu coredump hook and provides a logging-only fallback when devcoredump support is disabled.

### Important APIs, Types, And Functions
With `CONFIG_DEV_COREDUMP`, it declares `ivpu_dev_coredump(struct ivpu_device *vdev)`. Without it, the inline fallback creates a DRM info printer and dumps firmware logs with `ivpu_fw_log_print()`.

### Control Flow
Callers can invoke `ivpu_dev_coredump()` unconditionally. The compile-time branch either emits a devcoredump artifact or logs firmware buffers to the kernel log.

### State, Persistence, And Dependencies
No state is stored in the header. The fallback has no persistent coredump artifact, only log output. It depends on `ivpu_drv.h`, `ivpu_fw_log.h`, and DRM printer types.

### Integration Points
The header is included by driver boot/recovery code and hides `CONFIG_DEV_COREDUMP` from those callers.

### Risks
The fallback may produce less discoverable diagnostics than devcoredump. Both branches require valid firmware log buffers at call time.

### Test Signals
Compile with and without `CONFIG_DEV_COREDUMP`; trigger a failure and verify either a devcoredump file appears or firmware logs are printed.
