# sources/cloud-native/buildkit/client/client_test.go lines 1-9244

## Scope And Purpose

This chunk is the first, larger portion of BuildKit's `client` package integration test file. It covers the package imports, integration test registration, the main `TestIntegration` orchestration, and concrete integration tests from `testCacheExportCacheKeyLoop` through the opening portion of `testMergeOp`. The tests exercise the public client entry points (`New`, `Client.Solve`, `Client.Build`, `Client.Prune`, `Client.DiskUsage`, control-client build history APIs, and content clients) by constructing LLB graphs and validating solver behavior against real workers, registries, containerd content stores, session services, and exporters.

The file is not production runtime code, but it is a high-signal executable specification for the client-facing BuildKit contract. It verifies that LLB definitions, solve options, exporters, cache import/export backends, session attachables, gateway frontends, platform metadata, image media types, filesystem diffs, and entitlement handling remain compatible across OCI, containerd, dockerd, Linux, Windows, rootless, and feature-gated worker configurations.

This chunk ends mid-function in `testMergeOp`; subsequent merge-cache helper coverage begins in the next chunk at line 9245.

## Test Harness And Registration

`init` selects the worker test backend. Dockerd test mode initializes a dockerd worker; otherwise OCI and containerd workers are registered. This means the same test list is intended to run across several worker implementations with feature compatibility checks deciding what is valid for each sandbox.

`allTests` is the central registry for most integration cases. It includes tests in this chunk and also names functions defined later in the file or in related test files, such as validation, proxy-network, CDI, and source-policy cases. The order is meaningful for coverage but each test should be isolated by sandbox setup and by its own temporary directories, registries, or cache cleanup.

`TestIntegration` calls `testIntegration` with `allTests` plus `validationTests`. `testIntegration` sets mirrored official images for Unix and Windows (`busybox`, `alpine`, `nanoserver`, plus specialized images), wraps the function list through `integration.TestFuncs`, appends diff-op test cases, and runs the matrix through `integration.Run`. It then skips Windows for Linux-only matrices and runs additional security-mode, host-network, proxy-network, bridge-DNS, and CDI matrices with `integration.WithMatrix`. These matrix values are consumed by tests through `sb.Value("secmode")` and `sb.Value("netmode")`.

`newContainerd` is a small helper around `ctd.New` using a 60 second client timeout. It is used by tests that inspect containerd image services and content stores directly.

## Client And LLB APIs Exercised

The chunk repeatedly uses `New(ctx, sb.Address())` to create a BuildKit client and then calls `Solve` with marshaled `llb.State` definitions. Common `SolveOpt` fields under test include:

- `Exports`: local, tar, OCI, Docker, image, and moby exporters, including `Output`, `OutputDir`, `OutputStore`, image naming, `push`, `push-by-digest`, `unpack`, `compression`, `force-compression`, `oci-mediatypes`, `image-manifest`, `tar=false`, local exporter `mode`, and `platform-split`.
- `CacheImports` and `CacheExports`: local, registry, inline, S3, and Azure blob backends, including compression, mode, reset, ignore-error, and backend-specific credentials.
- `Session`: secret providers, SSH providers, raw socket providers, exporter providers, and file sync targets.
- `LocalMounts`: host filesystem mounts mapped to `llb.Local` inputs.
- `OCIStores`: content stores used by `llb.OCILayout`.
- `FrontendAttrs`: build arguments such as `SOURCE_DATE_EPOCH`, attestation toggles, hostname metadata, and exporter-related attrs.
- `AllowedEntitlements`: host networking and security.insecure toggles.
- `Ref`: explicit build refs later inspected through build history.

The tests cover LLB construction primitives including `llb.Image`, `llb.Scratch`, `llb.Local`, `llb.HTTP`, `llb.OCILayout`, `llb.Copy`, `llb.Mkdir`, `llb.Mkfile`, `llb.Rm`, `llb.Merge`, `llb.Diff`, `llb.Run`, `llb.AddMount`, `llb.AddSecret`, `llb.AddSSHSocket`, `llb.WithProxy`, `llb.Network`, `llb.Security`, `llb.Hostname`, `llb.User`, `llb.Dir`, cache mounts, tmpfs mounts, cgroup/resource options, source maps, chmod/chown/timestamp options, and platform metadata returned from gateway frontends.

`Client.Build` is used to exercise gateway frontend callbacks. These callbacks call `gateway.Client.Solve`, `ResolveImageConfig`, `ReadDir`, convert refs back to LLB state via `ToState`, and return `gateway.Result` objects with refs and metadata such as platform lists, image configs, `image.name`, and frontend-prefixed metadata.

## Functional Areas Covered

### Cache Export And Import

`testCacheExportCacheKeyLoop` checks local cache export when equivalent cache keys can appear through different graph shapes. `testCacheExportCacheDeletedContent` exports cache in max mode, deletes a blob backing a RUN layer, prunes all local state, imports the degraded cache, and verifies the re-export preserves cache records while omitting missing layer content. `testLocalCacheExportReset` validates `reset=true` on a local cache destination by comparing the remaining blob directory to blobs referenced by the current manifest.

`testZstdLocalCacheExport`, `testUncompressedLocalCacheImportExport`, `testUncompressedRegistryCacheImportExport`, `testZstdLocalCacheImportExport`, `testImageManifestRegistryCacheImportExport`, and `testZstdRegistryCacheImportExport` validate cache compression and media-type options. `testBasicCacheImportExport` is the shared helper: it builds deterministic and random outputs, exports cache, prunes BuildKit state, imports the cache, and expects the random output to be reused exactly. Wrappers bind that helper to registry, local, S3, Azure blob, uncompressed, zstd, and image-manifest configurations.

`testBasicInlineCacheImportExport` pushes an image with inline cache, prunes state, imports from the registry, and checks digest stability when inline cache is reproduced. It also verifies changed compression produces a different image digest while preserving filesystem content, and that omitting inline cache export changes the final image digest while still reusing build content. `testRegistryEmptyCacheExport` validates that exporting an empty scratch cache to registry does not create fetchable image content. `testMultipleRecordsWithSameLayersCacheImportExport` covers the case where distinct LLB records produce identical layers and confirms unused imported cache refs are releasable.

`testCacheExportIgnoreError` builds a matrix where local, registry, and S3 cache export failures are either surfaced or ignored based on the `ignore-error` attr. This is important because cache export failures should not corrupt the main export path when explicitly configured as best effort.

### Networking, Entitlements, Resources, And Execution Environment

Bridge, host, DNS, no-network, and proxy environment behavior are validated by `testBridgeNetworking`, `testBridgeNetworkingDNSNoRootless`, `testHostNetworking`, `testNetworkMode`, and `testProxyEnv`. These tests use echoservers, `nc`, `wget`, and matrix values to assert both success paths and expected entitlement failures. Proxy variables are intentionally not part of the cache key: the second `testProxyEnv` solve changes proxy values but expects cached output from the first run.

`testSecurityMode`, `testSecurityModeSysfs`, and `testSecurityModeErrors` validate sandbox versus insecure security mode. They check effective Linux capabilities, sysfs/cgroup write behavior, and expected "not allowed" errors when entitlements are configured inconsistently.

`testExtraHosts`, `testShmSize`, `testUlimit`, `testCgroupParent`, `testLinuxResources`, `testReadonlyRootFS`, `testHostnameLookup`, `testHostnameSpecifying`, and `testStdinClosed` verify runtime environment details: `/etc/hosts` injection, tmpfs size, per-exec ulimit, cgroup parent and resource controls, read-only rootfs failures, hostname resolution/customization, and closed stdin behavior.

### Sessions, Secrets, SSH, And Session Exporters

`testSSHMount` builds an in-memory SSH agent, exposes it through `sshprovider`, checks absent/default/custom/optional ID behavior, verifies the socket path and key listing inside the build, asserts forbidden `ssh-add` operations are refused, and checks private-key-on-disk provider setup. `testRawSocketMount` uses a raw Unix socket as an SSH mount target and confirms a build-time curl reaches the host-side HTTP server through that socket.

`testSecretMounts` validates Linux file-based secret mounts: tmpfs backing, missing optional secrets, required-secret failure, custom secret IDs, UID/GID/mode options, and empty secret files. `testSecretEnv` provides the cross-platform environment-variable secret equivalent with provided, optional, required, and multiple custom-ID secrets.

`testSessionHealthMonitorFailsBlockedSecretResponse` creates a `gatedSecretProvider` and a `gatedSessionTunnelProxy`. The proxy wraps the client's session dialer with a `net.Pipe`, blocks client-to-daemon traffic after the secret provider starts, and expects the solve to fail after a custom session health timeout. This is a targeted regression test for session health monitoring when a session response stalls inside the tunnel.

`testSessionExporter` enables the session exporter path. It attaches a file sync target and an exporter provider, uses a gateway client for the build ID to inspect refs with `ReadDir`, then exports an OCI result through the session and verifies zstd-compressed layers in the emitted tar stream.

### File Operations, Local Sources, And Filesystem Diffs

Basic file-op tests include `testFileOpMkdirMkfile`, `testFileOpCopyRm`, `testFileOpCopyChmodText`, `testFileOpCopyUIDCache`, `testFileOpCopyIncludeExclude`, `testFileOpCopyAlwaysReplaceExistingDestPaths`, `testFileOpInputSwap`, `testFileOpSymlink`, `testFileOpRmWildcard`, and `testRmSymlink`. Together they verify mkdir/mkfile semantics, copy/remove sequencing, symbolic chmod strings, UID/GID cache separation, include/exclude cache behavior, replacing destination paths of different types, correct invalidation when inputs are swapped, symlink ownership/timestamp preservation, wildcard removal, and removing symlinks without removing their targets.

`testLocalSymlinkEscape` validates `llb.Local` with `FollowPaths`: explicitly followed symlinks that point outside the source remain symlinks and do not include the outside targets. `testLocalSourceDiffer` and `testLocalSourceWithDiffer` compare `DiffNone` and `DiffMetadata` by mutating file content while preserving timestamps, then expecting either fresh content or cached content depending on differ mode. `testLocalSourceWithHardlinksFilter` verifies a follow-path filter preserves hardlink relationships among included files while excluding unrequested names.

Whiteout and layer-diff behavior is covered by `testDuplicateWhiteouts`, `testWhiteoutParentDir`, and `testMoveParentDir`. These export OCI tar streams, parse image manifests and last layers, and inspect tar entries to ensure directory removals create correct whiteouts, parent directories are retained when needed, duplicate child whiteouts are avoided, and moved directories are represented correctly on Linux and Windows.

`testCopyFromEmptyImage`, `testMountWithNoSource`, `testTmpfsMounts`, `testBuildMultiMount`, `testRunCacheWithMounts`, and cache mount tests cover empty/scratch image copies, nil-state mounts, tmpfs mounts, multiple mounts in a RUN, run cache separation by mounted image/source, and persistent cache mount behavior.

### Cache Mounts

`testCachedMounts` uses named persistent cache directories across solves and confirms later builds can read files written in earlier runs while preserving base-source content. `testSharedCacheMounts` and `testSharedCacheMountsNoScratch` launch two execs that coordinate through a shared cache directory, once from scratch and once from an image source. `testLockedCacheMounts` validates locked cache mounts by asserting two concurrent users of the same cache ID are serialized. `testDuplicateCacheMount` verifies two mounts with the same cache ID in one exec see the same filesystem. `testCacheMountNoCache` confirms `llb.IgnoreCache` does not wipe persistent cache state globally and that separate cache IDs keep their own data.

### HTTP, OCI Layout, And Source Resolution

`testBuildHTTPSource` covers HTTP source status errors, GET versus HEAD cache validation, gzip content encoding normalization, file naming, chmod/chown, last-modified timestamps, request headers, and releasability. `testBuildHTTPSourceUnauthorizedChecksumRace` repeatedly builds a graph with the same unauthorized URL used with and without checksum to catch resolver-cache races. `testBuildHTTPSourceEtagScope` verifies a shared ETag across different URL paths does not cause cross-path content reuse. `testBuildHTTPSourceAuthHeaderSecret`, `testBuildHTTPSourceHostTokenSecret`, `testBuildHTTPSourceHeader`, and `testBuildHTTPSourcePGPSignatureVerify` validate explicit auth-header secrets, host-token secrets, custom request headers, and PGP signature verification with valid, wrong-key, and concatenated-key cases.

`testOCILayoutSource` exports an image as an OCI layout tar, materializes it into a local content store, then consumes it via `llb.OCILayout` and an `OCIStores` map. `testOCILayoutPlatformSource` does the same for multi-platform output by producing gateway refs per platform and reading platform-specific files back from the OCI layout. These tests integrate the client with containerd local content stores and OCI image-index semantics.

### Exporters, Images, Media Types, And Containerd Integration

`testExportBusyboxLocal`, `testMultipleExporters`, `testOCIExporter`, `testOCIExporterContentStore`, `testNoTarOCIIndexMediaType`, `testOCIIndexMediatype`, `testExporterTargetExists`, `testTarExporterWithSocket`, `testTarExporterWithSocketCopy`, and `testTarExporterSymlink` validate local/tar/OCI/Docker/image exporter behavior. They inspect filesystem outputs, tar entries, OCI layout contents, Docker `manifest.json`, exporter metadata callbacks, multiple exporters in one solve, build history records, sockets, symlinks, and no-tar directory output.

`testFrontendImageNaming`, `testFrontendMetadataReturn`, and `testFrontendUseSolveResults` validate gateway frontend integration. Frontend-provided image names can be selected or overridden by caller-provided export attrs; only metadata keys with the `frontend.` prefix are returned in exporter response; and refs returned from a gateway solve can be converted back to LLB state and used in subsequent solves.

`testBuildExportScratch`, `testBuildExportWithForeignLayer`, `testBuildExportWithUncompressed`, `testBuildExportZstd`, `testPullZstdImage`, `testBuildPushAndValidate`, `testLazyImagePush`, and the stargz lazy tests cover image export and registry flows. They verify scratch images with no layers, multi-platform configs, foreign layer propagation versus conversion, uncompressed and gzip media types, zstd media types and magic bytes, direct push and pull by digest, image config/history/rootfs fields, registry-resolved manifests, lazy snapshot content that should or should not exist in containerd's content store, and that export paths force lazy content to materialize when required.

`testExportedImageLabels` specifically checks containerd GC reference labels for exported image layers/configs, then validates prune and image deletion behavior across containerd's `buildkit` namespace, BuildKit's content client, and build history soft-deletion.

`testPushByDigest`, `testPushProgressSameVertex`, and `testPullWithDigestCheck` cover direct-push edge cases: digest-only push without a tag, solve progress vertex attribution for push statuses, pulling by explicit digest versus tag plus checksum, and checksum mismatch errors.

### Source Date Epoch And Reproducibility

`testSourceDateEpochLayerTimestamps`, `testSourceDateEpochClamp`, `testSourceDateEpochReset`, `testSourceDateEpochLocalExporter`, `testSourceDateEpochTarExporter`, and `testSourceDateEpochImageExporter` validate reproducible timestamp handling. They use `SOURCE_DATE_EPOCH`, exporter image config overrides, local/tar/image outputs, and containerd image metadata to ensure created times and layer/file timestamps are clamped, reset, or propagated as expected.

### Local Export Modes And Multi-Platform Output

`testExportLocalNoPlatformSplit`, `testExportLocalNoPlatformSplitOverwrite`, `testExportLocalForcePlatformSplit`, `testExportLocalModeCopyKeepsStaleDestinationFiles`, `testExportLocalModeDeleteRemovesStaleDestinationFiles`, `testExportLocalModeCopyMultiPlatformKeepsAllPlatforms`, `testExportLocalModeDeleteMultiPlatformKeepsAllPlatforms`, and `testExportLocalModeInvalid` specify local exporter behavior for platform splitting and destination cleanup. They validate no-split output, collision errors when no-split would overwrite paths, forced platform split for a single result, default copy mode preserving stale files, delete mode removing stale files, multi-platform delete mode cleaning each platform directory without deleting fresh output from other platforms, and invalid mode errors.

### Source Maps

`testSourceMap` attaches several source-map locations to a failing exec and checks that `errdefs.Sources` returns the expected filename, data, nil definition, line, and character metadata in unwrap order. `testSourceMapFromRef` creates a source map tied to an LLB state, then verifies a gateway frontend failure preserves filename, language, data, definition, and range information after ref-to-state conversion.

### Merge Operation Start

The chunk reaches the start of `testMergeOp`. It requires `FeatureMergeDiff`, creates states A, B, C, and D with overlapping files, removals, directory modes, and conflicting contents, then begins validating merge precedence through `requireContents`. Covered assertions include:

- `llb.Merge([]llb.State{stateA, stateC})` where later state C overrides `/foo` and `/bar/A` while state A contributes `/a`.
- `llb.Merge([]llb.State{stateC, stateB})` where state B's deletion of `/foo`, directory mode, `/a`, `/b`, and `/bar/B` combine with state C's `/c`.
- The beginning of a nested merge `llb.Merge([]llb.State{mergeA, mergeB, stateD})`; the expected content list continues beyond this chunk.

The helper `requireContents` itself is not defined in this chunk, so the merge-op analysis here is limited to the visible setup and first assertions.

## State And Persistence Behavior

Temporary state is isolated through `t.TempDir`, `integration.Tmpdir`, in-memory buffers, local content stores, generated registries, and per-test BuildKit clients. Persistent BuildKit state is intentionally manipulated in several tests:

- `ensurePruneAll` and `checkAllReleasable` are repeatedly used after exports, imports, image deletion, and lazy-pull tests to confirm content leases, cache refs, and build records are released.
- Containerd state is inspected and deleted through `ImageService`, `ContentStore`, `GetImage`, `Pull`, and synchronous delete calls in the `buildkit` namespace.
- Registry state is created through `sb.NewRegistry` and used for direct push, cache export, inline cache import, lazy image pushes, and remote manifest inspection.
- Cache mount state persists by cache ID across execs and solves; local/registry/S3/Azblob cache state persists outside the BuildKit daemon and is imported after daemon-side pruning.
- Session state is transient but important: secrets, SSH agents, raw sockets, session exporters, and health-monitor timeouts are all attached to the solve and should not leak beyond it.
- Exported local directories may intentionally preserve or delete pre-existing files depending on local exporter mode.

The tests frequently assert that content remains present only while referenced by images, build history, or explicit exporter outputs, then becomes releasable once those references are removed.

## Dependencies And Integration Points

This chunk depends heavily on BuildKit internals and test utilities:

- BuildKit client packages: `client`, `client/llb`, gateway client/pb, solve/result metadata, source policy/provenance/attestation types, session exporters, filesync, secrets, SSH forwarding, solver error definitions, entitlements, content utilities, and test helpers.
- Containerd APIs: image service, content store, snapshots, namespaces, Docker resolver, local content store, GC labels, and error definitions.
- OCI and Docker image specs: `ocispecs`, `images.MediaTypeDockerSchema2*`, indexes, manifests, descriptors, configs, layers, diff IDs, and media types.
- Test infrastructure: `integration.Sandbox`, worker feature gates, mirrored images, temporary registries, echoserver, httpserver, MinIO/Azurite helpers, `fstest`, tar reading utilities, and platform normalization.
- Standard library integration: HTTP servers, raw Unix sockets, gzip, tar parsing, filesystem operations, cgroups, RSA/PEM key generation, contexts, errgroups, atomics, and synchronization primitives.

External services are usually test-local: ephemeral registries, HTTP test servers, MinIO, Azurite, raw socket servers, and containerd workers. Some cases depend on environment variables (`BUILDKIT_RUN_NETWORK_INTEGRATION_TESTS`, `BUILDKIT_TEST_SIGN_FIXTURES`) or host features (Linux, cgroup v2, rootful mode, stargz snapshotter, containerd address).

## Risks And Edge Cases Captured

The chunk is intentionally broad and catches many historical regressions:

- Cache correctness when blobs disappear, cache keys collide, cache records share layers, ignore-error is toggled, and backend compression/media-type combinations vary.
- Lazy content bugs where registry/stargz/lazy-pushed layers must stay remote until execution/export requires materialization.
- Incorrect GC label or build-history retention causing leaked or prematurely deleted content.
- Security regressions around secrets, SSH agents, raw sockets, session health monitoring, host networking, insecure mode, cgroups, and rootfs read-only enforcement.
- Filesystem diff regressions involving whiteouts, moved directories, symlinks, hardlinks, chmod strings, UID/GID metadata, include/exclude filters, local symlink escapes, and copy-overwrite semantics.
- Exporter regressions in OCI/Docker media types, zstd/uncompressed/foreign layers, local destination cleanup, multi-platform path splitting, tar sockets, image naming, and frontend metadata propagation.
- HTTP resolver regressions around ETag scoping, unauthorized checksum races, auth secrets, custom headers, gzip normalization, PGP verification, and timestamp handling.
- Platform-specific risk: many tests branch or skip for Windows, rootless, dockerd, containerd-only features, cgroup v2, stargz snapshotter, and worker feature compatibility. Any implementation changes must preserve these gates or tests will either fail incorrectly or silently stop covering an important path.

## Test Signals

The strongest pass/fail signals are direct solver errors and assertions over exported artifacts:

- `require.NoError` or expected `require.ErrorContains` around `Solve`/`Build` calls validates public client behavior.
- Filesystem checks read exported local directories and tar streams to compare file contents, modes, symlinks, hardlinks, whiteouts, mtimes, and stale-file deletion.
- OCI/Docker checks unmarshal indexes, manifests, configs, histories, layers, media types, diff IDs, descriptors, and image metadata.
- Containerd checks inspect image existence, content-store blob presence, GC labels, lazy-content absence, and releasability after deletes/prunes.
- Registry and resolver checks push, pull, resolve, fetch, and validate remote manifests or missing blobs.
- Session checks prove attached providers are used and failure paths are surfaced when sessions stall or required inputs are absent.
- Build history checks verify exporter result counts, media types, exporter records, and cleanup via soft deletion.

Because this is an integration file, many signals are environment-sensitive. Feature gates (`workers.CheckFeatureCompat`), platform skips (`integration.SkipOnPlatform`, `requiresLinux`), rootless skips, and containerd/stargz availability checks are part of the behavioral contract, not incidental test boilerplate.
