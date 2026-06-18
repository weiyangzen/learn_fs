# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echo3g_dsp.c

## Purpose

This file provides Echo3G card-specific DSP initialization, external-box classification, mixer defaults, and phantom-power control hooks.

## Important APIs, types, and functions

`init_hw()` initializes the comm page, seeds the 48 kHz frequency register, sets firmware `FW_ECHO3G_DSP`, enables MIDI, loads firmware/ASIC, interprets returned box type as Gina3G or Layla3G, fills clock masks, card name, pipe/bus indexes, and box capabilities, then advertises SPDIF RCA/optical/ADAT modes. `set_mixer_defaults()` sets default digital/SPDIF/phantom state and initializes line levels. `set_phantom_power()` toggles `E3G_PHANTOM_POWER` through `write_control_reg()`.

## Control flow

The shared probe calls `init_hw()`. Firmware loading returns a box type from `load_asic()` in `echoaudio_3g.c`; the result controls subsequent channel layout. Phantom-power ALSA control calls `set_phantom_power()` only when `chip->has_phantom_power` is true.

## State and persistence behavior

State persists in comm-page control/frequency registers, `card_name`, dynamic pipe/bus indexes, `input_clock_types`, `digital_modes`, `has_phantom_power`, `hasnt_input_nominal_level`, `phantom_power`, `bad_board`, and `has_midi`.

## Dependencies and integration points

It forward-declares helpers implemented in `echoaudio_3g.c`, uses shared DSP helpers, and is textually included by `echo3g.c` before the shared driver.

## Risks and test signals

Risks include `local_irq_enable()` during init, misclassification of external boxes, partially initialized dynamic indexes on errors, and phantom-power control writes racing with other control-register updates. Tests should cover both box types, missing box, firmware failure, phantom-power toggling, MIDI availability, and control registration differences.
