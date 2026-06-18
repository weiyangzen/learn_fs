# sources/distributed-fs/ceph-client/include/linux/fprobe.h

## Purpose
This header defines `fprobe`, a simple ftrace-based function entry/exit probe wrapper, with optional sharing for kprobes.

## APIs, types, and control flow
Entry callbacks return `int` and receive the probe, entry IP, return IP, ftrace registers, and per-entry data. Exit callbacks receive the same context and entry data. `struct fprobe_hlist_node` and `struct fprobe_hlist` support address-based hash lookup with RCU-deferred release. `struct fprobe` tracks missed events, flags, entry data size, callbacks, and hash-list array. Registration can be by ftrace filter strings, raw IPs, or symbol names; unregister can be synchronous or async. With `CONFIG_FPROBE` disabled, all operations return `-EOPNOTSUPP` or false. Inline helpers soft-disable/enable probes and test shared/disabled flags.

## State and dependencies
State includes registered ftrace hooks, hash tables, RCU lifetime, missed counters, and optional per-entry data bounded by `MAX_FPROBE_DATA_SIZE`. Dependencies include ftrace, RCU, refcounting, rhashtable, and slab allocation.

## Integration, risks, and tests
Tracing, profiling, and dynamic instrumentation use this layer. Risks include unregister races with callbacks, excessive entry data, probing invalid or duplicate addresses, missed-event accounting, and flag mutation without synchronization. Tests should cover filter/IP/symbol registration, disabled stubs, soft disable/enable, async unregister lifetime, entry/exit data passing, and max data-size rejection.
