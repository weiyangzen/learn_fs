# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_helper.c

## Purpose

`audio_helper.c` provides ASoC cleanup and DAPM helper routines needed by Greybus audio's dynamic topology model.

## Important APIs, Types, and Functions

Exports are `gbaudio_dapm_link_component_dai_widgets()`, `gbaudio_dapm_free_controls()`, and `gbaudio_remove_component_controls()`. Internal helpers locate matching stream widgets, free DAPM paths/widgets, and remove ALSA controls by element ID.

## Control Flow

When a card is already instantiated, Greybus module registration can call the DAI-widget linker to scan card widgets for matching stream names. On module unregister, the codec calls component-control removal and DAPM widget freeing. Widget cleanup removes list nodes, associated paths in both directions, kcontrol lists, names, stream names, and the widget object.

## State and Persistence Behavior

No persistent state is owned. The functions mutate ASoC card widget/control lists and free dynamically allocated objects for a module.

## Dependencies and Integration Points

It depends on ALSA core, ASoC component/card/DAPM internals, and is called by `audio_codec.c`.

## Risks and Edge Cases

The link helper currently logs potential DAI/widget links but the actual `snd_soc_dapm_add_path()` code is commented out. Manual DAPM widget/path removal relies on ASoC internal list layout and may break across kernel versions. Widget lookup by name can remove the wrong object if names collide within a DAPM context. Error handling logs failed control removals but continues.

## Test Signals

Test dynamic module add/remove repeatedly under lockdep/KASAN, duplicate widget names, routes involving shared paths, controls with prefixes, card instantiated and not instantiated, and current ASoC list invariants.
