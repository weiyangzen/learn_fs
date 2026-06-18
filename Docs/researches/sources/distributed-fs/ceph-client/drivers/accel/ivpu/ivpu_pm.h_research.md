<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.h

### Purpose
`ivpu_pm.h` defines ivpu PM state and the driver-internal API for runtime PM, reset/recovery, timeout detection, and DCT control.

### Important APIs, Types, And Functions
`struct ivpu_pm_info` contains the owning device, delayed job timeout work, recovery work, reset read/write semaphore, reset and engine-reset counters, reset-pending flag, and DCT active percentage. Exported functions cover PM init/enable/disable, suspend/resume callbacks, PCI reset callbacks, runtime get/put, recovery triggering, job timeout start/stop, and DCT operations.

### Control Flow
The header itself has no control flow, but its `reset_lock` forms a central control-flow gate: submitters take read access while reset/recovery takes write access.

### State, Persistence, And Dependencies
PM state persists for the device lifetime and spans runtime suspend/resume. Dependencies include workqueues, rwsems, atomics, device/PCI callback types, and ivpu device state.

### Integration Points
Used by job submission/completion, MMU suspend/resume, firmware boot, PCI driver callbacks, and hardware DCT IRQ handling.

### Risks
New code using runtime PM must use `ivpu_rpm_get()`/`ivpu_rpm_put()` consistently and respect `reset_lock` when touching firmware or hardware.

### Test Signals
Lockdep-clean reset versus submit races, balanced runtime PM usage, timeout work cancellation, and recovery work disable during driver teardown are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.h -->
