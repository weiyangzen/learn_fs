# sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina24_dsp.c

## Purpose

`gina24_dsp.c` implements Gina24 hardware initialization, ASIC selection, sample-rate programming, input-clock selection, and GML digital-mode handling.

## Important APIs, Types, and Functions

`init_hw()` validates Gina24, initializes the comm page, selects 56301 or 56361 DSP firmware, enables internal/S/PDIF/ESYNC/ESYNC96/ADAT clocks, and sets supported digital modes. `set_mixer_defaults()` initializes S/PDIF RCA, consumer S/PDIF, and digital auto-mute. `detect_input_clocks()` maps GML S/PDIF, ADAT, and ESYNC detect bits. `load_asic()` loads the correct Gina24 ASIC and initializes the GML control register to converter enabled, 48 kHz internal. `set_sample_rate()` maps fixed rates into GML clock bits and forbids double-speed ADAT. `set_input_clock()` selects internal, S/PDIF, ADAT, ESYNC, or ESYNC96. `dsp_set_digital_mode()` handles RCA/optical/CDROM/ADAT and incompatible clock fallback.

## Control Flow

Probe boots firmware and ASIC, then common mixer initialization restores line state. Rate changes only program hardware while using the internal clock; external clock mode records the requested rate for ALSA state. Digital-mode changes may force internal 48 kHz first, then rewrite `control_register`.

## State and Persistence Behavior

Persistent state includes `dsp_code_to_load`, `asic_code`, `digital_modes`, `digital_mode`, `digital_in_automute`, `input_clock`, `sample_rate`, and `comm_page->control_register`. The `device_id` distinguishes 56301-only CDROM S/PDIF mode from 56361 behavior.

## Dependencies and Integration Points

This file depends on `echoaudio_gml.c` for `write_control_reg()`, `set_digital_mode()`, and S/PDIF format handling, plus shared DSP firmware helpers. It is driven by ALSA clock, digital-mode, and PCM rate controls.

## Risks and Test Signals

Risks include allowing ADAT above 48 kHz, failing to clear double-speed bits when switching to ADAT, and incorrect CDROM mode on 56361 hardware. Test signals are ASIC status success, correct external-clock detection, digital-mode fallback to internal clock when needed, and working playback/capture in S/PDIF and ADAT modes.
