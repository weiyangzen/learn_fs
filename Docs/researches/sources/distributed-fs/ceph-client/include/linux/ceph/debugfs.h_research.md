# sources/distributed-fs/ceph-client/include/linux/ceph/debugfs.h

## Purpose

`debugfs.h` declares libceph debugfs lifecycle hooks for global Ceph debugfs setup and per-client debugfs entries.

## Important APIs, Types, and Functions

The API consists of `ceph_debugfs_init()`, `ceph_debugfs_cleanup()`, `ceph_debugfs_client_init()`, and `ceph_debugfs_client_cleanup()`.

## Control Flow

Global init/cleanup are called when the Ceph support module initializes and exits. Per-client init/cleanup are called as `struct ceph_client` instances are created and destroyed.

## State and Persistence Behavior

This header owns no state. Runtime state is held by debugfs dentries in `struct ceph_client` under `CONFIG_DEBUG_FS`, including monmap, osdmap, options, and client directories.

## Dependencies and Integration Points

It includes Ceph types and uses forward-declared `struct ceph_client` from includer context. It integrates with `libceph.h` fields and debugfs implementation code.

## Risks and Edge Cases

Debugfs is optional. Callers and implementations must handle disabled debugfs, partially initialized clients, and cleanup order so dentries are not removed after the client storage is gone.

## Test Signals

Build with and without `CONFIG_DEBUG_FS`, create/destroy clients repeatedly, inspect expected debugfs files, and run teardown paths after failed client initialization.
