# sources/distributed-fs/ceph-client/sound/Kconfig

## Purpose

This top-level sound Kconfig file declares legacy sound support, OSS compatibility controls, ALSA, all ALSA child driver menus, and the generic legacy `AC97_BUS` symbol that can be selected by non-sound drivers sharing AC97 hardware.

## Important APIs, types, and functions

Important symbols are `SOUND`, `SOUND_OSS_CORE`, `SOUND_OSS_CORE_PRECLAIM`, `SND`, and `AC97_BUS`. The file sources Kconfig files for sound core, drivers, ISA, PCI, HDA, PowerPC, AC97, AOA, ARM, USB, FireWire, SoC, virtio, and other platform-specific sound trees.

## Control Flow

Kconfig nesting gates OSS and ALSA options under `SOUND`; ALSA submenus appear only under `SND`. `AC97_BUS` is outside the `SOUND` block so it remains buildable without the full sound subsystem.

## State and Persistence

Selected config values persist in `.config` and control compiled sound subsystems. There is no runtime state.

## Dependencies and Integration Points

It integrates with the kernel configuration system and the top-level sound Makefile. AC97 and AOA files researched in this item are sourced from here.

## Risks and Test Signals

Risks include dependency ordering for bus-specific Kconfig files, misplaced options causing missing symbols, and AC97 buildability when sound is disabled. Test signals are `allyesconfig`, `allmodconfig`, and minimal configs selecting only `AC97_BUS`.
