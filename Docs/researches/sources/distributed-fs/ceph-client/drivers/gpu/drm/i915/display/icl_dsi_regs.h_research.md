# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi_regs.h

## Purpose

`icl_dsi_regs.h` defines Gen11+ Intel DSI, D-PHY, command, interrupt, timing, transcoder, low-power message, and timeout register addresses and bitfields. It is the register contract used by `icl_dsi.c` when programming MIPI DSI ports and transcoders.

## Important APIs, Types, And Macros

Important address helpers include `_MMIO_DSI()`, `ICL_DSI_ESC_CLK_DIV(port)`, `ICL_DPHY_ESC_CLK_DIV(port)`, `ADL_MIPIO_DW(port, dw)`, `DSI_CMD_FRMCTL(port)`, `DSI_INTR_MASK_REG(port)`, `DSI_INTR_IDENT_REG(port)`, `ICL_DSI_IO_MODECTL(port)`, `TGL_DSI_CHKN_REG(port)`, `ICL_DSI_T_INIT_MASTER(port)`, `DPHY_*_TIMING_PARAM(port)`, `DSI_*_TIMING_PARAM(port)`, `DSI_TRANS_FUNC_CONF(tc)`, `DSI_CMD_RXCTL(tc)`, `DSI_CMD_TXCTL(tc)`, `DSI_CMD_TXHDR(tc)`, `DSI_CMD_TXPYLD(tc)`, `DSI_LP_MSG(tc)`, and timeout registers `DSI_HSTX_TO()`, `DSI_LPRX_HOST_TO()`, `DSI_PWAIT_TO()`, and `DSI_TA_TO()`.

Key fields include escape clock divisors, frame update request/periodic/null-packet bits, DSI interrupt status bits, Combo PHY DSI mode, LP-to-HS guardband, D-PHY clock/data/turnaround timing overrides, transcoder operation mode, TE source, link ready, pixel format, BGR transmission, virtual channel, continuous clock, low-power clock during LPM, calibration, blanking packet enable, command TX/RX credit fields, packet header flags, ULPS/LPTX bits, and timeout values.

## Control Flow

The header has no runtime control flow. It supplies packed field encoders and masks for the DSI implementation to program based on VBT data, atomic CRTC state, panel mode, command/video mode, DSC use, and platform generation.

## State And Persistence Behavior

No software state is stored here. The named hardware registers persist DSI clocking, protocol mode, packet queues, link state, ULPS state, timing, timeout, and interrupt status. Some registers are port-indexed and others are DSI-transcoder-indexed, so correct conversion between port and transcoder is required by consumers.

## Dependencies And Integration Points

The header depends on `intel_display_reg_defs.h` for MMIO and bitfield helpers. It is paired with `icl_dsi.c` and also aligns with Combo PHY/DDI/DSS register programming in other headers. Platform-specific fields such as ADL MIPIO and TGL chicken registers support generation-specific workarounds in the DSI implementation.

## Risks And Edge Cases

Field misuse can wedge DSI links: packet credit shifts, payload/header masks, ULPS bits, TE mode, and timeout fields have side effects. Some pixel-format constants exceed the documented two-bit `PIX_FMT_MASK` shape, so consumer assumptions must follow the actual hardware definition. Address helpers mix port and transcoder domains, and accidental use of `PORT_B` where `TRANSCODER_DSI_1` is required would target the wrong register.

## Test Signals

Register trace comparison during DSI enable, command transfer credit tests, command-mode frame update, video-mode timing programming, DSC compressed-pixel format, ULPS entry, ADL/TGL platform branches, interrupt status decoding, and static checks against the hardware specification are useful validation signals.
