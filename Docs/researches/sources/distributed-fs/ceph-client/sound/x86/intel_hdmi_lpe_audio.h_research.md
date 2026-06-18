# sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_lpe_audio.h

## Purpose
Defines Intel HDMI/DP LPE audio hardware constants, register offsets, register bitfields, buffer limits, audio sample-rate constants, and HDMI/DP InfoFrame/clocking values.

## Important APIs, Types, And Functions
- PCM constraints include channel, buffer, period, FIFO, and rate limits.
- `enum hdmi_ctrl_reg_offset_common` and `enum hdmi_ctrl_reg_offset` define MMIO layout.
- Unions such as `aud_cfg`, `aud_ch_status_0`, `aud_ch_status_1`, `aud_hdmi_cts`, `aud_hdmi_n_enable`, `aud_buf_addr`, `aud_buf_len`, `aud_ctrl_st`, and `aud_info_frame*` define register-level bit layout.
- Constants define DP link rates, DP MAUD/NAUD values, HDMI N values, DIP words, IRQ status bits, and buffer descriptor flags.

## Control Flow
No executable flow. `intel_hdmi_audio.c` uses these definitions to program channel status, N/CTS or MAUD/NAUD, DIP packets, FIFO thresholds, buffer descriptors, and interrupt acknowledgments.

## State And Persistence
The header defines register value layout rather than storing state. `union aud_cfg` is cached in `snd_intelhad` to work around hardware read/modify/write behavior.

## Dependencies And Integration Points
Integrates directly with MMIO programming in the Intel LPE driver and with the hardware programming model for HDMI/DP audio on supported Atom platforms.

## Risks
Incorrect bitfield layout or constants directly misprogram hardware. Fixed DP link-rate tables mean unsupported link rates must be rejected or extended. Buffer constants enforce 20-bit aligned addresses and 64-byte period alignment assumptions.

## Test Signals
Playback at every advertised rate on HDMI and DP, IRQ status clearing, one-period buffer behavior, four-BD wraparound, and register tracing around prepare/trigger paths validate the constants.
