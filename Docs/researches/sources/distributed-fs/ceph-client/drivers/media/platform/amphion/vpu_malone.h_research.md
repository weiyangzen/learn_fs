<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_malone.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_malone.h

Purpose: declares the Malone decoder iface contract consumed by generic RPC dispatch and decoder code.

Important APIs: declarations cover RPC layout/init, log/system config, version, stream-buffer sizing and pointer updates, decode parameter setting, command packing, message conversion/unpacking, start-code insertion, input-frame submission, command readiness, instance initialization, max-instance count, format support, and runtime format enablement.

Control/state behavior: no state in the header; functions operate on `struct vpu_shared_addr`, instance IDs, `struct vpu_buffer`, `struct vpu_inst`, and firmware event packets.

Dependencies and integration: paired with `vpu_malone.c` and plugged into decoder entries of `imx8q_rpc_ops` in `vpu_rpc.c`.

Risks and test signals: ABI mismatch between this header and `vpu_rpc.c` iface table is the main risk. Build tests and decoder boot/start/input/message tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_malone.h -->
