# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-presonus.c

Purpose: supplies fixed stream format detection for the PreSonus FireStudio DICE device.

Important APIs/functions: `snd_dice_detect_presonus_formats` and `struct dice_presonus_spec`.

Control flow and state: reads the model ID from the unit directory, matches it against a small table, copies low/middle TX/RX channel maps, and enables one MIDI port on stream 0 when supported. High mode is left unsupported.

Dependencies/integration: selected by the PreSonus ID entry in `dice.c`. Risks include typo in the internal spec name only affecting readability, limited model table, and lack of high-rate channel support. Test signals are correct formation proc output, PCM device creation for two streams, and MIDI device creation.
