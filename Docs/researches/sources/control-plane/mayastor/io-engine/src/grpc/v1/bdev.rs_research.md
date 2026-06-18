# sources/control-plane/mayastor/io-engine/src/grpc/v1/bdev.rs

Purpose: this v1 service exposes typed bdev list/create/destroy/share/unshare RPCs. Compared with v0 it returns richer protobuf responses, supports optional name filtering in `list`, and returns the resulting `Bdev` after create/share.

Important APIs/types/functions: `impl<T> From<core::Bdev<T>> for Bdev` maps core bdev metadata to protobuf. `BdevService::new/default` constructs the stateless service. `BdevRpc` methods are `list`, `create`, `destroy`, `share`, and `unshare`.

Control flow: all SPDK-affine work is submitted through `rpc_submit`. `list` either returns a named bdev or all bdevs. `create` calls `bdev_create`, then looks up the created bdev by name before returning it. `destroy` delegates to `bdev_destroy`. `share` accepts protobuf `Protocol`, only permits `Nvmf`, applies allowed hosts, and returns a fresh bdev snapshot. `unshare` succeeds for missing bdevs and unshares only if present.

State and persistence: this mutates SPDK bdev state and NVMf shares, but does not write persistence directly. It reflects share URI and claim state from core bdevs.

Dependencies and integration points: integrates `io_engine_api::v1::bdev`, `bdev_api`, `core::{UntypedBdev, Bdev, Share, NvmfShareProps, Protocol}`, `url::Url`, and common gRPC status mapping. Registered by `server.rs` for v1.

Risks: create fails if the bdev cannot be found immediately after creation; `unshare` remains idempotent and may hide absent resources; share rejects all protocols except NVMf; URI conversion failures produce an empty string, which may be ambiguous. Test signals should cover filtered list, create lookup failure, allowed-host update, invalid protocol status, and destroy error mapping.
