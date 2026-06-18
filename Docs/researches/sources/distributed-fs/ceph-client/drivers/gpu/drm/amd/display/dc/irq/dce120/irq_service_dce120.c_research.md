# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c

## Purpose

`irq_service_dce120.c` implements the DCE 12 IRQ service table and constructor. It adapts the DCE IRQ patterns to SOC15/Vega10-style register address calculation while reusing DCE110 source translation and dummy/vblank helpers.

## Important APIs, Types, And Functions

The file defines IRQ source function tables for HPD, HPDRX, PFLIP, VBLANK, VUPDATE, and dummy sources. SOC15 helper macros compute register addresses using base-index data. Entry macros describe HPD, HPDRX, PFLIP, VUPDATE, VBLANK, I2C, DP sink, GPIO pad, and underflow entries. `irq_source_info_dce120` populates `DAL_IRQ_SOURCES_NUMBER` entries. `irq_service_funcs_dce120` points to `to_dal_irq_source_dce110`. `dal_irq_service_dce120_create` allocates and constructs the service.

## Control Flow

Generic IRQ handling translates IV source IDs with the shared DCE110 translator, then uses the DCE120 table to mask, unmask, or acknowledge SOC15 register locations. HPD uses the shared `hpd0_ack` helper from DCE110-era code, while vblank uses `dce110_vblank_set`.

## State And Persistence Behavior

Service state is the table and funcs pointer. Hardware state persists in SOC15 interrupt control/status registers and timing-generator vblank-arm registers.

## Dependencies And Integration Points

It depends on DCE 12 offset/mask headers, SOC15 and Vega10 IP offsets, Vislands IV IDs, logger, common IRQ service code, and DCE110 helper declarations. It integrates with Vega/DCE12 resource initialization and common DC interrupt dispatch.

## Risks And Test Signals

Risks include incorrect SOC15 base-index arithmetic, using DCE110 translation where a DCE12-specific source differs, HPD ack helper mismatch, and missing table entries. Test signals include HPD, HPDRX, PFLIP, VUPDATE, VBLANK, and underflow behavior on DCE12 hardware plus build/link coverage for SOC15 register names.
