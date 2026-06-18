# sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx.c

## Purpose

`cs46xx.c` is the top-level PCI module wrapper for Cirrus Logic Sound Fusion CS46xx-based sound cards. It provides module parameters, PCI device matching, ALSA card allocation, high-level device construction order, optional new-DSP PCM devices, MIDI/gameport startup, card naming, registration, and PCI driver binding. Most hardware logic is delegated to functions declared in `cs46xx.h` and implemented in the companion library/DSP files.

## Important APIs, Types, and Functions

- Module parameters: `index`, `id`, `enable`, `external_amp`, `thinkpad`, and `mmap_valid` configure each ALSA card slot.
- `snd_cs46xx_ids[]` matches Cirrus PCI device IDs 0x6001, 0x6003, and 0x6004, corresponding to CS4280, CS4612, and CS4615 families.
- `snd_card_cs46xx_probe()` is the PCI probe function. It allocates an ALSA card with embedded `struct snd_cs46xx`, calls the lower-level create/mixer/PCM/MIDI/DSP functions, and registers the card.
- `cs46xx_driver` wires the probe, ID table, and optional `snd_cs46xx_pm` power-management operations into the PCI core.
- `module_pci_driver(cs46xx_driver)` supplies module init/exit boilerplate.

## Control Flow

On PCI probe, the static `dev` index selects the current module-parameter slot. Disabled slots are skipped with `-ENOENT`; too many devices return `-ENODEV`. The function allocates a managed ALSA card, obtains the embedded `struct snd_cs46xx`, and calls `snd_cs46xx_create(card, pci, external_amp[dev], thinkpad[dev])` for low-level PCI/hardware initialization.

After hardware creation, probe sets `chip->accept_valid` from `mmap_valid[dev]`, creates the primary PCM device, conditionally creates rear and IEC958 PCM devices when `CONFIG_SND_CS46XX_NEW_DSP` is enabled, builds mixer controls, optionally creates center/LFE PCM when two AC97 codecs are present, creates MIDI, starts the DSP, starts gameport support, sets user-visible card strings, registers the ALSA card, stores PCI driver data, and advances `dev`.

Error handling uses a common `error:` label to free the ALSA card. Because card allocation is devres-managed through `snd_devm_card_new()`, teardown integrates with device lifecycle, but explicit `snd_card_free(card)` is still used on probe failure before registration.

## State and Persistence Behavior

This file maintains only the static `dev` probe index and module-parameter arrays. The meaningful runtime state is stored in `struct snd_cs46xx` allocated as card private data and initialized by lower-level functions. `mmap_valid` is copied into `chip->accept_valid` and affects OSS mmap-valid reporting. No persistent storage is used.

## Dependencies and Integration Points

The wrapper depends on Linux PCI/module/init headers, ALSA core/initval, and the local `cs46xx.h` declarations. It is tightly coupled to `cs46xx_lib.c` for `snd_cs46xx_create()`, PCM, mixer, MIDI, DSP start, and gameport implementations, and to optional DSP objects under `CONFIG_SND_CS46XX_NEW_DSP`. Power management is provided externally through `snd_cs46xx_pm`.

## Risks and Edge Cases

- The static `dev` counter is incremented only on disabled slots and successful registration; repeated probe failures before increment can reuse the same module-parameter slot.
- Optional new-DSP paths add several device creation steps and a dependency on `chip->nr_ac97_codecs` for center/LFE PCM creation.
- `card->private_data` is assigned to `chip` after `snd_cs46xx_create()`, although it already came from card private storage; this is redundant but harmless if lower-level code does not replace private data.
- DSP startup occurs after MIDI creation and mixer/PCM creation; failures late in probe tear down the whole card.

## Test Signals

Validation should include probe and removal for supported PCI IDs, module-parameter slot behavior with multiple cards, `enable=false` handling, primary PCM creation, new-DSP build behavior with rear/IEC958/center-LFE devices, MIDI creation, DSP start failure unwinding, gameport setup, card longname formatting, and suspend/resume callback registration when PM sleep is configured.
