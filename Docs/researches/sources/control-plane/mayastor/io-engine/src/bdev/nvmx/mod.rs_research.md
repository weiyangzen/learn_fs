## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/mod.rs

### Purpose
`nvmx/mod.rs` is the module root for the Rust-native NVMe/NVMe-oF block-device stack. It re-exports public types, owns the global controller registry, and exposes running NVMe bdev configuration.

### Important APIs, Types, And Functions
`NVMeCtlrList` wraps a `RwLock<HashMap<String, Arc<Mutex<NvmeController>>>>`. It provides `lookup_by_name()`, `remove_by_name()`, `insert_controller()`, and `controllers()`. `NVME_CONTROLLERS` is the process-wide lazy registry. `nvme_bdev_running_config()` returns `Config::get().nvme_bdev_opts`. The module re-exports controller, device, handle, namespace, qpair, snapshot, and URI template types.

### Control Flow
Controllers are inserted first under their NQN-derived name, then after attach under the SPDK pointer-derived controller id. Removal by name removes both the name entry and the id entry by locking the controller to read its id. `controllers()` returns keys containing `nqn`, filtering out numeric id aliases.

### State, Persistence, And Dependencies
Controller registry state is in-memory only. Values are shared `Arc<Mutex<_>>` handles used by device lookup, channel creation, destroy, timeout, and event notification paths. Dependencies include `parking_lot`, `once_cell`, `Config`, and `CoreError`.

### Integration Points
Almost every `nvmx` submodule uses `NVME_CONTROLLERS` to move from URI-created controllers to block devices, I/O channels, timeouts, and destroy. External code imports `lookup_by_name`, `open_by_name`, `NvmeDeviceHandle`, and snapshot message types through this module.

### Risks
Using multiple keys for the same controller means insertion/removal must stay balanced; stale id aliases can keep controllers reachable. `controllers()` filters by substring `"nqn"`, so nonstandard names may be hidden. `remove_by_name()` locks a controller while holding the write lock, which should be checked for deadlock against paths that lock in the opposite order.

### Test Signals
Test insertion by name and id, lookup cloning, removal removing both keys, missing removal error, controller list filtering, duplicate insert overwrites, and lock ordering under concurrent lookup/remove.
