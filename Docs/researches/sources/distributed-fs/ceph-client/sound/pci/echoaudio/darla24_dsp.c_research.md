# sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla24_dsp.c

## Purpose

This file implements Darla24-specific DSP initialization, external clock detection, sample-rate programming, and input-clock selection.

## Important APIs, types, and functions

`init_hw()` validates Darla24 subsystem IDs, initializes the comm page, selects firmware `FW_DARLA24_DSP`, marks no-ASIC loaded, advertises internal and ESync clocks, loads firmware, and clears `bad_board`. `detect_input_clocks()` maps DSP `GLDM_CLOCK_DETECT_BIT_ESYNC` to `ECHO_CLOCK_BIT_ESYNC`. `set_sample_rate()` maps supported rates to GD24 clock codes and uses `GD24_EXT_SYNC` when ESync is selected. `set_input_clock()` accepts internal or ESync and reapplies the current sample rate.

## Control flow

Firmware load happens during shared probe. Runtime rate or clock changes update `chip->sample_rate`, comm-page `sample_rate` and `gd_clock_state`, then clear the handshake and send `DSP_VC_SET_GD_AUDIO_STATE`.

## State and persistence behavior

Persistent state includes current `sample_rate`, `input_clock`, `input_clock_types`, firmware index, `asic_loaded`, and comm-page clock fields. ESync mode overrides the clock code while keeping the requested sample rate in software.

## Dependencies and integration points

It uses `echoaudio.h` constants and shared DSP helpers. Shared ALSA clock-source controls call `set_input_clock()` and channel-info controls call `detect_input_clocks()`.

## Risks and test signals

Risks include invalid clock-source acceptance, race with open PCM streams through shared controls, incorrect ESync detect mapping, and unsupported rate rejection. Tests should change every supported rate, toggle ESync with and without detected clock, and verify controls report valid clock masks.
