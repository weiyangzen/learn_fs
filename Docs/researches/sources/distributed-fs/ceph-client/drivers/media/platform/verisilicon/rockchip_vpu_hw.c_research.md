# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu_hw.c

## Purpose
Declares Rockchip Hantro VPU variants and their supported formats, codec-operation tables, IRQ handlers, reset hooks, clock setup, and postprocessor capabilities. It is the integration layer between Rockchip SoC compatibles and generic Hantro core logic.

## Important APIs, Types, And Functions
- Exports `rk3036_vpu_variant`, `rk3066_vpu_variant`, `rk3288_vpu_variant`, `rk3328_vpu_variant`, `rk3399_vpu_variant`, `rk3568_vepu_variant`, `rk3568_vpu_variant`, `px30_vpu_variant`, and `rk3588_vpu981_variant`.
- Defines Rockchip encoder/decoder/postproc format tables, codec-op arrays for G1/H1/VDPU2/VEPU2/VPU981, IRQ handlers for VEPU/VDPU/VPU981, and reset helpers.
- Hardware init functions raise selected ACLKs to expected performance rates.

## Control Flow
During probe, the Hantro core selects one exported `struct hantro_variant`. The variant controls which formats appear to userspace, which clocks/IRQs are requested, which codec run/reset/init/exit/done hooks execute, and which postprocessor ops are available. IRQ handlers read hardware status, classify the vb2 result as done or error, clear interrupt/AXI state, and call `hantro_irq_done()`.

## State And Persistence
The file owns static const variant data only. Runtime state is in `struct hantro_dev` and `struct hantro_ctx`. Clock rate changes persist while the device is active, but no durable storage is used.

## Dependencies And Integration Points
Depends on Linux clocks, Hantro core structures, G1/H1/VPU2/VPU981 register headers, and codec-specific run functions. Device-tree compatible tables elsewhere point at these exported variants.

## Risks And Edge Cases
Format limits and codec masks decide userspace-visible ABI for each SoC. The RK3399 variant intentionally disables H.264 decode despite having ops to steer userspace to a better VDEC core. IRQ handlers use simple status-bit checks, so incomplete error decoding can hide timeout/bus/fuse causes. Clock index assumptions must match `clk_names`.

## Test Signals
Probe each compatible, verify advertised V4L2 formats and frame-size bounds, run JPEG/H.264/MPEG-2/VP8/AV1 where enabled, force error IRQs, test reset during streamoff, and confirm clock names/rates match device tree.
