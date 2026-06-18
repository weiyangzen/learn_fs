<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.h -->
## sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.h

### Purpose
`mhi_controller.h` declares qaic's MHI controller lifecycle API for PCI probe, teardown, and reset flows.

### Important APIs, Types, And Functions
It exports `qaic_mhi_register_controller()`, `qaic_mhi_free_controller()`, `qaic_mhi_start_reset()`, and `qaic_mhi_reset_done()`.

### Control Flow
There is no executable flow in the header. The API expresses a lifecycle: register and power up; power down/free; power down before reset; power up after reset.

### State, Persistence, And Dependencies
The returned `struct mhi_controller` is persisted in `qaic_device`. The prototypes depend on PCI device, MHI controller, MMIO BAR pointer, IRQ, MSI sharing, and family ID.

### Integration Points
Used by qaic PCI driver code and reset callbacks. It hides channel table and MHI-core setup details from the rest of the driver.

### Risks
Family ID must be valid for the static arrays in the implementation. Callers must pair successful registration with free and must not call reset helpers after unregister.

### Test Signals
Build coverage, probe/remove cycles, PCI reset cycles, and family-specific AIC100/AIC200 boot are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.h -->
