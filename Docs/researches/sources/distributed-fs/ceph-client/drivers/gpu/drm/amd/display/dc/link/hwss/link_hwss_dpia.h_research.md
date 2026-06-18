# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dpia.h

## Purpose

`link_hwss_dpia.h` declares the DPIA HWSS vtable getter and applicability check, plus the DIG mode constants used when enabling tunneled SST or MST output.

## Important APIs, Types, And Functions

- `DIG_SST_MODE` is `0`; `DIG_MST_MODE` is `5`.
- `get_dpia_link_hwss()` returns the static DPIA `struct link_hwss`.
- `can_use_dpia_link_hwss()` checks whether a link/resource combination supports the DPIA sequencing path.

## Control Flow

There is no runtime flow in the header. The constants are consumed by `enable_dpia_link_output()` and `disable_dpia_link_output()` to tell the link encoder which DPIA output mode to program.

## State And Persistence Behavior

No state is held. The implementation changes DMUB slot state, DIO/DPIA encoder state, and trace state.

## Dependencies And Integration Points

It includes `link_hwss.h` and is part of the generic HWSS selection layer for USB4 DPIA links.

## Risks And Edge Cases

The DIG mode values are magic protocol constants; if encoder firmware expectations change, stale constants would break DPIA SST/MST selection. The header does not expose the no-op lane-setting behavior, so callers must rely on the vtable contract.

## Test Signals

Build coverage catches signature drift. Runtime validation should include USB4 DPIA SST/MST link enable/disable and MST payload table update paths.
