# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mert.h

## Purpose
`xe_mert.h` defines MERT state and declares the MERT lifecycle/IRQ APIs, with IRQ no-op support when PCI IOV is disabled.

## Important APIs, Types, And Functions
- `struct xe_mert` contains the spinlock, invalidation-triggered flag, and completion.
- Declares early init, LMTT invalidation, and IRQ handler under `CONFIG_PCI_IOV`.
- Provides a no-op `xe_mert_irq_handler()` stub for non-IOV builds.

## Control Flow
Root tile initialization sets up the structure, LMTT code calls invalidation, and IRQ code calls the handler on relevant master interrupt bits.

## State And Persistence
The state lives in the root tile for the device lifetime. The header owns no storage by itself.

## Dependencies And Integration Points
Depends on Linux completion/spinlock/types and forward-declares `struct xe_device`. It links MERT into SR-IOV, LMTT, and IRQ paths.

## Risks
Only the IRQ handler is stubbed for non-IOV builds; callers of init/invalidate must be compiled under the same feature guard. The structure is synchronization-sensitive and must be initialized before invalidation or IRQ handling.

## Test Signals
Build both PCI IOV and non-IOV configurations; runtime test init-before-use and invalidation timeout/completion paths.
