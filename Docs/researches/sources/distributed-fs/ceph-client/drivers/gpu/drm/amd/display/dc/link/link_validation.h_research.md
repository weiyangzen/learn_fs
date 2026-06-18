# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_validation.h

## Purpose

`link_validation.h` declares link timing, DP tunnel bandwidth, DP link bandwidth, and DP hblank audio bandwidth validation helpers.

## Important APIs, Types, And Functions

It declares `link_validate_mode_timing()`, `link_validate_dp_tunnel_bandwidth()`, `dp_link_bandwidth_kbps()`, and `dp_required_hblank_size_bytes()`.

## Control Flow

There is no runtime flow in the header. The declarations are installed into `link_service` by `link_factory.c` and used by validation and DPMS paths.

## State And Persistence Behavior

The header stores no state. Implementations are mostly read-only calculations over stream timing, link caps, tunnel settings, and audio parameters.

## Dependencies And Integration Points

It includes `link_service.h` for `dc`, `dc_state`, `dc_stream_state`, `dc_link`, timing, status, settings, and audio parameter types.

## Risks And Edge Cases

The exposed helpers are used both for rejecting modes and for programming-related calculations. Any formula change can alter visible mode lists, tunnel admission, MST/SST payload sizing, or hblank requirements.

## Test Signals

Build coverage catches prototype drift. Functional validation should compare bandwidth/status outputs for representative DP, eDP, DPIA, dongle, DSC, and audio hblank scenarios.
