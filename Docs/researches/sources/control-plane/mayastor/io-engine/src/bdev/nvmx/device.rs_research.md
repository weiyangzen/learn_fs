## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/device.rs

### Purpose
`nvmx/device.rs` exposes a running NVMe controller namespace as the repository's generic `BlockDevice`, `BlockDeviceDescriptor`, and `DeviceIoController` abstractions.

### Important APIs, Types, And Functions
`NvmeBlockDevice` stores namespace, name, and cached geometry. `NvmeDeviceDescriptor` stores namespace, SPDK controller, I/O device id, name, and protection flags. `NvmeBlockDevice::open_by_name()` and free functions `lookup_by_name()`/`open_by_name()` are the lookup APIs. `NvmeDeviceIoController` forwards timeout action operations to the controller.

### Control Flow
Open and lookup paths read `NVME_CONTROLLERS`, require the controller to be `Running`, and create descriptors or block-device views from namespace 1. Descriptors can create synchronous or nonblocking `NvmeDeviceHandle`s. The `BlockDevice` implementation delegates geometry and capabilities to `NvmeNamespace`, gathers I/O stats through controller channel traversal, opens descriptors, returns an I/O controller, and registers event listeners on the controller.

### State, Persistence, And Dependencies
State is runtime-only and mostly references shared namespace/controller state. Cached block count and block size act as fallbacks if namespace queries later return zero. Dependencies include the global controller list, `NvmeDeviceHandle`, `NvmeNamespace`, `BlockDevice` traits, `DeviceEventSink`, and `DeviceTimeoutAction`.

### Integration Points
This file is the bridge from `nvmx` controller internals into generic bdev/device APIs used by nexus, initiator tools, and I/O paths. It also exposes per-device timeout action control to higher layers.

### Risks
Read-only open is logged but not enforced. Namespace absence after a running check uses `expect()` in lookup. The device supports `Reset`, `NvmeAdmin`, `NvmeIo`, and `Abort` based on controller namespace capabilities, but actual implementation sits in `handle.rs`; capability drift between files is possible.

### Test Signals
Cover lookup/open for missing, new, faulted, and running controllers; no-namespace errors; descriptor handle creation; geometry fallback; capability flags for compare/unmap/write-zeroes/metadata; I/O stats callback success/failure; timeout action get/set; and listener registration.
