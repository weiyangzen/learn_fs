# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_integ.h

## Purpose
Declares integration-layer initialization and cancellation helpers plus timing constants.

## Important APIs, Types, and Functions
Defines `CXD2880_TNRDMD_WAIT_INIT_TIMEOUT` as 500 ms, `CXD2880_TNRDMD_WAIT_INIT_INTVL` as 10 ms, and `CXD2880_TNRDMD_WAIT_AGC_STABLE` as 100 ms. Declares `cxd2880_integ_init()`, `cxd2880_integ_cancel()`, and `cxd2880_integ_check_cancellation()`.

## Control Flow
No executable flow in the header; constants are consumed by integration waits.

## State and Persistence
No state. APIs operate on `struct cxd2880_tnrdmd`.

## Dependencies and Integration Points
Includes the core tuner-demod header and provides wait parameters to frontend tune/scan code.

## Risks and Edge Cases
Changing constants changes user-visible tuning latency and timeout behavior. AGC stable wait must match hardware requirements.

## Test Signals
Compile users after constant changes and run init/scan timing tests on real hardware or bus-level simulation.
