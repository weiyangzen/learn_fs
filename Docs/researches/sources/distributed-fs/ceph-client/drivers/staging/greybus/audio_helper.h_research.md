# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_helper.h

## Purpose

`audio_helper.h` declares the Greybus audio ASoC helper functions used for DAPM widget linking/freeing and component control removal.

## Important APIs, Types, and Functions

It declares `gbaudio_dapm_link_component_dai_widgets()`, `gbaudio_dapm_free_controls()`, and `gbaudio_remove_component_controls()`.

## Control Flow

The codec includes this header to call helpers during dynamic module registration and unregistration.

## State and Persistence Behavior

No state is defined. The declared helpers mutate ASoC card/component state owned elsewhere.

## Dependencies and Integration Points

It assumes ASoC types such as `struct snd_soc_card`, `struct snd_soc_dapm_context`, `struct snd_soc_dapm_widget`, `struct snd_soc_component`, and `struct snd_kcontrol_new` are visible through including C files.

## Risks and Edge Cases

The header does not include ASoC headers directly, so include order matters. Any helper signature change must stay synchronized with `audio_codec.c`.

## Test Signals

Compile with strict prototypes and include-order checks in every Greybus audio object that uses the helper functions.
