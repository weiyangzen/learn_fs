# sources/distributed-fs/ceph-client/drivers/soundwire/Kconfig

## Purpose
Defines the Kconfig surface for the SoundWire subsystem and the in-tree AMD, Cadence, Intel, Qualcomm, and generic bandwidth-allocation components. It controls whether the SoundWire bus core and platform master drivers are built and which helper libraries are selected.

## Important APIs, Types, and Functions
The primary symbol is `SOUNDWIRE`, a tristate menuconfig gated by `ACPI || OF` and `SND_SOC_SDCA_OPTIONAL`. Driver symbols are `SOUNDWIRE_AMD`, `SOUNDWIRE_CADENCE`, `SOUNDWIRE_INTEL`, `SOUNDWIRE_QCOM`, and `SOUNDWIRE_GENERIC_ALLOCATION`. `SOUNDWIRE_AMD` and `SOUNDWIRE_INTEL` select `SOUNDWIRE_GENERIC_ALLOCATION`; Intel additionally selects `SOUNDWIRE_CADENCE` and `AUXILIARY_BUS`; Cadence selects `CRC8`; Qualcomm implies `SLIMBUS`.

## Control Flow
Kconfig has no runtime control flow. At configuration time, enabling `SOUNDWIRE` opens the subordinate driver symbols. Selecting AMD or Intel pulls in the generic allocation module, while Intel also pulls in the Cadence library used by Intel-specific master drivers. Build dependencies enforce ACPI/OF discovery support and ASoC integration for master drivers that expose DAIs.

## State and Persistence Behavior
State is the generated kernel configuration. Tristate values persist in `.config` and affect module linkage through the Makefile. No runtime state is defined here.

## Dependencies and Integration Points
This file feeds `drivers/soundwire/Makefile`, the bus core, ASoC master drivers, and optional libraries. The `SND_SOC_SDCA_OPTIONAL` dependency ties SoundWire enablement to the SDCA helper configuration used by modern audio codecs. The Intel constraints include compatibility expressions for SOF HDA multi-link support and aligned HDA MMIO.

## Risks
Incorrect selects or dependencies can produce missing symbols at link time or hide required drivers from platform configurations. The hidden `SOUNDWIRE_CADENCE` and `SOUNDWIRE_GENERIC_ALLOCATION` symbols are library-like; direct user selection is not intended. Because AMD and Intel select generic allocation, changes to that library affect multiple drivers. Qualcomm only implies SLIMBUS, so builds without SLIMBUS must still compile.

## Test Signals
Configuration matrix tests should cover built-in and module builds for `SOUNDWIRE`, AMD, Intel, Qualcomm, and Cadence-selected-by-Intel paths; ACPI-disabled and OF-only builds; debugfs/IRQ-domain optional objects through Makefile conditionals; and `allyesconfig`, `allmodconfig`, and minimal ASoC configurations.
