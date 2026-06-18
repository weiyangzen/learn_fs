# sources/distributed-fs/ceph-client/include/video/imx-ipu-v3.h

## Purpose
`imx-ipu-v3.h` is the central public interface for Freescale/NXP i.MX IPU v3 display, capture, DMA, conversion, deinterlace, and pixel-processing blocks. It defines hardware channel numbers, image formats, colorspace data, signal timing, and subsystem operations used by DRM, framebuffer, and V4L2 drivers.

## Important APIs, Types, and Functions
Important types include `struct ipu_soc`, `struct ipu_di_signal_cfg`, `struct ipuv3_channel`, `struct ipu_rgb`, `struct ipu_image`, `struct ipu_ic_colorspace`, `struct ipu_ic_csc_params`, `struct ipu_ic_csc`, and `struct ipu_client_platformdata`. Enums cover IPU variants, CSI destinations, rotation modes, color spaces, motion modes, channel IRQ types, IC tasks, and many fixed IDMAC channel numbers. APIs cover IRQ mapping, common mux/dump helpers, IDMAC get/put/enable/buffer/link operations, CPMEM programming, DC/DI/DMFC/DP/PRG/CSI/IC/VDI/SMFC get/put/configure/enable/disable paths, colorspace conversion calculation, DRM-fourcc and V4L2 pixel-format colorspace mapping, and degrees-to-rotation conversion. Inline helpers include `ipu_rot_mode_is_irt()`, `ipu_channel_alpha_channel()`, and `ipu_ic_fill_colorspace()`.

## Control Flow
Client drivers acquire IPU sub-block handles, configure muxes and timing, program channel parameter memory with image layout and DMA buffers, link flow units where needed, configure display or capture pipelines, enable sub-blocks in dependency order, service EOF/status IRQs, and disable/put resources during teardown. Display paths typically combine DI timing, DC/DMFC/DP setup, IDMAC channels, and optional PRG. Capture/conversion paths combine CSI/SMFC/IC/VDI and IDMAC channels.

## State and Persistence Behavior
State is in opaque IPU objects and hardware registers: channel allocation, buffer-ready bits, CPMEM descriptors, flow links, display timing, colorspace matrices, and active sub-block enables. State lasts while devices and channels are held and is lost or restored through driver power-management paths, not persisted in files.

## Dependencies and Integration Points
The header depends on Linux types, V4L2, DRM color management, framebuffer bitfields, OF nodes, media bus formats, and generic `videomode`. It is a cross-subsystem integration point for DRM/KMS display drivers, V4L2 capture/mem2mem code, device tree platform data, DMA buffer programming, and IPU IRQ handling.

## Risks and Test Signals
Risks include channel-number misuse, incorrect alpha-channel mapping, unsupported rotation sent to non-IRT paths, colorspace/quantization errors, stale double-buffer readiness, incorrect enable/disable ordering, and resource leaks from unmatched get/put calls. Test signals include display modeset, capture streaming, IC conversion with RGB/YUV and limited/full range, deinterlace setup, PRG modifier support, suspend/resume, IRQ mapping, buffer flip timing, and static checks for get/put balance.
