# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.h

## Purpose

`irq_service_dcn10.h` declares the DCN10 IRQ service constructor.

## Important APIs, Types, And Functions

The public API is `dal_irq_service_dcn10_create(struct irq_service_init_data *init_data)`, returning a constructed IRQ service for DCN 1.0 hardware.

## Control Flow

DCN10 resource initialization calls the constructor. The returned service provides the DCN10 source table and translation vtable to common IRQ dispatch.

## State And Persistence Behavior

The header stores no state. Constructed service state is allocated in the implementation and hardware interrupt state is programmed by common IRQ operations.

## Dependencies And Integration Points

It depends on common IRQ service definitions and integrates with DCN10 resource-pool creation and display interrupt handling.

## Risks And Test Signals

Risks are constructor declaration drift or missing object linkage. Test signals include DCN10 build coverage and runtime HPD, page-flip, vblank, vline0, and vupdate interrupts.
