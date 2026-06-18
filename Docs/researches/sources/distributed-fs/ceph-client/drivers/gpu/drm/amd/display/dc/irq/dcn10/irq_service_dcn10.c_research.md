# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c

## Purpose

`irq_service_dcn10.c` implements the DCN 1.0 IRQ service. It maps DCN source IDs to DAL IRQ sources and builds SOC15/base-indexed IRQ source entries for HPD, HPDRX, HUBP flips, OTG vstartup/vupdate-no-lock/vline0, GPIO, DDC, sink, and underflow placeholders.

## Important APIs, Types, And Functions

`to_dal_irq_source_dcn10` translates DCN 1.0 source IDs: OTG vstartup to VBLANK, vertical interrupt control to VLINE0, OTG vupdate-no-lock to VUPDATE, HUBP flip to PFLIP, and HPD source/ext contexts to HPD or HPDRX. Function tables exist for HPD, HPDRX, PFLIP, VBLANK, VLINE0, VUPDATE_NO_LOCK, and dummy sources. Macros `BASE`, `SRI`, and `IRQ_REG_ENTRY` compute SOC15 register addresses and masks. `irq_source_info_dcn10` maps DAL sources, with PFLIP5/6 dummy because DCN10 exposes four HUBP flip entries. `dal_irq_service_dcn10_create` allocates and constructs the service.

## Control Flow

The common dispatcher calls the DCN translator and then programs IRQ masks/acks from `irq_source_info_dcn10`. HPD uses `hpd0_ack`; vblank and vupdate entries directly use OTG global sync status events; vline0 entries use OTG vertical interrupt control. Unsupported sources use DCE110 dummy handlers.

## State And Persistence Behavior

The service stores the DCN10 table and funcs pointer. Hardware state persists in HPD, HUBP request, OTG global sync, and vertical interrupt registers. The translator is stateless but must match firmware interrupt source IDs.

## Dependencies And Integration Points

It depends on DCN 1.0 offset/mask headers, SOC15/Vega10 offsets, DCN IRQ source IDs, DCE110 helper declarations, logger/services, and common IRQ service code. It integrates with HUBP page flips, OTG timing/vblank/vline interrupts, HPD handling, and DCN resource construction.

## Risks And Test Signals

Risks include source ID mismatches, base-index calculation errors, treating DCN vstartup as DCE-style vblank without accounting for timing differences, PFLIP5/6 dummy surprises, and missed vupdate-no-lock semantics. Test signals include DCN10 HPD/HPDRX, four-HUBP page flips, vblank/vline0 IRQs, vupdate delivery, underflow diagnostics, and SOC15 register trace validation.
