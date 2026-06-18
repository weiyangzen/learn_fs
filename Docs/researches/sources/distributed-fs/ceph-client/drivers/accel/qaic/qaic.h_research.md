<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic.h -->
## sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic.h

### Purpose
`qaic.h` is the central shared header for the Qualcomm Cloud AI accelerator driver. It defines device, user, DMA bridge channel, DRM device, GEM BO, and BO slice state plus cross-module function prototypes for control, data, reset, sysfs, and MHI callbacks.

### Important APIs, Types, And Functions
Important constants include DBC BAR offsets/sizes, SSR sentinel, no-partition sentinel, and container macros. Enums define AIC families, device states (`OFFLINE`, `BOOT`, `ONLINE`), and DBC subsystem/reset states. `struct qaic_user` tracks DRM users with kref and SRCU. `struct dma_bridge_chan` tracks a DBC's queues, DMA address, locks, user, request IDs, IRQ/polling, BO lists, wait queue, and state. `struct qaic_device` aggregates PCI/MHI/MMIO, control channel queues, DBCs, SRCU, device state, MHI side channels, RAS counters, SSR state, workqueues, and DRM device reference. `struct qaic_drm_device`, `struct qaic_bo`, and `struct bo_slice` define DRM accel-facing state. Prototypes cover manage ioctls, MHI callbacks, control open/close, user release, DBC enable/disable/release/wakeup, GEM/data ioctls, reset cleanup, SSR transitions, and sysfs.

### Control Flow
The header has no executable flow but describes the cross-file driver architecture. PCI probe creates `qaic_device`, registers MHI, creates DRM devices, and initializes DBC/control/sysfs state. Users open a DRM device, issue manage ioctls to activate/deactivate DBCs, create/attach/execute/wait BOs through data ioctls, and release resources on close or reset. MHI callbacks drive control and side-channel completions.

### State, Persistence, And Dependencies
State spans PCI device lifetime (`qaic_device`), logical DRM partition lifetime (`qaic_drm_device`), open-file lifetime (`qaic_user`), DBC assignment lifetime, and GEM BO/slice lifetime. Synchronization uses mutexes, spinlocks, SRCU, wait queues, completions, workqueues, and krefs. Dependencies include Linux PCI, MHI, interrupt, DRM device/GEM, dma-buf/import, and coredump/RAS/SSR support in other qaic files.

### Integration Points
Every qaic source file includes or depends on this header: PCI driver setup, MHI controller, control-message encoding, data-path DMA queues, RAS/SSR handlers, sysfs/debugfs, timesync, and Sahara boot loading. UAPI ioctls eventually map into the prototypes declared here.

### Risks
This header is a broad coupling point. Struct layout changes can break assumptions in many files, especially DBC queue ownership, BO slicing, reset cleanup, and SSR state transitions. Synchronization is subtle: DBC lists use spinlocks and SRCU, users use krefs/SRCU, control path uses mutexes and workqueues, and BOs use completions and mutexes. Device reset must clean local state while MHI callbacks and users may still reference objects.

### Test Signals
Probe/remove, user open/close, manage activate/deactivate/status, BO create/mmap/import/attach/execute/wait/detach, DBC interrupt and polling modes, MHI control callbacks, SSR enter/exit, RAS counters, reset cleanup under active users, sysfs DBC state updates, and KASAN/KCSAN/lockdep runs are high-signal coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic.h -->
