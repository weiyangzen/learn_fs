<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/parisc/Kconfig

## Purpose
This Kconfig file defines PA-RISC bus, IOMMU, PCI bridge, legacy bus, chassis, SuperIO, and stable-storage options. It controls which drivers in `drivers/parisc` are built for PA-RISC machines.

## Important APIs, Types, And Functions
The file declares `GSC`, `HPPB`, `IOMMU_CCIO`, `GSC_LASI`, `GSC_WAX`, `ISA`, `GSC_DINO`, `PCI_LBA`, hidden `IOSAPIC` and `IOMMU_SBA`, plus PA-RISC-specific `SUPERIO`, `CHASSIS_LCD_LED`, `PDC_CHASSIS`, `PDC_CHASSIS_WARN`, and `PDC_STABLE`.

## Control Flow
There is no executable control flow. The dependency graph controls build selection: `GSC` selects EISA and I/O port support; `IOMMU_CCIO` depends on GSC; Dino depends on PCI and GSC; LBA enables IOSAPIC and SBA IOMMU by default through hidden bools; chassis warning support depends on procfs; stable storage can be modular.

## State And Persistence
Kconfig choices persist in kernel configuration and determine compiled driver availability. Defaults are mostly `y` for platform features likely present on supported PA-RISC systems.

## Dependencies And Integration Points
The options map directly to the Makefile objects in the same directory. They also gate architecture-level services such as PCI, EISA, procfs, sysfs, LED class support, and I/O port availability.

## Risks
Incorrect dependencies can build drivers without required architecture services or omit required bus/IOMMU drivers. Help text encodes platform coverage knowledge; stale descriptions can lead users to disable necessary hardware support. Defaults to `y` are practical for old platform bootability but increase kernel surface.

## Test Signals
Build matrix coverage should include PCI and non-PCI PA-RISC configs, GSC with/without Dino and CCIO, LBA with implicit IOSAPIC/SBA, procfs-disabled chassis warnings, LED-class-disabled chassis LED support, and modular `PDC_STABLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/Kconfig -->
