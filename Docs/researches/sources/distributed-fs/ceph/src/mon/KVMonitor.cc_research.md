# sources/distributed-fs/ceph/src/mon/KVMonitor.cc

## Purpose
`KVMonitor.cc` implements the monitor-backed config-key key/value service, including command handling, Paxos deltas, OSD dm-crypt helpers, and `kv:` subscriptions.

## Important APIs, Types, and Functions
Important methods are `preprocess_command`, `prepare_command`, `encode_pending`, `update_from_paxos`, `_have_prefix`, OSD validate/do helpers, subscription checks, and `maybe_send_update`. `KV_PREFIX` is `mon_config_key`; pending values are optional bufferlists where empty optional means delete.

## Control Flow
Read commands are answered during preprocess from the store. Mutating commands parse key/value or input payload, enforce entry-size limits, stage pending deltas, force immediate propose, and reply after commit. `update_from_paxos()` advances version and notifies subscribers.

## State and Persistence
Each commit writes an encoded pending delta under the service version and applies actual values under `mon_config_key`. Only the last 50 delta versions are retained for incremental subscribers.

## Dependencies and Integration Points
It uses `MonitorDBStore`, `KeyValueDB`, `MMonCommand`, `MKVData`, session subscriptions, config limits, and OSD lifecycle code for dm-crypt and daemon-private keys.

## Risks
Subscribers outside retained history require full dumps. Prefix scans for OSD destroy must catch all relevant keys. `validate_osd_new()` uses positive `EEXIST` for idempotent success and negative `-EEXIST` for mismatch.

## Test Signals
Cover get/exists/list/dump, binary masking, size rejection, set/delete commits, full/incremental subscription updates, onetime removal, and OSD dm-crypt idempotency/removal.
