# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_peerni.c

## Purpose
This file implements EFALND peer-NI metadata discovery and caching. For small IPv4-style EFA NIDs, it discovers remote EFA GID and CM QP information by issuing an LNet TCP metadata ping and caches results in a global rhashtable.

## Important APIs, Types, And Functions
Public functions are `kefalnd_lookup_or_create_peer_ni()`, `kefalnd_put_peer_ni()`, `kefalnd_update_peer_ni()`, `kefalnd_find_remote_peer_ni()`, and `kefalnd_get_nid_metadata()`. Internal helpers include `efa_nid_to_tcp_nid()`, `peer_ni_free()`, and `get_peer_ni()`. The metadata payload uses `struct kefa_nid_md_entry` from `efalnd_proto.h`.

## Control Flow
For small NIDs, `kefalnd_find_remote_peer_ni()` first looks up the EFA NID address in the peer rhashtable. On miss, it derives the remote TCP NID by combining the local underlay subnet with the EFA NID host bytes, calls `lnet_discover_nid_metadata()` with a 30 second timeout, scans returned mappings for EFALND entries matching the requested address, and inserts or retrieves a `kefa_peer_ni` with GID, CM QP number, and QKEY. Local nodes publish their own metadata through `kefalnd_get_nid_metadata()`, which fills the ping reply entry from the local EFA device.

## State, Persistence, And Dependencies
Peer metadata is stored in `kefalnd.peer_ni`, keyed by 32-bit EFA NID address, protected by RCU plus per-peer rwlock and kref. `peer_ni_free()` removes entries unless EFALND is shutting down, decrements `peer_ni_count`, and frees via `kfree_rcu()`. The cache is in-memory only and is destroyed during base shutdown.

## Integration Points
Connection establishment uses this file for small-NID remote GID/CM-QP lookup. LNet discovery supplies remote metadata over TCP. Debugfs reads the same rhashtable. `efalnd.c` creates a self peer-NI for small local NIDs.

## Risks
The small-NID to TCP-NID derivation assumes IPv4 and same upper subnet bits. Cache keying by address means collisions are possible if generated small NIDs are not unique. Metadata lookup can block connection establishment for the TCP ping timeout. Updating peer entries races with debug reads and connection reads, so rwlock/RCU use must remain correct. `PTR_ERR(NULL)` patterns require care when helpers can return NULL.

## Test Signals
Tests should cover cache hit/miss, TCP metadata discovery success/failure/timeout, multiple returned mappings, non-EFALND mappings, self metadata publication, concurrent lookup/update/free, shutdown while lookups are in flight, and small-NID derivation from representative IP/device values.
