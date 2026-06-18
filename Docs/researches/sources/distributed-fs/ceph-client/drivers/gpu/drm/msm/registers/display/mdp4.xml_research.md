# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp4.xml

## Purpose
This XML describes the MSM MDP4 display controller register map. It covers overlay mixers, DMA engines, pipes, CSC tables, layer-mixer routing, interrupts, interface selection, LCDC/DTV timing, LVDS control, cursor state, scaling, format packing, flush/kick registers, and gamma/LUT state.

## Important APIs, Types, and Functions
Generated APIs include `REG_MDP4_*` address macros, array helpers for overlay, DMA, pipe, CSC, LUT, LCDC, and DTV blocks, plus bitfield packers for formats, polarity, active/display timing, layer routing, and IRQ masks. Important enums and bitsets include `mdp4_pipe`, `mdp4_mixer`, `mdp4_intf`, `mdp4_cursor_format`, `mdp4_frame_format`, `mdp4_scale_unit`, `mdp4_dma`, `mdp4_layermixer_in_cfg`, `MDP4_IRQ`, `mdp4_ctrl_polarity`, `mdp4_active_hctl`, and display timing bitsets. It imports shared display types from `display/mdp_common.xml`.

## Control Flow
MDP4 KMS code programs source pipes with framebuffer base/stride/format/unpack/scaling/CSC state, routes pipes into mixer stages, programs overlay or DMA output state, flushes changed blocks with `OVERLAY_FLUSH`, then kicks overlay/DMA blocks to latch the update. Encoder paths program LCDC, DTV, LVDS, DSI-video, or DSI-command interface selection and timing registers. IRQ flow uses `INTR_ENABLE`, `INTR_STATUS`, and `INTR_CLEAR` for vblank, overlay done, DMA done, histogram, read-pointer, and underrun events.

## State and Persistence Behavior
Runtime state includes pipe source addresses, strides, formats, scaling phase steps, CSC matrices, mixer-stage routing, alpha/transparency, cursor image/position/blend state, DMA/LUT state, interface timings, LVDS mux/PHY settings, interrupt masks, and pending flush bits. This state is hardware-resident and is reconstructed by atomic modeset/plane update paths after reset, suspend, or display pipeline disable.

## Dependencies and Integration Points
The map is consumed by `disp/mdp4` KMS, plane, CRTCs, IRQ, LCDC/DTV/LVDS encoders, DSI integration, HDMI/DTV output, DRM atomic plane state, framebuffer format handling, and shared MDP helpers. It depends on `mdp_common.xml` for shared pixel-format, bpc, alpha, chroma, unpack, and width/height coordinate types.

## Risks
Layer mixer routing packs many pipes into one register, so stage and mixer-bit mistakes can show the wrong plane or blank output. Format/unpack/fetch-plane fields are sensitive to DRM format and modifier interpretation. Flush/kick ordering controls when register writes latch; missing flushes look like stale frames. IRQ clear/enable mistakes cause lost vblank or underrun storms. Some comments document guessed legacy interface mappings, so changes around DSI/LCDC/DTV selection require hardware verification.

## Test Signals
Useful tests include generated-header build, plane update and format tests, cursor movement/blending, scaling and CSC validation, vblank/overlay-done IRQs, underrun logging, LCDC/DTV/DSI output modes, LVDS mux cases, suspend/resume restore, and atomic modeset stress with multiple pipes and mixers.
