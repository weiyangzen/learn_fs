# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dtv.h

## Purpose
Defines generic digital-TV system and bandwidth enums shared by CXD2880 DVB-T and DVB-T2 code.

## Important APIs, Types, and Functions
`enum cxd2880_dtv_sys` covers unknown, DVB-T, DVB-T2, and any. `enum cxd2880_dtv_bandwidth` covers unknown plus 1.7, 5, 6, 7, and 8 MHz values encoded mostly by MHz number.

## Control Flow
No executable flow. Tuning paths switch on these enums to choose standard-specific register programming and validation.

## State and Persistence
Values are stored in `struct cxd2880_tnrdmd` as current tuned system and bandwidth.

## Dependencies and Integration Points
Used by tune parameter structures, common tune helpers, state tracking, and frontend conversion from Linux delivery-system/cache values.

## Risks and Edge Cases
The enum does not include all DVB-T2 bandwidth encodings present in low-level DVB-T2 definitions, such as 10 MHz, so frontend mapping must constrain supported values. Unknown/any must not be sent into hardware programming paths that expect concrete standards.

## Test Signals
Tune attempts for every supported bandwidth, rejection of unknown/unsupported bandwidths, and correct persisted state after successful DVB-T and DVB-T2 tune flows.
