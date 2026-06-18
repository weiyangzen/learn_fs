# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw.c

## Purpose
This file provides the common firmware abstraction dispatcher for MediaTek vcodec. It selects a VPU or SCP backend and forwards operations through a backend ops table.

## Important APIs, Types, And Functions
`mtk_vcodec_fw_select()` chooses `mtk_vcodec_fw_vpu_init()` or `mtk_vcodec_fw_scp_init()` based on `enum mtk_vcodec_fw_type` and whether the caller is an encoder or decoder. The exported wrappers `mtk_vcodec_fw_release()`, `mtk_vcodec_fw_load_firmware()`, capability getters, `mtk_vcodec_fw_map_dm_addr()`, `mtk_vcodec_fw_ipi_register()`, `mtk_vcodec_fw_ipi_send()`, and `mtk_vcodec_fw_get_type()` call the selected backend.

## Control Flow
Probe code selects firmware once, stores the returned `struct mtk_vcodec_fw`, then all later operations are virtual dispatch through `fw->ops`.

## State, Persistence, And Dependencies
State is the backend object allocated by SCP or VPU init. No persistence. Dependencies include decoder/encoder device structs and `mtk_vcodec_fw_priv.h`.

## Integration Points
Decoder probe uses selection, load, capability, and release. Codec interfaces use IPI registration/send and DM address mapping. Encoder code uses the same abstraction.

## Risks
The wrappers assume `fw` and `fw->ops` are valid. Invalid firmware type returns an error pointer after logging through the caller platform device. Backend stubs under disabled Kconfig return `-ENODEV`.

## Test Signals
Probe with VPU and SCP device-tree properties, disabled backend builds, invalid type handling, firmware release on probe errors, and IPI send/register smoke tests.
