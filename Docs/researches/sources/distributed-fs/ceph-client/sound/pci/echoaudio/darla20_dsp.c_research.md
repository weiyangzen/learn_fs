# sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla20_dsp.c

## Purpose

This file provides Darla20-specific DSP initialization and clock/sample-rate behavior for the shared Echoaudio driver.

## Important APIs, types, and functions

`init_hw()` validates the subsystem family, initializes the DSP communication page, sets firmware index `FW_DARLA20_DSP`, initializes SPDIF/clock cached state, marks ASIC loaded because none exists, sets internal-only clock support, loads firmware, and clears `bad_board`. `set_mixer_defaults()` calls `init_line_levels()`. `detect_input_clocks()` returns internal only. `load_asic()` is a no-op. `set_sample_rate()` maps 44.1/48 kHz to Darla20 DSP clock/SPDIF states and sends `DSP_VC_SET_GD_AUDIO_STATE`.

## Control flow

The shared probe calls `init_hw()`, then mixer defaults. Rate changes wait for DSP handshake, update comm-page fields, update cached clock/SPDIF state only when changed, clear handshake, and send a DSP vector.

## State and persistence behavior

State persists in `chip->device_id`, `subdevice_id`, `bad_board`, `dsp_code_to_load`, `spdif_status`, `clock_state`, `asic_loaded`, `input_clock_types`, `sample_rate`, and comm-page audio-state fields.

## Dependencies and integration points

It relies on constants and helpers from `echoaudio.h` and `echoaudio_dsp.c`, including `init_dsp_comm_page()`, `load_firmware()`, `wait_handshake()`, `clear_handshake()`, and `send_vector()`.

## Risks and test signals

Risks include unsupported rates silently using no-change DSP states, handshake failures, and stale cached clock/SPDIF state. Tests should cover firmware load, set rate to 44100 and 48000, reject wrong subsystem IDs, and verify no ASIC load is attempted.
