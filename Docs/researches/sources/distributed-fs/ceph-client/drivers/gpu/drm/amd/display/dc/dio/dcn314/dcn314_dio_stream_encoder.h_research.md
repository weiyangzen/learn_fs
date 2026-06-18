# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn314/dcn314_dio_stream_encoder.h

## Purpose
This header defines the DCN314 stream encoder register/mask surface and exposes the DCN314 FIFO, DP unblank, HDMI/DVI setup, DSC, and input-mode APIs.

## Important APIs, Types, and Macros
`SE_DCN314_REG_LIST(id)` is DCN30-like but removes `DP_DSC_BYTES_PER_PIXEL`, adds `DIG_FIFO_CTRL0`, and includes DP/HDMI/AFMT/DME register coverage. `SE_COMMON_MASK_SH_LIST_DCN314(mask_sh)` maps DP pixel-per-cycle processing, DP/HDMI packet fields, audio, DSC mode, metadata, `DIG_SYMCLK_FE_ON`, and FIFO output/read/enable/reset/done fields.

The prototypes expose constructor, shared DCN30 packet/audio helpers, `enc314_stream_encoder_dvi_set_stream_attribute`, `enc314_stream_encoder_hdmi_set_stream_attribute`, DP blank/unblank, FIFO reset/enable/disable, input mode, state readback, ODM combine, and DSC config.

## Control Flow and State
No executable flow lives in the header. It declares the hardware contract for the C implementation and for later DCN35 reuse. State is held in DP/DIG/HDMI/AFMT/DME registers.

## Dependencies and Integration Points
It includes VPG, AFMT, generic stream encoder, and DCN20 stream encoder headers. DCN35 includes this header to reuse FIFO, blank, read-state, DSC, and ODM functions.

## Risks and Test Signals
Risk comes from subtle field changes relative to DCN30, especially removed DSC bytes/slice registers and added FIFO control fields. Tests should cover build-time mask generation, FIFO enable/reset, DP unblank, HDMI info/audio packets, DSC mode readback, dynamic metadata, and DCN35 callers that reuse these declarations.
