# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-harman.c

Purpose: supplies fixed format detection for the Lexicon I-ONYX FW810S Harman DICE device.

Important APIs/functions: `snd_dice_detect_harman_formats`.

Control flow and state: for low and middle rate modes, it sets first TX stream to 12 PCM channels plus one MIDI port and first RX stream to 10 PCM channels plus one MIDI port. High mode remains unsupported.

Dependencies/integration: selected by the Harman entry in `dice.c`. Risks include limited coverage to frequencies up to 96 kHz and dependence on comments for hardware capabilities. Test signals are proc formation low/middle rows, expected PCM constraints, and successful reserve without cache mismatch.
