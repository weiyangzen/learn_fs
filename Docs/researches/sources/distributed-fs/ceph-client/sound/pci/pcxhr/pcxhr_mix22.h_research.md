# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mix22.h

## Purpose

This header declares the HR222/stereo-card helper API and mixer level constants used by the generic PCXHR files when `mgr->is_hr_stereo` is true.

## Important APIs, Types, And Functions

- Initialization and clocking: `hr222_sub_init()`, `hr222_sub_set_clock()`, and `hr222_get_external_clock()`.
- Proc/hardware helpers: `hr222_read_gpio()`, `hr222_write_gpo()`, and `hr222_manage_timecode()`.
- Mixer helpers: `hr222_update_analog_audio_level()`, `hr222_set_audio_source()`, `hr222_iec958_capture_byte()`, `hr222_iec958_update_byte()`, and `hr222_add_mic_controls()`.
- Constants define playback, line-capture, and microphone capture level ranges for HR222 boards.

## Control Flow

Generic code dispatches to these functions for stereo-card special cases: board initialization from firmware setup, clock operations from `pcxhr_set_clock()`, mixer updates from `pcxhr_mixer.c`, and proc GPIO/LTC paths from `pcxhr.c`.

## State And Persistence

The header stores no state. It defines the valid mixer level ranges that gate ALSA control writes and hardware programming.

## Dependencies And Integration Points

It forward-declares `struct pcxhr_mgr` but relies on including code already knowing `enum pcxhr_clock_type` and `struct snd_pcxhr` through `pcxhr.h`. It is the coupling point between generic PCXHR logic and HR222-specific hardware programming.

## Risks

Range constants must match both ALSA TLV descriptions and the hardware conversion code in `pcxhr_mix22.c`. Signature changes require updates in main, hwdep, and mixer files.

## Test Signals

Compile all PCXHR objects and run stereo-board mixer/clock tests. Boundary writes at min/zero/max levels are especially useful because this header defines accepted ranges.
