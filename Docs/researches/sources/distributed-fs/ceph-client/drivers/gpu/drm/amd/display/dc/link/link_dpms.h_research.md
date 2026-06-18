# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_dpms.h

## Purpose

`link_dpms.h` declares the link DPMS, blanking, payload, and DSC control API exposed through `struct link_service`.

## Important APIs, Types, And Functions

It declares `link_set_dpms_on()`, `link_set_dpms_off()`, `link_resume()`, DP/eDP blanking helpers, `link_set_all_streams_dpms_off_for_link()`, `link_get_master_pipes_with_dpms_on()`, MST payload increase/reduce, DSC PPS packet control, SST average slot calculation, DSC stream enable, DSC hardware enable, and DSC config update.

## Control Flow

There is no runtime flow in the header. The declarations divide DPMS operations into stream state transitions, global blanking helpers, MST bandwidth changes, and DSC operations.

## State And Persistence Behavior

The header stores no state. Implementations mutate hardware, DPCD, link status, payload tables, stream DSC PPS buffers, PSP stream config, and audio/blanking state.

## Dependencies And Integration Points

It includes `link_service.h`. `link_factory.c` assigns many of these functions into `link_service`, while other DC code can call the DSC and payload helpers directly.

## Risks And Edge Cases

The API exposes low-level operations that must be called in valid display commit contexts. `link_set_dpms_on()` expects master pipes and valid resources; payload/DSC helpers assume signal-specific prerequisites.

## Test Signals

Build coverage catches prototype drift. Runtime validation comes from DPMS on/off, blanking, MST payload changes, DSC PPS updates, and resume HPD filter programming.
