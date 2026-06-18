# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.h

## Purpose

`irq_service_dce120.h` declares the DCE120 IRQ service constructor.

## Important APIs, Types, And Functions

The single public API is `dal_irq_service_dce120_create(struct irq_service_init_data *init_data)`, returning a constructed `struct irq_service` or NULL on allocation failure.

## Control Flow

Resource initialization calls the constructor for DCE12 ASICs. The returned service uses the DCE120 source table and shared DCE translator.

## State And Persistence Behavior

No state is stored in the header. Constructed service state lives in the allocated `irq_service` object and hardware registers programmed by the implementation.

## Dependencies And Integration Points

It depends on `../irq_service.h` and integrates with DCE12 resource-pool creation and common interrupt dispatch.

## Risks And Test Signals

Risks are limited to constructor declaration drift or missing build inclusion. Test signals are successful DCE12 builds and runtime interrupt delivery on DCE12 hardware.
