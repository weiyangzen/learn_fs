# sources/distributed-fs/ceph-client/kernel/trace/rv/rv.h

## Purpose

This private RV header defines shared RV interface structures, tracefs wrappers, size limits, exported RV core symbols, and reactor stubs/prototypes.

## Important APIs, Types, and Functions

It defines `struct rv_interface`, aliases RV file modes and create/remove helpers to tracefs APIs, `DEFINE_FREE(rv_remove, ...)`, `MAX_RV_MONITOR_NAME_SIZE`, `MAX_RV_REACTOR_NAME_SIZE`, and extern declarations for locks, monitor list, monitor control helpers, and reactor setup.

## Control Flow

The header has no runtime flow. Compile-time conditionals provide real reactor functions under `CONFIG_RV_REACTORS` or no-op stubs otherwise.

## State and Persistence Behavior

It declares shared in-memory state but owns none. Tracefs dentries are managed by implementation files using the cleanup helper.

## Dependencies and Integration Points

It includes tracing internals, tracefs, mutex, and public `<linux/rv.h>`. It is used by RV core and reactor implementation files.

## Risks and Edge Cases

Name size constants constrain user-visible monitor/reactor names. Stubbing reactors when disabled means monitor directories omit reactor files without changing monitor code.

## Test Signals

Compile coverage with and without `CONFIG_RV_REACTORS`, and tests for monitor/reactor name length validation.
