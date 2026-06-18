# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_dp.h

## Purpose

`link_hwss_hpo_dp.h` declares the HPO DP HWSS interface for DP 2.x/HPO stream and link sequencing.

## Important APIs, Types, And Functions

The header declares throttled VCP, hblank minimum symbol width, stream encoder setup/reset/attribute, link output enable/disable, MST allocation update, audio setup/packet control, `get_hpo_dp_link_hwss()`, and `can_use_hpo_dp_link_hwss()`.

## Control Flow

The header has no runtime flow. It exposes routines assigned into the HPO DP `struct link_hwss` vtable and reused by the HPO fixed-VS/PE retimer specialization.

## State And Persistence Behavior

No state is stored. Implementations mutate HPO encoder, DCCG, audio, and trace state.

## Dependencies And Integration Points

It includes `link_hwss.h` and `link_service.h`. It is consumed by HPO DP implementation files and DPMS/HWSS selection code.

## Risks And Edge Cases

The prototype for `set_hpo_dp_hblank_min_symbol_width()` appears twice in the header. This is harmless in C because the declarations match, but it is a maintenance signal. As with DIO, most parameters are generic pointers, so type safety does not prevent mismatched resource usage.

## Test Signals

Build coverage catches signature drift. Runtime coverage comes from HPO DP SST/MST link enablement, payload allocation, audio, DSC PPS, test patterns, and FFE/lane-setting operations.
