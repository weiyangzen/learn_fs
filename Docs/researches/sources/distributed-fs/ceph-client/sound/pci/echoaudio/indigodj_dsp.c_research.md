# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodj_dsp.c

## Purpose

`indigodj_dsp.c` provides Indigo DJ-specific DSP initialization and vmixer/sample-rate operations for the four-output DJ card.

## Important APIs, Types, and Functions

The structure mirrors `indigo_dsp.c`: `init_hw()` validates the Indigo DJ subdevice, selects `FW_INDIGO_DJ_DSP`, marks the no-ASIC card as loaded, enables internal-only clocking, and loads firmware. `set_mixer_defaults()`, `detect_input_clocks()`, `load_asic()`, `set_sample_rate()`, `set_vmixer_gain()`, and `update_vmixer_level()` provide defaults, fixed MIA-style rate encodings, and vmixer matrix updates.

## Control Flow

Common initialization calls the card `init_hw()` and then replays line/vmixer defaults. ALSA rate changes write the control register and send `DSP_VC_UPDATE_CLOCKS`; vmixer changes are staged in the comm page and committed with `DSP_VC_SET_VMIXER_GAIN`.

## State and Persistence Behavior

The card persists no external clock or ASIC state. It keeps internal sample-rate state, control-register value, and a vmixer matrix sized by 4 outputs by 8 pipes.

## Dependencies and Integration Points

It depends on shared DSP primitives and constants from `echoaudio_dsp.h`, and it is consumed by the `indigodj.c` wrapper and common `echoaudio.c` mixer controls.

## Risks and Test Signals

Risks are unsupported rate programming and vmixer cell ordering. Test with all advertised rates, four-output playback, vmixer gain persistence after DSP reload, and absence of external clock or input controls.
