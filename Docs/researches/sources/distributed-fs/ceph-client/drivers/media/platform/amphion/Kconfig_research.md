
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/Kconfig

## Purpose

This Kconfig file defines the build option for the NXP Amphion VPU V4L2 mem2mem codec driver. The VPU contains Windsor encoder and Malone decoder blocks and targets NXP i.MX8Q-family hardware for H.264 encode plus H.264/HEVC and other decode workloads.

## Important APIs, Types, And Functions

The file defines a comment group `"Amphion drivers"` and one tristate symbol, `VIDEO_AMPHION_VPU`, prompted as `"Amphion VPU (Video Processing Unit) Codec IP"`. It does not define C functions, but its selected symbols enable the media-controller, V4L2 mem2mem, and VB2 memory infrastructure used by the Amphion source files.

## Control Flow

Kconfig permits the driver when `V4L_MEM2MEM_DRIVERS`, `ARCH_MXC || COMPILE_TEST`, `MEDIA_SUPPORT`, and `VIDEO_DEV && MAILBOX` are satisfied. Enabling it selects `MEDIA_CONTROLLER`, `V4L2_MEM2MEM_DEV`, `VIDEOBUF2_DMA_CONTIG`, and `VIDEOBUF2_VMALLOC`.

## State And Persistence

The only state is the kernel build configuration. Runtime state is implemented in the Amphion C files listed by the Makefile.

## Dependencies And Integration Points

The `MAILBOX` dependency reflects the driver's firmware/control-channel communication. The selected VB2 DMA-contig and VMALLOC allocators match its mixed buffer-management needs. The symbol integrates all Amphion objects into one composite `amphion-vpu` module through the Makefile.

## Risks

The option is broad: one symbol builds encoder, decoder, firmware RPC, mailbox, helper, color, debug, and SoC support code. This simplifies selection but makes it impossible to build only decoder or encoder pieces from Kconfig. Runtime use depends on firmware and platform resources not expressed in this file.

## Test Signals

Run config builds with `CONFIG_VIDEO_AMPHION_VPU=m` and `=y` under i.MX and compile-test configurations. Verify unmet `MAILBOX`, `VIDEO_DEV`, or `V4L_MEM2MEM_DRIVERS` dependencies hide the option. Confirm selected VB2/media symbols appear in the final config.
