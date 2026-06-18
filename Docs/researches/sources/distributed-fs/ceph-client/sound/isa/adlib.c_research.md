# sources/distributed-fs/ceph-client/sound/isa/adlib.c

## Purpose

`adlib.c` is a minimal legacy ISA driver for standalone AdLib-compatible FM synthesis cards. It reserves the OPL I/O ports, creates an ALSA OPL3 device and hwdep interface, and registers a card with no PCM path.

## Important APIs, Types, and Functions

- Module parameters expose `index`, `id`, `enable`, and `port`.
- `snd_adlib_match()` requires the slot to be enabled and a concrete port to be supplied.
- `snd_adlib_probe()` allocates the ALSA card, reserves four I/O ports, creates OPL3 with `snd_opl3_create()`, creates the FM hwdep with `snd_opl3_hwdep_new()`, registers the card, and stores drvdata.
- `module_isa_driver()` registers the legacy ISA probe over `SNDRV_CARDS` slots.

## Control Flow

The legacy ISA core calls match and probe. Probe is linear: allocate card, reserve ports with devm, fill strings, create OPL3 using base and base+2, create hardware-dependent FM interface, register card, and attach it to the device. Any failure aborts probe and devm cleanup releases resources.

## State and Persistence Behavior

Runtime state is limited to ALSA card objects and the devm I/O resource stored in `card->private_data`. No mixer, PCM, DMA, IRQ, or suspend state is managed here.

## Dependencies and Integration Points

The file depends on ALSA core, the legacy ISA driver model, and `<sound/opl3.h>`. It integrates with ALSA hwdep userspace for FM programming rather than with PCM playback.

## Risks and Edge Cases

The driver cannot autodetect a port; loading without `port=` is intentionally rejected. The reserved range is only four bytes, matching OPL2/OPL3 register layout, so conflicts with broader sound-card drivers must be avoided. `snd_opl3_create()` is called with integrated access checking; false positives or bus conflicts are the main hardware risks.

## Test Signals

Successful testing shows an ALSA card named "AdLib FM", an OPL hwdep node, and working FM register access through ALSA OPL tools. Failure tests include missing port, busy port, and absent OPL hardware.
