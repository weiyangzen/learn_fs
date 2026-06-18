# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.c

## Purpose

`irq_service_dce80.c` implements the DCE 8 IRQ service table and constructor. It adapts DCE110-style interrupt handling to DCE 8 register names while reusing the DCE110 source translator and helpers.

## Important APIs, Types, And Functions

Function tables are defined for HPD, HPDRX, PFLIP, VBLANK, VUPDATE, and dummy sources. Entry macros map DAL sources to DCE 8 HPD, DCP graphics flip, CRTC vupdate/vblank, GPIO, DDC, DP sink, and underflow registers. `irq_source_info_dce80` contains the mapping table. `irq_service_funcs_dce80` uses `to_dal_irq_source_dce110`. `dal_irq_service_dce80_create` allocates and constructs the service.

## Control Flow

Interrupt dispatch translates source IDs with the shared DCE translator, then uses the DCE80-specific table for enable/disable/ack. HPD uses `hpd1_ack`; vblank uses `dce110_vblank_set`; unsupported sources route to dummy functions.

## State And Persistence Behavior

Service state is the info table and funcs pointer. Hardware state persists in DCE 8 HPD, DCP, and CRTC interrupt registers.

## Dependencies And Integration Points

It depends on DCE 8 register/mask headers, Vislands IV IDs, logger/services, `dc_types`, and DCE110 helper declarations. It integrates with DCE80 resource-pool construction and common DC IRQ handling.

## Risks And Test Signals

Risks include register-name/index mismatches, helper reuse assumptions, and unsupported sources being enabled. Test signals include HPD, HPDRX, page-flip, vblank, vupdate, and underflow behavior on DCE8 ASICs plus clean build/link coverage.
