# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.h

## Purpose
This header exposes shared DCE clock-manager utilities and the DCE base constructor.

## Important APIs, Types, And Functions
It declares DP reference clock helpers, clock-state calculation, max pixel-clock scan, `dce_clk_mgr_construct()`, spread-spectrum info loading, DCE12 DP ref helper, `dce_set_clock()`, `dce_clk_mgr_destroy()`, and dentist divider decoding.

## Control Flow
The header provides declarations only. Implementations are used by DCE100 and later DCE clock-manager files.

## State And Persistence
No state is defined here; declarations operate on `struct clk_mgr`, `struct clk_mgr_internal`, and `struct dc_state`.

## Dependencies And Integration Points
It includes `dc.h` and is included by DCE110, DCE112, and DCE120 manager implementations. It is the shared clock-manager API for DCE generations.

## Risks
The declared `dce_clk_mgr_destroy(struct clk_mgr **clk_mgr)` is not implemented in the read C file and may be stale. Signature changes affect multiple generation-specific managers.

## Test Signals
Compile/link coverage detects stale declarations. Runtime coverage should exercise shared helpers through every DCE manager that includes this header.
