# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_irq.h

## Purpose
`xe_irq.h` declares the public interrupt-management interface for Xe and defines the default MSI-X vector index used by the driver.

## Important APIs, Types, And Functions
- `XE_IRQ_DEFAULT_MSIX` is 1, paired with static GuC2Host vector 0 in the implementation.
- Declares init/install/suspend/resume lifecycle functions.
- Declares `xe_irq_enable_hwe()` for per-GT engine interrupt programming.
- Declares dynamic MSI-X request/free helpers for other Xe subsystems.

## Control Flow
Subsystems include this header to interact with IRQ setup or allocate dedicated MSI-X vectors. The implementation decides whether MSI, MSI-X, or memory-backed interrupt handling is active.

## State And Persistence
The header owns no state; it exposes operations over `xe->irq` and hardware masks managed by `xe_irq.c`.

## Dependencies And Integration Points
Depends on Linux interrupt types and forward-declares Xe core structures. It is used by driver probe, PM, GT setup, and subsystems needing MSI-X vectors.

## Risks
Callers using dynamic MSI-X helpers must obey vector lifetime and free allocated vectors. The static default vector constant must stay synchronized with the implementation's `enum xe_irq_msix_static`.

## Test Signals
Build/link tests plus runtime checks for MSI-X dynamic allocation/free and correct default vector reservation.
