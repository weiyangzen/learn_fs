# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_mdp_rdma.c

## Purpose
Implements a MediaTek MDP RDMA display component that reads framebuffer memory into the display pipeline. It exposes format support, CMDQ-backed configuration, start/stop, clock/runtime PM helpers, and component registration.

## Important APIs, types, and functions
- `struct mtk_mdp_rdma` stores MMIO, clock, and optional CMDQ client register base.
- `mtk_mdp_rdma_config()` programs source format, address, pitch, crop offset, size, clip, FIFO/ultra settings, compression disable, output mode, and YUV-to-RGB CSC.
- `mtk_mdp_rdma_start()` / `mtk_mdp_rdma_stop()` toggle enable and reset.
- `mtk_mdp_rdma_get_formats()` and `mtk_mdp_rdma_get_num_formats()` expose supported DRM formats.
- Power/clock helpers wrap PM runtime and clock APIs.

## Control flow
Probe maps MMIO, gets the clock, optionally gets CMDQ register metadata, enables runtime PM, and adds a component. Configuration converts DRM fourcc into hardware input format plus swap/10-bit flags, enables uniform config, sets ARGB output when appropriate, writes base address and pitch, disables AFBC/UFBDC, enables 10-bit/simple output fields, selects CSC matrix for YUV formats, calculates byte offset from crop x/y, and writes source/clip dimensions. Start sets enable; stop clears enable and pulses reset.

## State and persistence
Driver state is resource-oriented: registers, clock, CMDQ metadata. Frame-specific state comes from `struct mtk_mdp_rdma_cfg` and is written into hardware registers via `mtk_ddp_write*()` with optional CMDQ packet persistence until command execution.

## Dependencies and integration points
Depends on DRM format info, MediaTek DDP/CMDQ helpers, component framework, platform clocks/MMIO, PM runtime, and the config struct declared in `mtk_mdp_rdma.h`. It integrates with MediaTek CRTC/overlay-adaptor paths that need an RDMA memory source.

## Risks
`drm_format_info(cfg->fmt)` is assumed non-NULL. The exported `formats[]` list omits some formats that `rdma_fmt_convert()` can handle, which may be intentional for caller policy but should be understood before expanding. Address is `unsigned int` in the config header, so DMA addresses above 32 bits need scrutiny. CSC selection only distinguishes BT.709 and BT.601.

## Test signals
Signals include component probe/runtime PM, correct scanout for each advertised format, YUV CSC output, crop offsets, 10-bit formats if enabled by callers, RDMA reset on stop, CMDQ versus direct write behavior, and underflow/ultra FIFO behavior under memory pressure.
