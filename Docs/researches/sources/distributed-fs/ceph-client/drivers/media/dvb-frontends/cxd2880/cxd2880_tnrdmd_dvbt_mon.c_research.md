# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt_mon.c

## Purpose
Implements DVB-T monitor/statistics functions for sync, mode/guard, carrier offset, TPS information, packet errors, spectrum sense, SNR, sampling offset, and SSI.

## Important APIs, Types, and Functions
Exports the functions declared in `cxd2880_tnrdmd_dvbt_mon.h`. Static helpers include `is_tps_locked()`, `dvbt_read_snr_reg()`, `dvbt_calc_snr()`, and `dvbt_calc_ssi()`. `ref_dbm_1000` maps modulation and code rate to SSI reference levels.

## Control Flow
Functions validate active state, select demod banks, read and decode registers, and use SLV-T freeze/unfreeze for coherent reads where needed. TPS-dependent functions check TPS lock before decoding. Carrier and sampling offsets are sign-extended and scaled by bandwidth/clock-specific formulas. Diversity SNR combines main/sub readings.

## State and Persistence
No persistent driver state is modified, except transient hardware register freeze/unfreeze. Outputs are snapshots of current hardware acquisition state.

## Dependencies and Integration Points
Depends on common conversion helpers, core tuner-demod state/freeze operations, RF level monitor, and DVB-T protocol definitions. DVB-T lock checks call sync monitor functions.

## Risks and Edge Cases
Reading detailed metrics before TPS lock can return invalid data and should produce errors. Register freeze cleanup on error is critical. SSI depends on RF compensation callback correctness. Integer formulas and bandwidth branches are easy to regress.

## Test Signals
DVB-T streams with QPSK/16QAM/64QAM, all code rates and guards, spectrum inversion, packet errors, low/high RF levels, diversity SNR combining, and injected I/O errors during frozen reads.
