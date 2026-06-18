# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_maxim_common.h

Purpose: Header exposing Maxim amplifier constants and helper entry points for Intel SOF board drivers.

Important APIs, types, and functions: It defines codec DAI names and ACPI-derived device names for MAX98373, MAX98390, MAX98357A, and MAX98360A. It declares link patch helpers (`max_98373_dai_link()`, `max_98390_dai_link()`, `max_98357a_dai_link()`, `max_98360a_dai_link()`) and codec-conf helpers for multi-amp prefix setup.

Control flow and integration: Machine drivers call these helpers after the common board helper creates an amp DAI link, selecting the helper by detected `enum snd_soc_acpi_intel_codec` amp type.

State and persistence: No mutable state is declared in the header.

Dependencies: ASoC and Intel ACPI SSP codec identifiers.

Risks: DAI names and ACPI component names must match codec drivers and firmware descriptions. Test signals include compile-time API use across board drivers and runtime detection of each supported Maxim amp family.
