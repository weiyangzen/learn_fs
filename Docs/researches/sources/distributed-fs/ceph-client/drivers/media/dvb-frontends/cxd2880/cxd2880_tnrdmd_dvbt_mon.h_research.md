# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt_mon.h

## Purpose
Declares the DVB-T monitoring interface for CXD2880.

## Important APIs, Types, and Functions
Prototypes cover sync status, sub sync status, mode/guard, carrier offset main/sub, TPS info, packet error number, spectrum sense, SNR and diversity SNR, sampling offset main/sub, and SSI main/sub.

## Control Flow
No executable flow. APIs are expected to be called after DVB-T activation and return current acquisition or statistic snapshots.

## State and Persistence
No state in the header. Implementations read hardware into caller-owned outputs.

## Dependencies and Integration Points
Includes tuner-demod and DVB-T definitions. Used by lock checks and top-level frontend stat reporting.

## Risks and Edge Cases
Callers must not ignore return codes, especially for TPS-dependent metrics. Sub APIs require diversity-main objects.

## Test Signals
Compile all monitor users and read all metrics before lock, after lock, after unlock, and in diversity mode.
