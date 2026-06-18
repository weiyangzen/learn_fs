# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_vpu.c

## Purpose
This file implements the legacy VPU firmware backend for the vcodec firmware abstraction and registers watchdog reset handlers.

## Important APIs, Types, And Functions
Backend ops map to VPU APIs: `vpu_load_firmware()`, capability getters, `vpu_mapping_dm_addr()`, `vpu_ipi_register()`, `vpu_ipi_send()`, and `put_device()`. `mtk_vcodec_fw_vpu_init()` obtains the VPU platform device, registers decoder or encoder watchdog handlers, allocates the backend object, and stores the firmware use. Reset handlers mark every active decoder or encoder context `MTK_STATE_ABORT` under the device context spinlock.

## Control Flow
Probe selects the VPU backend when device tree exposes `mediatek,vpu`. Init finds the VPU device, registers a reset callback for the appropriate reset ID, creates the backend, and returns it. Runtime wrappers dispatch firmware operations. Watchdog callbacks asynchronously abort all contexts after a firmware timeout.

## State, Persistence, And Dependencies
State is the referenced VPU platform device and firmware use stored in `struct mtk_vcodec_fw`. It depends on legacy VPU APIs, decoder/encoder device lists, spinlocks, and common firmware private definitions.

## Integration Points
Used on MT8173-style platforms and other VPU-backed configurations. The reset path integrates with V4L2 instance state by preventing further buffer queue/dequeue after abort.

## Risks
Watchdog handlers iterate all contexts and must hold the right lock. Encoder reset logs with the decoder debug macro name, which is harmless but confusing. `vpu_ipi_send()` ignores the common `wait` argument. Missing VPU device returns `-EINVAL`, not probe defer.

## Test Signals
VPU probe readiness, firmware load, IPI send/register, watchdog timeout forcing `MTK_STATE_ABORT`, and open/close after reset.
