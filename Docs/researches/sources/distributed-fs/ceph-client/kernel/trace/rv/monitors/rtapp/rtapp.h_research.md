# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/rtapp.h

## Purpose

This header declares the `rtapp` monitor container symbol for child monitors.

## Important APIs, Types, and Functions

It exposes `extern struct rv_monitor rv_rtapp;`.

## Control Flow

There is no control flow; child modules include it and pass `&rv_rtapp` to `rv_register_monitor()`.

## State and Persistence Behavior

It declares shared container state owned by `rtapp.c`.

## Dependencies and Integration Points

It requires `struct rv_monitor` to be visible from including code and is used by RT-app child monitors.

## Risks and Edge Cases

Linkage requires the container object to be built when children are built.

## Test Signals

Compile/link tests with `pagefault` and `sleep` enabled verify the declaration.
