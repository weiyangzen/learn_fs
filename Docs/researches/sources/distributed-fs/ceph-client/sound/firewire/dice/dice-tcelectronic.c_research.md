# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-tcelectronic.c

Purpose: supplies static stream format maps for TC Electronic DICE devices including Konnekt and Impact/Digital Konnekt variants.

Important APIs/functions: `snd_dice_detect_tcelectronic_formats`, `struct dice_tc_spec`, and static specs for Desktop Konnekt 6, Impact Twin, Konnekt 8/24D/Live, Studio Konnekt 48, and Digital Konnekt x32.

Control flow and state: reads model ID from the unit directory, selects the matching static spec, copies TX/RX channel maps into the DICE state, and sets one MIDI port when the spec has MIDI. No device stream registers are read for channel counts.

Dependencies/integration: selected by multiple TC Electronic entries in `dice.c`. Risks include model table incompleteness, static maps diverging from firmware, and no validation against current device registers until reserve-time cache checks. Test signals are formation proc rows matching device manuals and successful stream reserve with no cache mismatch.
