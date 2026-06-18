# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/mtk_vpu.h

## Purpose
`mtk_vpu.h` is the public MediaTek VPU client API header. It describes the small video processor used by codec, scaler, and media data path blocks and exposes the IPI, firmware, watchdog, capability, and memory-mapping entry points used by other MediaTek media drivers.

## Important APIs, Types, and Functions
`ipi_handler_t` is the interrupt callback signature invoked with message data and caller private state. `enum ipi_id` defines firmware channels for initialization, H.264/VP8/VP9 decode, H.264/VP8 encode, and MDP. `enum rst_id` defines watchdog reset clients for encoder, decoder, and MDP. Exported prototypes include `vpu_ipi_register()`, `vpu_ipi_send()`, `vpu_get_plat_device()`, `vpu_wdt_reg_handler()`, `vpu_get_vdec_hw_capa()`, `vpu_get_venc_hw_capa()`, `vpu_load_firmware()`, and `vpu_mapping_dm_addr()`.

## Control Flow
Clients obtain the VPU platform device, register one IPI handler per channel, load or rely on VPU firmware, and use `vpu_ipi_send()` to synchronously hand requests to firmware. Completion arrives later through the registered handler in interrupt context. Watchdog clients register reset callbacks that the VPU driver invokes when firmware watchdog recovery occurs.

## State and Persistence
This header owns no state directly. Runtime state is held by the VPU implementation: IPI handler tables, watchdog callbacks, firmware boot state, hardware capability masks, and mapped DTCM/DMEM windows. There is no filesystem persistence.

## Dependencies and Integration Points
The API depends on `struct platform_device` and is consumed by MediaTek codec and MDP drivers. It integrates the Linux AP side with VPU firmware through shared memory and interrupts.

## Risks and Edge Cases
Handlers run in interrupt context, so clients must avoid sleeping and must validate message lengths. `vpu_ipi_send()` only succeeds once firmware and the IPI channel are ready. `vpu_mapping_dm_addr()` returns `ERR_PTR(-EINVAL)` on invalid firmware memory addresses, so callers must not treat every non-NULL pointer as usable.

## Test Signals
Useful signals are successful firmware load and `IPI_VPU_INIT`, successful IPI round trips for codec channels, correct watchdog callback invocation, accurate decoder/encoder capability masks, and safe failure for invalid DMEM/DTCM mappings.
