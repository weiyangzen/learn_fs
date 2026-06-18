# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_mon.c

## Purpose
Implements common monitor helpers shared across DVB-T and DVB-T2: RF level measurement and internal CPU status reads.

## Important APIs, Types, and Functions
`cxd2880_tnrdmd_mon_rf_lvl()` triggers and reads RF level measurement, converts an 11-bit signed value, scales by 125, and applies optional RF compensation callback. `cxd2880_tnrdmd_mon_rf_lvl_sub()` delegates to the diversity sub demod. `cxd2880_tnrdmd_mon_internal_cpu_status()` and `_sub()` read the internal CPU status word.

## Control Flow
RF level requires active state, writes measurement control registers, waits 2-3 ms, checks status, reads the result, restores a demod control bit, and applies compensation. CPU status selects SYS bank `0x1a` and reads two bytes.

## State and Persistence
RF monitor temporarily toggles hardware measurement controls and returns a snapshot. The compensation callback pointer lives in `struct cxd2880_tnrdmd`.

## Dependencies and Integration Points
Used by integration init polling, SSI calculations, and frontend signal-strength reporting. Depends on register I/O and two's-complement conversion.

## Risks and Edge Cases
RF measurement returns `-EINVAL` if status bytes are nonzero, so callers must handle unavailable readings. Compensation callbacks can skew all SSI/signal output. Sub reads require diversity main mode.

## Test Signals
CPU status polling during init, RF readings at known signal levels, compensation callback tests, inactive-state rejection, and diversity sub RF reporting.
