# sources/control-plane/mayastor/io-engine/src/grpc/v1/host.rs

Purpose: this v1 service reports host/io-engine identity, supported features/bugfixes, block devices, process resource usage, and NVMe controller information. It is the typed replacement for v0 host/resource/controller methods.

Important APIs/types/functions: `HostService` stores node name, optional NQN, gRPC socket, enabled API versions, and a mutex-protected `GrpcClientContext`. It implements `Serializer` for panic/cancellation logging. Conversion impls map features, bugfixes, block-device structures, resource usage, controller info, controller state, and I/O stats into v1 protobuf types. `HostRpc` methods include `get_mayastor_info`, `list_block_devices`, `get_mayastor_resource_usage`, `list_nvme_controllers`, and `stat_nvme_controller`.

Control flow: information-only calls directly build responses except controller list/stat, which lock through `self.locked` and use `rpc_submit` for reactor-affine controller access. `get_mayastor_info` embeds registration payload including node id, endpoint, instance UUID, API versions, host NQN, features, bugfixes, and version.

State and persistence: no mutations or persistence. It reads registration state, process resource usage, udev/mount data, and controller stats.

Dependencies and integration points: depends on `host::blk_device`, `host::resource`, `controller_grpc`, `Registration`, `MayastorFeatures`, `MayastorBugFixes`, version info, and v1 registration protobufs. It is created by `server.rs` with node/server configuration.

Risks: block-device availability depends on udev and mount table freshness; feature/bugfix reporting can affect control-plane scheduling; controller stat errors are propagated for a single named controller; context storage uses a mutex, serializing controller calls. Test signals should verify registration info fields, API version conversion, block-device conversion including connection/rotational fields, and controller not-found/error behavior.
