<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.c

## Purpose
Implements the Ingenic JZ47xx Image Processing Unit as an atomic DRM overlay plane. The driver accepts RGB and YUV framebuffers, programs IPU DMA addresses, optional color-space conversion, resize coefficient LUTs, and vblank-driven address updates so the IPU output can feed the Ingenic LCD controller.

## Important APIs, types, and functions
Key types are `struct soc_info`, `struct ingenic_ipu_private_state`, and `struct ingenic_ipu`. The atomic plane hooks are `ingenic_ipu_plane_atomic_check()`, `ingenic_ipu_plane_atomic_update()`, and `ingenic_ipu_plane_atomic_disable()`. Scaling helpers include `reduce_fraction()`, `jz4725b_set_coefs()`, `jz4760_set_coefs()`, `ingenic_ipu_set_coefs()`, and the bicubic fixed-point `cubic_conv()`. Component lifecycle is handled by `ingenic_ipu_bind()`, `ingenic_ipu_unbind()`, `ingenic_ipu_probe()`, and `ingenic_ipu_remove()`. `ingenic_ipu_irq_handler()` commits cached buffer addresses and forwards vblank.

## Control flow
Atomic check validates visibility, minimum dimensions, even input/output widths, fixed hardware scaling-table limits, and noncoherent damage tracking. It marks the CRTC mode changed when the IPU is enabled, disabled, resized, repositioned, or has sharpness changed. Atomic update enables the clock, optionally resets and enables the IPU on modeset, syncs noncoherent framebuffer memory, caches plane DMA addresses, and only reprograms full registers on modeset. Full programming writes input strides, input size, format mapping, output RGB888 geometry, YUV-to-RGB CSC coefficients, scaling mode bits, LUT index, horizontal/vertical coefficients, clears status, and starts the frame interrupt. The IRQ acknowledges completion, writes cached Y/U/V addresses for the next frame, restarts older hardware when needed, and calls `drm_crtc_handle_vblank()`.

## State and persistence
Runtime state is mostly in `struct ingenic_ipu`: regmap, clock, SoC data, cached plane DMA addresses, clock-enabled flag, and the mutable `sharpness` property. Atomic scaling numerator/denominator state is held in a DRM private object so LUT programming is tied to the atomic transaction. Hardware state persists in IPU control, DMA, CSC, and resize registers until reset, disable, or next modeset.

## Dependencies and integration points
Depends on the Ingenic DRM master helpers for plane routing, noncoherent mapping, and disable/config operations. It uses DRM atomic plane helpers, GEM DMA framebuffer address helpers, regmap MMIO, platform component binding, one IRQ, and the IPU clock. Compatible strings select JZ4725B or JZ4760 format tables and coefficient algorithms.

## Risks
Scaling is hardware-constrained to 31 LUT entries, and `reduce_fraction()` can reject otherwise valid user modes. The check path permits up to 102 percent internal scaling distortion to find a legal coefficient ratio. Packed YUV422 is disabled on JZ4725B because some resize ratios crash hardware. Clock enable failure during update leaves the plane silently unprogrammed. Address updates are split between atomic update and IRQ, so missed frame interrupts can delay buffer flips.

## Test signals
Useful coverage includes atomic modeset and plane-update tests with RGB, planar YUV, packed YUV on JZ4760, sharpness values 0/1/bicubic, downscale/upscale/integer-upscale ratios, noncoherent framebuffer damage clips, enable/disable transitions, suspend/resume, and vblank delivery. Kernel logs expose scaling ratios, clock errors, and unsupported-format warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.c -->
