# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-weiss.c

Purpose: supplies stream format maps for Weiss DICE devices including DAC, interface, archive player, ADC, and AFI models.

Important APIs/functions: `snd_dice_detect_weiss_formats` and `struct dice_weiss_spec`.

Control flow and state: reads model ID from the unit directory, selects a static spec table entry, and copies TX/RX channel maps. Most models use 2 channels in all rate modes; AFI1 uses 24/16/8 channels across low/middle/high. No MIDI ports are configured.

Dependencies/integration: selected by Weiss entries in `dice.c`. Risks include table coverage, comments documenting similar models, and no validation until reserve-time hardware register reads. Test signals are correct PCM channel constraints for each Weiss model and no rawmidi device creation.
