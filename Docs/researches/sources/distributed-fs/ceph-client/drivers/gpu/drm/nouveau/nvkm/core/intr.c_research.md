# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/intr.c

## Purpose
This file implements NVKM interrupt controller registration, top-level IRQ handling, interrupt source translation, handler lists, arm/unarm, and per-handler allow/block controls.

## Important APIs, Types, and Functions
Public APIs include `nvkm_intr_ctor`, `nvkm_intr_install`, `nvkm_intr_dtor`, `nvkm_intr_add`, `nvkm_intr_rearm`, `nvkm_intr_unarm`, `nvkm_intr_allow`, `nvkm_intr_block`, `nvkm_inth_add`, `nvkm_inth_allow`, and `nvkm_inth_block`.

## Control Flow
Interrupt providers call `nvkm_intr_add` with leaf count, data mapping, and backend ops. Handlers call `nvkm_inth_add`, which translates subdevice/vector type into leaf/mask and adds the handler to a priority list. IRQ handling locks, unarms top-level sources, rearms MSI, samples pending masks, checks device presence, dispatches allowed handlers by priority, blocks unhandled pending bits to avoid storms, then rearms. Rearm lazily adds legacy subdev handlers from topology.

## State and Persistence Behavior
Device state includes the provider list, priority handler lists, lock, armed flag, IRQ number, allocation flag, and legacy initialization flag. Provider state includes stat/mask arrays. Handler state includes leaf/mask, allowed flag, callback, and list node.

## Dependencies and Integration Points
It depends on NVKM device, subdev, PCI MSI, topology discovery, backend interrupt ops, and subdev interrupt callbacks.

## Risks
IRQ handling runs under a device spinlock, so callbacks must be appropriate. Unhandled bits are blocked, which protects from storms but can mask real interrupts. Translation must match topology and legacy data tables.

## Test Signals
Signals include IRQ install/free, provider add/remove, handler allow/block, pending interrupt dispatch by priority, MSI rearm, unhandled-storm blocking, and legacy topology handler registration.
