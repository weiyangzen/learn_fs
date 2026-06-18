# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2.h

## Purpose
Declares DVB-T2 tune parameters, tune result metadata, PLP selection constant, and control APIs for CXD2880.

## Important APIs, Types, and Functions
`enum cxd2880_tnrdmd_dvbt2_tune_info` reports OK or invalid PLP ID. `struct cxd2880_dvbt2_tune_param` carries center frequency, bandwidth, data PLP ID, profile, and tune info. `CXD2880_DVBT2_TUNE_PARAM_PLPID_AUTO` requests automatic PLP selection. Prototypes cover tune phases, sleep, lock checks, PLP config, diversity FEF setting, and L1-post validity.

## Control Flow
No executable flow. The API separates setup/activation and exposes additional DVB-T2 signalling controls needed after acquisition.

## State and Persistence
Tune parameters are transient; implementation updates tuner-demod state and hardware PLP/profile registers.

## Dependencies and Integration Points
Includes the tuner-demod core and is consumed by top-level frontend tune/scanning code.

## Risks and Edge Cases
`data_plp_id` is 16-bit but hardware programming casts explicit IDs to 8-bit; callers must constrain values. Profile ANY is not valid in diversity mode.

## Test Signals
Automatic and explicit PLP tune flows, invalid PLP reporting, profile handling, L1-post wait loops, and lock checks after tune2.
