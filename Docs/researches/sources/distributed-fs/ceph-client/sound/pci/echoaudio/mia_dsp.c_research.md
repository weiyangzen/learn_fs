# sources/distributed-fs/ceph-client/sound/pci/echoaudio/mia_dsp.c

## Purpose

`mia_dsp.c` implements Mia-specific initialization, MIDI revision detection, MIA control-register rate/clock programming, vmixer routing, and S/PDIF flag handling.

## Important APIs, Types, and Functions

`init_hw()` validates `MIA`, selects `FW_MIA_DSP`, marks no ASIC, sets `has_midi` for `MIA_MIDI_REV`, enables internal and S/PDIF clocks, and loads firmware. `detect_input_clocks()` maps GLDM S/PDIF detection. `set_sample_rate()` maps fixed rates to MIA constants and ORs S/PDIF clock bits when needed. `set_input_clock()` accepts internal or S/PDIF and reapplies the sample rate. `set_vmixer_gain()` and `update_vmixer_level()` update the virtual mixer. `update_flags()` and `set_professional_spdif()` toggle S/PDIF professional mode.

## Control Flow

Probe initializes hardware and optional MIDI capability. Rate and clock controls converge through `set_sample_rate()`, so changing to S/PDIF clock reprograms the same stored sample rate with the S/PDIF clock bit. S/PDIF format changes send `DSP_VC_UPDATE_FLAGS`.

## State and Persistence Behavior

State includes `has_midi`, `input_clock`, `sample_rate`, `control_register`, `professional_spdif`, and vmixer gains. No ASIC state exists, but DSP reloads restore these fields through common code.

## Dependencies and Integration Points

It depends on shared DSP helpers, MIA constants in `echoaudio_dsp.h`, common Echoaudio controls, and optional `midi.c` rawmidi creation.

## Risks and Test Signals

Risks are wrong MIDI revision detection, unsupported rates, and stale S/PDIF clock bits after input-clock changes. Test signals are MIDI only on revision 1, internal and S/PDIF clock switching, professional S/PDIF control, and vmixer operation.
