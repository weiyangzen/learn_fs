# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_scp.c

## Purpose
This file implements the SCP firmware backend for the vcodec firmware abstraction.

## Important APIs, Types, And Functions
Backend ops map common operations to SCP APIs: `rproc_boot(scp_get_rproc())`, `scp_get_vdec_hw_capa()`, `scp_get_venc_hw_capa()`, `scp_mapping_dm_addr()`, `scp_ipi_register()`, `scp_ipi_send()`, and `scp_put()`. `mtk_vcodec_fw_scp_init()` selects the caller platform device from decoder or encoder private data, obtains the SCP handle with `scp_get()`, allocates `struct mtk_vcodec_fw`, and fills type, ops, and SCP fields.

## Control Flow
Probe calls init after discovering an SCP firmware phandle. Init validates caller use, gets SCP, allocates the backend object, and returns it. Later public wrappers call the SCP ops. Release drops the SCP reference.

## State, Persistence, And Dependencies
State is the SCP handle stored in `fw->scp` plus devm-allocated backend metadata. Dependencies include decoder/encoder private structs, SCP remoteproc helpers, and the common firmware private header.

## Integration Points
Decoder and encoder probes use this backend when device tree exposes `mediatek,scp`. Codec-specific interfaces use common IPI wrappers over SCP.

## Risks
`scp_get()` failure returns `-EPROBE_DEFER`, so probe ordering matters. The backend does not set `fw_use`, unlike VPU init, so code must not depend on it for SCP. Release assumes an SCP handle is present.

## Test Signals
SCP probe defer, firmware boot, capability query, IPI register/send, release on probe error, and decoder/encoder users both selecting SCP.
