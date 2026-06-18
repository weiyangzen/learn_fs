# sources/distributed-fs/ceph-client/drivers/ata/pata_of_platform.c

## Purpose
Adapts Open Firmware `ata-generic` nodes to the generic `__pata_platform_probe()` helper, letting device-tree systems instantiate simple PIO-only ATA interfaces.

## Important APIs, Types, And Functions
`pata_of_platform_probe()` is the only substantive function. It resolves two address resources with `of_address_to_resource()`, obtains an optional IRQ with `platform_get_irq_optional()`, parses `reg-shift`, `pio-mode`, and `ata-generic,use16bit`, builds a cumulative PIO mask, and calls `__pata_platform_probe()`.

## Control Flow
Probe fails if IO or CTL resources are missing, accepts no IRQ as polling mode, defaults absent `pio-mode` to PIO0, rejects modes above PIO6, and delegates all host allocation, register mapping, and activation to `pata_platform.c`.

## State And Persistence
No private persistent state is allocated here. The resulting ATA host state is owned by the generic platform helper and removed by `ata_platform_remove_one`.

## Dependencies And Integration Points
Depends on OF address translation, `ata_platform.h`, libata SFF support, and the `ata-generic` compatible string.

## Risks And Edge Cases
Incorrect DT resource ordering or bad `reg-shift` gives wrong taskfile register addresses. IRQ values less than zero except `-ENXIO` are propagated, while no IRQ intentionally becomes polling. The 16-bit flag changes the data transfer callback selected by the helper.

## Test Signals
DT nodes with and without IRQ, several `pio-mode` values, invalid PIO mode rejection, nonzero `reg-shift`, 16-bit transfer property, and removal via the platform driver's generic remove path.
