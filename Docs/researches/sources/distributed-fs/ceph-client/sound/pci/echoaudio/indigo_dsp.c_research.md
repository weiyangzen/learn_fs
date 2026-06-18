# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo_dsp.c

## Purpose

`indigo_dsp.c` implements the original Indigo card DSP behavior: no ASIC, internal-only clocking, fixed MIA-style sample-rate register values, and vmixer routing.

## Important APIs, Types, and Functions

`init_hw()` validates `INDIGO`, sets `FW_INDIGO_DSP`, marks ASIC loaded, enables only the internal clock, and loads firmware. `set_mixer_defaults()` delegates to `init_line_levels()`. `detect_input_clocks()` returns internal only. `load_asic()` is a no-op. `set_sample_rate()` maps 32/44.1/48/88.2/96 kHz to MIA clock constants and sends `DSP_VC_UPDATE_CLOCKS`. `set_vmixer_gain()` updates `chip->vmixer_gain` and `comm_page->vmixer`; `update_vmixer_level()` sends `DSP_VC_SET_VMIXER_GAIN`.

## Control Flow

After firmware load, common initialization restores muted output and vmixer state. ALSA rate changes rewrite the comm-page control register when the selected clock encoding changes. Mixer controls update individual vmixer cells and then ask the DSP to reread the vmixer table.

## State and Persistence Behavior

State includes `sample_rate`, `control_register`, `input_clock_types`, `vmixer_gain`, and `comm_page->vmixer`. Because there is no ASIC or external clock, reload restore is simpler than GML cards.

## Dependencies and Integration Points

It integrates with shared DSP helpers and common vmixer ALSA controls. It reuses MIA clock constants from `echoaudio_dsp.h` for the Indigo hardware clock register.

## Risks and Test Signals

Risks include unsupported rates and vmixer index mistakes across `output * num_pipes_out + pipe`. Test signals are stable internal-clock detection, successful rate changes, correct 8-pipe to 2-output vmixer controls, and no ASIC load attempts.
