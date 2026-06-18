# sources/distributed-fs/ceph-client/drivers/soundwire/irq.c

## Purpose

`irq.c` implements optional IRQ-domain support for SoundWire slave interrupt mapping. It creates a linear IRQ domain per bus, maps slave hardware indices to nested Linux IRQs, and registers device-managed cleanup for slave mappings.

## Important APIs, types, and functions

- `sdw_irq_create()` initializes `bus->irq_chip.name` and creates a linear irqdomain sized to `SDW_FW_MAX_DEVICES`.
- `sdw_irq_delete()` removes the bus IRQ domain.
- `sdw_irq_create_mapping()` maps `slave->index` to `slave->irq` and registers `sdw_irq_dispose_mapping()` as a devm cleanup action.
- `sdw_irq_map()` sets irq chip data to the bus, assigns `bus->irq_chip`, marks the IRQ nested-threaded, and disables probing.

## Control flow

When a SoundWire bus is registered with IRQ-domain support, the bus creates its domain. When a slave is discovered, the core calls `sdw_irq_create_mapping()`, which creates a virtual IRQ from the slave index. On slave device removal, the devm action disposes the mapping. Bus teardown removes the entire domain.

## State and persistence behavior

State is held in `bus->domain`, `bus->irq_chip`, and each `slave->irq`. Mappings live for the slave device lifetime and are cleaned up through devm. No hardware state is programmed here; actual interrupt status and dispatch are handled by bus/controller code.

## Dependencies and integration points

The file depends on `CONFIG_IRQ_DOMAIN`, Linux irqdomain APIs, device-managed actions, and SoundWire bus/slave structures. It integrates with the SoundWire bus core that creates domains and maps slaves, and with slave drivers that request/use nested IRQs.

## Risks and edge cases

- A failed `irq_create_mapping()` only warns; drivers must tolerate `slave->irq == 0`.
- The domain is linear and sized to firmware max devices, so `slave->index` must be stable and in range.
- `sdw_irq_delete()` assumes a valid domain pointer.
- The irq chip callbacks must be populated elsewhere in `bus->irq_chip`; this file only assigns chip identity.

## Test signals

Build with `CONFIG_IRQ_DOMAIN` enabled. Validate domain creation/removal, slave mapping/disposal, failure of mapping allocation, and nested IRQ delivery through a slave driver. KASAN/devm tests should confirm no mapping survives slave removal.
