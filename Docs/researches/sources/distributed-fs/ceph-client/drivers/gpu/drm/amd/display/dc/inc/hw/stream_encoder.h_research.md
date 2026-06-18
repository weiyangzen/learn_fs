# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/stream_encoder.h

## Purpose

`stream_encoder.h` defines the stream encoder abstraction that converts DC stream timing and pixel data into protocol-specific stream attributes for DP, HDMI, DVI, LVDS, and HPO DP. It also handles audio packet setup, info packets, blank/unblank, DSC PPS packets, ODM combine, FIFO control, and stream-to-link mapping.

## Important APIs, Types, And Functions

The header defines DP pixel encoding and component depth enums, audio clock info, stream encoder state, DP PHY pattern state, and `struct stream_encoder`. `stream_encoder_funcs` includes DP/HDMI/DVI/LVDS attribute setup, throttled VCP sizing, HDMI and DP info packet updates/stops, immediate SDP, DP blank/unblank, audio mute/setup/enable/disable, stereo sync, AV mute, DIG-to-OTG connection, stream enable, reset/readback, DSC config and PPS packet programming, dynamic metadata, ODM combine, FIFO level/control, stream-to-link mapping, and pixels-per-cycle queries.

HPO DP support is represented by `struct hpo_dp_stream_encoder`, `hpo_dp_stream_encoder_state`, and `hpo_dp_stream_encoder_funcs`, with DP2 stream enable/blank/disable, attributes, SDP/info packets, DSC PPS, stream-link mapping, audio, state readout, and hblank minimum symbol width.

## Control Flow

During enablement, stream setup programs attributes from `dc_crtc_timing`, maps the stream encoder to OTG/link encoder, emits protocol info packets, configures DSC when used, sets up audio, and unblanks. Disable paths blank the stream, stop packets/audio, and may disable FIFO or reset attributes.

## State And Persistence Behavior

The software object stores identity and vtable; protocol state persists in stream encoder registers and packet RAM. HPO stream state readback exposes enabled state, mapping, MSA timing, ODM, and DSC status.

## Dependencies And Integration Points

The file depends on audio types and `hw_shared.h`. It integrates with link encoders, `link_hwss` sequencing, timing generators, audio resources, DSC code, MST bandwidth allocation, HDR/dynamic metadata, and DP/HDMI compliance tests.

## Risks And Test Signals

Risks include packet programming races, wrong pixel encoding/depth, audio N/CTS errors, stale DSC PPS packets, bad stream-link mapping during transient link encoder assignment, and FIFO under/overflow. Test signals include DP/HDMI bring-up, audio playback, HDR metadata, DSC displays, MST streams, DP2/HPO modes, blank/unblank transitions, and protocol compliance test patterns.
