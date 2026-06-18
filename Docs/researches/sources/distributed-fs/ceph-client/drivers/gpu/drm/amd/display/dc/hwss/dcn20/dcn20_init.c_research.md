# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_init.c

## Purpose
Builds the DCN 2.0 hardware sequencer vtables. `dcn20_hw_sequencer_construct()` assigns `dc->hwss` to `dcn20_funcs` and `dc->hwseq->funcs` to `dcn20_private_funcs`, selecting the generation-specific implementation for display enable, plane programming, bandwidth, writeback, DMData, VM context setup, ODM/DSC, color, and power gating.

## Important APIs, Types, and Functions
The key exported API is `dcn20_hw_sequencer_construct(struct dc *dc)`. The file defines two static dispatch tables: `struct hw_sequencer_funcs dcn20_funcs` for public DC operations and `struct hwseq_private_funcs dcn20_private_funcs` for lower-level sequencing helpers. Most entries reuse DCE110, DCN10, and DCN20 helpers such as `dcn20_program_front_end_for_ctx`, `dcn20_update_plane_addr`, `dcn20_enable_stream`, `dcn20_prepare_bandwidth`, `dcn20_enable_writeback`, `dcn20_init_sys_ctx`, `dcn20_init_vm_ctx`, `dcn20_update_odm`, and `dcn20_dsc_pg_control`.

## Control Flow
Construction is table assignment only; there is no runtime branching. Later display manager paths call through `dc->hwss` and `dc->hwseq->funcs`, so the table composition controls boot, mode set, plane update, blanking, link control, and color management behavior for DCN20 ASICs. Public hooks route user-visible operations while private hooks drive pipe reset, power gating, transfer functions, and clock initialization.

## State and Persistence Behavior
The only local state change is overwriting the function tables in `struct dc` and `struct dce_hwseq`. This persists for the lifetime of the DC instance. The functions selected by the table mutate hardware registers, pipe state, and resource-pool members elsewhere; this file has no independent memory allocation or cleanup.

## Dependencies and Integration Points
Depends on `dce110_hwseq.h`, `dcn10_hwseq.h`, and `dcn20_hwseq.h`. It integrates with the DC constructor/resource code that chooses the ASIC-specific HWSS constructor and with every caller that dereferences `dc->hwss` or `dc->hwseq->funcs`.

## Risks and Test Signals
The risk is dispatch-table mismatch: a wrong or missing hook changes hardware sequencing globally for the ASIC. Important signals are successful boot/modeset, plane flip, writeback, DMData, DSC/ODM, backlight, and clock/power tests on DCN20 hardware, plus compile coverage for all assigned function prototypes.
