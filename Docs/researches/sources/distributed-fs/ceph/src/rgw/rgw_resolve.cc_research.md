# sources/distributed-fs/ceph/src/rgw/rgw_resolve.cc

## Purpose

Implements the RGW DNS CNAME resolver wrapper used by REST virtual-host request preprocessing.

## Important APIs, Types, and Functions

`RGWResolver::RGWResolver()` obtains the singleton `DNSResolver`. `resolve_cname()` delegates to `DNSResolver::resolve_cname()`. `rgw_init_resolver()` allocates the global `rgw_resolver`, and `rgw_shutdown_resolver()` deletes it.

## Control Flow and Data Flow

During RGW startup, `rgw_init_resolver()` creates the wrapper. REST preprocessing can call `rgw_resolver->resolve_cname(host, cname, found)` when configured to resolve CNAMEs. Shutdown deletes the global wrapper.

## State and Persistence Behavior

Only process-global resolver pointer state is managed. No DNS results are persisted here; caching, if any, belongs to `DNSResolver`.

## Dependencies and Integration Points

Depends on resolver system headers, Ceph DNS resolver, `rgw_common.h`, and global `g_ceph_context`. Integrated with `rgw_rest_transform_s3_vhost_style()`.

## Risks and Edge Cases

`rgw_shutdown_resolver()` does not null the global pointer after deletion. Callers must ensure initialization before use and no concurrent use during shutdown. Resolver errors are propagated from the DNS layer.

## Test Signals

Cover init/shutdown lifecycle, successful CNAME, not found, resolver error, REST fallback when resolver returns failure, and repeated init/shutdown behavior.
