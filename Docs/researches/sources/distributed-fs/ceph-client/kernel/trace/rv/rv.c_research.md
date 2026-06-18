# sources/distributed-fs/ceph-client/kernel/trace/rv/rv.c

## Purpose

This file implements the runtime-verification user interface, monitor registration hierarchy, monitor enable/disable control, global monitoring switch, per-task monitor slot allocation, and tracefs/debugfs-style files under `rv/`.

## Important APIs, Types, and Functions

It defines `rv_interface_lock`, `rv_root`, `rv_monitors_list`, task monitor slot state, `get_monitors_root()`, `rv_get_task_monitor_slot()`, `rv_put_task_monitor_slot()`, `rv_is_nested_monitor()`, `rv_is_container_monitor()`, `rv_enable_monitor()`, `rv_disable_monitor()`, `rv_register_monitor()`, `rv_unregister_monitor()`, `rv_monitoring_on()`, and `rv_init_interface()`. File operations implement `available_monitors`, `enabled_monitors`, `monitoring_on`, and per-monitor `enable`/`desc`.

## Control Flow

Initialization creates `rv/`, `rv/monitors`, monitor list files, global `monitoring_on`, initializes reactors, and turns monitoring on. Monitor registration validates name length and uniqueness, rejects nested parents beyond one level, creates the monitor directory, and inserts children next to their parent. Enabling a container enables each direct child; disabling a container disables all direct children and synchronizes tracepoint callbacks once. Writing `enabled_monitors` enables or disables by name, with `!` disabling and truncate disabling all. Turning monitoring back on resets enabled monitors first to resynchronize state after ignored events.

## State and Persistence Behavior

State is in memory: registered monitor list, tracefs dentries, enabled flags, parent/root pointers, global `monitoring_on`, and per-task monitor slot allocation. There is no persistence across reboot or module unload.

## Dependencies and Integration Points

It depends on tracefs helpers, seq files, mutex/guard cleanup helpers, RV public APIs, optional RV tracepoints, and reactor initialization. Monitor modules call `rv_register_monitor()`/`rv_unregister_monitor()` and use `rv_monitoring_on()` indirectly through monitor frameworks.

## Risks and Edge Cases

Global locking serializes registration and user writes. Disable paths call `tracepoint_synchronize_unregister()` to avoid callbacks using destroyed state. Container detection relies on child list adjacency and missing enable callbacks. Writing nested names trims the parent prefix and matches by child name only, so duplicate child names across containers would conflict with the global uniqueness check.

## Test Signals

Tracefs tests should cover available/enabled reads, enable/disable writes, `!monitor` disable, truncate disable-all, container enable/disable, monitoring_on reset behavior, registration duplicate/name-length failures, and task monitor slot exhaustion.
