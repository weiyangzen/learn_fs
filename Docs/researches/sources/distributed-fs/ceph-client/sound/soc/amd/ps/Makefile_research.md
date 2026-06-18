# sources/distributed-fs/ceph-client/sound/soc/amd/ps/Makefile

## Purpose
This Makefile wires the AMD Pink Sardine (`ps`) ASoC platform objects into the kernel build. It declares composite module object lists for the ACP PCI/common layer, the PDM DMA engine, the SoundWire DMA engine, and the DMIC machine driver, then attaches those modules to Kconfig symbols.

The file has no runtime code, but it defines which C files are linked together and which features appear when `CONFIG_SND_SOC_AMD_PS` or `CONFIG_SND_SOC_AMD_PS_MACH` is enabled.

## Important APIs, types, and build targets
Composite targets:

- `snd-pci-ps-y := pci-ps.o ps-common.o` links the common PCI driver with platform-specific hardware operation callbacks from `ps-common.c`.
- `snd-ps-pdm-dma-y := ps-pdm-dma.o` builds the ACP PDM DMA component.
- `snd-soc-ps-mach-y := ps-mach.o` builds the Pink Sardine DMIC machine driver.
- `snd-ps-sdw-dma-y := ps-sdw-dma.o` builds the ACP SoundWire DMA component.

Kconfig-driven objects:

- `obj-$(CONFIG_SND_SOC_AMD_PS)` includes `snd-pci-ps.o`, `snd-ps-pdm-dma.o`, and `snd-ps-sdw-dma.o`.
- `obj-$(CONFIG_SND_SOC_AMD_PS_MACH)` includes `snd-soc-ps-mach.o`.

## Control flow
Build-time flow:

1. Kbuild evaluates the relevant Kconfig symbols.
2. If `CONFIG_SND_SOC_AMD_PS` is enabled, the PCI driver and both DMA platform components are built.
3. If `CONFIG_SND_SOC_AMD_PS_MACH` is enabled, the DMIC-only machine driver is built.
4. At runtime, `pci-ps.c` probes ACP6.3/7.x PCI devices, calls hardware ops from `ps-common.c`, and registers platform devices named for the PDM and SoundWire DMA modules. `ps-mach.c` can then bind the DMIC card when the PCI layer registers the `acp_ps_mach` platform device.

## State and persistence behavior
The Makefile stores no runtime state. Its build selections influence persistent kernel/module artifacts: which `.o` files are linked into built-in code or loadable modules, which platform drivers are registered, and whether runtime platform-device registration can find a matching driver.

## Dependencies and integration points
The Makefile depends on Kconfig symbols defined elsewhere in the AMD ASoC tree, especially `CONFIG_SND_SOC_AMD_PS` and `CONFIG_SND_SOC_AMD_PS_MACH`. Its targets correspond to source files in the same directory:

- `pci-ps.c` and `ps-common.c` depend on `acp63.h` for shared constants, data structures, and hardware-op declarations.
- `ps-pdm-dma.c` and `ps-sdw-dma.c` expose ALSA component/platform functionality used by machine drivers and SoundWire managers.
- `ps-mach.c` registers the DMIC capture card that references the `acp_ps_pdm_dma.0` CPU/platform DAI and `dmic-codec.0`.

## Risks and edge cases
If `CONFIG_SND_SOC_AMD_PS` is enabled without the machine driver for a DMIC-only configuration, the PCI and PDM DMA pieces may probe but no complete ALSA card will appear for that path. Conversely, building `CONFIG_SND_SOC_AMD_PS_MACH` without the platform device producer would leave the machine driver with nothing to bind. Splitting `pci-ps.o` from `ps-common.o` would break hardware operation resolution because the PCI probe initializes callbacks declared in `acp63.h` and defined in `ps-common.c`.

SoundWire support also depends on broader SoundWire and ACPI support; this Makefile builds the DMA side under `CONFIG_SND_SOC_AMD_PS`, but runtime SoundWire probing still depends on the rest of the kernel configuration and firmware description.

## Test signals
Useful checks include:

- Kernel build with `CONFIG_SND_SOC_AMD_PS=m/y` and `CONFIG_SND_SOC_AMD_PS_MACH=m/y`.
- Module inspection confirming expected modules or built-in objects include `snd-pci-ps`, `snd-ps-pdm-dma`, `snd-ps-sdw-dma`, and `snd-soc-ps-mach`.
- Boot probe on ACP6.3/7.x systems verifying the PCI module registers PDM/SoundWire platform devices and matching component drivers bind.
- ALSA card enumeration for DMIC-only and SoundWire configurations.
