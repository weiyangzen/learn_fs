# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_priv.h

## Purpose
This private firmware header defines the concrete firmware object, backend operations table, and conditional backend initializer declarations.

## Important APIs, Types, And Functions
`struct mtk_vcodec_fw` stores backend type, ops table, VPU platform device, SCP handle, and firmware use. `struct mtk_vcodec_fw_ops` defines backend methods for load, capability queries, DM address mapping, IPI register/send, and release. Conditional declarations expose `mtk_vcodec_fw_vpu_init()` and `mtk_vcodec_fw_scp_init()` only when their Kconfig options are enabled; otherwise inline stubs return `ERR_PTR(-ENODEV)`.

## Control Flow
Common selection code creates one of these backend objects. Later public wrapper calls dispatch to the ops table stored in the object.

## State, Persistence, And Dependencies
Backend state is runtime-only. The header depends on `mtk_vcodec_fw.h` and forward-declares decoder/encoder device structs.

## Integration Points
Included by `mtk_vcodec_fw.c`, backend implementations, and decoder driver state. Kconfig/backend Makefile choices control which initializers are real.

## Risks
Backend objects are allocated with devm but release methods also drop references to VPU/SCP devices; misuse can leave stale firmware handles. Stub behavior must match probe error handling.

## Test Signals
Compile matrix for backend enablement, firmware select error paths, and release behavior for both VPU and SCP.
