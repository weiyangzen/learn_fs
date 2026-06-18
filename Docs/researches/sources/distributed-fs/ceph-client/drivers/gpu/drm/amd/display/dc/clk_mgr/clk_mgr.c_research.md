# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/clk_mgr.c

## Purpose
This file provides common clock-manager helpers, power-state transitions, the ASIC-family clock-manager factory, and destruction logic.

## Important APIs, Types, And Functions
- `clk_mgr_helper_get_active_display_cnt()` counts non-phantom active displays and streams with planes or switch-in-progress.
- `clk_mgr_helper_get_active_plane_cnt()` sums stream plane counts.
- `clk_mgr_exit_optimized_pwr_state()` and `clk_mgr_optimize_pwr_state()` coordinate HW sequencer optimized power states with PSR/Replay allow-active settings on eDP links.
- `dc_clk_mgr_create()` allocates and constructs the correct clock manager for SI/CI/KV/CZ/VI/AI and many DCN families.
- `dc_destroy_clk_mgr()` invokes family-specific destroy functions for DCN managers and frees the allocation.

## Control Flow
The factory switches on `ctx->asic_id.chip_family`, then often on hardware revision or `ctx->dce_version`. It allocates a structure sized for the selected manager, calls the generation-specific constructor, and returns the embedded base pointer. The destroy path switches on the same family/revision categories for managers that need explicit teardown before `kfree()`.

## State And Persistence
The file creates persistent `struct clk_mgr` or generation-specific derived objects for the lifetime of the DC instance. Power-state helpers temporarily cache PSR allow-active state in `clk_mgr->psr_allow_active_cache` and manipulate eDP PSR/Replay permissions.

## Dependencies And Integration Points
It depends on ASIC ID macros, DCCG, `clk_mgr_internal`, DC state helpers, link service, and every generation-specific clock-manager constructor header. It integrates clock management into DC initialization and teardown.

## Risks
The factory must stay synchronized with supported ASIC revisions, constructor object sizes, and Makefile object lists. Some branches allocate `struct clk_mgr_internal`, others allocate derived DCN structs, making destroy casts sensitive. The active display count deliberately skips SubVP phantom streams, so changes to SubVP classification affect power management.

## Test Signals
Boot/display initialization on every supported ASIC family, correct constructor selection in logs/debug traces, successful suspend/resume, PSR/Replay behavior around optimized power states, and leak/error checks on destroy are important signals.
