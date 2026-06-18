# sources/distributed-fs/ceph-client/sound/soc/amd/acp/Makefile

## Purpose
`sound/soc/amd/acp/Makefile` builds the modular AMD ACP common stack: PCM, I2S, PDM, PCI, platform-specific drivers, ACPI matching, legacy/SOF machine drivers, and SoundWire helpers.

## Important APIs, Types, And Functions
Composites include `snd-acp-pcm-y`, `snd-acp-i2s-y`, `snd-acp-pdm-y`, `snd-acp-legacy-common-y`, `snd-acp-pci-y`, `snd-amd-sdw-acpi-y`, `snd-amd-acpi-mach-y`, platform drivers `snd-acp-renoir-y`, `snd-acp-rembrandt-y`, `snd-acp63-y`, `snd-acp70-y`, machine drivers `snd-acp-mach-y`, `snd-acp-legacy-mach-y`, `snd-acp-sof-mach-y`, ACPI match modules, and SoundWire machine modules.

## Control Flow
There is no runtime flow. Kbuild composes modules and objects according to the `CONFIG_SND_*` symbols declared in the adjacent Kconfig.

## State And Persistence
Only build artifacts persist. Runtime state belongs to the generated drivers.

## Dependencies And Integration Points
The Makefile is included through `sound/soc/amd/Makefile` when `SND_AMD_ACP_CONFIG` selects the `acp/` subdirectory. It ties the common code in `acp-i2s.c`, `acp-legacy-common.c`, and `acp-legacy-mach.c` to module names.

## Risks And Edge Cases
Machine modules aggregate subdirectory objects such as `acp3x-es83xx`. Kconfig and Makefile drift would break module composition or exported namespace availability. Some objects import/export namespaces, so missing module pieces can fail at link or load time.

## Test Signals
Signals include successful module builds for PCM/I2S/PDM/common/PCI/platform/machine/SDW variants and namespace import/export checks under `modpost`.
