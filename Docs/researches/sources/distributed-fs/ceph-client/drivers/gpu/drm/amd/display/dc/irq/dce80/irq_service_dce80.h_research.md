# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.h

## Purpose

`irq_service_dce80.h` declares the DCE80 IRQ service constructor.

## Important APIs, Types, And Functions

The public API is `dal_irq_service_dce80_create(struct irq_service_init_data *init_data)`.

## Control Flow

DCE80 resource initialization calls this constructor and receives an IRQ service using DCE80 table entries and shared DCE source translation.

## State And Persistence Behavior

No state is in the header; constructed service state lives in the allocated IRQ service object.

## Dependencies And Integration Points

It depends on common IRQ service definitions and integrates with DCE80 build and resource initialization.

## Risks And Test Signals

Risks are declaration/implementation drift or missing Makefile inclusion. Test signals include DCE80 build coverage and runtime HPD/vblank/page-flip interrupts.
