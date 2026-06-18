# sources/distributed-fs/ceph-client/kernel/trace/rv/reactor_printk.c

## Purpose

This module registers the `printk` RV reactor, which logs monitor exception messages to the kernel log without halting the system.

## Important APIs, Types, and Functions

`rv_printk_reaction()` calls `vprintk_deferred(msg, args)`. `rv_printk` is a `struct rv_reactor` named `printk`, with module init/exit registration.

## Control Flow

On load, the reactor is registered. When selected for a monitor and reactors are globally enabled, `rv_react()` invokes the deferred printk callback for violations.

## State and Persistence Behavior

State is limited to reactor registration and monitor selection. No messages are persisted beyond normal kernel log behavior.

## Dependencies and Integration Points

It depends on RV reactor APIs and integrates with the reactor selection tracefs files created by `rv_reactors.c`.

## Risks and Edge Cases

High-frequency monitor violations can flood kernel logs. Registration return value is ignored, so duplicate-name failures are silent to module init.

## Test Signals

Select `printk` on a monitor that can violate and verify deferred kernel log output without panic.
