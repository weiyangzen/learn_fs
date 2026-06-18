# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_modparams.c

## Purpose

`gnilnd_modparams.c` declares and validates module parameters for the gnilnd driver and exposes them through the global `kgnilnd_tunables` pointer table. These tunables control send credits, mailbox sizing, timeout/reconnect behavior, checksum policy, RDMA options, scheduler behavior, peer health handling, purgatory limits, and platform-specific defaults.

## Important APIs, Types, And Functions

Parameters cover flow control (`credits`, `peer_credits`, `concurrent_sends`, `fma_cq_size`, `eager_credits`, `mbox_credits`), timeouts and reconnects (`timeout`, `min_reconnect_interval`, `max_reconnect_interval`, `hardware_timeout`, `mdd_timeout`, `sched_timeout`, `dgram_timeout`, `fast_reconn`, `to_reconn_disable`), message/RDMA sizing and checksums (`max_immediate`, `checksum`, `checksum_dump`, `vmap_cksum`, `reverse_rdma`), GNI behavior (`bte_put_dlvr_mode`, `bte_get_dlvr_mode`, `bte_relaxed_ordering`, `ptag`, `pkey`, `thread_safe`), retry/resource limits (`max_retransmits`, `rdmaq_intervals`, `max_conn_purg`, `reg_fail_timeout`, `vzalloc_no_retry`), threading (`nice`, `sched_nice`, `sched_threads`, `loops`, `thread_affinity`), hash/datagram sizing (`hash_size`, `net_hash_size`, `nwildcard`, `mbox_per_block`, `nphys_mbox`), peer health (`peer_health`, `peer_timeout`), and fault behavior (`efault_lbug`).

`kgn_tunables_t kgnilnd_tunables` stores pointers to all parameter variables so other files read current values through a uniform global structure.

`kgnilnd_tunables_init()` validates checksum mode, bounds `max_immediate`, normalizes `mbox_per_block`, and derives or validates `concurrent_sends`.

`kgnilnd_tunables_setup(struct lnet_ni *ni)` applies credit defaults to the LNet network when net tunables were not explicitly set, fills gnilnd-specific ioctl tunables, records `CURRENT_LND_VERSION`, and exports the effective timeout.

## Control Flow

At module load, Linux module parameter declarations make values available through module arguments/sysfs permissions. `kgnilnd_tunables_init()` is the validation gate before the driver uses them. It switches over checksum mode and emits console messages for valid enabled modes; invalid checksum modes return `-EINVAL`. It rejects `max_immediate` above `GNILND_MAX_IMMEDIATE`, clamps `mbox_per_block` to at least 1, and if `concurrent_sends` is zero sets it to `peer_credits`; otherwise it rejects values larger than `peer_credits`.

When an LNet NI is configured, `kgnilnd_tunables_setup()` copies driver credit defaults into `ni->ni_net->net_tunables` only if the LNet network tunables were not already set. It then writes gnilnd-specific tunables under `ni->ni_lnd_tunables.lnd_tun_u.lnd_gni`.

## State And Persistence Behavior

The module parameter variables are static file-scope kernel state. Many are read-only after module load due to mode `0444`; others are runtime-writable with `0644`, including reconnect intervals, checksum mode/dump level, BTE delivery modes, relaxed ordering, RDMA throttle intervals, loop count, vmap checksum, mailbox block size/credits, MDD/scheduler/dgram timeouts, reverse RDMA, fault LBUG behavior, fast reconnect, purgatory limit, reg-failure timeout, timed-out reconnect disable, and vmalloc retry behavior.

`kgnilnd_tunables` stores pointers, not copies, so runtime-writable parameters affect code paths that read through the pointer table after the write. No disk persistence is implemented; sysfs/module parameter persistence depends on normal kernel/module configuration outside this file.

## Dependencies And Integration Points

The file depends on `gnilnd.h` for `kgn_tunables_t`, constants, `kgnilnd_timeout()`, and gnilnd/LNet tunable structures. Platform defaults from headers such as `gnilnd_gemini.h` feed initial values for timeout, checksum, RDMA delivery mode, scheduler threads, reverse RDMA, and thread-safe KGNI.

`gnilnd_cb.c` reads timeout, checksum, max immediate, RDMA delivery/ordering, retry limits, RDMA throttling, scheduler loops/timeouts/nice, reverse RDMA, eager credits, purgatory, and failure behavior. `gnilnd_conn.c` reads mailbox sizing/credits, physical mailbox count, wildcard datagram count, hash size, timeout, register-failure timeout, and nice values.

## Risks And Edge Cases

- Runtime-writable tunables can change while data-plane code is executing. Many paths intentionally reread checksum and RDMA options at send time, but changes to sizing/timeouts can create mixed behavior across existing connections.
- `eager_credits` defaults to `256 * 1024`, a large count-like limit that can cause high memory pressure for eager copies.
- Very small `max_immediate` values can force more RDMA and memory registration pressure.
- `concurrent_sends` is only validated against `peer_credits`; comments say it sizes mailbox buffers rather than enforcing a hard send cap.
- `checksum` can be changed at runtime. Mixed enabled/disabled endpoints are tolerated by warnings around missing checksums, but fault isolation may be harder during live changes.
- Runtime-writable recovery knobs (`efault_lbug`, `reg_fail_timeout`, `to_reconn_disable`, `max_conn_purg`) can materially change recovery characteristics on a live system.
- Hash-size parameters are expected to be prime by description but not validated as prime here.

## Test Signals

- Module-load tests should validate invalid checksum values, excessive `max_immediate`, `mbox_per_block < 1`, `concurrent_sends == 0`, and `concurrent_sends > peer_credits`.
- LNet setup tests should verify NI credit defaults are applied only when net tunables were not user-set and that gnilnd ioctl tunables report version and timeout.
- Runtime sysfs tests should flip writable parameters such as checksum mode, checksum dump, RDMA delivery mode, rdmaq intervals, reverse RDMA, fast reconnect, and purgatory limit while traffic is active.
- Configuration tests should cover platform defaults from Gemini/compute versus service builds and KNC-specific `ptag` selection under `CONFIG_MK1OM`.
