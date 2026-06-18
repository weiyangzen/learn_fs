# sources/distributed-fs/ceph-client/sound/soc/amd/acp/Kconfig

## Purpose
`sound/soc/amd/acp/Kconfig` declares the newer common AMD ACP ASoC infrastructure, platform drivers for Renoir/Rembrandt/ACP6.3/ACP7.0, shared PCM/I2S/PDM components, ACPI machine matching, legacy/SOF machine drivers, and SoundWire machine support.

## Important APIs, Types, And Functions
Important symbols include `SND_SOC_AMD_ACP_COMMON`, `SND_SOC_ACPI_AMD_MATCH`, `SND_SOC_AMD_ACP_PDM`, `SND_SOC_AMD_ACP_LEGACY_COMMON`, `SND_SOC_AMD_ACP_I2S`, `SND_SOC_AMD_ACPI_MACH`, `SND_SOC_AMD_ACP_PCM`, `SND_SOC_AMD_ACP_PCI`, `SND_AMD_ASOC_RENOIR`, `SND_AMD_ASOC_REMBRANDT`, `SND_AMD_ASOC_ACP63`, `SND_AMD_ASOC_ACP70`, `SND_SOC_AMD_MACH_COMMON`, `SND_SOC_AMD_LEGACY_MACH`, `SND_SOC_AMD_SOF_MACH`, SoundWire machine symbols, and `SND_AMD_SOUNDWIRE_ACPI`.

## Control Flow
There is no runtime flow. Enabling `SND_SOC_AMD_ACP_COMMON` exposes internal module symbols and platform choices. Platform symbols select PCM/I2S/PDM/common/machine pieces. Machine symbols select codec dependencies and shared machine helpers. SoundWire symbols add SDW utility and codec dependencies.

## State And Persistence
Build configuration persists in `.config`. Runtime state is in the built ACP PCI/platform, PCM, I2S, PDM, and machine drivers.

## Dependencies And Integration Points
This file is sourced by `sound/soc/amd/Kconfig` and paired with `sound/soc/amd/acp/Makefile`. It integrates with X86, PCI, ACPI, AMD_NODE, I2C, SoundWire, SOF, codec drivers, and ASoC ACPI matching.

## Risks And Edge Cases
The select graph is complex and can pull many codec drivers into a build. Platform symbols require matching PCI/ACPI hardware and machine tables. SoundWire variants depend on both AMD SoundWire support and codec-specific SDW drivers.

## Test Signals
Build matrices should cover each platform symbol, legacy versus SOF machines, SoundWire legacy/SOF machines, and ACPI match helpers, with module dependency checks for selected codec drivers.
