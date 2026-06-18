# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_windsor.h

Purpose: Declares the Windsor encoder firmware operations consumed by the generic Amphion RPC interface.

Important APIs: The header exports data-size discovery, RPC initialization, log/system config, stream-buffer sizing and manipulation, command packing, message conversion/unpack, memory-resource configuration, encode-parameter programming, frame input, version, and max-instance-count queries.

Control flow and state: No local state is defined here; it describes the callable surface that `vpu_iface_ops` can bind to for Windsor-capable encoder cores. The implementation stores state in `struct vpu_shared_addr`, RPC DMA memory, and private host control structures.

Dependencies and integration: Requires Amphion shared types such as `vpu_shared_addr`, `vpu_buffer`, `vpu_rpc_event`, `vpu_rpc_buffer_desc`, `vpu_encode_params`, `vpu_inst`, and vb2 buffers from including units. It integrates `vpu_windsor.c` with core interface tables.

Risks: Prototype drift from `vpu_iface_ops` would be compile-detected, but semantic mismatches such as instance bounds and address units require runtime tests.

Test signals: Build coverage and end-to-end encoder startup using the Windsor interface table.
