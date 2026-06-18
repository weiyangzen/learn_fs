# sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina20_dsp.c

## Purpose

`gina20_dsp.c` implements Gina20-specific DSP setup, clocking, sample-rate control, analog input gain, and S/PDIF flag handling for the shared Echoaudio runtime.

## Important APIs, Types, and Functions

`init_hw()` validates the Gina20 subdevice, initializes the comm page, sets `FW_GINA20_DSP`, marks the no-ASIC board as loaded, enables internal and S/PDIF clock types, and loads firmware. `set_mixer_defaults()` clears professional S/PDIF and initializes line levels. `detect_input_clocks()` maps GLDM S/PDIF detection to generic clock bits. `load_asic()` is a no-op. `set_sample_rate()` maps 44.1/48 kHz into Gina/Darla clock and S/PDIF state bytes. `set_input_clock()` selects internal or S/PDIF clock. `set_input_gain()` applies the GL20 gain magic offset. `set_professional_spdif()` toggles `DSP_FLAG_PROFESSIONAL_SPDIF` and calls `update_flags()`.

## Control Flow

Common probe calls `init_hw()`, which boots the DSP and clears `bad_board`. Mixer initialization calls `set_mixer_defaults()` and then `init_line_levels()`. Rate and clock controls write Gina/Darla-specific comm-page state and send `DSP_VC_SET_GD_AUDIO_STATE`; S/PDIF format updates send `DSP_VC_UPDATE_FLAGS`.

## State and Persistence Behavior

The file maintains `clock_state`, `spdif_status`, `professional_spdif`, `input_clock`, `sample_rate`, and per-input gain in `struct echoaudio` and mirrors them into `comm_page->gd_clock_state`, `gd_spdif_status`, `gd_resampler_state`, flags, and `line_in_level`.

## Dependencies and Integration Points

It depends on shared DSP helpers, GLDM/GD constants in `echoaudio_dsp.h`, and ALSA controls from `echoaudio.c`. It has no ASIC or digital-mode switch dependency.

## Risks and Test Signals

Risks are stale GD clock/S/PDIF state, invalid unsupported sample rates slipping through, and incorrect 0.5 dB input-gain encoding. Test signals are clean DSP load, selectable internal/S/PDIF clocks, correct rejection of non-44.1/48 rates from the PCM layer, and audible/observable input-gain and S/PDIF professional mode changes.
