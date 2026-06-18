# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-teac.c

Purpose: detects stream formats for Tascam/TEAC IF-FW/DM MkII DICE devices.

Important APIs/functions: `snd_dice_detect_teac_formats`.

Control flow and state: reads TX stream count and RX stream count from DICE registers, assigns 16-channel low/middle TX/RX stream 0 with MIDI, and enables stream 1 with 16 channels in low/middle modes when the device reports more than one stream. High mode remains unsupported.

Dependencies/integration: selected by the TEAC-specific ID entry in `dice.c`. Risks include assuming 16 channels for all reported streams, no high-rate support, and dependence on stream count reads before normal stream initialization. Test signals are correct one- or two-stream PCM device creation and reserve success on DM-3200/DM-4800 hardware.
