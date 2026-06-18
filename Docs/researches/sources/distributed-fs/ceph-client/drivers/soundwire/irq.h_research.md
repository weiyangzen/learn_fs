# sources/distributed-fs/ceph-client/drivers/soundwire/irq.h

## Purpose

`irq.h` declares the local SoundWire IRQ-domain helpers and provides no-op inline stubs when IRQ domains are disabled. It lets bus code call IRQ setup uniformly across configurations.

## Important APIs, types, and functions

- `sdw_irq_create()` creates a bus IRQ domain when `CONFIG_IRQ_DOMAIN` is enabled and otherwise returns success.
- `sdw_irq_delete()` removes a bus IRQ domain or does nothing in stub builds.
- `sdw_irq_create_mapping()` maps a slave IRQ or does nothing in stub builds.

## Control flow

Callers include this header and invoke the helpers during bus/slave setup and teardown. The preprocessor selects real declarations or no-op definitions based on `IS_ENABLED(CONFIG_IRQ_DOMAIN)`.

## State and persistence behavior

The header itself has no state. In stub builds, no `bus->domain` or `slave->irq` state is created by these helpers.

## Dependencies and integration points

It depends on SoundWire public types and firmware-node types. It is paired with `irq.c` and used by the SoundWire bus core.

## Risks and edge cases

- Stub builds silently skip IRQ mapping; slave drivers must not assume an IRQ exists.
- Call sites must be valid in both compiled-in and no-op configurations.
- The header uses `IS_ENABLED`, so the inline path also applies when IRQ domain support is a module-incompatible absence.

## Test signals

Compile with IRQ domain support enabled and disabled. In disabled builds, verify bus registration still succeeds and slave drivers handle absent IRQs gracefully.
