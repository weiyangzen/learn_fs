# sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs.cpp

## Purpose
Implements the original curl-backed registry filesystem. It exposes OCI/Docker registry blobs as read-only Photon files with range GET support, authentication challenge handling, redirect caching, optional acceleration proxying, and metadata size caching.

## Important APIs and Types
`RegistryFSImpl` implements `RegistryFS`; `RegistryFileImpl` implements `VirtualReadOnlyFile`. Important methods include `GET`, `getActualUrl`, `getScopeAuth`, `authenticate`, `getAuthUrl`, `setAccelerateAddress`, `open`, `stat`, `RegistryFileImpl::preadv`, `getMetaLength`, and exported factory `new_registryfs_v1`.

## Control Flow
Opening a path constructs a file and calls `fstat`, which obtains metadata with a one-byte/ranged GET. Reads use `preadv`, clamp requested bytes to cached file size, and call `RegistryFSImpl::GET`. `GET` resolves or reuses an actual URL, attaches bearer auth when needed, optionally rewrites through an acceleration URL, issues a curl GET with range headers, and invalidates URL cache on non-2xx responses.

## State and Persistence
Runtime state includes a small curl identity pool, cached metadata sizes, cached bearer tokens by scope, cached actual URLs, CA/client cert/key paths, timeout, and acceleration prefix. It does not persist files locally.

## Dependencies and Integration Points
Depends on Photon curl wrapper, Photon HTTP URL/header utilities, `ObjectCache`, RapidJSON, base64 helper, Photon virtual files, and password callback delegation. It is created through `new_registryfs_v1` declared in `registryfs.h`.

## Risks
TLS verification is explicitly disabled despite CA configuration. Challenge parsing is simple comma splitting and can misparse quoted commas. `preadv` declares `ret_len` in retry logging without initialization. URL/token caches need careful invalidation on auth failures.

## Test Signals
Useful tests include anonymous registry reads, bearer-token auth reads, redirects, 401/403 retry invalidation, content-range size parsing, timeout behavior, acceleration URL rewriting, and client certificate configuration.
