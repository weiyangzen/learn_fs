# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/netns.py

## Purpose
This module provides Python context managers for creating network namespaces and temporarily entering an existing namespace.

## Important APIs and Types
`NetNS(name=None)` creates a named or random namespace through `ip netns add`, deletes it in `__del__`/context exit, and stringifies to the namespace name. `NetNSEnter(ns_name)` opens `/run/netns/<name>`, saves `/proc/thread-self/ns/net`, calls `setns` via libc on entry, and restores the saved namespace on exit.

## Control Flow and State
`NetNS` persists kernel namespace state until explicit context exit or object destruction. `NetNSEnter` changes the calling thread's network namespace for the duration of the `with` block and stores the saved namespace file object in `self.saved`.

## Dependencies and Integration
It depends on `ip` from `utils.py`, `ctypes` loading `libc.so.6`, `/run/netns`, and Linux `setns`. Python tests use it to build isolated topologies and to instantiate netlink sockets inside a namespace.

## Risks and Test Signals
Destructor-based cleanup is not deterministic if references survive, so context-manager use is preferred. `setns` affects only the current thread and can be dangerous in multi-threaded tests. Missing privileges or namespace paths cause immediate exceptions from `ip` or libc calls.
