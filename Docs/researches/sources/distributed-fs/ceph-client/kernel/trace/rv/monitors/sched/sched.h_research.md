# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/sched.h

## Purpose

This header declares the scheduler RV monitor container.

## Important APIs, Types, and Functions

It exposes `extern struct rv_monitor rv_sched;`.

## Control Flow

There is no runtime flow; child monitor modules include it for parent registration.

## State and Persistence Behavior

It declares state owned by `sched.c`.

## Dependencies and Integration Points

Including code must already know `struct rv_monitor`. It integrates all scheduler child monitors with the container.

## Risks and Edge Cases

The child modules must link with the container symbol.

## Test Signals

Compile/link tests with scheduler child monitors enabled verify the declaration and symbol.
