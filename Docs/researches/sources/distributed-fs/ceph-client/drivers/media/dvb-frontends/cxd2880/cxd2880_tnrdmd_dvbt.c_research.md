# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt.c

## Purpose
Implements DVB-T-specific tuning, demodulator setup, sleep programming, and lock interpretation for CXD2880.

## Important APIs, Types, and Functions
Public APIs are `cxd2880_tnrdmd_dvbt_tune1()`, `cxd2880_tnrdmd_dvbt_tune2()`, `cxd2880_tnrdmd_dvbt_sleep_setting()`, `cxd2880_tnrdmd_dvbt_check_demod_lock()`, and `cxd2880_tnrdmd_dvbt_check_ts_lock()`. Static helpers include register-sequence demod setup, sleep setup, and `dvbt_set_profile()`.

## Control Flow
`tune1()` validates main/single state, calls common tune setup for DVB-T, programs bandwidth/clock dependent demod settings on main and optional sub, then selects HP or LP profile. `tune2()` completes common tune stage, marks main/sub active, and stores frequency/system/bandwidth. Sleep delegates demod-specific sleep settings. Lock checks read sync status and TS lock; diversity reports locked if either branch locks and unlocked only when both branches detect unlock.

## State and Persistence
Updates `struct cxd2880_tnrdmd` active state, tuned frequency, system, and bandwidth. Profile is programmed into hardware but not separately stored in the state object.

## Dependencies and Integration Points
Depends on core tune/sleep helpers and DVB-T monitor sync status. Top-level frontend tune paths call these around tuner setup and lock polling.

## Risks and Edge Cases
Only main/single objects are valid entry points. Lock result semantics differ in diversity mode. Invalid state transitions return `-EINVAL`. Bandwidth and clock-specific register values must match hardware tables.

## Test Signals
DVB-T tune for 5/6/7/8 MHz, HP and LP profile streams, sleep after active tune, demod and TS lock polling in single/diversity modes, and register trace validation against known-good hardware sequences.
