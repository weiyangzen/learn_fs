# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2.c

## Purpose
Implements DVB-T2-specific tune setup, PLP selection, profile programming, sleep behavior, diversity FEF handling, L1-post validity check, and lock interpretation.

## Important APIs, Types, and Functions
Public APIs include `cxd2880_tnrdmd_dvbt2_tune1()`, `tune2()`, `sleep_setting()`, `check_demod_lock()`, `check_ts_lock()`, `set_plp_cfg()`, `diver_fef_setting()`, and `check_l1post_valid()`. Static helpers program bandwidth/clock demod settings, sleep settings, and base/lite/any profile selection.

## Control Flow
`tune1()` validates state, rejects `ANY` profile in diversity mode, performs common DVB-T2 tune setup, programs main/sub demod settings, sets profile on both branches, and configures automatic or explicit PLP ID. `tune2()` chooses FEF intermittent control by profile, completes common tune stage, and marks active state. Lock checks mirror DVB-T semantics using DVB-T2 sync monitors. `diver_fef_setting()` reads OFDM data and programs diversity FEF registers only for mixed signals.

## State and Persistence
Successful tune stores active frequency/system/bandwidth in main and sub state. PLP, profile, and FEF behavior are programmed into hardware registers. FEF enable flags are stored in `struct cxd2880_tnrdmd`.

## Dependencies and Integration Points
Depends on core tune helpers and DVB-T2 monitor functions for sync, OFDM, and L1 status. Higher-level frontend code uses it for DVB-T2 scan/tune and PLP management.

## Risks and Edge Cases
PLP ID auto versus explicit selection needs correct caller mapping; invalid PLP detection is exposed through tune info elsewhere. Diversity cannot use profile ANY. L1-post validity can change during acquisition. Register tables are sensitive to bandwidth and clock mode.

## Test Signals
Base/lite/any profile tuning, explicit and auto PLP, invalid PLP cases, diversity mixed FEF streams, TS/demod lock in single/diversity modes, L1-post validity polling, and sleep after T2 tune.
