## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/uri.rs

### Purpose
`nvmx/uri.rs` converts NVMe-oF URLs into Rust-native NVMe controller instances. It owns async SPDK connect/probe setup, host NQN/host ID option construction, initial controller registry insertion, and cleanup on attach failure.

### Important APIs, Types, And Functions
`NvmfDeviceTemplate` stores name, alias, host, port, subsystem NQN, protection flags, optional UUID, and optional host NQN. `NvmeControllerContext` owns controller opts, transport ID, attach completion channel, poller, and attached flag. `connect_attach_cb()` handles SPDK attach completion. The `CreateDestroy` implementation performs create and destroy. `TryFrom<&Url>` parses the URI.

### Control Flow
Parsing requires a host and one path segment, accepts `reftag`, `guard`, `uuid`, and `hostnqn`, strips IPv6 brackets, and defaults port to 8420. `create()` rejects existing controller names, inserts a new uninitialized controller as a guard, builds connect context and transport options, calls `spdk_nvme_connect_async()`, installs the boxed context as callback context, starts a poller that drives `spdk_nvme_probe_poll_async()`, and awaits the attach result. Attach callback unregisters the poller, marks attached, and delegates successful controller setup to `connected_attached_cb()`. On attach error, `create()` destroys the partially initialized controller and returns the original create failure. `destroy()` delegates to `controller::destroy_device()`.

### State, Persistence, And Dependencies
State is runtime controller registry state plus an attach context temporarily owned through a raw pointer. Host identity is derived from explicit `hostnqn`, `MayastorEnvironment`, or `MAYASTOR_NVMF_HOSTID`. Dependencies include SPDK async connect/probe APIs, `controller` option and transport builders, global config, URI helpers, `NVME_CONTROLLERS`, and `BdevError`.

### Integration Points
This is the URI entry point for the newer `nvmx` stack. It creates controllers later discovered by `device.rs` and opened by generic device APIs. Host identity choices affect NVMe-oF target-side connection tracking and reservation/PTPL behavior.

### Risks
Unlike older URI adapters, this parser does not call `reject_unknown_parameters()`, so unexpected query parameters are silently ignored after known removals. `uuid` and `alias` are stored but not visibly enforced or added in this path. Raw attach context/poller management must unregister exactly once. On failure, cleanup calls full controller destroy while the controller may still be in `New`.

### Test Signals
Cover URI validation, IPv6 bracket stripping, default port 8420, protection flag parsing, hostnqn and hostid option selection, unknown query handling, duplicate create guard, async connect null failure cleanup, poller failure path invoking callback, namespace attach failure cleanup, successful running-state assertion, and destroy behavior.
