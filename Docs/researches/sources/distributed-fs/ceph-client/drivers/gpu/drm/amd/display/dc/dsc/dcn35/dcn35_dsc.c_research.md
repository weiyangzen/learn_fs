# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn35/dcn35_dsc.c

## Purpose

`dcn35_dsc.c` adapts the DCN20 DSC implementation for DCN3.5 hardware. It reuses most DCN20 DSC behavior, adds DCN35-specific construction and function table wiring, resets DSCC memory power controls during enable, exposes FGCg control, and reports single-encoder capabilities based on maximum DSCCLK.

## Important APIs, Types, And Functions

The file exports `dsc35_construct` and `dsc35_set_fgcg`; internally it defines `dsc35_enable` and `dsc35_get_single_enc_caps`. The DCN35 `dsc_funcs` table delegates state reads, validation, config, PPS packing, disable, disconnect, and disconnect wait to DCN20 helpers while using DCN35 enable and single-encoder cap logic.

## Control Flow

Construction stores DC context, instance, function table, DCN20-compatible register pointers, DCN35 shift/mask pointers cast to DCN20 base types, and max image width. Enable clears `DSCC_MEM_PWR_FORCE` and `DSCC_MEM_PWR_DIS` because idle exit can leave DSCC memory shut down, then follows DCN20 enable checks and writes clock/forwarding state. FGCg programming toggles `DSC_FGCG_REP_DIS` opposite the requested enable flag.

## State, Dependencies, Risks, And Test Signals

State lives in the base `struct dcn20_dsc`, hardware registers, and function table. The file mutates DSCC memory power control, top clock enable, DSCRM forwarding, and FGCg disable state. It depends on `dcn35_dsc.h`, `reg_helper`, and the DCN20 shared implementation. Risks include unsafe casts if field layouts diverge, power reset interactions, and DSCCLK-derived cap accuracy. Tests should cover enable after idle, FGCg toggling, config reuse, and cap scaling.
