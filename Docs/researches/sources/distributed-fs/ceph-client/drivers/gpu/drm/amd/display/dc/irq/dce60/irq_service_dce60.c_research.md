# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce60/irq_service_dce60.c

## Purpose

`irq_service_dce60.c` implements the DCE 6 IRQ service, mainly for SI-era display support. It builds a DCE60-specific source table and source translator while reusing DCE110 dummy and vblank helper functions where compatible.

## Important APIs, Types, And Functions

The file defines D1-D6 vblank source IDs, function tables for HPD, HPDRX, PFLIP, VBLANK, DCE60-specific vblank, and dummy sources. Entry macros use DCE 6 register names such as `mmDC_HPD*_INT_CONTROL`, `mmDCP*_GRPH_INTERRUPT_CONTROL`, `mmCRTC*_CRTC_INTERRUPT_CONTROL`, and `mmLB*_VBLANK_STATUS`. `irq_source_info_dce60` maps DAL IRQ sources. `to_dal_irq_source_dce60` maps Vislands source/ext IDs for VBLANK, VUPDATE, PFLIP, HPD, and HPDRX. `dal_irq_service_dce60_create` allocates and constructs the service.

## Control Flow

Generic DC interrupt dispatch uses `to_dal_irq_source_dce60` and then table entries to program masks and acknowledge status. HPD uses `hpd1_ack`; VUPDATE uses the DCE110 vblank set helper in this table, while VBLANK entries use a DCE60-specific function table without a set hook because LB vblank registers differ.

## State And Persistence Behavior

The service object persists with DCE60 info/funcs pointers. Hardware mask/ack state persists in HPD, DCP, CRTC, and LB registers. Source translation is stateless.

## Dependencies And Integration Points

It depends on Linux slab allocation, DCE 6 register/mask headers, Vislands IV IDs, common services/logger, `dc_types`, and DCE110 helpers. It is included in the build only under `CONFIG_DRM_AMD_DC_SI`.

## Risks And Test Signals

Risks include one-based HPD register numbering, LB-based vblank differences, SI-only build coverage gaps, and helper reuse mismatches. Test signals include SI build coverage, HPD plug/unplug, vblank/page-flip interrupts, vupdate interrupts, and absence of dummy-handler logs on supported sources.
