# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-extension.c

Purpose: detects DICE stream formats through the TCAT application protocol extension used by TCD2210/2220-class firmware.

Important APIs/functions: `snd_dice_detect_extension_formats`, `detect_stream_formats`, `read_stream_entries`, and `read_transaction`.

Control flow and state: the detector reads the extension section pointer table at `DICE_EXT_APP_SPACE`, rejects layouts with duplicate section offsets as unsupported/fallback, then reads stream configuration entries from the current/application section. For each supported rate mode implied by clock capabilities, it reads TX/RX stream counts and per-stream audio/MIDI counts into `dice->tx/rx_pcm_chs` and `tx/rx_midi_ports`.

Dependencies/integration: used as a preferred generic detector from `snd_dice_stream_detect_current_formats` and for specific device IDs. Risks include relying on section index 6, ignoring unsupported rate modes based only on clock caps, duplicate offset fallback, and fixed entry sizes. Test signals are successful probe on extension-capable devices, correct low/mid/high formation proc rows, and fallback to current-format detection on `-ENXIO`.
