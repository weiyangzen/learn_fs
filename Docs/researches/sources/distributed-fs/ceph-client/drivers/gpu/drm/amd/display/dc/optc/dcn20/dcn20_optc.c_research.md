# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.c

## Purpose
`dcn20_optc.c` extends the base DCN10 timing generator with DCN2.0 capabilities: segmented OPTC source selection, ODM combine/bypass, DSC configuration/status, global swap lock support, DWB source selection, vblank alignment, triple buffering, double-buffer lock programming, manual trigger updates, CRC stream-mode configuration, and last-used DRR vtotal readback.

## Important APIs, types, and functions
Key functions are `optc2_enable_crtc()`, `optc2_set_gsl()`, `optc2_set_gsl_source_select()`, `optc2_set_dsc_config()`, `optc2_get_dsc_status()`, `optc2_set_odm_bypass()`, `optc2_set_odm_combine()`, `optc2_get_optc_source()`, `optc2_set_dwb_source()`, `optc2_align_vblanks()`, `optc2_triplebuffer_lock()`, `optc2_triplebuffer_unlock()`, `optc2_lock_doublebuffer_enable()`, `optc2_lock_doublebuffer_disable()`, `optc2_setup_manual_trigger()`, `optc2_program_manual_trigger()`, `optc2_configure_crc()`, `optc2_get_last_used_drr_vtotal()`, and `dcn20_timing_generator_init()`.

## Control flow
Enable selects `OPTC_SEG0_SRC_SEL`, enables VTG, and turns on OTG master enable. ODM bypass routes one OPP segment and sets H timing division based on two-pixels-per-container formats. ODM combine asserts two OPPs, derives a non-overlapping memory mask from OPP ids, sets segment sources/width, forces divide-by-two timing, and records `opp_count`. GSL functions assign OTGs to groups and select ready sources. Vblank alignment temporarily disables a slave OTG, locks it to the master, computes an X/Y unlock point from pixel clocks and totals, starts the slave at the calculated phase, then restores lock ownership. Manual trigger uses TRIGA and DMCUB-friendly min/max selectors.

## State and persistence behavior
State is held in OTG/OPTC registers and in `optc1->opp_count` for ODM width and lock calculations. There is no nonvolatile persistence.

## Dependencies and integration points
The file depends on DCN10 OPTC helpers, DCN20 register fields, `dc.h`, division helpers, GSL/ODM/DSC/DWB timing-generator interfaces, and CRC parameter structures. It integrates with multi-OPP wide-display composition, DSC stream formatting, DWB routing, and multi-display synchronization.

## Risks and edge cases
ODM combine assumes exactly two OPPs and reserves memory based on OPP ids. Vblank alignment uses integer math and direct master/slave register switching, so wrong clock inputs can misphase displays. Double-buffer lock positions subtract fixed pixel margins from blank start and depend on `opp_count`. `get_optc_source()` works around VBIOS not updating segment count by checking `SEG1 == 0xf`.

## Test signals
ODM bypass/combine modes, DSC enable/disable and CRC with DSC/ODM modes, GSL master/slave synchronization, DWB source selection, triple-buffer lock/unlock, double-buffer lock timing, manual trigger DRR, last-used DRR readback, and multi-display vblank alignment tests are relevant.
