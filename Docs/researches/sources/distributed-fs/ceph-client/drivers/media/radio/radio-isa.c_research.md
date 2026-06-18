# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-isa.c

Purpose: framework that supplies V4L2 scaffolding for legacy ISA radio drivers. Board-specific drivers provide hardware callbacks while this file handles device allocation flow, I/O region ownership, V4L2 device/video registration, standard radio ioctls, controls, optional PnP, and removal.

Important APIs: exported functions are `radio_isa_match`, `radio_isa_probe`, `radio_isa_remove`, and under PnP `radio_isa_pnp_probe/remove`. V4L2 operations include querycap, tuner get/set, frequency get/set, log status, control subscribe/unsubscribe, and mute/volume control handling.

Control flow: match succeeds if probing is enabled or an explicit I/O parameter exists. Probe allocates a board card through `ops->alloc`, optionally scans candidate ports with `ops->probe`, validates the selected port, then calls common probe. Common probe claims the I/O region, registers V4L2 device, creates mute and optional volume controls, initializes the video device, calls board `init`, sets up controls, programs default low FM frequency and stereo mode, and registers a radio video node. Removal mutes the card, unregisters the video device, frees controls/V4L2 device, releases I/O, and frees memory.

State and persistence: `struct radio_isa_card` holds current frequency, stereo mode, mute/volume controls, V4L2/video objects, mutex, and I/O port. State is runtime only; hardware may remain in last frequency/mute until removal.

Dependencies and integration: ISA bus registration, optional PnP, V4L2 control/event APIs, board callbacks in `radio_isa_ops`, and valid I/O-port lists in `radio_isa_driver`.

Risks: failure paths must free allocated card correctly; `radio_isa_probe` returns `-ENODEV` without freeing `isa` when `isa->io < 0`, which is a leak risk in that path. Only mute control changes call `s_mute_volume`; clustered volume updates rely on V4L2 control behavior. Test signals include board-driver registration, invalid/valid I/O parameters, probe scanning, PnP probe/remove, default frequency setup, mute-on-remove, and `v4l2-compliance` for radio ioctls/events.
