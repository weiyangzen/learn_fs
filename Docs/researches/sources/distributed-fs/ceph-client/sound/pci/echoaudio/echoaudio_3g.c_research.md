# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_3g.c

## Purpose

This file contains common low-level control logic for Echoaudio 3G cards, especially ASIC loading, external clock detection, digital mode switching, sample-rate programming, SPDIF flags, and input clock selection.

## Important APIs, types, and functions

Key functions are `check_asic_status()`, `get_frq_reg()`, `write_control_reg()`, `set_digital_mode()`, `set_spdif_bits()`, `set_professional_spdif()`, `detect_input_clocks()`, `load_asic()`, `set_sample_rate()`, `set_input_clock()`, and `dsp_set_digital_mode()`.

## Control flow

ASIC load sends the generic 3G ASIC firmware, waits for hardware settle, tests ASIC status, and writes the default 48 kHz internal/SPDIF RCA control state. Control-register updates wait for DSP handshake, compare desired little-endian comm-page values, update only on change or force, clear handshake, and send `DSP_VC_WRITE_CONTROL_REG`. Sample-rate and input-clock changes manipulate control bits and frequency register depending on internal, SPDIF, ADAT, or word-clock mode. Digital-mode changes reject incompatible active pipes, switch incompatible clocks to internal, update control bits, then refresh monitor/gain state when ADAT changes channel meaning.

## State and persistence behavior

Persistent state includes `asic_loaded`, `asic_code`, `digital_mode`, `input_clock`, `sample_rate`, `professional_spdif`, `non_audio_spdif`, comm-page `control_register`, `e3g_frq_register`, `status_clocks`, and gain/meter state refreshed through shared helpers.

## Dependencies and integration points

It depends on DSP vectors, 3G constants from `echoaudio_dsp.h`, shared helper functions from `echoaudio_dsp.c`, and ALSA controls in `echoaudio.c` that call digital, SPDIF, clock, and channel-info functions.

## Risks and test signals

Risks include control-register lost updates under concurrent controls, ADAT rejecting high sample rates, incorrect detection masks for SPDIF96/WORD96, one-second ASIC load delay affecting probe latency, and failure to refresh gains after channel-count mode changes. Tests should switch RCA/optical/ADAT modes, try incompatible clocks, test continuous rates, verify SPDIF professional/non-audio bits, load ASIC from cold boot, and read channel-info clock masks with different external clocks connected.
