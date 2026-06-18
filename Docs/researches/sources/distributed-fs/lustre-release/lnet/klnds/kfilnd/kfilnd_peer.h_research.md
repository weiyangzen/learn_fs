<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.h_research.md`.

Purpose: declares peer-cache and peer-health APIs used by transaction and device code.

Important APIs/types/functions: `KP_PURGE_LIMIT`, `kfilnd_peer_get/put()`, `kfilnd_peer_alive()`, `kfilnd_peer_destroy/init()`, `kfilnd_peer_get_kfi_addr()`, `kfilnd_peer_target_rx_base()`, `kfilnd_peer_process_hello()`, and `kfilnd_peer_tn_failed()`.

Control flow: transactions acquire peers during allocation, update liveness on completions, process hellos, and report failures; device teardown destroys the cache.

State and persistence behavior: no state is defined here, but `KP_PURGE_LIMIT` establishes how long stale/down peers can remain before cache removal.

Dependencies and integration: includes `kfilnd.h`, so callers share private peer/device/message structures.

Risks: timeout-derived purge duration changes with `kfi_timeout`. Callers must hold/release peer references correctly.

Test signals: compile all users, run peer lifecycle under traffic, and verify purge timing changes when timeout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.h -->
