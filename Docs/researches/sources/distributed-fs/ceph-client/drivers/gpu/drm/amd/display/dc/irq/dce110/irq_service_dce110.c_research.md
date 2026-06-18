# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce110/irq_service_dce110.c

## Purpose

`irq_service_dce110.c` implements the DCE 11 IRQ source table, source-id translator, HPD acknowledge behavior, dummy handlers, vblank enable helper, constructor, and allocator for the DCE110 IRQ service.

## Important APIs, Types, And Functions

`hpd_ack` acknowledges an HPD interrupt, reads delayed sense status, toggles interrupt polarity based on current connection status, and writes the control register. `dal_irq_service_dummy_set` and `dal_irq_service_dummy_ack` log errors for unsupported sources. `dce110_vblank_set` arms the timing generator vertical interrupt when enabling vblank, then delegates generic mask programming. `irq_source_info_dce110` maps DAL IRQ sources to DCE110 HPD, HPDRX, PFLIP, VUPDATE, VBLANK, GPIO, DDC, sink, underflow, DMCU, and VBIOS entries. `to_dal_irq_source_dce110` maps Vislands IV source/ext IDs to DAL IRQ sources. `dal_irq_service_dce110_create` allocates and constructs the service.

## Control Flow

Runtime interrupt handling calls the service's `to_dal_irq_source` function to translate IV source IDs. Generic IRQ service code indexes `irq_source_info_dce110` to enable, disable, or acknowledge sources. HPD uses custom ack/polarity handling; vblank enable arms TG interrupt width before unmasking.

## State And Persistence Behavior

The IRQ service object stores context, info table pointer, and funcs pointer. Hardware interrupt mask, ack, status, polarity, and TG vertical interrupt registers persist until changed. Dummy handlers deliberately do not change hardware.

## Dependencies And Integration Points

It depends on DCE 11 register/mask headers, Vislands IV source IDs, `dm_services`, logger, `dc`, `core_types`, and common IRQ service helpers. It integrates with timing generators for vblank, HPD handling, page flips, and the common DC interrupt dispatcher.

## Risks And Test Signals

Risks include wrong source/ext mapping, HPD polarity bugs causing interrupt storms or missed hotplugs, invalid pipe offset in vblank enable, and unsupported sources being called unexpectedly. Test signals include HPD plug/unplug on six connectors, HPDRX IRQs, page-flip/vblank delivery, log absence of dummy-handler errors for active sources, and modesets after vblank enable failures.
