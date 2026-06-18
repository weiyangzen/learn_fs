<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen3.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen3.c

## Purpose
Implements the VFE hardware ops for newer CAMSS Gen3-style IFE/VFE blocks used by platforms such as SM8550, SM8650, QCS8300, and SA8775P. It programs RDI write-master bus registers and delegates generic queueing to the shared VFE v2 helpers.

## Important APIs, Types, And Functions
- Exports `const struct vfe_hw_ops vfe_ops_gen3`.
- Implements `vfe_wm_start()`, `vfe_wm_stop()`, `vfe_wm_update()`, `vfe_reg_update()`, `vfe_reg_update_clear()`, `vfe_subdev_init()`, `vfe_global_reset()`, `vfe_isr()`, and `vfe_halt()`.
- Uses SoC-version and lite/full VFE macros to choose BUS register bases and RDI write-master indices.

## Control Flow
On VFE subdevice init, the file installs Gen3 video ops that call `vfe_queue_buffer_v2()` and `vfe_flush_buffers()`. Stream enable from common code reserves a logical WM, then `vfe_wm_start()` maps it to the correct hardware RDI client, sets bus clock-gating override, frame increment, image config defaults, optional top-core downscaling disable for VFE 690 platforms, frame-drop/subsample settings, MMU prefetch, and WM enable. Buffer updates write the image address, with address shifting for non-690 hardware. Register updates are routed to the CSID wrapper via `camss_reg_update()`.

## State And Persistence
No persistent state is stored. The file writes MMIO registers through `vfe->base` and relies on common `vfe_output` state for active buffers and stream counts. Gen3 reset and ISR handling are minimal: global reset completes immediately through `vfe_isr_reset_ack()`, the ISR is a no-op, and halt relies on common output disable.

## Dependencies And Integration Points
Depends on Linux MMIO helpers, the common CAMSS VFE v2 helpers, CSID register-update integration, and SoC resource version/lite metadata from `camss.c`. The actual buffers come from `camss-video.c` and are advanced by `vfe_buf_done()` callbacks.

## Risks And Edge Cases
Register offsets and RDI mappings differ between VFE 690 and 780 families and between lite/full blocks; incorrect version metadata will program wrong clients. The no-op ISR means completion must come through CSID/buffer-done paths, so missing external interrupt routing can silently stall. Address shifting for non-690 hardware assumes the hardware expects 256-byte granularity.

## Test Signals
Expected signals are successful RDI capture on full and lite Gen3 VFEs, correct address programming in debug logs, no buffer starvation under `vfe_queue_buffer_v2()`, and correct operation on both VFE 690 and 780 register-layout families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen3.c -->
