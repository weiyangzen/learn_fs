# sources/distributed-fs/ceph-client/include/net/bluetooth/hci_sync.h

## Purpose

`hci_sync.h` declares the synchronous HCI command/request framework and higher-level synchronous Bluetooth state-update helpers used by HCI core and management code.

## Important APIs, Types, and Functions

`struct hci_request` holds an HCI device, a command queue, and an error accumulator. `struct hci_cmd_sync_work_entry` queues a work function, data pointer, optional destroy callback, and list node. Sync command APIs allocate and send commands, wait for command complete/status or a specific event, optionally associate a socket, and return skbs or status. Queue APIs initialize/clear/cancel sync state, submit/queue/run work entries, find/cancel/dequeue entries, and provide once-only variants. Higher-level helpers cover EIR/class/name/SSP, random address selection, advertising data and instances, periodic advertising, passive/active scan updates, RSSI/TX power/clock reads, SC/LE host support, reset/open/close/powered transitions, discoverable/connectable/discovery, suspend/resume, connection abort/connect/cancel/update, CIS/BIG/PA operations, PAST, remote LE features, ACL packet type changes, and LE PHY changes.

## Control Flow

Callers serialize sync command work with `hdev->req_lock` and command-sync workqueues. A sync helper builds one or more HCI commands, waits for completion or status with timeout, and updates core state through the event path. Comments explicitly warn that `*_sync` functions must not be called with `hdev->lock` held because received events may try to acquire that lock, causing deadlock.

## State and Persistence Behavior

No persistent storage is declared. Runtime state is `hci_dev` request queues, wait queues, sync work lists, command skbs, status/result fields, and command timeout behavior. Operations can change controller configuration such as advertising, scanning, power, and connection state.

## Dependencies and Integration Points

The header depends on HCI core/device structures, sk_buffs, workqueues, sockets, and HCI command/event definitions. It integrates with management operations, setup/open/close, LE advertising/scanning, privacy, ISO, and connection management.

## Risks and Edge Cases

Deadlock risk is explicit if sync calls run while holding `hdev->lock`. Queue-once semantics depend on matching function/data/destroy triples. Cancellation must invoke destroy callbacks exactly once with a meaningful error. Timeout handling must free returned skbs and leave command state consistent. Socket-associated commands need correct attribution and cleanup if the socket closes.

## Test Signals

Test sync command success/status/error/timeout, expected-event matching, cancellation and cancel-sync paths, queue/run/once/dequeue behavior, destroy callback invocation, lockdep for `hdev->lock` misuse, advertising/scan/discovery helpers, suspend/resume, connection abort/connect/update, ISO CIG/BIG/PA helpers, and socket-associated command cleanup.
