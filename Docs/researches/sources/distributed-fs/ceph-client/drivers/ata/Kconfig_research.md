# sources/distributed-fs/ceph-client/drivers/ata/Kconfig

## Purpose
`drivers/ata/Kconfig` defines the kernel configuration menu for libata, SATA, PATA, AHCI, SFF, platform, DMA, ACPI, and legacy ATA drivers. It controls which ATA subsystems and host drivers can be built and which dependencies/selects are applied.

## Important APIs, Types, And Functions
This is Kconfig, not C. Key symbols include `ATA`, `SATA_HOST`, `ATA_SFF`, `ATA_BMDMA`, `PATA_TIMINGS`, `ATA_VERBOSE_ERROR`, `ATA_FORCE`, `ATA_ACPI`, `SATA_ZPODD`, `SATA_PMP`, AHCI host drivers such as `SATA_AHCI`, `SATA_ACARD_AHCI`, and many platform/SFF/PATA driver symbols. `SATA_ACARD_AHCI` is the symbol that builds `acard-ahci.o`.

## Control Flow
Kconfig control flow gates symbols under `if ATA`, `if HAS_DMA`, `if ATA_SFF`, and `if ATA_BMDMA`. Selecting `ATA` pulls in SCSI and GLOB. Driver symbols express dependencies such as PCI, OF, architecture, DMA, or `COMPILE_TEST`, and many select `SATA_HOST`, `PATA_TIMINGS`, or helper subsystems.

## State And Persistence
The persistent output is the kernel `.config`. Those config choices control built-in versus module behavior and which Makefile `obj-*` entries are active.

## Dependencies
Kconfig depends on global kernel symbols such as `HAS_IOMEM`, `BLOCK`, `SCSI`, `HAS_DMA`, `PCI`, `ACPI`, `PM`, architecture symbols, `OF`, `DMADEVICES`, `HAS_IOPORT`, and many SoC-specific symbols.

## Integration Points
`drivers/ata/Makefile` consumes these config symbols to build libata and individual drivers. Users, distro configs, and defconfigs select options here to enable storage hardware. The ACard AHCI driver is enabled by `CONFIG_SATA_ACARD_AHCI`, depends on PCI, and selects `SATA_HOST`.

## Risks
Dependency mistakes can expose drivers on unsupported architectures or hide valid hardware. Overbroad `select` usage can force helper subsystems without their dependencies. Because `ATA` selects SCSI, disabling ATA can remove disk access on systems depending on libata. Experimental or legacy drivers need careful dependency gating around IO port, DMA, and architecture assumptions.

## Test Signals
Run `make olddefconfig`/`allnoconfig`/`allyesconfig`/`randconfig`, verify no unmet dependency warnings, build representative AHCI/PATA configs, confirm `CONFIG_SATA_ACARD_AHCI=m/y` builds `acard-ahci.o`, and boot-test storage discovery on supported hardware or emulation.
