# sources/distributed-fs/ceph-client/kernel/trace/rv/reactor_panic.c

## Purpose

This module registers the `panic` RV reactor, which panics the kernel when a monitor exception triggers the selected reactor.

## Important APIs, Types, and Functions

`rv_panic_reaction()` calls `vpanic(msg, args)`. `rv_panic` is a `struct rv_reactor` with name `panic`, description, and reaction callback. Module init/exit register and unregister the reactor.

## Control Flow

When loaded, `register_react_panic()` calls `rv_register_reactor(&rv_panic)`. If a monitor selects this reactor and `reacting_on` is true, RV core calls the reaction through `rv_react()`, leading directly to `vpanic()`.

## State and Persistence Behavior

The only state is the reactor's registration in the RV reactor list and any monitor selection pointing at it. It persists while the module is loaded.

## Dependencies and Integration Points

It depends on `<linux/rv.h>` reactor APIs and integrates with `rv_reactors.c` selection files under `monitors/*/reactors`.

## Risks and Edge Cases

This reactor is destructive by design. It should be used only when a monitor violation should halt the system. Registration ignores the return value, so duplicate registration failures do not abort module init.

## Test Signals

In a controlled test kernel, select `panic` for a deliberately failing monitor such as `wwnr` and verify a panic occurs with the monitor message.
