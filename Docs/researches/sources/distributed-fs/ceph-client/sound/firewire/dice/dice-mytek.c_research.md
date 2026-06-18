# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-mytek.c

Purpose: supplies fixed stream formats for the Mytek Stereo 192 DSD-DAC DICE device.

Important APIs/functions: `snd_dice_detect_mytek_formats` and `struct dice_mytek_spec`.

Control flow and state: copies static TX/RX channel maps into the device state for all rate modes, with 8 capture channels and 4 playback channels on stream 0, no second stream, and no MIDI ports.

Dependencies/integration: selected by `dice.c` for Mytek model ID. Risks include incomplete coverage of other Mytek FireWire products and assumptions about native DSD presentation through PCM channel counts. Test signals are expected PCM constraints across 44.1-192 kHz and no rawmidi device creation.
