# sources/distributed-fs/ceph-client/sound/synth/emux/emux_nrpn.c

## Purpose
This file converts MIDI NRPN, XG controller, and SYSEX events into EMUX raw effect or port update operations. It provides AWE32-specific NRPN effects, experimental GS and XG mappings, and SYSEX master-volume handling.

## Important APIs, types, and functions
`struct nrpn_conv_table` maps a MIDI control number to an EMUX effect and conversion callback. Conversion helpers such as `fx_delay`, `fx_attack`, `fx_decay`, `fx_conv_pitch`, `gs_cutoff`, and `xg_filterQ` translate MIDI values into soundfont/EMUX units. Public functions are `snd_emux_nrpn`, `snd_emux_xg_control`, and `snd_emux_sysex`.

## Control flow
For AWE32 NRPNs, `snd_emux_nrpn` matches MSB 127 and LSB 0-26, combines data-entry MSB/LSB into a signed value centered at 8192, and sends a set-mode raw effect. In GS mode with NRPN MSB 1, it uses only data-entry MSB and sends add-mode GS effects. XG controller handling is invoked from `snd_emux_control` and maps controller 71/72/73/74 to cutoff, release, attack, and resonance effects. SYSEX master volume triggers a port volume update; unknown parsed SYSEX events are delegated to hardware `emu->ops.sysex` when present.

## State and persistence behavior
This file owns no persistent storage. It mutates per-channel effect state through `snd_emux_send_effect` and causes live voice updates through the synth layer.

## Dependencies and integration points
It depends on ALSA MIDI parser constants, EMUX raw effect APIs, soundfont parameter calculators, MIDI channel control arrays, and optional hardware SYSEX callbacks.

## Risks and edge cases
The conversion tables are described as experimental for GS/XG and use fixed sensitivity arrays tuned for particular soundfonts. `snd_emux_xg_control` validates only upper bound against `ARRAY_SIZE(chan->control)`; negative params are not expected but would be unsafe if passed. Raw effect support must be present for conversion outputs to have effect.

## Test signals
Send AWE32 NRPNs for every table entry, GS NRPNs in GS mode, XG controllers in XG mode, master-volume SYSEX, unknown SYSEX delegation, and boundary values 0/64/127 to verify conversion signs and magnitudes.
