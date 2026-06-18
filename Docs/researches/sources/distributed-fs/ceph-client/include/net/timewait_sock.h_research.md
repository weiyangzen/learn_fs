# sources/distributed-fs/ceph-client/include/net/timewait_sock.h

## Purpose

`timewait_sock.h` declares the minimal allocator contract for protocol-specific time-wait sockets. It lets protocols describe the slab cache used for compact time-wait socket objects.

## Important APIs, types, and functions

The only defined type is `struct timewait_sock_ops`, with `twsk_slab`, `twsk_slab_name`, and `twsk_obj_size`. There are no functions in this header.

## Control flow

Protocol code supplies a `timewait_sock_ops` instance to time-wait allocation/teardown code elsewhere. The common time-wait infrastructure uses the slab cache and object size to allocate and free per-protocol time-wait sockets.

## State and persistence behavior

The header owns no state. The referenced `kmem_cache` persists while the protocol is registered; individual time-wait objects persist until their timers expire or are reclaimed.

## Dependencies and integration points

It includes slab, bug, and socket infrastructure. It integrates with TCP/DCCP-style time-wait implementations and generic socket lifetime code.

## Risks and test signals

Risks include an object size smaller than the concrete time-wait structure, stale slab pointers during protocol unload, and mismatched slab names in diagnostics. Tests should cover protocol init/exit, time-wait allocation/free, timer expiry, and memory-debug builds.
