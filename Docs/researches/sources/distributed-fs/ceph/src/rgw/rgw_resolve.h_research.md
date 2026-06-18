# sources/distributed-fs/ceph/src/rgw/rgw_resolve.h

## Purpose

Declares the RGW DNS resolver wrapper and global lifecycle functions.

## Important APIs, Types, and Functions

`RGWResolver` owns a `DNSResolver*` and exposes `resolve_cname(hostname, cname, found)`. Global functions `rgw_init_resolver()` and `rgw_shutdown_resolver()` manage `extern RGWResolver* rgw_resolver`.

## Control Flow and Data Flow

RGW startup initializes the global resolver; REST host preprocessing asks it for CNAME resolution; RGW shutdown releases it.

## State and Persistence Behavior

No durable state. The global pointer is mutable process state and should be treated as a singleton service.

## Dependencies and Integration Points

Depends on `rgw_common.h` and forward declares `ceph::DNSResolver`. Integrated with virtual-host bucket routing and CNAME support.

## Risks and Edge Cases

Global mutable pointer has lifecycle and thread-safety risks. The wrapper does not expose copy/move restrictions, though it only contains a raw pointer.

## Test Signals

Compile/link lifecycle tests, null-global protection in callers, CNAME routing integration, and shutdown ordering under concurrent request handling.
