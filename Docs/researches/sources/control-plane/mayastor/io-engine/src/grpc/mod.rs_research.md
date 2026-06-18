# sources/control-plane/mayastor/io-engine/src/grpc/mod.rs

Purpose: this module is the common gRPC support layer for the io-engine. It publishes `MayastorGrpcServer`, declares the v0/v1 service modules, maps common internal errors to `tonic::Status`, defines the standard `GrpcResult<T>`, and provides reactor submission and request serialization primitives used by almost every gRPC service.

Important APIs/types/functions: `GrpcClientContext` captures method id, debug args, and timeout from `grpc-timeout`; `Serializer`, `RWSerializer`, and `RWLock` standardize service locking; `spdk_submit!` wraps `rpc_submit_ext2` and converts reactor results into `tonic::Response`; `rpc_submit`, `rpc_submit_ext`, and `rpc_submit_ext2` schedule futures on the primary SPDK reactor; `acquire_subsystem_lock` bridges gRPC operations to `ResourceSubsystem` locks; `endpoint_from_str`, `node_name`, `get_request_timeout`, and `lvm_enabled` provide service setup helpers.

Control flow: service handlers generally build `GrpcClientContext`, lock through the service trait, submit SPDK work with `rpc_submit`/`spdk_submit!`, await the oneshot receiver, map cancellation to `Status::cancelled`, and map domain errors via `From` impls. Timeout parsing follows gRPC timeout units and falls back to `DEFAULT_GRPC_TIMEOUT_SEC`.

State and persistence: the module does not persist business data. It controls in-memory operation context and lock acquisition, and it may expose stale timed-out context warnings when a previous cancelled top-level future left a marker behind.

Dependencies and integration points: depends on `tonic`, `tokio`, `futures::oneshot`, `nix::Errno`, `Reactor`, `ResourceSubsystem`, `MayastorFeatures`, and domain errors from bdev/core. It is the integration point between generated protobuf services and SPDK reactor-affine code.

Risks: incorrect error mapping can change control-plane retry behavior; `endpoint_from_str` panics on invalid endpoints; malformed or overflowing timeout values silently fall back or may multiply seconds without explicit saturation; all reactor submissions report spawn failure as resource exhaustion. Test signals should cover timeout parsing, status mapping, lock contention, LVM feature gating, and cancellation of submitted futures.
