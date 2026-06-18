## sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_share.rs

### Purpose
`nexus_share.rs` adapts nexus devices to the generic `Share` API and manages nexus-specific sharing state. It handles NVMf exports with ANA, allowed hosts, controller-id ranges, and PTPL metadata, and preserves legacy NBD sharing for tests that request `Protocol::Off`.

### Important APIs, Types, And Functions
The `Share for Nexus` implementation forwards NVMf share/unshare/property operations to the pinned inner bdev and exposes `shared()`, `share_uri()`, `allowed_hosts()`, and URI accessors. `Nexus::share()`, `share_ext()`, `unshare_nexus()`, `get_share_uri()`, and `ptpl()` manage the higher-level nexus target enum. `NexusPtpl` implements `PtplFileOps` for nexus reservation persistence files under `nexus/<uuid>.json`.

### Control Flow
`share_nvmf()` is idempotent: if unshared it calls the bdev NVMf share path and returns the resulting URI; if already NVMf shared it returns the existing URI. `share_ext()` first checks `nexus_target`; same-protocol requests update allowed hosts and return the current URI, while different protocols fail with `AlreadyShared`. `Protocol::Nvmf` builds `NvmfShareProps` with controller-id range, ANA, allowed hosts, and PTPL props, then records `NexusNvmfTarget`. `Protocol::Off` creates an `NbdDisk` and records that target. `unshare_nexus()` clears the target, destroys NBD if needed, and always asks the bdev to unshare.

### State, Persistence, And Dependencies
Sharing state is split between SPDK bdev share state and the Rust `nexus_target` field. PTPL persistence is file-based through `PtplFileOps`; `destroy()` removes the per-nexus JSON file if it exists. Dependencies include `core::Share`, `NvmfShareProps`, `UpdateProps`, `UnshareProps`, `PtplProps`, `NbdDisk`, and nexus error contexts from `snafu`.

### Integration Points
Control-plane publish/unpublish operations call this layer to expose nexus devices over NVMe-oF. Reservation persistence integrates with the target-share path through `create_ptpl()`. Allowed-host updates allow idempotent republish without unsharing the target.

### Risks
The implementation uses `unsafe` pin projection to mutate `nexus_target`, so structural changes to `Nexus` need care. `get_share_uri().unwrap()` is used after idempotent checks and assumes the underlying bdev state is coherent. Mapping `Protocol::Off` to NBD is legacy behavior and can surprise callers that interpret Off literally. PTPL file deletion errors surface as share failures when creating PTPL props.

### Test Signals
Tests should cover first NVMf share, repeated same-protocol share updating allowed hosts, different-protocol rejection, unshare from NVMf and NBD targets, unshare when `nexus_target` is `None`, PTPL subpath format and removal, `From<&NexusTarget> for Protocol`, and error propagation from bdev share/unshare/update calls.
