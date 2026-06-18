# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce60/irq_service_dce60.h

## Purpose

`irq_service_dce60.h` declares DCE60 IRQ-service entry points for SI-era display support.

## Important APIs, Types, And Functions

It declares `to_dal_irq_source_dce60` for source/ext translation and `dal_irq_service_dce60_create` for allocation/construction.

## Control Flow

Resource code calls the constructor when selecting the DCE60 IRQ service. Common interrupt dispatch later calls the translator through the service vtable.

## State And Persistence Behavior

The header stores no state. Created services carry the DCE60 source table and mutate hardware interrupt registers through common IRQ helpers.

## Dependencies And Integration Points

It depends on `../irq_service.h` and integrates with SI/DCE60 resource initialization and common IRQ dispatch.

## Risks And Test Signals

Risks include SI build exclusion hiding declaration drift and incorrect translator assignment. Test signals are `CONFIG_DRM_AMD_DC_SI` builds and runtime HPD/vblank/PFLIP interrupts on supported hardware.
