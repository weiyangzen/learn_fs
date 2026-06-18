# sources/distributed-fs/ceph-client/drivers/ssb/driver_gige.c

## Purpose
Built-in driver for the SSB Gigabit Ethernet core that exposes the core as a pseudo PCI controller/device so standard PCI-oriented Ethernet plumbing can bind and receive fixed resources/IRQ routing.

## Important APIs, Types, and Functions
Defines SSB ID table for `SSB_DEV_ETHERNET_GBIT`, SSB driver `ssb_gige_driver`, PCI config-space read/write ops, `ssb_gige_probe`, `pdev_is_ssb_gige_core`, `ssb_gige_pcibios_plat_dev_init`, `ssb_gige_map_irq`, `ssb_gige_init`, and `ssb_gige_exit`.

## Control Flow
Probe allocates `struct ssb_gige`, initializes PCI controller/resources/ops, enables the SSB device, derives BAR0 base from `SSB_ADMATCH1`, writes emulated PCI BAR/command registers, configures write flushing, adjusts GMII/RGMII TMSLOW bits, stores driver data, and registers the PCI controller. Platform PCI fixups later match the pseudo bus ops, overwrite PCI resource 0, and assign IRQ `ssb_mips_irq(sdev)+2`.

## State and Persistence
Runtime state is allocated `struct ssb_gige` with spinlock, PCI ops/controller, resources, and `has_rgmii`. Hardware state includes PCI config shadow registers, shim flush control, and TMSLOW DLL/bypass bits.

## Dependencies and Integration Points
Integrates with SSB driver core, MIPS PCI controller registration, embedded PCI BIOS callbacks, `ssb_admatch_base`, and Linux PCI resource/IRQ setup.

## Risks
Only slot/function zero is emulated. Resource naming is used by `pdev_is_ssb_gige_core`, so changes can break detection. IRQ is hard-coded relative to MIPS IRQ assignment. Flush behavior notes that IRQ handlers must manually flush writes.

## Test Signals
GigE core should register a PCI controller, expose fixed BAR0 and IRQ, select RGMII/GMII path correctly, and allow the Ethernet PCI driver to probe. Config-space accesses outside function zero should return device-not-found.
