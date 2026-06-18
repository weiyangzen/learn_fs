# sources/control-plane/mayastor/io-engine/src/core/device_events.rs

## Purpose
Defines the in-process device event listener model used by block-device implementations and nexus children. It lets device owners publish removal, resize, media, and NVMe admin-queue failure events without hard-coupling to the nexus logic that reacts to them.

## Important APIs, Types, and Functions
- `DeviceEventType` enumerates operational events: `DeviceRemoved`, `LoopbackRemoved`, `DeviceResized`, `MediaManagement`, `AdminCommandCompletionFailed`, `AdminQNoticeCtrlFailed`, and `AdminQBroken`.
- `DeviceEventListener` is the consumer trait with `handle_device_event(evt, dev_name)` and optional `get_listener_name`.
- `DeviceEventSink` wraps a listener in an `Arc` and exposes a weak reference to the dispatcher.
- `DeviceEventDispatcher` stores `Weak<SinkInner>` listeners, supports `add_listener`, `dispatch_event`, `count`, and internal `purge`.

## Control Flow and State
Callers create a `DeviceEventSink` from a listener and retain a clone as the lifetime anchor. `DeviceEventDispatcher::add_listener` stores only a weak reference, then purges stale entries. `dispatch_event` upgrades live weak references into temporary `Arc`s while holding the listener-list mutex, drops the mutex before invoking callbacks, and purges again afterwards.

State is entirely memory resident. There is no persistence; listener retention is intentionally driven by `Arc` ownership outside the dispatcher.

## Dependencies and Integration Points
Uses `parking_lot::Mutex` and `Arc`/`Weak`. Integrated from `core/mod.rs`, bdev/device event dispatch, NVMe controller notifications, and nexus child handling. Nexus implements `DeviceEventListener` in `nexus_bdev_children.rs`.

## Risks and Test Signals
The sink uses `transmute` to convert a borrowed trait object to `'static`, relying on the caller retaining the actual listener for as long as its `DeviceEventSink` exists. Misuse can create dangling references. The dispatcher avoids callback-under-lock deadlocks, which is a key concurrency property to preserve. Tests should exercise listener drop/purge behavior, multiple listeners, and dispatch during callbacks that mutate registration state.
