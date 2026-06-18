# sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla20_dsp.c

## Purpose

`layla20_dsp.c` implements Layla20-specific DSP initialization, ASIC loading, external clock control, sample-rate programming, output clock selection, input gain, and S/PDIF flag handling.

## Important APIs, Types, and Functions

`init_hw()` validates Layla20, initializes the comm page, selects `FW_LAYLA20_DSP`, enables internal/S/PDIF/word/super clocks, and loads firmware. `load_asic()` uses `load_asic_generic()` with `FW_LAYLA20_ASIC` and `check_asic_status()`. `detect_input_clocks()` maps GLDM S/PDIF, word, and super-clock bits. `set_sample_rate()` programs Layla sample-rate state. `set_input_clock()` selects internal, S/PDIF, word, or super. `set_output_clock()` switches word versus super clock output. `set_input_gain()`, `update_flags()`, and `set_professional_spdif()` update analog gain and S/PDIF flags.

## Control Flow

Probe boots DSP and ASIC, then default mixer restore writes muted levels and clock defaults. Clock/rate changes use comm-page fields plus `DSP_VC_SET_LAYLA_SAMPLE_RATE` or `DSP_VC_UPDATE_FLAGS`. ASIC status is checked after load and during restore.

## State and Persistence Behavior

State includes `asic_loaded`, `input_clock`, `output_clock`, `sample_rate`, `professional_spdif`, input gains, and output nominal levels. These values are replayed by `restore_dsp_settings()` after reload.

## Dependencies and Integration Points

It depends on shared ASIC and DSP loader helpers, GLDM/Layla clock constants, and optional MIDI shutdown through shared code. ALSA controls for clocks, S/PDIF, gain, and output level reach these functions.

## Risks and Test Signals

Risks include external-box ASIC load failures, wrong output clock mode, and unsupported continuous rates. Test signals are successful ASIC test, valid clock detection, output clock control behavior, MIDI operation, and no DSP handshake timeout during rate/gain changes.
