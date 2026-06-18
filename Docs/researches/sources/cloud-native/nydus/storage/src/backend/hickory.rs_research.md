# sources/cloud-native/nydus/storage/src/backend/hickory.rs

## Purpose
This module implements a `reqwest::dns::Resolve` adapter backed by `hickory-resolver`. It gives reqwest clients DNS lookup caching, negative caching, IPv4-then-IPv6 ordering, and singleflight deduplication for concurrent lookups.

## Important APIs, Types, and Functions
`HickoryDnsResolver` is the exported resolver wrapper. It owns a lazily initialized `OnceCell<ResolverState>` and a `lookup_count` counter used by tests. `ResolverState` contains the `TokioResolver`, an async `RwLock<HashMap<String, Arc<CachedLookup>>>`, and a `nydus_utils::singleflight::Group`. `CachedLookup` stores resolved IPs, expiration, and optional error text. `SocketAddrs` adapts `IpAddr` values into `SocketAddr` entries with port `0`. `new_resolver_state` reads system resolver config and sets `LookupIpStrategy::Ipv4thenIpv6`.

## Control Flow
`resolve` initializes resolver state on first use, checks the cache under a read lock, and returns either cached addresses or a cached error when the TTL is still valid. Cache misses enter singleflight by domain name; only one task performs the actual Hickory lookup and updates the cache. Successful lookups use Hickory-provided TTLs. Failed lookups are cached for `NEGATIVE_CACHE_TTL` of 60 seconds.

## State and Persistence Behavior
All state is in memory and shared by clones. The cache grows by domain name and has TTL validation but no explicit eviction sweep. Failed lookups persist temporarily as negative cache entries, reducing pressure on DNS infrastructure during repeated failures.

## Dependencies and Integration Points
The resolver implements `reqwest::dns::Resolve`, so `connection.rs` installs it via `Client::builder().dns_resolver(...)`. It relies on Tokio async synchronization even though the surrounding client is blocking reqwest.

## Risks
The cache does not proactively remove expired entries, so long-running processes with many unique domains can accumulate stale keys. Negative cache duration may hide recovery for up to 60 seconds. The live DNS tests use public domains such as `baidu.com`, `qq.com`, and `taobao.com`, which can fail in isolated CI or restricted networks.

## Test Signals
Tokio tests cover successful resolution, concurrent singleflight, cache hits, negative caching, negative cache expiry, per-domain independence, TTL expiry refresh, and concurrent refresh after expiry.
