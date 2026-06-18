<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-codec.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-codec.h

## Purpose
This header defines platform data for the audio portions of AB8500-family chips, especially analog microphone topology, mic-bias routing, and ear common-mode voltage selection.

## Important APIs, Types, And Functions
- `enum amic_type` distinguishes single-ended and differential analog microphone wiring.
- `enum amic_micbias` selects `VAMIC1`, `VAMIC2`, or unknown mic-bias routing.
- `enum ear_cm_voltage` encodes supported ear common-mode voltages from 0.95 V through 1.58 V plus unknown.
- `struct amic_settings` describes mic1/mic2 topology and mic-bias assignment for mic1a, mic1b, and mic2.
- `struct ab8500_codec_platform_data` aggregates analog microphone settings and ear common-mode voltage.

## Control Flow
The header contributes data consumed by the AB8500 codec/audio driver during probe or machine setup. Board or platform code fills `ab8500_codec_platform_data`; the codec driver translates those enum values into AB8500 audio register programming.

## State And Persistence
This file defines static configuration rather than runtime state. Once consumed, the settings become hardware audio-path state in AB8500 registers. Persistence is limited to platform data and live hardware register programming.

## Dependencies And Integration Points
It is referenced by `struct ab8500_platform_data` in `ab8500.h` and integrates with ASoC codec drivers for AB8500-family audio. It also indirectly depends on microphone bias supplies and jack/mic detection paths configured elsewhere.

## Risks And Edge Cases
- The `UNKNOWN` enum values must be handled defensively by codec users to avoid programming invalid voltage or bias selections.
- Board data must match actual analog wiring; wrong single-ended/differential or mic-bias assignments can break capture or damage signal quality.
- The header has no range checking; validation belongs in the consuming codec driver.

## Test Signals
Validate codec probe with populated platform data, confirm register programming for each microphone topology and bias route, measure capture on mic1 and mic2, verify ear output common-mode selection, and test behavior when unknown/default values are supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-codec.h -->
