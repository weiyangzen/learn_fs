# sources/distributed-fs/ceph-client/net/dcb/dcbevent.c

## Purpose

`dcbevent.c` implements the small exported DCB event notification bus. It lets DCB users register notifier blocks and lets DCB core code broadcast events such as application-priority mapping changes.

## Important APIs, Types, and Functions

The public functions are `register_dcbevent_notifier()`, `unregister_dcbevent_notifier()`, and `call_dcbevent_notifiers()`. They operate on the file-local `ATOMIC_NOTIFIER_HEAD(dcbevent_notif_chain)`.

## Control Flow

Consumers register a `struct notifier_block` into the atomic notifier chain. DCB code calls `call_dcbevent_notifiers(val, v)` with an event ID and event payload. The notifier core invokes registered callbacks in priority order and returns the aggregate notifier result.

## State and Persistence Behavior

The notifier chain is global kernel state for the lifetime of the DCB subsystem. It stores registered notifier blocks but does not own their memory; callers must unregister before freeing their blocks.

## Dependencies and Integration Points

The file depends on Linux notifier APIs and exports its functions for other kernel modules. `dcbnl.c` calls `call_dcbevent_notifiers(DCB_APP_EVENT, &event)` after successful APP table changes.

## Risks

The chain is atomic, so notifier callbacks must obey atomic notifier constraints and avoid sleeping where not allowed. Lifetime bugs occur if a module frees a notifier block without unregistering it.

## Test Signals

Tests should register multiple notifier blocks, trigger DCB app changes, verify callback ordering and payload content, and validate clean unregister paths during module/device teardown.
