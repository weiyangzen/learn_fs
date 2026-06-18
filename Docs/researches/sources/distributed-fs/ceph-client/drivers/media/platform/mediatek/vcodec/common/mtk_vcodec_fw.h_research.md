# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw.h

## Purpose
This public firmware header exposes the vcodec firmware abstraction to decoder and encoder code without revealing backend internals.

## Important APIs, Types, And Functions
`enum mtk_vcodec_fw_type` selects VPU or SCP. `enum mtk_vcodec_fw_use` distinguishes decoder and encoder users. `mtk_vcodec_ipi_handler` defines the common callback signature. The declared API covers firmware selection/release, firmware load, decode/encode capability queries, data-memory mapping, IPI registration, IPI send, and backend type retrieval.

## Control Flow
Caller probe selects a backend, loads firmware on first use, registers IPI handlers, and sends messages through this API. The implementation dispatches to backend ops.

## State, Persistence, And Dependencies
The header forward-declares device structs and the opaque `struct mtk_vcodec_fw`. It depends on remoteproc/SCP and legacy VPU headers for type availability.

## Integration Points
Used by decoder/encoder probe and codec-specific VPU interfaces. `mtk_vcodec_fw_priv.h` extends it for backend implementers.

## Risks
The common IPI handler signature must remain compatible with both SCP and VPU APIs. Exposing backend type allows callers to branch and can leak abstraction details.

## Test Signals
Builds across backend configurations, IPI handler registration for decoder and encoder, and capability queries after firmware load.
