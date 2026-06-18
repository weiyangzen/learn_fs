# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2_mon.h

## Purpose
Declares the DVB-T2 monitoring interface for CXD2880.

## Important APIs, Types, and Functions
Prototypes cover sync status, sub sync status, carrier offset, L1-pre/version/OFDM/data PLPs/active PLP/data PLP error/L1 change/L1-post/BB header/in-band B TS rate, spectrum sense, SNR and diversity SNR, packet error number, sampling offset, QAM, code rate, profile, and SSI for main/sub.

## Control Flow
No executable flow. APIs generally require active DVB-T2 state and return decoded signalling or statistics through output pointers.

## State and Persistence
No state in the header. Implementations read current hardware state and fill caller-owned outputs.

## Dependencies and Integration Points
Includes tuner-demod and DVB-T2 definitions. Used by lock logic and top-level frontend statistic/property reporting.

## Risks and Edge Cases
Many APIs expose raw protocol detail; callers must check return codes and respect active-state requirements. Sub variants are valid only in diversity-main contexts.

## Test Signals
Compile users against each prototype and run frontend stat reads across acquisition, lock, unlock, and diversity modes.
