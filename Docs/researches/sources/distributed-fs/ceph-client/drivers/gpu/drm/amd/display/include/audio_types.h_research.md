# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/audio_types.h

Purpose: defines shared AMD display audio data structures used for HDMI/DP audio programming, DTO calculation, and stream/audio capability propagation.

Important APIs and control flow: key types include `audio_dp_link_info` for link bandwidth, encoding, rate, lane count, and MST; `audio_crtc_info` for timing, pixel clock, DSC, color depth/encoding, refresh, repetition, and interlace; `azalia_clock_info` for DTO register values; `audio_dto_source`; `audio_pll_info` for source clock and spread-spectrum data; `audio_channel_associate_info` bitfield mapping eight logical channels; `audio_output` combining engine/signal/video/link/PLL data; and `audio_payload` with channel split mapping change.

State and persistence behavior: no runtime state. These structures are copied between display pipeline, audio, and link code; persistent meaning is in the ABI of field units such as 100 Hz, 10 kHz, kHz, and channel nibbles.

Dependencies and integration points: depends on `signal_types.h`, `fixed31_32.h`, and `dc_dp_types.h`. It integrates with audio packet/DTO programming, DP link configuration, and CRTC timing code.

Risks and test signals: risks include unit confusion across pixel-clock fields, bitfield layout assumptions in `audio_channel_associate_info`, display-name size limits, and keeping DP link encoding/rate enums synchronized. Test signals include audio DTO values matching expected sample clocks, HDMI/DP audio working for deep color/DSC/MST, and channel mapping changes producing correct payloads.
