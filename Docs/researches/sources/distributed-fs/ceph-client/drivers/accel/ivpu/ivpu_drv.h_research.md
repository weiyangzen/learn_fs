## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_drv.h

### Purpose
`ivpu_drv.h` defines the central ivpu driver constants, debug macros, workaround table, device/file-private structures, module parameters, test-mode bits, lifecycle prototypes, and hardware-generation helpers.

### Important APIs, Types, And Functions
It defines PCI device IDs, hardware IP and buttress generations, SSID/doorbell/cmdq/job ID limits, platform IDs, debug masks, logging macros, `struct ivpu_wa_table`, `struct ivpu_user_limits`, `struct ivpu_device`, and `struct ivpu_file_priv`. Inline helpers include `ivpu_revision()`, `ivpu_device_id()`, `ivpu_hw_ip_gen()`, `ivpu_hw_btrs_gen()`, `to_ivpu_device()`, context/doorbell count helpers, platform predicates, and `ivpu_is_force_snoop_enabled()`.

### Control Flow
The inline generation helpers branch on PCI device ID to select hardware IP and buttress implementations. Platform helpers validate `vdev->platform` and classify silicon, Simics, FPGA, or HSLE.

### State, Persistence, And Dependencies
This header defines the in-memory state layout for the full driver. `ivpu_device` persists from probe to remove and owns BAR pointers, IRQ, subsystem pointers, MMU contexts, xarrays, work items, BO/job lists, counters, and timeouts. `ivpu_file_priv` persists per open DRM file and owns context, cmd queues, metric streamer state, limits, and abort/fault flags. Dependencies include DRM, PCI, xarray, hash table, MMU context, IPC, and ivpu UAPI headers.

### Integration Points
Nearly every ivpu source file includes this header. It is the contract between the PCI/DRM front end and firmware, MMU, IPC, PM, job, GEM, debugfs, and hardware layers.

### Risks
Structure layout and lock comments document ownership boundaries; violating them risks races in context/BO/job lists. Unknown PCI IDs return generation zero after logging/dump_stack, which downstream code must not treat as valid. Debug/test module parameters can change hardware behavior and should remain configuration-gated.

### Test Signals
Compile coverage across all source files, generation mapping tests for every PCI ID, lockdep on context/user-limit/BO/job locks, open/close stress, forced-snoop behavior, and platform predicate coverage after hardware platform init.
