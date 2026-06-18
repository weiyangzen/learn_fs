# sources/distributed-fs/ceph-client/include/net/xdp_priv.h

## Purpose

`xdp_priv.h` exposes the private XDP memory allocator structure used by `net/core/xdp.c` and trace events. It is not a broad driver API.

## Important APIs, types, and functions

The only type is `struct xdp_mem_allocator`, containing `struct xdp_mem_info`, an allocator pointer or page-pool pointer union, an rhashtable node, and an RCU head.

## Control flow

XDP core registers memory allocators in a hash table keyed by memory info, then lookup/return paths use the allocator or page pool to release packet memory. Tracepoints may inspect this shape.

## State and persistence behavior

Allocator entries persist while an XDP memory model is registered and are removed through RCU to protect concurrent readers.

## Dependencies and integration points

It depends on rhashtable and public `net/xdp.h`. It integrates with XDP memory registration, page-pool return paths, and XDP trace events.

## Risks and test signals

Risks include treating this private header as stable external API, freeing allocator entries before RCU readers finish, and mismatching union interpretation with `mem.type`. Tests should cover memory registration/unregistration, trace event builds, page-pool and non-page-pool allocator returns, and RCU lifetime.
