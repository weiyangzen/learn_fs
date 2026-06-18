# sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-audio.c

## Purpose
This file implements audio clock, routing path, and audio control support for the CX25840 family driver. It programs PLL/SRC registers for 32 kHz, 44.1 kHz, and 48 kHz sample rates, switches between serial and tuner/demod audio paths, and maps V4L2 audio controls onto chip registers.

## Important APIs, Types, And Functions
`cx25840_s_clock_freq()` is the V4L2 audio clock entry point. `cx25840_audio_set_path()` is called by core input routing to reset and reconfigure the audio path. `cx25840_audio_ctrl_ops` exposes `cx25840_audio_s_ctrl()` for volume, balance, bass, and treble. Internal helpers include `cx25840_set_audclk_freq()`, `cx23885_set_audclk_freq()`, `cx231xx_set_audclk_freq()`, `set_audclk_freq()`, `set_volume()`, and `set_balance()`.

## Control Flow
Clock changes first validate the frequency, select the chip-family-specific setter, and write PLL/SRC constants. For non-serial analog inputs, `cx25840_audio_set_path()` asserts soft reset, stops the audio microcontroller, mutes outputs, writes `PATH1` routing for serial or analog demod, sets the clock, optionally restarts the microcontroller for tuner audio, and deasserts reset. Direct `s_clock_freq` follows the same mute/stop/program/restart pattern. Audio controls scale V4L2 ranges to chip-specific volume, EQ, and balance fields.

## State And Persistence
`state->audclk_freq` caches the selected sample rate and is reused when routes change. `state->aud_input`, `state->volume`, and `state->mute` influence path and volume programming. Hardware state persists in PLL, SRC, path, mute, EQ, and balance registers until reset or another V4L2 call changes it.

## Dependencies And Integration Points
The file depends on register helpers and model predicates from `cx25840-core.h`, V4L2 control IDs, and media driver interface constants from `media/drv-intf/cx25840.h`. It is linked into the composite `cx25840` module and called by `cx25840-core.c` during input routing, probe control setup, and audio subdev ops.

## Risks
Several chip/frequency combinations are documented as unknown and intentionally avoid programming registers while still caching the requested rate. PLL constants contain FIXME notes about reference frequency mismatch and out-of-range AUX PLL operation at 32 kHz. Control writes generally ignore I2C errors. Volume scaling preserves legacy mappings but is non-obvious and can surprise callers expecting linear dB behavior.

## Test Signals
Tests should cover valid and invalid sample rates, serial versus analog path setup, mute-cluster behavior, volume/balance register mappings, and regression audio capture at all supported rates on each chip family. Hardware logging should confirm the microcontroller restarts for tuner audio and stays stopped for serial inputs where intended.
