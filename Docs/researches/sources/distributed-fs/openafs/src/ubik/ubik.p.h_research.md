
# sources/distributed-fs/openafs/src/ubik/ubik.p.h

`ubik.p.h` is the main private/public Ubik interface header. It defines the transaction API, database and client handles, service ids, quorum constants, internal state structures, lock macros, module globals, and prototypes used across Ubik implementation files and generated Rx code.

Public-facing types include `struct ubik_client`, `struct ubik_hdr`, `struct ubik_trans`, `struct ubik_trunc`, `struct ubik_stat`, `struct ubik_dbase`, and `ubik_updatecache_func`. Public constants include transaction modes `UBIK_READTRANS` and `UBIK_WRITETRANS`, lock modes `LOCKREAD`, `LOCKWRITE`, `LOCKWAIT`, client flags `UPUBIKONLY` and `UBIK_CALL_NEW`, service ids `VOTE_SERVICE_ID`, `DISK_SERVICE_ID`, `USER_SERVICE_ID`, `MAXSERVERS`, `UBIK_MAGIC`, and `UBIK_MILESTONE`.

The central state model is `struct ubik_dbase`: path prefix, active transactions, version, version lock, transaction counters, disk-operation callbacks, reader counts, `cachedVersion`, and `cache_lock`. `struct ubik_trans` binds a transaction to its database, lock state, queued truncates, tid, seek position, flags, type, and write batching iovec buffers. `struct ubik_client` stores randomized Rx connections, per-server failure bits, sync-site hint, and a pthread mutex where available.

Under `UBIK_INTERNALS`, the header defines disk/log constants, transaction flags (`TRDONE`, `TRABORT`, `TRREADANY`, `TRCACHELOCKED`, `TRREADWRITE`), timer constants (`MAXSKEW`, `POLLTIME`, `RPCTIMEOUT`, `BIGTIME`, `SMALLTIME`, `VOTE_RPCTIMEOUT`), `struct ubik_server`, recovery state bits, and global structures for beacon, vote, address, and version locks. The lock-order comment is a critical integration contract: application cache, database, beacon, vote, version, then address lock.

Dependencies are broad: Rx-generated `ubik_int.h`, pthread or LWP, AFS locks, cell configuration, security classes, and physical disk/recovery/beacon/vote modules. The header is also where server/client security callback APIs and generic client initialization (`ugen_ClientInit*`) are declared.

Risks are mostly ABI and concurrency risks. This header exposes private internals to many compilation units, so flag or struct layout changes can silently affect lock/recovery semantics. `vcmp` subtracts version fields and assumes safe signed deltas. Test signals are compile- and integration-heavy: build all Ubik consumers, run client/server initialization, validate cache callback contracts, and stress lock ordering with pthread builds.
