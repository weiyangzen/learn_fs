# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.h

## Purpose

`dmub_dcn303.h` declares the DCN303 DMUB register table and inherits the common DCN20 API model.

## Important APIs, Types, And Functions

It includes `dmub_dcn20.h` and declares `extern const struct dmub_srv_common_regs dmub_srv_dcn303_regs`.

## Control Flow And Data Flow

The header provides no runtime flow. It supports generation-selection code that binds DCN303 hardware to its register table.

## State And Persistence Behavior

No state is owned here.

## Dependencies And Integration Points

The dependency on `dmub_dcn20.h` pulls in common register structs and hardware operation declarations. The exported table symbol is implemented in `dmub_dcn303.c`.

## Risks And Edge Cases

The empty hardware-functions section means the generation has no local operation overrides in this subset. Any required DCN303-specific behavior must be implemented elsewhere or tests will expose initialization failures.

## Test Signals

Build/link success and runtime DMUB initialization on DCN303 hardware are the relevant signals.
