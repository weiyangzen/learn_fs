# Research: sources/distributed-fs/ceph-client/net/llc/llc_proc.c

## sources/distributed-fs/ceph-client/net/llc/llc_proc.c

Purpose: Exposes LLC socket and connection-core diagnostics under `/proc/net/llc`.

Important APIs/types/functions: Provides `llc_proc_init()` and `llc_proc_exit()`. It defines seq_file operations for `socket` and `core`, iterator helpers over `llc_sap_list` and each SAP's `sk_laddr_hash`, and a state-name table for `LLC_CONN_STATE_*`.

Control flow: Init creates `/proc/net/llc/socket` and `/proc/net/llc/core`; failure unwinds previously created entries. Seq iteration starts under `rcu_read_lock_bh()`, locates sockets by logical position, keeps the current SAP `sk_lock` held while walking a hash bucket, advances across buckets and SAPs, and unlocks in stop. Show functions render socket addressing/queues/state/user/link or LLC2 internals like retry count, windows, flags, timer pending bits, backlog presence, and socket ownership.

State and persistence behavior: This file stores only the proc directory pointer and static names. It reads live socket/SAP state and timer state without changing protocol behavior.

Dependencies and integration points: Depends on `llc_sap_list` from `llc_core.c`, `llc_sock` layout from LLC connection headers, seq_file/proc APIs, user namespace UID formatting, and timer/backlog helpers.

Risks and test signals: Iterator locking is delicate: early returns intentionally keep `sap->sk_lock` until seq stop. State-name indexing assumes valid LLC states. Test by opening/reading proc files while sockets are created/destroyed, with multiple SAP hash buckets populated, and with connections in each major state. KASAN/lockdep are useful for iterator lifetime issues.
