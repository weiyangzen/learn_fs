# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn20/dcn20_dccg.c

## Purpose
`dcn20_dccg.c` implements the base DCN 2.0 Display Clock Generator object. It programs DPP DTOs, reference clock handling, FIFO error override, OTG add/drop pixel controls, initialization dividers, clock gating, memory low power, and object creation/destruction.

## Important APIs And Functions
`dccg2_update_dpp_dto` computes phase/modulo for a requested per-pipe DPP clock relative to `dccg->ref_dppclk`, writes `DPPCLK_DTO_PARAM[dpp_inst]`, enables/disables the corresponding DTO, clamps phase to 0xff, and records `pipe_dppclk_khz`.

`dccg2_get_dccg_ref_freq` reads `REFCLK_CNTL`, asserts if the refclk is enabled to a non-xtalin source, and reports the xtalin frequency. `dccg2_set_fifo_errdet_ovr_en` writes `DCCG_FIFO_ERRDET_OVR_EN`. `dccg2_otg_add_pixel` and `dccg2_otg_drop_pixel` clear both add/drop bits then pulse one bit for an OTG instance.

`dccg2_init` writes hardcoded 100 MHz-refclk divider/control values to microsecond/millisecond time base and dispclk change control, then clears `REFCLK_CNTL` if present. `dccg2_refclk_setup` clears refclk after hubbub init. `dccg2_is_s0i3_golden_init_wa_done` detects a BIOS marker in `MICROSECOND_TIME_BASE_DIV`. `dccg2_allow_clock_gating` writes gate disable registers to all zero or all ones. `dccg2_enable_memory_low_power` updates `DC_MEM_GLOBAL_PWR_REQ_DIS`.

`dccg2_create` allocates `struct dcn_dccg`, initializes base context/function table and register/shift/mask tables. `dcn_dccg_destroy` frees and nulls the object pointer.

## Control Flow And State
The object is a `struct dcn_dccg` wrapping `struct dccg`. Runtime state includes function-table dispatch, register tables, mask/shift tables, `ref_dppclk`, and per-pipe cached DPP clocks. Hardware state is changed through register helper macros.

## Dependencies And Integration Points
It includes Linux slab, `reg_helper.h`, `core_types.h`, and `dcn20_dccg.h`. It is called by resource creation for DCN2-family ASICs and by hardware sequencer clock programming paths.

## Risks
`dpp_inst` and `otg_inst` index arrays without local bounds checks; callers must validate pipe counts. Hardcoded init values assume a 100 MHz refclk unless overridden by later generations. `get_dccg_ref_freq` asserts on non-xtalin but still returns xtalin, so unsupported clocking may limp forward. Clock gating all-ones writes can disable broad DCCG gating and affect power. Phase/modulo rounding can overclock slightly and clamps at 0xff.

## Test Signals
Hardware bring-up on DCN2, per-pipe DPP clock programming, DTO disable when request is zero, OTG add/drop pixel behavior, S0i3 golden-init marker detection, clock-gating toggles, memory low-power toggles, and object create/destroy leak checks are important.
