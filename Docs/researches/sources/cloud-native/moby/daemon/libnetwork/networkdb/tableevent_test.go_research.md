## sources/cloud-native/moby/daemon/libnetwork/networkdb/tableevent_test.go

Purpose: targeted tests for table event ordering, watch synthesis, filtering, and leave/rejoin races in NetworkDB. It focuses on subtle Lamport and tombstone behavior that broad cluster tests may not isolate.

Important APIs/types/functions: tests include `TestWatch_out_of_order`, `TestWatch_filters`, and `TestLeaveRejoinOutOfOrder`; helpers include `messageBuffer`, `Append`, `Compound`, `Reset`, and `tableEventHelper`. The tests exercise `eventDelegate.NotifyJoin`, `delegate.NotifyMsg`, `makeCompoundMessage`, `encodeMessage`, `Watch`, and `WalkTable`.

Control flow: tests manually build compound gossip payloads with specific Lamport times, inject them into a single NetworkDB instance, then drain watch channels or table state. The out-of-order test creates cases such as create/delete gaps, hidden recreates, update-before-create, and stale delete/create pairs.

State and persistence behavior: the tests inspect in-memory table entries and watch queue output. Synthetic initial watch events exclude local entries and deleted entries. Leave/rejoin regression verifies that rebroadcast or bulk-sync table events do not lose valid state when network leave/join events arrive around them.

Dependencies and integration points: integrates generated protobuf event types, memberlist node notification, Serf Lamport times, docker/go-events channels, and helpers from the broader networkdb package.

Risks: the tests encode exact event sequences, so changing watch semantics or event ordering must update expected event lists carefully. Manual message injection bypasses some memberlist paths, which is good for determinism but not full end-to-end coverage.

Test signals: high-value regression signal for watchers. Expected behavior includes deletes reporting the last observed value, updates to unknown/deleted keys surfacing as creates, stale create/delete suppression, table/network filters, and correct state after leave/rejoin out-of-order delivery.
