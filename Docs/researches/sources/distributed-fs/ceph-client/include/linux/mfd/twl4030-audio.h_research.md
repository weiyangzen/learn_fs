# sources/distributed-fs/ceph-client/include/linux/mfd/twl4030-audio.h

## Purpose
`twl4030-audio.h` defines TWL4030 audio codec register offsets, bitfields, codec resource IDs, and resource/MCLK helper APIs used by audio and vibra subdrivers.

## Important APIs, Types, and Functions
The register map covers codec mode, analog/digital mic paths, ADC/DAC controls, audio and voice interfaces, TX/RX PGAs, Bluetooth interface, ear/headset/pre-driver/handsfree outputs, ALC, boost, soft volume, DTMF, APLL, misc settings, PCM/BT muxing, RX path, vibra control, and analog mic gain. Bitfields define APLL sample rates, interface format/width, mic bias and input enables, output gains, pop/ramp delays, APLL input frequencies, smooth volume, FM loop, digital mic swap, and vibra routing. `enum twl4030_audio_res` identifies power and APLL resources. APIs are `twl4030_audio_disable_resource()`, `twl4030_audio_enable_resource()`, and `twl4030_audio_get_mclk()`.

## Control Flow
Codec users enable the shared power/APLL resources before programming audio paths, set codec/APLL rates and interface formats, then enable ADC/DAC/output blocks. Resource helpers mediate shared power/reference use between codec and vibra/audio clients.

## State and Persistence Behavior
Hardware persists codec mode, APLL rate/input, mic bias, analog/digital path enables, interface format, gain, pop/ramp timing, DTMF, vibra control, and misc clock/loop settings. Software state is not declared, except resource IDs used by the implementation.

## Dependencies and Integration Points
The header integrates with the TWL4030 MFD core, ASoC codec driver, vibra driver, clock/MCLK configuration, and audio platform data from `twl.h`.

## Risks and Test Signals
Risks include unsupported APLL rate encodings, failing to enable shared resources before register writes, incorrect interface width/format matching with the CPU DAI, and pop/noise from bad ramp timing. Test signals are ASoC playback/capture path tests, MCLK reporting, resource refcount tests, vibra enable tests, codec register readback for sample rates and format, and suspend/resume audio path restoration.
