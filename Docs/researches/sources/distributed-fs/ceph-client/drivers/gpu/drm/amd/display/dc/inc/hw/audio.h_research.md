# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/audio.h

## Purpose

`audio.h` defines the display audio endpoint abstraction for HDMI/DP audio programming through the Azalia/audio hardware block.

## Important APIs, Types, And Functions

`struct audio_funcs` provides `endpoint_valid`, `hw_init`, `az_enable`, `az_disable`, `az_configure`, `az_disable_hbr_audio`, `wall_dto_setup`, and `destroy`. `struct audio` stores the vtable, DC context, hardware instance, and enabled state.

## Control Flow

Resource code assigns an audio object to a stream. HWSS/link programming initializes and enables Azalia audio, configures it from signal type, CRTC timing, audio info, and DP link info, programs wall DTO using PLL info, disables HBR audio when needed, and disables/destroys the endpoint on teardown.

## State And Persistence Behavior

The audio object persists in the resource pool and tracks whether it is enabled. Hardware retains Azalia and DTO programming until changed or disabled. No disk persistence exists.

## Dependencies And Integration Points

It includes `audio_types.h`. It integrates with stream resources, link encoders, clock/PLL programming, infoframe/audio packet setup, and HWSS `enable_audio_stream`/`disable_audio_stream`.

## Risks And Edge Cases

Audio configuration depends on matching signal type, timing, PLL, and DP link rate/lane data. Endpoint validation must prevent programming unavailable hardware. HBR disable and wall DTO setup are timing-sensitive. `enabled` can become stale if hardware reset occurs outside the audio object.

## Test Signals

Tests should cover HDMI, DP, eDP/no-audio, HBR/non-HBR, link-rate changes, mode changes with audio active, suspend/resume, and endpoint destruction. Runtime signals include audio presence, sample-rate correctness, no underruns/pops, and valid infoframes.
