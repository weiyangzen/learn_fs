# sources/distributed-fs/ceph-client/sound/ppc/Kconfig

## Purpose

This Kconfig file defines ALSA PowerPC sound driver configuration for legacy PowerMac onboard audio and PS3 audio.

## Important APIs, types, and functions

`SND_PPC` gates the submenu on `PPC`. `SND_POWERMAC` depends on `I2C`, `INPUT`, and `PPC_PMAC`, selects `SND_PCM` and `SND_VMASTER`, and builds `snd-powermac`. `SND_POWERMAC_AUTO_DRC` optionally controls automatic dynamic range compression toggling for Tumbler/Snapper. `SND_PS3` depends on `PS3_PS3AV`, selects `SND_PCM`, and builds `snd_ps3`. `SND_PS3_DEFAULT_START_DELAY` provides the driver default silent startup delay.

## Control flow

Kconfig choices determine which Makefile objects are built and which code paths guarded by config macros compile, especially PowerMac PM/auto-DRC behavior and PS3 module defaults.

## State and persistence behavior

There is no runtime state. The selected options become build-time state and default module behavior, including PS3 startup delay.

## Dependencies and integration points

The file integrates the PPC sound subtree with ALSA core, I2C/input subsystems, PowerMac platform support, and PS3 AV support.

## Risks and test signals

Risks include stale dependencies as platform APIs evolve and enabling drivers without required platform services. Test with `allyesconfig`, `allmodconfig`, PowerMac-only, and PS3-only builds, plus dependency checks for `snd-powermac` and `snd_ps3`.
