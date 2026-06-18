# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-focusrite.c

Purpose: provides a hard-coded stream format detector for the Focusrite Saffire Pro 40 TCD3070-CH DICE variant that lacks TCAT extension support.

Important APIs/functions: `snd_dice_detect_focusrite_pro40_tcd3070_formats`.

Control flow and state: fills stream 0 TX/RX channel counts for low and middle modes and sets MIDI ports. No FireWire reads are performed. The function leaves high-rate mode unsupported by zero counts.

Dependencies/integration: selected by `dice.c` for the Focusrite model ID quirk. Risks include possible typo-like assignment of MIDI ports to index 1 for middle mode while PCM stays on stream 0, and lack of support for other Pro 40 firmware variants. Test signals are correct low/middle PCM device constraints and MIDI port availability on the physical device.
