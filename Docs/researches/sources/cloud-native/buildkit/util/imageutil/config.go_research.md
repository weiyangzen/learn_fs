## sources/cloud-native/buildkit/util/imageutil/config.go

Purpose: resolves an image reference to its manifest digest and configuration blob, using content cache, resolver fetcher, platform selection, and temporary leases.

Important APIs/types: `ContentCache` combines containerd content interfaces. Lease globals `CancelCacheLeases`, `AddLease` manage deferred lease cleanup. `ResolveToNonImageError` describes policy mutation to non-image refs. `Config(ctx,str,resolver,cache,leaseManager,p)` is the main entry point. Helpers: `childrenConfigHandler`, `DetectManifestMediaType`, `DetectManifestBlobMediaType`.

Control flow: `Config` parses the reference and platform matcher, optionally creates a temporary 5-minute lease and defers its cleanup registration. If the reference is digest-pinned, it probes cache for an existing manifest whose source label matches and detects media type. Missing media type triggers `resolver.Resolve`. It creates a fetcher, rejects Docker schema1 manifests with conflict, builds handlers to fetch/retry, apply distribution source labels, and traverse only one matching manifest/config, dispatches them, then reads and returns config blob data with the resolved manifest digest.

State/persistence: writes/fetches blobs into content cache; creates leases and stores deferred cleanup funcs in package globals until `CancelCacheLeases`. Dependencies: containerd content/images/leases/remotes/docker/reference/platforms, BuildKit contentutil/leaseutil/resolver handlers, OCI specs.

Integration points: image source resolution, frontend metadata, cache warming. Risks: global lease list uses `context.TODO` on cancellation; temporary lease deletion is intentionally delayed and may retain blobs until cleanup; media type detection reads whole blob into memory; unknown child media types hard-error. Test signals: `config_test.go` covers multi-platform index selection from cache and non-matching platform errors.
