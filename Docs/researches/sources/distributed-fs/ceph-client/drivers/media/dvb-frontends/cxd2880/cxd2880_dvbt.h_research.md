# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dvbt.h

## Purpose
Defines DVB-T modulation, hierarchy, coding, guard, FFT mode, profile, and TPS information structures for CXD2880 monitor and tuning code.

## Important APIs, Types, and Functions
Enums model DVB-T constellation, hierarchy, code rates, guard intervals, 2K/8K modes, and high/low priority profiles. `struct cxd2880_dvbt_tpsinfo` contains decoded TPS fields including constellation, hierarchy, HP/LP rates, guard, mode, frame number, length indicator, cell ID, and reserved bits.

## Control Flow
No executable flow. Monitor code fills these types from registers; tune code selects profile.

## State and Persistence
These types are transient result containers. Active profile selection influences hardware registers during tune.

## Dependencies and Integration Points
Used by `cxd2880_tnrdmd_dvbt.c`, `cxd2880_tnrdmd_dvbt_mon.c`, and higher-level frontend statistic/property conversion.

## Risks and Edge Cases
Reserved enum values are represented explicitly; consumers must not treat them as valid modulation settings. TPS lock must be verified before trusting decoded fields.

## Test Signals
Known DVB-T streams with each constellation/rate/guard/mode combination, HP/LP profile selection tests, and invalid TPS lock scenarios returning errors rather than stale data.
