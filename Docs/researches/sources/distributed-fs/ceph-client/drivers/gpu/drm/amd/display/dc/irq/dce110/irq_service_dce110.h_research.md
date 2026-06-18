# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce110/irq_service_dce110.h

## Purpose

`irq_service_dce110.h` publishes the DCE110 IRQ service constructor and shared helper functions used by later DCE IRQ service implementations.

## Important APIs, Types, And Functions

It declares `dal_irq_service_dce110_create`, `to_dal_irq_source_dce110`, `dal_irq_service_dummy_set`, `dal_irq_service_dummy_ack`, and `dce110_vblank_set`. These helpers are reused by DCE80/DCE120 and DCE60 variants where source translation or dummy/vblank behavior is compatible.

## Control Flow

ASIC resource code calls the constructor to obtain an IRQ service. Other IRQ services include this header to assign the shared translator or function pointers in their own IRQ tables.

## State And Persistence Behavior

The header stores no state. It exposes functions that mutate IRQ masks, acknowledgements, logging, and timing-generator vertical interrupt state in implementation files.

## Dependencies And Integration Points

It depends on the common `irq_service.h` definitions. It integrates with DCE generation IRQ services, common IRQ dispatch, and timing-generator vblank programming.

## Risks And Test Signals

Risks include signature drift with common IRQ service types, accidental reuse of DCE110 source mapping on incompatible hardware, and missing dummy-handler visibility. Test signals are build coverage for all includers and runtime vblank/HPD/PFLIP IRQs on DCE110-compatible ASICs.
