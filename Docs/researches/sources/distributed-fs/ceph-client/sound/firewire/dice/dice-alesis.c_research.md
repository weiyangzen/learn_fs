# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-alesis.c

Purpose: supplies stream format detection for Alesis iO14/iO26 and MasterControl DICE devices using static per-mode channel maps.

Important APIs/functions: `snd_dice_detect_alesis_formats` and `snd_dice_detect_alesis_mastercontrol_formats`.

Control flow and state: iO detection reads current TX audio channel count to distinguish smaller and larger models, copies a static TX map, sets RX channels to 8 for all modes, and enables one MIDI port. MasterControl fills explicit two-stream channel counts for low/middle/high modes and two MIDI ports on both streams.

Dependencies/integration: called through `dice.c` ID table during probe before PCM/MIDI creation. Risks include model inference from current TX channel count, firmware variants with different stream layouts, and unsupported high-rate second stream assumptions. Test signals are formation proc output matching hardware, creation of expected PCM devices/ports, and no `keep_dual_resources` cache mismatch at stream reserve.
