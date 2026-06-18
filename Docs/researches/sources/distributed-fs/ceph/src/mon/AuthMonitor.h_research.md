<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/AuthMonitor.h -->
# sources/distributed-fs/ceph/src/mon/AuthMonitor.h

## Purpose
`AuthMonitor.h` declares the monitor Paxos service that manages Ceph authentication metadata. It exposes the public auth-handshake, global-id, OSD key lifecycle, and diagnostic entry points while keeping command processing, auth map persistence, capability validation, and format upgrade machinery private.

## Important APIs, types, and functions
`AuthMonitor` derives from `PaxosService`. Its nested `Incremental` type is the persisted update record and has two variants: `GLOBAL_ID` for id range extension and `AUTH_DATA` for encoded `KeyServerData::Incremental` CephX changes. `auth_entity_t` groups `EntityName` with `EntityAuth` for OSD creation flows. The public methods include `_assign_global_id()`, `_set_mon_num_rank()`, `pre_auth()`, `tick()`, OSD create/destroy validation and apply methods, `dump_info()`, and `is_valid_cephx_key()`.

Private declarations cover bootstrap and upgrade helpers, keyring import/export, pending incremental encoding, Paxos hooks, command preprocess/prepare split, auth handshake preparation, cap validation and encoding, entity create/update/delete helpers, pending-key promotion, and global-id range management. The `caps_update` enum communicates whether `fs authorize` cap merging requires a stored update.

## Control flow
The header defines the service contract used by `Monitor`: read-only auth and auth handshakes can be handled during preprocess, while mutating auth commands and leader-only maintenance are prepared through Paxos. Bootstrap starts with `create_initial()`, normal updates replay through `update_from_paxos()`, and each new proposal starts from `create_pending()`.

## State and persistence behavior
Persistent state is represented by encoded `Incremental` records and full snapshots implemented in the `.cc` file. In-memory pending state is `std::vector<Incremental> pending_auth`; committed id allocation state is `max_global_id`; local id allocation cursor is `last_allocated_id`. `mon_num` and `mon_rank` are explicitly protected by `mon.auth_lock`, and the header documents that `_assign_global_id()` and `_set_mon_num_rank()` must be called under that lock.

## Dependencies and integration points
The declaration depends on Ceph auth primitives (`CephxKeyServer`, `KeyRing`, `EntityName`, `EntityAuth`), monitor persistence (`PaxosService`, `MonitorDBStore`), wire feature encoding, and monitor message request references. The `WRITE_CLASS_ENCODER_FEATURES(AuthMonitor::Incremental)` macro makes incrementals part of the Ceph encoding contract.

## Risks and edge cases
The header exposes `_assign_global_id()` publicly despite requiring lock discipline, so callers must honor the comment contract. `Incremental::decode()` asserts the enum range and assumes only known variants. Any new auth update kind requires changing both encoding and replay logic. `is_valid_cephx_key()` only validates base64 decoding into a `CryptoKey`; policy validation must happen elsewhere.

## Test signals
Compile-time encoder tests should cover all `Incremental::generate_test_instances()`. Runtime tests should verify lock-protected global id assignment, command routing through preprocess/prepare, OSD key helper contracts, pending-key feature gating, and backward-compatible decoding of auth incrementals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/AuthMonitor.h -->
