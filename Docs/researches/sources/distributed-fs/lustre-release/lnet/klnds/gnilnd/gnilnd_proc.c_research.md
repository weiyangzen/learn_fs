<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_proc.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_proc.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_proc.c_research.md`.

Purpose: implements the `/proc` diagnostics and test controls for the Lustre GNI LND. It exposes aggregate device counters, memory descriptor debug views, SMSG/FMA mailbox inventory, connection and peer listings, per-peer connection tracing, and a write-only checksum benchmark.

Important APIs/types/functions: proc entry names are `stats`, `mdd`, `smsg`, `conn`, `peer_conns`, `peer`, and `cksum_test`. `_kgnilnd_proc_run_cksum_test()` allocates bio_vec pages and compares `kgnilnd_cksum_kiov()` over copied data. `kgnilnd_stats_seq_show()` and `kgnilnd_proc_stats_write()` sample and reset counters. Iterator structs `kgn_mdd_seq_iter_t`, `kgn_smsg_seq_iter_t`, `kgn_conn_seq_iter_t`, and `kgn_peer_seq_iter_t` back seq-file walkers. `kgnilnd_proc_init()` creates the tree and `kgnilnd_proc_fini()` removes it.

Control flow: init creates the proc directory named from `libcfs_lnd2modname(GNILND)`, then registers checksum, stats, MDD, SMSG, connection, per-peer connection, and peer files with unwind labels on failure. Reads enter seq-file start/seek/show/next/stop callbacks. MDD iteration locks the device map list for the read pass, SMSG iteration versions and locks FMA blocks around individual seeks/shows, and peer/connection walkers use `kgn_peer_conn_lock` with version checks plus temporary refcounts. Writes either parse small user buffers or reset sampled counters.

State and persistence behavior: no durable state is stored. The proc files expose live global `kgnilnd_data`, device atomics, peer/connection lists, FMA memory blocks, and transmit map state. `stats` write clears selected counters with a write barrier. `peer_conns` stores a global debug NID until changed. Iterators detect list mutation using version counters and may return `-ESTALE`.

Dependencies and integration: depends on `gnilnd.h`, Linux procfs/seq_file, Lustre libcfs allocation/logging helpers, LNet NID formatting, GNI memory handle fields, and internal peer/connection/FMA structures. The checksum test integrates with LNet iov copy helpers and GNI checksum code.

Risks: several readers intentionally sample racy state; MDD holds a spinlock over seq traversal, which can be intrusive on large maps. `smsg_seq_next()` frees the iterator on seek failure even though `stop()` may also run, so error-path ownership is delicate. User-triggered checksum tests can allocate many pages and run long loops. Proc teardown order must match creation order.

Test signals: mount procfs and read each file before and after traffic, reset `stats` and confirm selected counters clear, exercise checksum cases 0-3 with odd/even offsets, mutate peers/connections while reading for `-ESTALE` behavior, set `peer_conns` to valid and invalid NIDs, and verify init unwind leaves no partial proc entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_proc.c -->
