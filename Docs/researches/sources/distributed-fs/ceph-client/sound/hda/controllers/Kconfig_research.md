# sources/distributed-fs/ceph-client/sound/hda/controllers/Kconfig

## Purpose
This Kconfig file declares the selectable HD-audio controller drivers: PCI `snd-hda-intel`, NVIDIA Tegra, CIX IPBLOQ, and generic ACPI-described HDA controllers.

## Important APIs, Types, and Functions
There are no runtime APIs. The important symbols are `SND_HDA_INTEL`, `SND_HDA_TEGRA`, `SND_HDA_CIX_IPBLOQ`, and `SND_HDA_ACPI`. They select shared core support (`SND_HDA`) and, where needed, aligned MMIO or Intel DSP configuration support.

## Control Flow
Kconfig controls which controller modules are built and therefore which platform/PCI match tables can bind at runtime. Intel depends on `SND_PCI`; Tegra depends on `ARCH_TEGRA`; CIX depends on `ARCH_CIX || COMPILE_TEST`; ACPI depends on `ACPI`.

## State and Persistence Behavior
The file contributes build-time state only. Selected symbols persist in the generated kernel configuration and affect module availability and dependency closure.

## Dependencies and Integration Points
The symbols integrate controller implementations with the shared `sound/hda/core` module and platform-specific subsystems. Intel additionally selects `SND_INTEL_DSP_CONFIG`, allowing the PCI probe path to defer to SOF/SST drivers when appropriate.

## Risks
Incorrect dependencies can build drivers on platforms missing required bus, clock, reset, or ACPI support, or omit shared HDA pieces needed by the controller. The controller symbols are user-visible module choices and affect module names documented in help text.

## Test Signals
Config tests should verify each symbol builds as `y` and `m`, dependency selections pull in `SND_HDA`, Tegra/CIX select aligned MMIO, Intel selects DSP config, and module names match `snd-hda-intel`, `snd-hda-tegra`, `snd-hda-cix-ipbloq`, and `snd-hda-acpi`.
