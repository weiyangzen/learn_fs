<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams.h -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams.h

Purpose: This header defines the shared Apple Motion Sensor data model and backend interface used by the core, PMU backend, I2C backend, and input emulation code.

Important APIs and types: `enum ams_irq` defines freefall, shock, global, and all interrupt masks. `struct ams` contains locks, OF/platform device pointers, presence/vendor/orientation fields, interrupt work state, backend callbacks, optional I2C client, input device pointer, bus type, and calibration offsets. It declares the singleton `ams_info` and functions for sensor reading, attach/detach, backend init, and input init/exit.

Control flow and state: The header has no executable control flow but establishes the locking contract: backend function pointers are called with the main mutex held. `irq_lock` protects `worker_irqs`, while `lock` protects sensor and backend operations.

Dependencies and integration: It includes I2C, input, kthread, mutex, platform device, spinlock, and types headers. Conditional I2C fields depend on `CONFIG_SENSORS_AMS_I2C`.

Risks and test signals: Because `ams_info` is a global singleton, the design assumes one sensor per machine. Changes to backend callbacks must preserve the lock-held contract. Compile-test PMU-only and I2C-only configurations to verify conditional fields and prototypes remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams.h -->
