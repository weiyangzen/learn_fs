# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt.h

## Purpose
Declares DVB-T tune parameters and control APIs for CXD2880.

## Important APIs, Types, and Functions
`struct cxd2880_dvbt_tune_param` carries center frequency, bandwidth, and HP/LP profile. Prototypes cover two-phase tune, sleep setting, demod lock check, and TS lock check.

## Control Flow
No executable flow. The two-phase tune API lets callers perform common/hardware preparation and then complete activation after any required waits or tuner work.

## State and Persistence
Tune parameters are transient; successful implementation calls update `struct cxd2880_tnrdmd` state.

## Dependencies and Integration Points
Includes common and tuner-demod headers. Used by top-level DVB frontend operations for DVB-T delivery systems.

## Risks and Edge Cases
Callers must use valid bandwidth/profile combinations and call phases in order. Lock APIs require active state.

## Test Signals
Compile frontend glue against this contract and test tune1/tune2 sequencing, invalid profile rejection through implementation, and active-only lock checks.
