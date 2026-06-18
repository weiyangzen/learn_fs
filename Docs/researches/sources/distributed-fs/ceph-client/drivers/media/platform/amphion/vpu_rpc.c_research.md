<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_rpc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_rpc.c

Purpose: provides common RPC ring-buffer send/receive helpers and selects the firmware iface operation table for i.MX8Q encoder/decoder cores.

Important APIs/functions: `vpu_iface_check_memory_region()`, `vpu_core_get_iface()`, and `vpu_inst_get_iface()` are exported. Internal `vpu_rpc_send_cmd_buf()` writes command packets into the shared command ring; `vpu_rpc_receive_msg_buf()` reads firmware messages from the shared message ring; `vpu_rpc_check_buffer_space()` handles ring free/used calculations. `imx8q_rpc_ops` binds encoder cores to Windsor ops and decoder cores to Malone ops.

Control flow: command code packs a `vpu_rpc_event`, calls the selected iface send function, then mailbox-signals firmware. Message work calls receive repeatedly until no full message is available. Core/instance code uses `vpu_core_get_iface()` or `vpu_inst_get_iface()` to dispatch all firmware-specific behavior.

State and persistence: no private persistent state beyond the static iface table. Ring state lives in shared RPC memory descriptors owned by firmware and initialized by Windsor/Malone init code.

Dependencies and integration: includes i.MX8Q platform ops, Windsor encoder ABI, and Malone decoder ABI. It is the dispatch bridge between generic VPU code and firmware-specific implementations.

Risks: `imx8q_rpc_ops` is indexed by enum values where decoder is `0x10`, so the array is sparse and `ARRAY_SIZE` must remain large enough. `vpu_rpc_check_msg()` compares message payload word count to available words without adding the header word, which matches existing logic only if firmware semantics align. Ring helpers assume descriptors and memory pointers are valid and not concurrently corrupted by firmware.

Test signals: command/message ring wraparound, full/empty ring boundaries, sparse decoder iface lookup, platform type selection, encoder and decoder boot through selected ops, malformed packet `hdr.num`, and concurrent firmware message production while the driver drains messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_rpc.c -->
