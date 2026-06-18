# sources/distributed-fs/ceph-client/kernel/trace/rv/rv_reactors.c

## Purpose

This file implements the RV reactor registry and user interface. Reactors are selectable reactions invoked when a runtime monitor reports a model exception.

## Important APIs, Types, and Functions

It defines `rv_reactors_list`, `rv_register_reactor()`, `rv_unregister_reactor()`, `reactor_populate_monitor()`, `init_rv_reactors()`, `rv_react()`, and the built-in `nop` reactor. File operations expose `available_reactors`, global `reacting_on`, and per-monitor `reactors` selection files.

## Control Flow

Initialization creates `available_reactors` and `reacting_on`, registers `nop`, and enables reacting. Monitor directory creation calls `reactor_populate_monitor()`, which creates a `reactors` file and sets the monitor reactor to `nop`. Reading a monitor reactor file lists all reactors with the selected one in brackets. Writing a reactor name swaps the monitor to that reactor, disabling and re-enabling the monitor if necessary; container swaps propagate to direct children. `rv_react()` checks `reacting_on` and monitor callback presence before invoking the selected reaction under a lockdep wait-free map.

## State and Persistence Behavior

State is in-memory: registered reactor list, per-monitor selected reactor pointer/callback, and global `reacting_on`. There is no persistence beyond module/runtime lifetime.

## Dependencies and Integration Points

It depends on RV core lock/list state, seq files, tracefs file creation through `rv.h`, memory barriers for `reacting_on`, and external reactors such as `printk` and `panic`.

## Risks and Edge Cases

Swapping a reactor on a container can enable all children afterward, even children that were previously off, as noted by the source comment. `reactor_populate_monitor()` assumes `nop` is registered before monitor population; initialization order must preserve that. Unregistering a reactor does not scan monitors that may still point to it.

## Test Signals

Test reactor listing, per-monitor selection, global `reacting_on` toggling, container reactor swaps, monitor re-enable around swaps, duplicate reactor registration, and violations with `nop`, `printk`, and `panic` reactors.
