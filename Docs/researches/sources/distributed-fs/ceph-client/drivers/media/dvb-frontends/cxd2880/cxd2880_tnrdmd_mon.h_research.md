# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_mon.h

## Purpose
Declares common tuner-demod monitor helpers for RF level and internal CPU status.

## Important APIs, Types, and Functions
Declares `cxd2880_tnrdmd_mon_rf_lvl()`, `cxd2880_tnrdmd_mon_rf_lvl_sub()`, `cxd2880_tnrdmd_mon_internal_cpu_status()`, and `cxd2880_tnrdmd_mon_internal_cpu_status_sub()`.

## Control Flow
No executable flow. CPU status APIs are usable during initialization; RF level requires active state in the implementation.

## State and Persistence
No header state. Implementations read hardware and fill caller-provided output values.

## Dependencies and Integration Points
Includes common and tuner-demod headers. Used by integration initialization, standard-specific SSI/statistics, and frontend status paths.

## Risks and Edge Cases
Sub variants are valid only through a diversity-main object. Callers should not assume RF readings are available before active tune.

## Test Signals
Compile monitor consumers and exercise CPU status and RF level APIs across init, active, inactive, and diversity modes.
