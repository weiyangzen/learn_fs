# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.h

## Purpose
Defines the DCN3 audio formatter register maps, function table interface, base/concrete object structures, and public setup functions.

## Important APIs, Types, And Functions
`AFMT_DCN3_REG_LIST` lists infoframe, VBI/audio packet, audio source, 60958 status, and memory-power registers. `DCN3_AFMT_MASK_SH_LIST` and `AFMT_DCN3_REG_FIELD_LIST` define fields for audio info update, source select, channel enable, 60958 update/layout/channel numbers/clock accuracy, sample send, and memory power force. `struct afmt_funcs` contains setup, mute, update, DP setup, and power callbacks. `struct afmt` is the base, `struct dcn30_afmt` stores register descriptors, and setup/constructor prototypes are exported.

## Control Flow
No executable flow; callers invoke function pointers or exported setup helpers.

## State And Persistence
The base object stores context, instance, and function table. The concrete object stores register descriptors. Hardware state is in AFMT registers.

## Dependencies And Integration Points
The header is used by `dcn30_afmt.c` and stream/audio resource code. It assumes common audio types such as `audio_info` and `audio_speaker_flags` are visible through including translation units.

## Risks
Power callbacks are optional, so implementations must guard them. Adding AFMT fields requires synchronized updates to register, shift, and mask lists. Header-defined base `struct afmt` becomes an ABI-like contract for all AFMT users.

## Test Signals
Compile-time structure/function compatibility, HDMI/DP audio setup, power callback invocation, and register readbacks for source select/channel enable/sample send.
