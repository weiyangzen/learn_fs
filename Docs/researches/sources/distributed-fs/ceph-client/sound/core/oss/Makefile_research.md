# sources/distributed-fs/ceph-client/sound/core/oss/Makefile

## Purpose
This Makefile defines the build composition for ALSA OSS emulation components under `sound/core/oss`.

## Important APIs, Types, and Functions
It builds `snd-mixer-oss` from `mixer_oss.o`. It builds `snd-pcm-oss` from `pcm_oss.o` and conditionally adds plugin objects `pcm_plugin.o`, `io.o`, `copy.o`, `linear.o`, `mulaw.o`, `route.o`, and `rate.o` when `CONFIG_SND_PCM_OSS_PLUGINS` is enabled. Final object inclusion is gated by `CONFIG_SND_MIXER_OSS` and `CONFIG_SND_PCM_OSS`.

## Control Flow and State
There is no runtime state. Build-time state is controlled entirely by Kconfig symbols and object lists.

## Dependencies and Integration Points
The file integrates OSS mixer and PCM emulation with the kernel build system. The plugin source files in this research set are only linked into OSS PCM emulation when plugin support is enabled.

## Risks and Test Signals
Risks are missing plugin objects when PCM OSS format conversion is expected, or unintended object inclusion when Kconfig changes. Test signals are build matrix coverage for `CONFIG_SND_MIXER_OSS`, `CONFIG_SND_PCM_OSS`, and `CONFIG_SND_PCM_OSS_PLUGINS`, plus module load tests for resulting `snd-mixer-oss` and `snd-pcm-oss` modules.
