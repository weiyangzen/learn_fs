# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.h

## Purpose

`dmub_dcn302.h` declares the DCN302 DMUB register table and reuses the DCN20 common DMUB API surface.

## Important APIs, Types, And Functions

It includes `dmub_dcn20.h` and declares `extern const struct dmub_srv_common_regs dmub_srv_dcn302_regs`.

## Control Flow And Data Flow

No direct control flow exists. Service setup uses the declaration to bind DCN302 hardware to the common register table model.

## State And Persistence Behavior

The header owns no runtime state.

## Dependencies And Integration Points

The integration point is ASIC selection code that uses `dmub_srv_dcn302_regs`. The header depends on common DCN20 declarations for type definitions.

## Risks And Edge Cases

As with DCN301, the hardware-functions section is empty. Tests must prove common behavior is sufficient for this generation.

## Test Signals

Build/link coverage and DMUB initialization on DCN302 hardware are the core signals.
