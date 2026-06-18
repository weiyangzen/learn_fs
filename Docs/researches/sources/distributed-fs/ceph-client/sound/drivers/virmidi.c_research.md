# sources/distributed-fs/ceph-client/sound/drivers/virmidi.c

Purpose: creates dummy ALSA sound cards that expose virtual rawmidi devices backed by the ALSA sequencer virtual MIDI layer. It is a userspace routing aid rather than a hardware driver.

Important APIs, types, and functions: module parameters provide card index/id/enable and number of MIDI devices per card, capped by `MAX_MIDI_DEVICES`. `struct snd_card_virmidi` stores the ALSA card and up to four rawmidi pointers. `snd_virmidi_probe()` creates the card and rawmidi devices via `snd_virmidi_new()`. `alsa_card_virmidi_init()` registers the platform driver and simple platform devices; `snd_virmidi_unregister_all()` tears them down.

Control flow: module init registers `snd_virmidi_driver`, then iterates `SNDRV_CARDS`, creating platform devices for enabled slots. Probe allocates a devm-managed ALSA card, caps `midi_devs[dev]`, creates each virtual rawmidi device, fills card identity strings, registers the card, and stores the card as platform driver data. If a platform device does not end up with drvdata, init unregisters it and continues. If no cards are created, init unregisters everything and returns `-ENODEV`.

State and persistence: runtime state is confined to devm card private data and the global `devices[]` table. There is no persistent state; virtual MIDI endpoints exist only while the module and card instances are loaded.

Dependencies and integration: depends on ALSA core, ALSA sequencer kernel API, `seq_virmidi`, and platform driver infrastructure. The rawmidi operations are provided by `snd_virmidi_new()` rather than this file.

Risks: `midi_devs[dev]` is mutable at probe time and values below zero are not explicitly checked here; behavior depends on ALSA helper validation and loop bounds. The driver has no `.remove` callback, relying on devm and platform unregister/card teardown paths. Test signals include default one-card/four-device behavior, capping values above four, disabled cards skipped, sequencer client creation, routeability with `aconnect`, and clean unload of all platform devices.
