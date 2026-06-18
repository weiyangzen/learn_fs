# sources/control-plane/mayastor/io-engine/src/grpc/v0/bdev_grpc.rs

Purpose: this v0 compatibility service exposes raw SPDK bdev lifecycle and NVMf sharing RPCs. It converts internal `UntypedBdev` objects into v0 protobuf `Bdev` records and forwards create/destroy/share/unshare work to the primary reactor.

Important APIs/types/functions: `impl From<UntypedBdev> for RpcBdev` maps name, UUID, size, block size, claim state, aliases, product, share URI, and parsed URI. `BdevSvc::new/default` constructs the stateless service. The `BdevRpc` implementation provides `list`, `create`, `destroy`, `share`, and `unshare`.

Control flow: `list` iterates `UntypedBdev::bdev_first()` and returns all current bdevs. `create` and `destroy` move a URI into `bdev_create` or `bdev_destroy`. `share` accepts only string protocol `"nvmf"`, looks up the bdev, builds `NvmfShareProps` with allowed hosts, shares it, then re-reads the bdev to return the effective URI. `unshare` is idempotent for missing names.

State and persistence: this file mutates SPDK bdev state and NVMf exports but persists nothing itself. Share state is reflected through core bdev metadata and any lower-level NVMf/PTPL behavior.

Dependencies and integration points: depends on `io_engine_api::v0`, `bdev_api`, `core::{UntypedBdev, Share, NvmfShareProps}`, `url::Url`, and `grpc::rpc_submit`. It is registered only when v0 API support is enabled in `server.rs`.

Risks: protocol validation is string-based and rejects anything except lowercase `"nvmf"`; `create` returns only a name, so clients must call list to inspect details; `unshare` silently succeeds when the bdev is absent; aliases are comma-joined and lose structure. Test signals should cover URI error mapping, NVMf allowed-host propagation, missing bdev share/unshare behavior, and list conversion for claimed/orphaned bdevs.
