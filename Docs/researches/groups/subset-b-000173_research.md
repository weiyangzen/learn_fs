<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_import.go -->
# sources/cloud-native/moby/daemon/containerd/image_import.go

Purpose: implements `ImageService.ImportImage`, the containerd-backed equivalent of importing a tar layer into a Docker image. It turns one layer archive plus Dockerfile-style config changes into content blobs, an OCI image config, an OCI manifest, a containerd image record, and an unpacked snapshot.

Important APIs and flow: `ImportImage` creates a containerd lease, defaults the requested platform, applies `dockerfile.BuildFromConfig`, stores the layer with `saveArchive`, labels the compressed blob with `containerd.io/uncompressed`, writes config and manifest JSON via `storeJson`, creates or replaces the image tag (or a synthetic dangling name), and calls `unpackImage`. `saveArchive` accepts gzip/zstd as-is and recompresses uncompressed, xz, and bzip2 inputs to gzip. `writeCompressedBlob` and `compressAndWriteBlob` use pipes and digest tee readers to compute compressed and uncompressed digests while streaming. `detectCompression`, `fillUncompressedLabel`, and `writeBlobAndReturnDigest` are small support points.

State and persistence: persistent writes go to the containerd content store and image metadata store under a lease. The manifest records GC labels for config and layer content, and the compressed layer content info is updated with the uncompressed diff ID label. A successful unpack persists snapshotter state and logs an image import event.

Dependencies and integration: depends on containerd content/images, Moby dockerfile config mutation, Docker image spec conversion in `imagespec.go`, dangling image helpers, and the snapshotter unpack path. Errors are mapped through Moby `errdefs` so daemon APIs receive Docker-compatible classifications.

Risks: the concurrent pipe/digest paths must close readers/writers correctly or can deadlock on copy errors. Zstd and gzip are trusted as precompressed input, while xz/bzip2 are decompressed and recompressed, so digest and media type behavior differs by input. Import creates the image record before unpack failure is returned, leaving content/tag state after an unpack error. Empty archives intentionally become empty uncompressed streams, which is compatibility-sensitive.

Test signals: direct coverage is light; `image_import_test.go` validates config conversion used by import, while broader load/list/inspect tests exercise content/config interpretation after images are materialized.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_import_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_import_test.go

Purpose: regression coverage for Docker container config to Docker OCI image config conversion, which import uses after applying Dockerfile-style changes.

Important APIs and flow: `TestContainerConfigToDockerImageConfig` builds a `container.Config` with `ExposedPorts`, calls `containerConfigToDockerOCIImageConfig`, and asserts that the OCI config uses string keys such as `80/tcp`.

State and persistence: no persistent state; the test is pure conversion logic.

Dependencies and integration: uses Moby API container/network types and `gotest.tools` assertions. It protects the conversion in `imagespec.go`, not just import, because the helper is shared by image creation/conversion paths.

Risks and gaps: this only covers exposed-port formatting. It does not cover import archive compression, history/comment fields, labels, healthcheck, shell, on-build, or unpack behavior.

Test signals: references the historical regression for Moby issue 45904.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_import_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_inspect.go -->
# sources/cloud-native/moby/daemon/containerd/image_inspect.go

Purpose: implements Docker image inspect against the containerd image/content/snapshot model, including manifest summaries, repo tags/digests, config fields, rootfs diff IDs, size, and optional identity data.

Important APIs and flow: `ImageInspect` resolves a reference or ID, finds all image records with the same target digest, calculates last tag time, builds a requested/default platform matcher, calls `size` and `multiPlatformSummary`, optionally selects the platform-specific target, and fills `imagebackend.InspectData`. `collectRepoTagsAndDigests` deduplicates Docker-style familiar tags and digests while skipping synthetic dangling references. `size` dispatches through descriptor children with a small semaphore and platform limiting.

State and persistence: inspect is read-only but consumes mutable containerd metadata and content. It reads image labels for the classic builder parent, image config JSON for Docker fields, and content descriptor sizes. Missing config content is tolerated in some paths to keep partial images inspectable.

Dependencies and integration: integrates with image resolution, platform matching, `multiPlatformSummary`, image identity cache helpers, containerd children handlers, Docker reference normalization, and API storage driver metadata. The graph-driver legacy field is populated with the snapshotter name for older API compatibility.

Risks: image records can change between resolve and list, producing `errInconsistentData`. Size calculation ignores missing child content except non-not-found errors, which favors partial-image visibility over strict integrity. Platform-specific inspect changes the returned descriptor/ID to the chosen manifest, which must remain aligned with Docker API expectations. Malformed image names are logged but still returned in repo tags for list compatibility.

Test signals: `image_inspect_test.go` covers missing multi-platform blobs, missing layer blobs, optional manifest output, and explicit platform selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_inspect_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_inspect_test.go

Purpose: validates inspect behavior for partial and multi-platform containerd images generated by Moby test helpers.

Important APIs and flow: `TestImageInspect` creates special-image indexes in a blob-backed fake service, registers containerd image records, then calls `ImageInspect` with different `ImageInspectOpts`. It checks that manifest summaries can be requested even when platform blobs are missing, that inspect survives a missing layer while still returning config/rootfs data, and that explicit `linux/amd64` or `linux/arm64` platform requests return matching architecture/OS fields.

State and persistence: uses a temporary blob directory and fake content store/image store. Tests mutate the content store by deleting a layer blob to simulate partial local state.

Dependencies and integration: depends on `specialimage`, `fakeImageService`, `imagesFromIndex`, containerd namespaces, and log test context. It primarily exercises `ImageInspect`, `multiPlatformSummary`, `ImageManifest.ReadConfig`, and partial-content handling.

Risks and gaps: it does not assert exact size values, repo digest generation, parent labels, identity output, or the error path for a requested missing platform. It relies on fake snapshot usage behavior.

Test signals: strong signal for API tolerance of incomplete content, which is a key containerd-store behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_list.go -->
# sources/cloud-native/moby/daemon/containerd/image_list.go

Purpose: implements Docker image listing on top of containerd images, content, snapshots, and daemon container metadata, including multi-platform aggregation, manifest metadata, labels, filters, shared size, and optional identity fields.

Important APIs and flow: `Images` validates filters, builds an `imageFilterFunc`, lists image records, collapses multiple names by target digest, hides intermediate dangling builder images unless `All` is set, gathers tags by digest, and computes summaries in parallel. `multiPlatformSummary` walks reachable manifests, classifies image vs attestation vs pseudo image, records availability, content size, unpacked snapshot size, chain IDs, containers using each manifest, and best platform. `imageSummary` emits either a combined multi-platform summary or a selected `singlePlatformImage`. `setupFilters` implements `before`, `since`, `until`, `label`, `label!`, `dangling`, and `reference`. `setupLabelFilter` walks present config blobs and deliberately skips BuildKit attestation subtrees. `computeSharedSize` counts shared snapshot chain IDs and shared content blobs without double-counting duplicates within one image.

State and persistence: read-only over image metadata, content metadata/blobs, snapshot usage, container store state, and identity cache. It treats descriptor availability as a first-class output so partially present indexes can be listed.

Dependencies and integration: tightly integrated with `ImageManifest`, `presentChildrenHandler` and `walkReachableImageManifests`, containerd `images.Dispatch`, Docker reference parsing, Moby filters/timestamp parsing, daemon container store, snapshotter usage APIs, and image identity cache helpers.

Risks: concurrent summary calculation requires careful locking around result slices and shared-size maps. The selected best platform uses host preference when no platform was requested, but total size/container counts still represent all manifests. Label filters can be expensive because they dispatch through content for each candidate. Shared size currently assumes one configured snapshotter. Some paths log and continue on corrupt/missing content, so list output may be partial rather than failing.

Test signals: `image_list_test.go` covers total content size, missing layers, multi-platform grouping, odd targets, identity-cache-only behavior, and shared-size content counting. `image_provenance_test.go` covers attestation manifest classification in list output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_list_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_list_test.go

Purpose: tests image-list behavior, size accounting, manifest classification, identity cache usage, and shared-size calculation for containerd-backed images.

Important APIs and flow: `imagesFromIndex` adapts special-image descriptors into containerd image records. `BenchmarkImageList` populates many generated images and optional containers to measure list scalability with shared-size computation. `TestImageListCheckTotalSize` builds a two-platform image and asserts combined and per-manifest content sizes, including after deleting layer blobs. `TestImageListIdentityUsesCacheOnly` and `TestImageListIdentityIsManifestScoped` verify identity data is not computed live and is keyed by image/index manifest/platform. `TestImageList` covers single image, multi-platform image, empty index, config target, text/plain pseudo content, and missing multi-platform state. `TestComputeSharedSizeIncludesSharedContentBlobs` validates shared layer and shared content blob accounting.

State and persistence: uses temporary blob directories and fake image services. Several tests mutate content by deleting blobs or inserting identity cache entries.

Dependencies and integration: depends on `specialimage`, fake content stores, containerd namespaces, daemon container store fakes, and `imagebackend.ListOptions`.

Risks and gaps: fake snapshotter usage is zero, so unpacked-size behavior is not fully validated. Some assertions depend on special-image descriptor ordering. Filter coverage for label/reference/before/since/until is not in this file.

Test signals: strong regression signal for partial content and multi-platform list semantics; benchmark signal for concurrent summary implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_load_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_load_test.go

Purpose: validates `LoadImage` platform filtering behavior for OCI/Docker archives loaded into the containerd image service.

Important APIs and flow: `TestImageLoad` creates single-platform, multi-platform, empty-index, and partial-content image archives with `specialimage`, tars them, and calls `imgSvc.LoadImage` with requested platform lists. `verifyImagePlatforms` inspects loaded images with manifest output and confirms the requested platforms appear.

State and persistence: uses a temporary labeled content store and fake image service. The `cleanup` helper removes image records through `ImageDelete` and deletes all content after each scenario to isolate cases.

Dependencies and integration: exercises archive import/load code outside this subset, then validates via `Images`/`ImageInspect` paths in this subset. It uses `platforms.Default` override to emulate daemon-native platform decisions.

Risks and gaps: the implementation under test is not in this work item, but the tests reveal expected containerd-store semantics: requested platforms must exist in the index and have required content, while all requested platforms can be retained. One platform constant is spelled `riskv64`, which is intentional test data but could hide typo-related expectations.

Test signals: covers empty index not-found, wrong single-platform request, all/single platform load from a multi-platform image, absent platform, and platform descriptor present with missing blobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_load_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_manifest.go -->
# sources/cloud-native/moby/daemon/containerd/image_manifest.go

Purpose: provides manifest-level helpers around containerd images so Docker can reason about one platform-specific manifest inside an index while preserving the original image/index metadata.

Important APIs and flow: `walkImageManifests` handles locally present manifests; `walkReachableImageManifests` walks known descriptors even when some child content is absent. `ImageManifest` embeds `containerd.Image`, stores `RealTarget`, and overrides `Metadata` to report the original target. `NewImageManifest` rejects non-manifest descriptors and wraps a single manifest with `platforms.All`. Methods classify attestations and pseudo images, cache/read manifest JSON, check content availability, infer platform from descriptor or config, read config subsets, calculate present content size, and calculate unpacked snapshot usage via diff-ID chain ID.

State and persistence: read-only except for cached manifest JSON in the `ImageManifest` instance. It reads content blobs and snapshot usage, and treats missing snapshot usage as zero for images not unpacked locally.

Dependencies and integration: central to list, inspect, push selection, snapshot creation, and attestation handling. It depends on BuildKit attestation annotations, containerd image child walking/checking, OCI identity chain IDs, and snapshot usage helpers.

Risks: `IsPseudoImage` intentionally treats unknown/unknown platform and attestation annotations as pseudo, but manifests with no layers are considered real enough for empty images. `walkReachableImageManifests` suppresses missing child errors to keep partial indexes usable. Snapshot usage depends on config rootfs diff IDs and the configured snapshotter only.

Test signals: indirectly exercised by list, inspect, push, load/save, and provenance tests; those cover partial content, pseudo/attestation classification, and platform selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_manifest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_provenance_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_provenance_test.go

Purpose: tests provenance and attestation behavior for image listing and `ImageAttestations`.

Important APIs and flow: helpers `provBlob`, `provJSON`, `buildFullIndex`, and `buildAttestationIndex` synthesize OCI indexes with platform image manifests and BuildKit-style attestation manifests. `TestAttestationDataFor` verifies list manifest summaries expose `AttestationData.For`. `TestImageAttestations` covers statement inclusion, default omission of statement body, order preservation, predicate type filtering, skipping layers without `in-toto.io/predicate-type`, missing statement blob errors, and nil output when no attestations exist.

State and persistence: writes synthetic blobs under temporary `blobs/sha256` directories and registers image records in the fake image service. Some scenarios intentionally omit layer blobs to validate lazy-vs-strict reads.

Dependencies and integration: depends on BuildKit attestation annotations, in-toto predicate annotations, containerd image descriptors, fake service/content store, `ImageAttestations`, and `Images` manifest summaries.

Risks and gaps: focused on synthesized minimal manifests, not registry-pulled referrer graphs. It does not test remote referrer fetching in `image_pull.go`; it validates local content interpretation after content exists.

Test signals: strong coverage for attestation classification and user-facing provenance output, especially the distinction between descriptor-only metadata and full statement body reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_provenance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_prune.go -->
# sources/cloud-native/moby/daemon/containerd/image_prune.go

Purpose: implements Docker image prune for the containerd-backed image store, including filter handling, lease cleanup, container-use protection, image metadata deletion, and reclaimed-space reporting.

Important APIs and flow: `ImagePrune` enforces a single active prune with `pruneRunning`, validates filters, interprets `dangling` defaulting to true, removes dangling filter values before calling `setupFilters`, deletes expiring pull leases labeled for prune, and delegates to `pruneUnused`. `pruneUnused` lists images, counts references per target digest, selects dangling or all unused candidates, removes candidates used by containers, preserves the last reference to a digest used by ID/digest-created containers, and calls `pruneAll`. `filterImagesUsedByContainers` protects dangling names, exact tags, ID-created containers, and tag+digest cases. `pruneAll` walks present children for size accounting, deletes image records synchronously, logs untag/delete events, and checks which blobs disappeared.

State and persistence: deletes containerd image records and may trigger content garbage collection via synchronous delete. It also deletes pull leases marked with `moby/prune.images`, using synchronous deletion for the final lease. The report is derived after deletion by probing content availability.

Dependencies and integration: reuses list filters and label filters, daemon container store, containerd leases/images/content, tracing spans, Docker event logging, and dangling image naming.

Risks: prune behavior depends on containerd GC timing and content availability after image delete. It walks blobs before deletion, so concurrent changes can skew `SpaceReclaimed`. Container reference protection is subtle for ID, truncated ID, tag, and tag+digest forms. Context cancellation returns accumulated errors early only for cancellation/deadline cases.

Test signals: no direct test file in this subset; behavior is indirectly related to image delete/list helpers. High-value missing tests include concurrent prune rejection, container reference preservation, label/until filters, and content reclaimed accounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_pull.go -->
# sources/cloud-native/moby/daemon/containerd/image_pull.go

Purpose: implements registry pull through containerd while preserving Docker API progress, leases, platform selection, dangling old-image retention, snapshot unpacking, referrer discovery, and registry error translation.

Important APIs and flow: `PullImage` rejects multiple platforms, creates a cancellable lease, pulls one tag or enumerates all tags for a name-only reference. `pullTag` configures media type ref-key prefixes, resolver/auth, old image preservation lease, platform matcher, progress jobs, layer/status handlers, pull unpack options, snapshotter info labels, and referrer provider/wrapper before calling `client.Pull`. It removes obsolete dangling refs, logs events, and warms the identity cache on success. `joinHandlerWrappers` composes containerd handler wrappers. `referrersForPull` and `referrersList` track inline attestation/referrer descriptors and fetch Sigstore referrers when needed. `parseSubject`, `writeStatus`, and `isModelMediaType` support subject parsing, Docker-compatible status output, and AI model warning behavior.

State and persistence: writes pulled content, image metadata, unpacked snapshots, snapshotter labels, temporary leases, dangling references for replaced images, and identity-cache state. A canceled cancellable lease may remain until expiration/prune.

Dependencies and integration: containerd remote pull/unpack, Moby registry tag enumeration, resolver/auth helpers, progress subsystem, snapshotter append-info handler, BuildKit attestation annotations, policy-helper media types, metrics, and Docker event logging.

Risks: referrer handling includes TODO-filtered provenance logic and registry-specific workarounds. Pull can leave old content protected as dangling if a new digest replaces it. Missing/unsupported platforms are translated from containerd errors by string inspection. AI model media types warn but are still processed by pull. Progress ordering depends on deferred final updates after the progress goroutine stops.

Test signals: load/provenance/list tests validate local outcomes of partial/multi-platform/referrer-style content, but direct registry pull/referrer/auth progress tests are outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_push.go -->
# sources/cloud-native/moby/daemon/containerd/image_push.go

Purpose: implements Docker image push through containerd, including all-tags push, platform-specific descriptor selection, cross-repository blob mount optimization, progress reporting, fallback from index to manifest when content is missing, distribution source labeling, and event/metric reporting.

Important APIs and flow: `PushImage` handles multi-platform rejection, all-tags repository push, and single-ref push. `pushRef` creates a lease, resolves the image tag, selects a target descriptor with `getPushDescriptor` when a platform is requested, builds resolver/status tracking, finds missing mountable blobs, wraps the content store to fake mountable blob metadata, pushes content with `remotes.PushContent`, retries an index push as a platform manifest on missing content, emits aux messages for fallback or missing content, appends distribution source labels, and logs events. `getPushDescriptor` walks reachable manifests, ignores attestations, filters by availability and platform, and decides between whole index, one manifest, not-found, or conflict. `findMissingMountable`, `getDigestSources`, `extractDistributionSources`, `distributionSource`, and `canBeMounted` implement cross-repo mount discovery.

State and persistence: read-mostly over image/content metadata, but it updates content labels after a successful push so future pushes can mount shared blobs from the target registry. It uses leases to protect pushed descriptors during traversal.

Dependencies and integration: depends on resolver/auth construction, progress jobs, fake content store wrapper, containerd remotes, Docker reference parsing, containerd distribution source labels, platform matchers, `ImageManifest`, and registry error translation.

Risks: descriptor selection is nuanced for partial multi-platform indexes and host platform preference. Fake content `Info` enables cross-repo mounts but `ReaderAt` still fails, so correctness depends on containerd remotes using labels for mounts rather than reading missing content. Distribution source labels strip target registry ports before comparison, which may conflate registries in unusual deployments. Multiple matching manifests without explicit platform can conflict.

Test signals: `image_push_test.go` exercises `getPushDescriptor` across all-present, partial, explicit platform, daemon-platform, ARM variant, not-found, and conflict cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_push_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_push_test.go

Purpose: validates platform and availability decision logic for push descriptor selection.

Important APIs and flow: `TestImagePushIndex` defines `pushTestCase` rows with index platforms, locally available platforms, optional requested platform, optional daemon platform override, and a checker. Each case creates a multi-platform image, deletes content for unavailable platforms with `deletePlatform`, then calls `getPushDescriptor`. Checkers assert whole-index selection, single-manifest selection, not-found, or conflict.

State and persistence: uses a temporary blob store and fake image service. `deletePlatform` walks matching platform manifests and deletes all present content descriptors to simulate a shallow/partial local index.

Dependencies and integration: uses `specialimage.MultiPlatform`, platform matchers, `walkImageManifests`, `ImageManifest.ImagePlatform`, `walkPresentChildren`, and containerd content deletion.

Risks and gaps: it tests selection only, not registry push, fake mountable blob behavior, progress, auth, distribution source labeling, or fallback aux output. Some comments identify open semantic questions around ARM fallback.

Test signals: strong regression coverage for host-preferred fallback and strict requested-platform behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_push_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_save_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_save_test.go

Purpose: validates multi-platform shallow export behavior for the containerd-backed image service.

Important APIs and flow: `TestImageMultiplatformSaveShallowWithNative` creates an index where native and another platform are present and one platform is missing, then verifies `ExportImage` succeeds for default/native/present platforms and fails for a missing platform. `TestImageMultiplatformSaveShallowWithoutNative` creates an index where native is missing, verifies requested native/nonexistent platforms fail, requested present platforms succeed, and mixed present+missing behavior depends on whether the missing entry is native. One default export case is skipped pending a CLI issue.

State and persistence: temporary blob directories plus fake image service/image store; no registry or long-lived state.

Dependencies and integration: exercises export implementation outside this work item but relies on platform matching and present-content traversal behavior shared with image manifest/list/push paths.

Risks and gaps: skipped default-without-native scenario records unresolved behavior. Tests use fake stores and do not inspect tar contents, only success/error.

Test signals: important for shallow multi-platform images where an index references platforms not locally available.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_save_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot.go -->
# sources/cloud-native/moby/daemon/containerd/image_snapshot.go

Purpose: adapts containerd snapshots into Docker `RWLayer` operations for container create/restore/export and computes snapshot usage.

Important APIs and flow: `CreateLayer` and `CreateLayerFromImage` call `createLayer` with an optional image manifest descriptor and init mount setup. `createLayer` resolves/unpacks the parent image snapshot, creates a non-expiring per-container lease, prepares an init layer when needed, then prepares or remaps the writable snapshot. `getImageSnapshot` wraps the descriptor as an `ImageManifest`, blocks Docker AI model media types, unpacks if needed, and returns the rootfs chain ID. `rwLayer` implements mount/unmount/metadata around a snapshotter and ref-count mounter. `GetLayerByID` restores an existing snapshot and lease. `ReleaseLayer` deletes the lease synchronously. `prepareInitLayer`, `calculateSnapshotParentUsage`, and `calculateSnapshotTotalUsage` support init snapshots and size accounting.

State and persistence: creates containerd leases named by container/layer ID, active/committed snapshots, optional init snapshots, and ref-count mounter mount state. Parent snapshots come from image unpack state.

Dependencies and integration: used by daemon container lifecycle, container restore, export, disk usage, service layer-size APIs, Unix/Windows remap helpers, containerd leases/snapshots/mounts, and Docker snapshotter mounter.

Risks: non-expiring per-container leases can leak resources, as noted in comments. Many operations use `context.TODO`, limiting cancellation. If init-layer setup fails after `Prepare`, cleanup is not explicit here. `Unmount` depends on remembered or discoverable mount root and returns an error when not mounted. AI model blocking is string-prefix based on config media type.

Test signals: no direct tests in this subset; list/inspect size tests use fake snapshotter behavior. Missing high-value tests include lease cleanup on prepare/init failures and remap behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot_unix.go -->
# sources/cloud-native/moby/daemon/containerd/image_snapshot_unix.go

Purpose: implements Unix user-namespace ownership remapping for containerd snapshots and root filesystems.

Important APIs and flow: `remapSnapshot` prepares a snapshot then mounts it and calls `remapRootFS`. `remapRootFS` walks the mounted root and maps container IDs to host IDs. `copyAndUnremapRootFS` copies a mounted source to destination, then walks destination and maps host IDs back to container IDs while deduplicating hard-linked inodes. `unremapRootFS` maps an existing rootfs back to container IDs. `chownWithCaps` preserves xattrs across `Lchown`, downgrading version-3 file capabilities to version 2 and trimming to the expected length.

State and persistence: mutates snapshot filesystem ownership and extended attributes in mounted snapshot directories. It does not directly edit containerd metadata beyond the snapshot prepared in the caller.

Dependencies and integration: used by `createLayer` and migration/export-like code paths that need userns remap. Depends on containerd mounts, continuity file copy/xattr helpers, syscall stat data, and Moby `idMapping`.

Risks: full filesystem walks can be expensive. Any xattr read/set failure aborts the remap. Capability byte indexing assumes expected xattr layout and length. `remapSnapshot` does not clean up the prepared snapshot if remapping fails. Hard-link dedup is only in copy/unremap, not plain remap.

Test signals: no direct tests here; userns remap behavior needs integration coverage with real snapshotters and file capabilities.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot_windows.go -->
# sources/cloud-native/moby/daemon/containerd/image_snapshot_windows.go

Purpose: provides Windows stubs for snapshot remap/unremap helpers that are meaningful on Unix user-namespace setups.

Important APIs and flow: defines the same `remapSuffix` constant and no-op `copyAndUnremapRootFS`, `remapSnapshot`, and `unremapRootFS` methods so cross-platform callers compile.

State and persistence: no state is changed on Windows by these functions.

Dependencies and integration: keeps `image_snapshot.go` portable while Windows layer-folder handling lives in `service_windows.go`.

Risks: because these are no-ops, any future Windows feature that expects ownership remapping must not silently rely on these methods. Behavior is intentionally platform divergent.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_squash.go -->
# sources/cloud-native/moby/daemon/containerd/image_squash.go

Purpose: placeholder for Docker image squash support in the containerd image service.

Important APIs and flow: `SquashImage(id, parent)` immediately returns a Moby `NotImplemented` error.

State and persistence: none.

Dependencies and integration: satisfies daemon image-service interface expectations while signaling that squash is unavailable for the containerd backend.

Risks: callers expecting legacy graphdriver squash support must handle `NotImplemented`. There is no migration or compatibility shim here.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_squash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_tag.go -->
# sources/cloud-native/moby/daemon/containerd/image_tag.go

Purpose: implements Docker image tagging for the containerd-backed image store, including replacement and dangling preservation semantics.

Important APIs and flow: `TagImage` resolves an image ID/reference to a target descriptor and calls `createOrReplaceImage` with a new image name and copied labels. `createOrReplaceImage` first attempts create, handles already-exists by resolving the existing reference set, no-ops if the target digest is unchanged, soft-deletes the replaced image otherwise, then creates the new record without cancellation. After successful non-dangling creation it logs a tag event, deletes any synthetic dangling name for the same digest, and warms the identity cache.

State and persistence: creates/deletes containerd image records, may create a synthetic dangling record for a replaced last reference via `softImageDelete`, deletes stale dangling records, and updates identity cache state.

Dependencies and integration: uses image resolution helpers, soft-delete helpers, Docker references, containerd image store, event logging, and identity cache warming.

Risks: replacement is multi-step and relies on non-cancelable cleanup to avoid losing the old digest. Concurrent tag operations can race between create/delete/create. Label copying carries source labels onto the new tag, except dangling creation strips name labels in `soft_delete.go`.

Test signals: lookup tests cover reference resolution, but direct tag replacement/dangling behavior is not covered in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_tag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_test.go

Purpose: shared tests and helpers for image reference resolution and fake services used by containerd image-service tests.

Important APIs and flow: `TestLookup` populates a metadata-backed image store with tagged, tagged+digested, digest-only, ambiguous short-name, and mutation-prone images, then verifies `resolveAllReferences` behavior. It covers default latest normalization, all records by image ID, tag+digest specificity, missing refs, short ID lookup, a repository literally named `sha256`, and retry/failure behavior when image metadata mutates mid-lookup. Helpers create deterministic descriptors/digests, open a test metadata DB, and provide a minimal snapshotter service.

State and persistence: uses temporary bbolt metadata through containerd `metadata.DB`; `mutateOnGetImageStore` intentionally changes image records during `Get` to simulate races.

Dependencies and integration: depends on containerd namespaces/metadata/images, Moby image reference errors, Docker reference helpers, and `gotest.tools`.

Risks and gaps: the tested functions are in nearby image-resolution code not included in this work item, but many listed files depend on correct resolution. It does not cover tag creation/deletion or content state.

Test signals: strong signal for Docker-compatible reference resolution and race detection, especially avoiding confusion between short image IDs and repository names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/imagespec.go -->
# sources/cloud-native/moby/daemon/containerd/imagespec.go

Purpose: converts between Moby internal `image.Image`/`container.Config` structures and Docker OCI image-spec structures used in the containerd content store.

Important APIs and flow: `dockerOciImageToDockerImagePartial` builds a Moby image from a Docker OCI image config without setting legacy container fields or details. `dockerImageToDockerOCIImage` converts a Moby image to Docker OCI image JSON. `containerConfigToDockerOCIImageConfig` maps user, env, entrypoint, cmd, volumes, workdir, labels, stop signal, args escaped, exposed ports, healthcheck, on-build, and shell. `dockerOCIImageConfigToContainerConfig` parses exposed port strings back to `network.Port` keys and reconstructs a `container.Config`.

State and persistence: pure conversion functions; persistence occurs when callers marshal/store config blobs.

Dependencies and integration: used by import, load/save/inspect-style conversion paths, Docker image spec, OCI image spec, Moby container/network API types, and internal image representation.

Risks: partial conversion intentionally omits legacy container metadata and details, so callers needing those fields must fill them separately. Invalid exposed port strings are silently skipped on OCI-to-container conversion. Slice/map cloning is partial and relies on struct assignment for nested values.

Test signals: `image_import_test.go` covers exposed-port string conversion; broader config field round-trip coverage is limited.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/imagespec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/leases.go -->
# sources/cloud-native/moby/daemon/containerd/leases.go

Purpose: centralizes temporary containerd lease creation for image operations that must protect content or snapshots from garbage collection.

Important APIs and flow: constants define an eight-hour expiration, the containerd GC expiration label, a Moby prune label, and a prune filter. `ImageService.withLease` reuses an existing lease in the context when present; otherwise it creates a random lease labeled for prune and expiration, attaches it to the context, and returns a cleanup function. If `cancellable` is true and the operation context was canceled, cleanup intentionally leaves the lease until expiration/prune.

State and persistence: creates and deletes containerd leases. Leases left after cancellation protect partially pulled resources and are later targeted by image prune via `pruneLeaseFilter`.

Dependencies and integration: used by pull and other image operations; prune deletes leases with the Moby prune label. It depends on containerd leases service and logging.

Risks: leaked leases can retain content until expiration or prune. Cleanup logs but does not return delete failures. Expiration is label-based, so correctness depends on containerd/prune respecting that metadata.

Test signals: no direct tests in this subset; cancellation/lease expiry behavior needs integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/leases.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/migration/migration.go -->
# sources/cloud-native/moby/daemon/containerd/migration/migration.go

Purpose: migrates legacy graphdriver images/layers into containerd content, image metadata, and snapshots.

Important APIs and flow: `LayerMigrator` holds legacy layer/reference/image stores plus containerd leases/content/images. `NewLayerMigrator` wires dependencies. `MigrateTocontainerd` supports overlay2 and vfs, creates a 24-hour lease, iterates Docker image heads, converts each legacy layer tar stream to compressed zstd content in parallel, copies each graphdriver upper/source directory into a prepared snapshot, commits snapshots by chain ID, writes the image config blob with snapshot GC labels, writes the manifest blob with content GC labels, maps children labels, and creates tagged or dangling containerd image records from legacy references. `extractSource` finds the writable source path from bind or overlay mounts.

State and persistence: writes new containerd content blobs, snapshot records/filesystem trees, image records, and temporary leases. It reads legacy graphdriver layer directories and legacy image/ref stores.

Dependencies and integration: bridges Moby legacy `layer.Store`, `refstore.Store`, and `image.Store` to containerd content/images/snapshots. Depends on containerd compression, content writers, snapshot labels, OCI manifests, and continuity `fs.CopyDir`.

Risks: migration is large and partially parallel; if a layer conversion goroutine fails after snapshots/content are written, cleanup is not comprehensive. Only overlay2/vfs and single-source bind/overlay snapshot mounts are supported. Zstd compression is hard-coded. Snapshot parent tracking must match diff ID chain order. Existing tags are skipped if already present, which can leave mixed old/new state.

Test signals: no direct tests in this subset; migration needs integration tests against real legacy stores and snapshotters.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/migration/migration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/platform_matchers.go -->
# sources/cloud-native/moby/daemon/containerd/platform_matchers.go

Purpose: wraps containerd platform matchers so Docker can match requested platforms strictly while preferring the daemon host platform when no platform was requested.

Important APIs and flow: `platformsWithPreferenceMatcher` matches either all platforms or a provided list, but delegates ordering to a preferred matcher. `matchAnyWithPreference` constructs it. `platformMatcherWithRequestedPlatform` embeds the matcher and remembers the explicit requested platform. `ImageService.matchRequestedOrDefault` returns a strict/requested matcher when a platform is supplied, otherwise a match-any matcher ordered by `hostPlatformMatcher`. `hostPlatformMatcher` uses a test override or `platforms.Default`.

State and persistence: stateless except for the test-only `defaultPlatformOverride` field on `ImageService`.

Dependencies and integration: used by list, inspect, push descriptor selection, and save/load behavior. Depends on containerd `platforms.MatchComparer`.

Risks: matching and ordering are intentionally separate; no requested platform means any platform can match, which is correct for summaries but can surprise push/export decisions when content is partial. Windows OSVersion semantics depend on containerd platform behavior and runtime OS.

Test signals: `platform_matchers_test.go` covers Linux ARM variant ordering, Windows OSVersion behavior where applicable, and list-limited preference matching.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/platform_matchers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/platform_matchers_test.go -->
# sources/cloud-native/moby/daemon/containerd/platform_matchers_test.go

Purpose: validates Docker/containerd platform matcher behavior used by list, inspect, push, load, and save paths.

Important APIs and flow: test fixtures define Linux amd64, ARM v5/v6, ARM64 v8, and Windows amd64 platforms. `TestMatcherOnLinuxArm64v8` checks default host preference and requested platform behavior with strict vs non-strict ARM variant matching. `TestMatcherOnWindowsAmd64` checks Windows OSVersion preference when running on Windows. `testOnlyAndOnlyStrict` executes the shared matrix. `TestPlatformsWithPreferenceMatcher` verifies list matching and preferred ordering.

State and persistence: no persistent state; uses `ImageService.defaultPlatformOverride` to emulate daemon platforms.

Dependencies and integration: depends on containerd `platforms`, Go runtime OS, and gotest assertions.

Risks and gaps: Windows OSVersion test is skipped outside Windows. The tests validate matcher mechanics, not every caller-specific policy decision.

Test signals: strong unit-level signal for strict requested platform and host-preferred ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/platform_matchers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/progress.go -->
# sources/cloud-native/moby/daemon/containerd/progress.go

Purpose: adapts containerd content transfer and snapshot unpack status into Docker-compatible JSON progress messages for pull and push.

Important APIs and flow: `jobs` tracks descriptors by digest and starts a progress goroutine with `showProgress`, calling a `progressUpdater` every 100ms and once more on cancellation. `pullProgress.UpdateProgress` reads active content ingest statuses, emits Downloading/Download complete/Already exists, tracks layers entering snapshot unpack, uses `findMatchingSnapshot` to show Extracting/Pull complete, and removes finished jobs. `pushProgress.UpdateProgress` reads docker status tracker entries and emits Waiting, Unavailable, Mounted from, Layer already exists, Already exists, Pushed, or Pushing. `combinedProgress` runs multiple updaters, and `showBlobProgress` hides small manifest/index/config descriptors while showing layers and unknown large blobs.

State and persistence: in-memory job maps and pull-progress layer/unpack state. Reads content ingest statuses, content info, docker push status tracker, and snapshotter metadata.

Dependencies and integration: used by pull and push. Depends on containerd content/remotes/docker/snapshotters labels, Moby progress output, string ID truncation, and snapshotter append-info labels.

Risks: progress is inherently racy with fast transfers and snapshot commits. `findMatchingSnapshot` requires `containerd.io/snapshot/target`-style annotations added by the pull handler; without them extracting progress is unavailable. The final update has only a 500ms timeout. Hidden layers on already-complete pulls can remove jobs before user sees per-layer status, intentionally matching legacy behavior.

Test signals: no direct tests in this subset; pull/push integration tests would be needed to validate output ordering and status transitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/registry_errors.go -->
# sources/cloud-native/moby/daemon/containerd/registry_errors.go

Purpose: translates containerd/docker registry errors into Docker/Moby error classes with user-facing messages.

Important APIs and flow: `translateRegistryError` returns nil for nil, extracts `docker.Errors`, `remoteerrors.ErrUnexpectedStatus`, or a single `docker.Error`, parses OCI registry error JSON bodies, handles legacy token-server `details` bodies for 401/403, maps known docker error codes to containerd errdefs (`NotImplemented`, `Unauthenticated`, `PermissionDenied`, `Unavailable`, `ResourceExhausted`, `Unknown`), joins multiple errors, and wraps the result as `error from registry`.

State and persistence: none.

Dependencies and integration: used by pull and push error paths. Depends on containerd remotes/docker error types, remote unexpected status bodies, JSON parsing, HTTP status codes, logging, and containerd errdefs.

Risks: failed JSON parsing of an unexpected status body returns an unknown wrapped error, possibly losing registry details. Multiple errors are joined after mapping, which can affect caller matching. Legacy `details` handling only applies when OCI errors array is empty.

Test signals: no direct tests in this subset; high-value tests would cover OCI error arrays, legacy token-server errors, rate limiting, and non-registry pass-through.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/registry_errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/resolver.go -->
# sources/cloud-native/moby/daemon/containerd/resolver.go

Purpose: builds authenticated containerd registry resolvers and authorizers from Docker daemon registry configuration and per-request auth.

Important APIs and flow: `newResolverFromAuthConfig` creates an in-memory docker status tracker, wraps registry hosts with auth when provided, clones meta headers, sets a Docker/containerd/storage-driver user agent, and returns `docker.NewResolver`. `hostsWrapper` replaces each host authorizer with one derived from request auth. `authorizerFromAuthConfig` normalizes auth server host, handles Docker Hub host aliases, returns a bearer authorizer for registry tokens, or a docker authorizer for username/password or identity token. `bearerAuthorizer` only adds Authorization when request host matches and returns not-implemented from `AddResponses` to avoid token retry.

State and persistence: no durable state; status tracker is in-memory for push progress.

Dependencies and integration: used by pull and push. Depends on Moby registry host conversion, Docker user-agent construction, containerd docker remotes, containerd version, daemon snapshotter name, and request auth config.

Risks: host mismatch results in warnings and no credentials, which can be confusing when aliases or ports differ. Bearer token authorizer performs exact `req.Host` matching. Meta headers are cloned then user-agent is overwritten.

Test signals: no direct tests in this subset; auth behavior needs registry integration or focused unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service.go -->
# sources/cloud-native/moby/daemon/containerd/service.go

Purpose: defines the containerd-backed `ImageService` core state and daemon-facing service methods for image counts, disk usage, layer status, cleanup, config reload, and container layer sizes.

Important APIs and flow: `ImageService` stores containerd client, image/content stores, container store, snapshotter cache, registry services, events, prune flag, ref-count mounter, ID mapping, policy verifier, identity cache state, and test platform override. `NewService` wires these dependencies and starts identity cache refresh. `snapshotterService` caches snapshotter clients by name. `CountImages` counts unique target digests. `LayerStoreStatus`, `StorageDriver`, `Cleanup`, `ImageDiskUsage`, `layerDiskUsage`, `UpdateConfig`, and `GetContainerLayerSize` implement daemon interface behavior. `DistributionServices`, `GetLayerMountID`, and upload/download config are not implemented or empty.

State and persistence: manages in-memory service dependencies and identity cache lifecycle. Disk usage methods read snapshotter usage and content descriptors. Cleanup closes identity cache backend.

Dependencies and integration: this is the dependency hub for the other files in this subset. It integrates containerd client APIs, daemon container store, registry/distribution, events, snapshotter mounter, policy verifier, identity cache backend, and Moby error definitions.

Risks: `snapshotterServices` map is not guarded by a mutex, so concurrent first access to different snapshotters could race. Disk usage assumes the configured snapshotter and walks every image's present content. `UpdateConfig` logs unsupported max transfer settings, so daemon reload knobs do not affect containerd transfers here.

Test signals: many tests build fake `ImageService` values directly; direct coverage of service lifecycle/disk usage is limited in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service_unix.go -->
# sources/cloud-native/moby/daemon/containerd/service_unix.go

Purpose: Unix/FreeBSD implementation placeholder for layer-folder introspection in the containerd image service.

Important APIs and flow: `GetLayerFolders` returns a Moby `NotImplemented` error on linux/freebsd.

State and persistence: none.

Dependencies and integration: satisfies daemon image-service interfaces for platforms where graphdriver layer folder paths are not exposed by this backend.

Risks: callers that need graphdriver-style layer folder paths must handle not-implemented when using the containerd store.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service_windows.go -->
# sources/cloud-native/moby/daemon/containerd/service_windows.go

Purpose: Windows implementation of layer-folder discovery for containerd snapshots.

Important APIs and flow: `GetLayerFolders` validates the RW layer, asserts it is the local `*rwLayer`, retrieves snapshot mounts, extracts Windows parent paths from the first mount with `GetParentPaths`, and returns parent paths plus the writable mount source.

State and persistence: read-only over snapshot mount metadata.

Dependencies and integration: used by Windows daemon paths that need the ordered layer folder list compatible with hcsshim runhcs logic. Depends on `rwLayer.mounts` and containerd mount helper behavior.

Risks: assumes at least one mount and that the first mount has Windows parent path metadata. Fails for unexpected layer implementations. Error messages include container ID context.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/soft_delete.go -->
# sources/cloud-native/moby/daemon/containerd/soft_delete.go

Purpose: preserves image content reachability when tags are replaced or deleted by creating synthetic dangling image records.

Important APIs and flow: `softImageDelete` creates a dangling image if the deleted image is the last reference to its target, then deletes the original name using a non-cancelable context. `ensureDanglingImage` copies the image metadata, strips name-related labels, renames it to `moby-dangling@<digest>`, and creates it if absent. `danglingImageName` and `isDanglingImage` define the synthetic naming convention.

State and persistence: creates and deletes containerd image records. Does not delete content directly; it protects target descriptors from becoming unreachable until prune/delete logic removes the dangling record.

Dependencies and integration: used by tag replacement, pull replacement, list hiding/filtering, prune, and inspect tag/digest collection.

Risks: the dangling convention is name-based and a TODO notes no expiration check. A failure to create the dangling image aborts replacement to avoid content loss. Concurrent references can make `len(imgs) == 1` stale.

Test signals: indirect behavior appears in list/prune/tag paths; no direct unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/soft_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/store.go -->
# sources/cloud-native/moby/daemon/containerd/store.go

Purpose: wraps a content store so push can pretend selected missing blobs exist for cross-repository mount attempts.

Important APIs and flow: `fakeStoreWithSources` embeds a real `content.Store` and a digest-to-distribution-source map. `wrapWithFakeMountableBlobs` constructs it. All content store methods delegate except `Info`: when the real store returns not-found and the digest has a source, `Info` returns synthetic content metadata with a `containerd.io/distribution.source.<domain>` label. `ReaderAt` still delegates and therefore still fails for missing content.

State and persistence: no durable writes; synthetic metadata exists only through this wrapper during push.

Dependencies and integration: used by `image_push.go` after `findMissingMountable`. It relies on containerd remotes recognizing distribution source labels to mount blobs instead of uploading/reading them.

Risks: this intentionally lies about content existence, so it must be scoped to push mount optimization. If a caller tried to read the synthetic blob, it would fail. Label domain/value formatting must match containerd expectations.

Test signals: no direct tests in this subset; push tests cover descriptor selection but not fake store mount behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerfs_linux.go -->
# sources/cloud-native/moby/daemon/containerfs_linux.go

Purpose: creates a private Linux mount-namespace view of a container filesystem so daemon code can run filesystem operations with the container root as `/`, while preserving mount safety and cleanup.

Important APIs and flow: `openContainerFS` mounts the container, sets up volume mounts, starts an unshared `CLONE_NEWNS` goroutine, makes `/` rslave, opens the container root with `os.OpenRoot`, resolves each mount destination through container symlinks, safely creates missing targets with `createIfNotExists`, bind/rbind mounts sources through pinned `/proc/self/fd/<fd>` targets, applies read-only and recursive read-only settings, makes mounts private, switches root with `mounttree.SwitchRoot`, and then processes serialized `future` work items. `RunInFS` synchronously runs a function in the view. `GoInFS` starts a function without waiting for completion. `Close` stops the worker and unmounts volumes/container. `Stat` performs an `Lstat` inside the view and resolves symlink targets in scope. `makeMountRRO` uses `mount_setattr` recursively.

State and persistence: holds a live container mount, private namespace mounts, per-view current working directory, and a goroutine/channel pair. The view is read-write for the container root but tmpfs/private mount behavior is isolated. A finalizer calls `Close` as a fallback.

Dependencies and integration: used by daemon filesystem APIs needing safe container-root context. Depends on daemon mount/setupMounts/unmount, container resource path resolution, `os.Root` protections, Moby mounttree/unshare helpers, sys mount APIs, and symlink scoped resolution.

Risks: this is security-sensitive TOCTOU code. It relies on fd-pinned bind mount targets to prevent symlink swaps, then real paths for remount/propagation because the kernel rejects those on `/proc/self/fd`. `GoInFS` does not wait for function completion. Closing while callers still hold the view can race with pending sends. Recursive read-only fallback logs unless force-recursive is required.

Test signals: `containerfs_linux_test.go` covers only `createIfNotExists`; mount namespace behavior needs privileged/integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerfs_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerfs_linux_test.go -->
# sources/cloud-native/moby/daemon/containerfs_linux_test.go

Purpose: unit coverage for safe creation of mount targets inside an `os.Root`.

Important APIs and flow: `TestCreateIfNotExists` opens a temporary directory as an `os.Root`, verifies directory creation is idempotent, verifies nested file creation creates parents and a file rather than a directory, and verifies repeated file creation succeeds.

State and persistence: writes only inside temporary test directories.

Dependencies and integration: targets `createIfNotExists` in `containerfs_linux.go`, using `gotest.tools` assertions and the Go `os.Root` API.

Risks and gaps: does not cover symlink escape attempts, bind mounting, recursive read-only behavior, mount namespace lifecycle, `RunInFS`, `GoInFS`, `Close`, or `Stat`.

Test signals: narrow but useful for idempotent mount-target preparation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerfs_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/content.go -->
# sources/cloud-native/moby/daemon/content.go

Purpose: configures a local containerd content store for the daemon and wraps content/lease services so a default namespace is always applied.

Important APIs and flow: `configureLocalContentStore` creates `<daemon.root>/content`, opens `metadata.db` with bbolt, creates a local content store under `content/data`, wraps it in containerd metadata DB, stores the bbolt handle on the daemon, and returns `namespacedContent` and `namespacedLeases`. `withDefaultNamespace` preserves an existing namespace or injects the configured default. `namespacedContent` implements content store methods by applying the namespace before delegating. `namespacedLeases` does the same for lease manager methods.

State and persistence: creates persistent daemon content metadata DB and blob data directories. Stores `daemon.mdDB` for later lifecycle management. All content and lease operations are namespaced in containerd metadata.

Dependencies and integration: used when the daemon needs a local content store outside a full external containerd setup. Depends on containerd local content plugin, metadata DB, namespaces, leases, bbolt, and daemon root configuration.

Risks: bbolt open uses default options and must be closed elsewhere through `daemon.mdDB`. Namespace wrapping is easy to bypass if callers retain the underlying provider. Directory permissions are restrictive for metadata/data roots, which is appropriate but can surface deployment permission issues.

Test signals: no direct tests in this subset; namespace wrapper behavior and persistence lifecycle need integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/content.go -->
