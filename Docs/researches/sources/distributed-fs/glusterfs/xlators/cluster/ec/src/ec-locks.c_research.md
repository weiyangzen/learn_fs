# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-locks.c

## Purpose
This file implements explicit lock FOP handling for the EC translator: entry locks, inode locks, fd inode locks, and POSIX byte-range `lk`. It fans lock requests out to child bricks, combines responses, converts blocking lock attempts into nonblocking parallel probes plus sequential fallback, and cleans up partially acquired locks when quorum cannot be reached.

## Important APIs, Types, And Functions
Public entry points are `ec_entrylk`, `ec_fentrylk`, `ec_inodelk`, `ec_finodelk`, and `ec_lk`. Callback/wind pairs include `ec_entrylk_cbk`/`ec_wind_entrylk`, `ec_inodelk_cbk`/`ec_wind_inodelk`, and `ec_lk_cbk`/`ec_wind_lk`. `ec_lock_check()` is the core quorum evaluator. It groups successful, `EAGAIN`, and `ESTALE` answers and returns success, retry, or a final error while producing the mask of bricks already locked. `ec_lock_unlocked()` and `ec_lock_lk_unlocked()` log failures from cleanup unlock requests.

## Control Flow
For blocking entry/inode/lk requests, the manager first converts the request to a nonblocking lock (`ENTRYLK_LOCK_NB` or `F_SETLK`) and sets mode `EC_LOCK_MODE_ALL`. After dispatch, `ec_lock_check()` decides whether enough bricks locked, whether `EAGAIN` contention requires retry, or whether partial locks must be released. If retry is needed, the manager changes the command back to blocking (`ENTRYLK_LOCK` or `F_SETLKW`) and uses `ec_dispatch_inc()` to acquire remaining locks incrementally. Unlock requests skip this special lock checking and use `ec_fop_prepare_answer()`.

For inode locks, the requested byte range is translated to EC fragment units by adjusting the start and length; partial cleanup unlocks translate back to user units when issuing a compensating unlock. `lk` uses `ec_combine_lk()` to reject mismatching flock answers from different bricks.

## State And Persistence Behavior
The file does not persist data directly. It coordinates backend lock state on child translators and uses transient `ec_fop_data_t` masks, callback groups, command fields, flock structures, and lock owner copies. Partially acquired backend locks are explicitly unwound by issuing child unlock FOPs against the mask returned by `ec_lock_check()`.

## Dependencies And Integration Points
It depends on `ec-common` dispatch/completion, `ec-combine` answer grouping, `ec-helpers` range and owner utilities, `ec-fops` recursive EC lock wrappers, and GlusterFS lock FOP contracts. It integrates with upstream `ec.c` wrappers, which choose `EC_MINIMUM_ALL` for acquiring locks and `EC_MINIMUM_ONE` for unlocks.

## Risks
The riskiest behavior is split-brain lock state if partial acquisitions are not cleaned up, if `EAGAIN` fallback is mishandled, or if range scaling does not match write/read range scaling. `ESTALE` is intentionally treated as quorum-relevant but not always fatal, which is subtle under concurrent unlink. The `ec_combine_lk()` mismatch path only logs and rejects grouping, so tests need to verify final answers under divergent brick lock state.

## Test Signals
Exercise blocking and nonblocking entry/inode/fd locks with one or more contended bricks, unlock failure logging, ESTALE during unlink, byte-range locks crossing EC fragment boundaries, and mixed child answers for `lk`. Failure injection should confirm that partial locks are released and that retries do not duplicate successful child locks.
