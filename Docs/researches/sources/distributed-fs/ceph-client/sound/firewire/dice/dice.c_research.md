# sources/distributed-fs/ceph-client/sound/firewire/dice/dice.c

Purpose: main DICE driver module implementing FireWire ID matching, DICE category validation, ALSA card setup, transaction/stream/proc/PCM/MIDI/hwdep initialization, bus reset handling, and module registration.

Important APIs/functions: `check_dice_category`, `check_clock_caps`, `dice_card_strings`, `dice_card_free`, `dice_probe`, `dice_remove`, `dice_bus_reset`, `alsa_dice_init`, and `alsa_dice_exit`. The `dice_id_table` maps many OUIs/models to detector functions.

Control flow and state: probe optionally validates GUID/category layout, allocates `struct snd_dice`, selects a detector from `driver_data` or generic current-format detection, applies high-rate double-frame quirks for M-Audio/Avid, initializes synchronization primitives, claims DICE transactions, checks clock caps, reads card strings, detects formats, initializes streams, creates proc/PCM/MIDI/hwdep interfaces, and registers the card. Bus reset re-registers notification ownership and forces streams stopped under mutex.

Dependencies/integration: integrates FireWire driver core, ALSA card lifecycle, DICE transaction/stream/detector modules, and common AM824 infrastructure. Risks include device table matching exceptions, GUID category assumptions, old firmware capabilities, double-wire disable quirks, and error cleanup through `snd_card_free`. Test signals include probe on typical and quirk devices, correct card strings, successful bus reset recovery, and detector-selected formation output.
