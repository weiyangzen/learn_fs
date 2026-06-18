# sources/distributed-fs/ceph-client/sound/soc/amd/Kconfig

## Purpose
`sound/soc/amd/Kconfig` declares AMD ASoC options for legacy ACP 2.x, ACP3x/Renoir/Vangogh/Yellow Carp/Pink Sardine families, machine drivers, shared ACP configuration selection, ACP common infrastructure, and SoundWire-capable newer platforms.

## Important APIs, Types, And Functions
Important symbols include `SND_SOC_AMD_ACP`, `SND_SOC_AMD_CZ_DA7219MX98357_MACH`, `SND_SOC_AMD_CZ_RT5645_MACH`, `SND_SOC_AMD_ST_ES8336_MACH`, `SND_SOC_AMD_ACP3x`, `SND_SOC_AMD_RENOIR`, `SND_SOC_AMD_ACP5x`, `SND_SOC_AMD_ACP6x`, `SND_AMD_ACP_CONFIG`, `SND_SOC_AMD_ACP63_TOPLEVEL`, `SND_SOC_AMD_SOUNDWIRE`, `SND_SOC_AMD_PS`, and `SND_SOC_AMD_PS_MACH`. It sources `sound/soc/amd/acp/Kconfig` for common ACP modules and machine drivers.

## Control Flow
There is no runtime flow. Config choices select codec drivers, ACPI matching, common ACP support, SOF/SoundWire helpers, and platform subdirectories. Many platform symbols select `SND_AMD_ACP_CONFIG`, which builds the machine configuration module used to choose legacy versus SOF paths.

## State And Persistence
Configuration state persists in `.config`; runtime state is held by the platform and machine drivers enabled by those symbols.

## Dependencies And Integration Points
The file integrates AMD ASoC with X86/PCI/ACPI, I2C/SPI/GPIO, codec drivers, SOF firmware matching, SoundWire, and the shared `amd/acp` common modules. It controls build inclusion in `sound/soc/amd/Makefile`.

## Risks And Edge Cases
Dependency and select chains are broad. Enabling a machine driver without required firmware, ACPI IDs, GPIOs, or codecs can build successfully but fail to probe. The legacy, SOF, and SoundWire paths overlap, so config and runtime machine selection must agree.

## Test Signals
Signals include build matrices for old ACP 2.x, ACP3x, Renoir, Vangogh, Yellow Carp, ACP6.3/7.x, SOF, and SoundWire configs; module dependency checks; and ACPI probe tests confirming the expected machine driver is selected.
