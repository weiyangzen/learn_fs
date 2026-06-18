# subset-b-000176 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/hosts.go -->
# sources/cloud-native/moby/daemon/hosts.go

Purpose: adapts Docker daemon registry configuration into containerd `docker.RegistryHost` records. It combines containerd-style `certs.d` host configuration with Moby's legacy mirror, custom certificate, and insecure registry settings.

Important APIs and control flow: `Daemon.RegistryHosts` calls containerd `ConfigureHosts` with `registry.CertsDir()`, then calls `mergeLegacyConfig` when daemon mirrors or insecure registries are configured. `mergeLegacyConfig` only modifies the single default host case, adds Docker Hub mirrors via `mirrorsToRegistryHosts`, loads TLS roots and client key pairs with `loadTLSConfig`, and wraps insecure transports with HTTP fallback. `mirrorsToRegistryHosts` normalizes mirror URLs, default schemes, and legacy `/v2` path behavior. `loadTLSConfig` scans `.crt`, `.cert`, and matching `.key` files into a `tls.Config`.

State and persistence: no daemon state is mutated except the returned host transport objects. It reads registry certificate directories on disk and daemon registry service configuration.

Dependencies and integration: integrates Moby registry config, containerd remotes/docker host resolution, Go TLS/x509 pools, and HTTP transports used by pull/push/build resolver paths.

Risks: legacy merge is intentionally skipped when containerd already supplies multiple hosts, so operator precedence is subtle. Insecure registry handling sets `InsecureSkipVerify` and HTTP fallback by design. Certificate loading tolerates missing or permission-denied directories but fails on malformed client key pairs. Mirror path normalization preserves legacy behavior that can append `/v2` even to paths that already contain it in the middle.

Test signals: `hosts_test.go` covers mirror URL normalization and capability shaping. TLS and insecure-registry branches are mainly covered through registry integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/hosts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/hosts_test.go -->
# sources/cloud-native/moby/daemon/hosts_test.go

Purpose: unit tests for converting legacy Docker registry mirrors into containerd registry host entries.

Important APIs and control flow: `TestMirrorsToHosts` builds a default Docker Hub host and checks `mirrorsToRegistryHosts` for HTTPS, HTTP, bare host, trailing slash, custom base path, `/v2`, and embedded `/v2/base` inputs. `testRegistryHost` is a compact fixture constructor.

State and persistence: no persisted state. Tests are table-driven and compare pure values.

Dependencies and integration: uses containerd `docker.HostCapabilities` plus `gotest.tools` assertions. It validates behavior expected by `Daemon.mergeLegacyConfig`.

Risks: tests focus on mirror conversion only, not TLS certificate loading or insecure transport mutation. The table encodes legacy `/v2` path quirks, so intentional behavior changes require updating expected paths carefully.

Test signals: direct coverage for pull/resolve/referrers-only mirror capabilities and preservation of the default registry host as the fallback entry.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/hosts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/id.go -->
# sources/cloud-native/moby/daemon/id.go

Purpose: owns the daemon engine ID file lifecycle.

Important APIs and control flow: `LoadOrCreateID(root)` reads `<root>/engine-id`; if missing, it generates a UUID and writes it with `atomicwriter.WriteFile` mode `0600`; otherwise it returns the file contents. Errors are wrapped with path or save context.

State and persistence: persists the engine ID as a root-owned file under the daemon root. The function assumes the daemon root already exists with correct permissions.

Dependencies and integration: uses `github.com/google/uuid` for ID generation and `moby/sys/atomicwriter` for safe file replacement. The daemon uses the returned ID in system info and BuildKit identity wiring.

Risks: existing file contents are trusted verbatim; there is no UUID validation or whitespace trimming. Concurrent first-start callers could race through UUID generation, although atomic file writes limit partial-file exposure.

Test signals: no direct tests in this subset; coverage is usually daemon startup and persistence behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/id.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_service.go -->
# sources/cloud-native/moby/daemon/image_service.go

Purpose: defines the daemon-level `ImageService` interface used while Moby supports both legacy graphdriver and containerd image-store implementations.

Important APIs and control flow: the interface groups image operations such as pull, push, create, delete, list, prune, import, tag, inspect, history, commit, squash, attestations, and disk usage; layer operations such as create/release/size/changes; builder support such as image cache and build-step commit; and cross-cutting functions such as distribution service access, storage driver reporting, cleanup, and config update.

State and persistence: the interface has no state itself, but it defines access to persistent image stores, reference stores, layer stores, and distribution metadata.

Dependencies and integration: this is a key contract between `daemon`, `daemon/images`, server backends, legacy builder, BuildKit migration shims, and containerd-backed alternatives. It imports API image/event types, backend option structs, internal image/layer types, and OCI platform values.

Risks: the comment explicitly says the interface is temporary and unstable. Its breadth couples daemon code to many image-store details, including Windows-specific and legacy-builder functions, which makes migration harder.

Test signals: no direct tests for the interface; compile-time conformance and daemon subsystem tests reveal drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_store_choice.go -->
# sources/cloud-native/moby/daemon/image_store_choice.go

Purpose: decides whether the daemon should use the containerd image store/snapshotter path or the legacy graphdriver image store.

Important APIs and control flow: `imageStoreChoice` encodes default, explicit, and prior-data choices. `IsGraphDriver` and `IsExplicit` classify those choices. `getDriverOverride` resolves a graphdriver or snapshotter name from `DOCKER_DRIVER`, daemon config, and Windows defaults. `determineImageStoreChoice` starts with containerd by default except Windows, applies the `containerd-snapshotter` feature flag, the `TEST_INTEGRATION_USE_GRAPHDRIVER` override, prior graphdriver data detection, and registered graphdriver recognition before returning a choice or an explicit-graphdriver error.

State and persistence: reads environment variables and checks prior graphdriver state under the configured daemon root through injectable functions. No state is written.

Dependencies and integration: depends on daemon config, `graphdriver.HasPriorDriver`, `graphdriver.IsRegistered`, runtime OS, and containerd logging. Its output steers daemon startup, storage initialization, and migration safety.

Risks: behavior depends on environment variables, feature flags, platform, and previously persisted driver state, so startup outcomes can be surprising. Non-registered driver names are treated as snapshotter names unless graphdriver mode was explicit. Prior graphdriver data takes precedence over configured graphdrivers in some paths to avoid accidental migration.

Test signals: `image_store_choice_test.go` covers feature flag precedence, integration-test overrides, registered graphdrivers, custom snapshotters, prior data, and Windows-specific choices.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_store_choice.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_store_choice_test.go -->
# sources/cloud-native/moby/daemon/image_store_choice_test.go

Purpose: table-driven coverage for image store selection across Linux-like and Windows daemon startup scenarios.

Important APIs and control flow: `TestDetermineImageStoreChoice` constructs cases for feature flags, `DOCKER_DRIVER`, `TEST_INTEGRATION_USE_GRAPHDRIVER`, graphdriver config, prior graphdriver data, custom snapshotter names, and Windows `windows`/`windowsfilter` driver names. It injects fake `hasPriorDriver`, fake graphdriver registry checks, and fake runtime OS values.

State and persistence: uses `t.Setenv` for environment isolation. No filesystem state is created because prior-driver detection is injected.

Dependencies and integration: depends on daemon config structs, slices membership helpers, and `gotest.tools` comparisons. It validates policy implemented by `determineImageStoreChoice` without requiring registered real drivers.

Risks: `expectError` support exists but the shown cases mostly exercise non-error paths; explicit invalid graphdriver errors may be undercovered. Platform simulation is string based, so any runtime-specific side effects outside `determineImageStoreChoice` are not tested.

Test signals: strong coverage for the startup decision matrix and precedence ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_store_choice_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/cache.go -->
# sources/cloud-native/moby/daemon/images/cache.go

Purpose: adapts `ImageService` to the legacy builder image-cache interface.

Important APIs and control flow: `cacheAdaptor` forwards image lookup, reference lookup, parent management, built-locally checks, and image creation to the service's image store. `Children` has special `FROM scratch` behavior: for an empty parent ID, it returns root images that were built locally. `Create` marshals an image config, creates the image, and optionally sets its parent. `MakeImageCache` constructs the actual cache with `cache.New`.

State and persistence: reads and writes image store records, parent links, and built-locally metadata. No layer data is written here.

Dependencies and integration: bridges `daemon/internal/image/cache`, the legacy builder package, the internal image store, and `ImageService.GetImage`.

Risks: `Children` logs and skips images when built-locally metadata cannot be read, which may reduce cache hits silently. `Create` ignores the diffID argument, so it relies on the supplied image config to be consistent with layers.

Test signals: no direct tests in this file; build cache behavior is covered indirectly by builder tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image.go -->
# sources/cloud-native/moby/daemon/images/image.go

Purpose: implements image lookup and platform compatibility checks for the legacy image service.

Important APIs and control flow: `ErrImageDoesNotExist` is a NotFound-style error. `manifestMatchesPlatform` looks at content leases named for an image, reads manifest lists and manifests from the content store, and checks whether a requested platform points to the image config digest. `GetImage` parses references, resolves named references through the refstore, falls back to image ID search, and on return verifies requested platforms with `OnlyPlatformWithFallback` plus the manifest-list fallback. `OnlyPlatformWithFallback` wraps `platforms.Only` and accepts images whose config lacks a CPU variant when OS and architecture match.

State and persistence: reads image store records, reference store entries, content store blobs, and content lease resources. It does not mutate state.

Dependencies and integration: used by almost every image API. It integrates distribution references, containerd content/lease APIs, OCI platform matching, and daemon API error classification.

Risks: `GetImage` can return both a non-nil image and a NotFound error on platform mismatch, and callers must handle that special case. `manifestMatchesPlatform` reads only up to 1 MB of content and skips malformed or missing resources with logs, so corrupt lease content may degrade platform validation rather than fail hard. The legacy store cannot model multiple platform variants for one tag cleanly.

Test signals: `images_test.go` covers the CPU-variant fallback matcher. Platform mismatch behavior is covered indirectly by pull/build paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_attestations.go -->
# sources/cloud-native/moby/daemon/images/image_attestations.go

Purpose: declares that image attestations are unsupported for the legacy image store.

Important APIs and control flow: `ImageAttestations` ignores its arguments and returns an `errdefs.NotImplemented` error explaining that the legacy image store does not support attestations.

State and persistence: no state is read or written.

Dependencies and integration: satisfies the daemon `ImageService` interface and lets API handlers return a typed not-implemented response when running without the containerd image store.

Risks: callers must not assume attestation support is universal across image-store backends. Feature detection should account for this backend-specific error.

Test signals: no direct tests in this subset; API behavior is expected to be checked in image-store mode integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_attestations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_builder.go -->
# sources/cloud-native/moby/daemon/images/image_builder.go

Purpose: provides legacy builder access to images and layers, including pull-on-demand, readonly layers, temporary writable layers, and image creation.

Important APIs and control flow: `roLayer` wraps a referenced layer and releases it exactly once. `rwLayer` mounts a temporary RW layer, exposes its root, commits its tar stream as a new readonly layer, and releases/unmounts it. `newROLayerForImage` holds a layer-store reference for an image rootfs. `pullForBuilder` normalizes refs, resolves auth, pulls, then tolerates a special platform-mismatch warning case. `GetImageAndReleasableLayer` implements builder `FROM` logic, including scratch handling, no-pull/force-pull behavior, OS checks, and final layer acquisition. `CreateImage` writes config JSON, parent links, and built-locally metadata.

State and persistence: creates and releases layer-store references, temporary RW layers, new image-store records, parent metadata, and built-locally flags. Pulling may update the image/reference/content stores.

Dependencies and integration: connects legacy builder interfaces to `ImageService`, registry auth resolution, distribution pull, layer store, streamformatter progress output, and OCI platform checks.

Risks: every `GetImageAndReleasableLayer` caller must release the returned layer or leak layer references. RW layer `Commit` registers tar content but leaves empty-layer optimization as a TODO. Platform mismatch handling intentionally emits a warning and suppresses an error in a known manifest/config inconsistency case.

Test signals: no direct unit tests here; behavior is covered by Dockerfile build and pull integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_changes.go -->
# sources/cloud-native/moby/daemon/images/image_changes.go

Purpose: returns filesystem changes for a container's writable layer.

Important APIs and control flow: `ImageService.Changes` locks the container, validates that `RWLayer` is present and implements `layer.RWLayer`, then returns `rwLayer.Changes()`.

State and persistence: reads the container's RW layer state through the layer store; no state is written.

Dependencies and integration: used by daemon change/diff APIs and depends on container locking plus the archive change model.

Risks: the function holds the container lock while calling `Changes`, so slow graphdriver operations can extend lock hold time. Unexpected RW layer types produce explicit errors.

Test signals: direct tests are not in this subset; daemon changes tests exercise this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_changes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_commit.go -->
# sources/cloud-native/moby/daemon/images/image_commit.go

Purpose: creates image records from container writable-layer diffs and provides a builder-specific commit shim.

Important APIs and control flow: `CommitImage` exports the container RW layer as a tar stream, resolves or creates the parent image, registers a new layer over the parent chain, builds a child image config, creates the image, logs a create event, marks it built locally, and records its parent. `exportContainerRw` gets, mounts, streams, unmounts, and releases the RW layer with cleanup on errors. `CommitBuildStep` looks up a container and fills mount label, OS, and parent image before delegating to `CommitImage`.

State and persistence: writes new layer-store layer data, image-store config records, built-locally metadata, parent links, and image events. It reads container store and existing parent image state.

Dependencies and integration: integrates backend commit configs, layer tar streams, internal image config construction, ioutils read-closer wrappers, and daemon events.

Risks: mount/unmount/release sequencing is error-prone; `exportContainerRw` must keep releasing on both happy and error paths. `CommitBuildStep` intentionally bypasses normal container-state validation, which is acceptable only for the legacy builder shim.

Test signals: no direct tests here; commit and builder integration tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_commit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_delete.go -->
# sources/cloud-native/moby/daemon/images/image_delete.go

Purpose: implements image and reference deletion semantics for the legacy image service.

Important APIs and control flow: `ImageDelete` resolves a ref/ID, handles optional single-platform validation, removes repository references first when a named ref was supplied, cleans up related digest refs, and then calls `imageDeleteHelper`. `isSingleReference` determines whether all refs are one repository with at most one tag. `removeImageRef` and `removeAllReferencesToImageID` manipulate refstore entries and append API delete records. `imageDeleteHelper` enforces hard and soft conflicts, deletes the image store entry, records layer deletions, logs events, and optionally prunes parents quietly. `checkImageDeleteConflict` checks child images, running containers, stopped containers, and active references.

State and persistence: mutates reference store entries, image store records, layer metadata through image-store delete, and event logs. It reads container store and image ancestry state.

Dependencies and integration: used by API image remove and image prune. It integrates API delete responses, event metrics, container store filters, image/reference/layer stores, platform-aware `GetImage`, and daemon error typing.

Risks: deletion semantics differ for named references and ID prefixes, and `force` only overrides soft conflicts. The conflict checks include normal container `ImageID` use and image mounts in one early branch, but later stopped/running conflict helpers only check `ImageID`. Quiet pruning deliberately suppresses some conflicts, so callers must inspect returned records rather than assume full ancestry deletion.

Test signals: no direct tests in this file; prune, remove, and container-use integration tests are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_events.go -->
# sources/cloud-native/moby/daemon/images/image_events.go

Purpose: emits image events with stable label and reference attributes.

Important APIs and control flow: `LogImageEvent` detaches from cancellation with `context.WithoutCancel`, attempts to load the image to copy config labels, adds the event `name` attribute when provided, and logs through the daemon events service. `copyAttributes` uses `maps.Copy` to avoid mutating the source labels map.

State and persistence: reads image config labels and writes daemon event records.

Dependencies and integration: used by pull, push, tag, delete, import, commit, and prune-related image operations. It integrates `ImageService.GetImage`, API event types, and event actor attributes.

Risks: delete events often happen after image removal, so missing images are ignored. Event emission surviving caller cancellation is intentional but means events may be emitted after request abort.

Test signals: no direct tests here; event assertions in image operation tests cover behavior indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_exporter.go -->
# sources/cloud-native/moby/daemon/images/image_exporter.go

Purpose: delegates save/load image archive behavior to the legacy tar exporter.

Important APIs and control flow: `ExportImage` and `LoadImage` accept zero or one platform only, reject multiple platforms with invalid-parameter errors, create a `tarexport.TarExporter` over the image, layer, reference stores and service, then call `Save` or `Load`.

State and persistence: `ExportImage` reads image/layer/ref state and writes to the caller stream. `LoadImage` reads a tar stream and can create image, layer, and reference records.

Dependencies and integration: backs API `docker save`/`docker load` for the legacy store and explicitly points multi-platform users to a containerd-snapshotter store.

Risks: multi-platform archives are not supported by this backend. Stream errors and partial loads are delegated to `tarexport`, so callers rely on its cleanup guarantees.

Test signals: no direct tests in this subset; save/load integration tests are the primary coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_exporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_history.go -->
# sources/cloud-native/moby/daemon/images/image_history.go

Purpose: builds the API image history response from image config history, layers, parents, and tags.

Important APIs and control flow: `ImageHistory` resolves the image, walks config history in order while mapping non-empty history entries to rootfs diff IDs and layer sizes, reverses entries for API output, then walks parent image IDs to fill IDs and tag lists from the reference store. It updates the image `history` metric.

State and persistence: reads image store, layer store, and reference store. No state is mutated.

Dependencies and integration: used by the image history API and depends on rootfs chain reconstruction, layer release discipline, and reference classification.

Risks: malformed images with more non-empty history entries than rootfs diff IDs return an error. Parent lookup failures stop ID/tag enrichment rather than failing the entire response after the current entries have been built.

Test signals: no direct tests in this subset; API history tests cover expected output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_history.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_import.go -->
# sources/cloud-native/moby/daemon/images/image_import.go

Purpose: implements `docker import` for the legacy image store.

Important APIs and control flow: `ImportImage` defaults nil platforms to `platforms.DefaultSpec`, validates OS support, applies Dockerfile-style `changes` to an empty container config, decompresses the input layer stream, registers it as a root layer, constructs a minimal image config with one diff ID and history entry, creates the image, optionally tags it, and logs an import event.

State and persistence: writes a new layer, image config record, optional reference tag, last-updated metadata through tagging, and image event.

Dependencies and integration: depends on archive compression, Dockerfile config mutation, image/layer stores, OCI platforms, and daemon event logging.

Risks: a failure after `imageStore.Create` but before tag/event leaves an untagged imported image. OS validation is based on the requested platform, not stream content. Layer release after registration is critical to avoid reference leaks.

Test signals: import integration tests cover this path; no direct unit test is in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_inspect.go -->
# sources/cloud-native/moby/daemon/images/image_inspect.go

Purpose: constructs the API image inspect response from legacy image, layer, and reference state.

Important APIs and control flow: `ImageInspect` resolves the image with optional platform, gets layer size and graphdriver metadata, reads last-updated time, splits references into tags and digests, derives fallback comment from history, converts container config to Docker OCI image config, and returns both modern inspect fields and deprecated legacy fields. `getLayerSizeAndMetadata` loads the rootfs chain layer, reads size and metadata, and releases it.

State and persistence: reads image store, reference store, layer store, and image last-updated metadata. No state is written.

Dependencies and integration: used by image inspect API and depends on storage driver metadata, `containerConfigToDockerOCIImageConfig`, and platform-aware `GetImage`.

Risks: corrupt or missing layer metadata fails the inspect request. Deprecated fields are still populated for compatibility, so config shape changes affect older clients.

Test signals: no direct tests in this subset; image inspect API tests provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_list.go -->
# sources/cloud-native/moby/daemon/images/image_list.go

Purpose: implements filtered image listing for the legacy image service.

Important APIs and control flow: `Images` validates filters, computes dangling/all image candidates, resolves `before`, `since`, and `until` filters to timestamps, filters labels and references, skips unsupported OS images, calculates layer size, fills tags/digests, applies dangling/reference/all visibility rules, counts containers per image, optionally computes shared layer size across selected/all images, sorts by creation time descending, and returns API summaries. `newImageSummary` initializes summary fields with sentinel shared/container values.

State and persistence: reads image store maps/heads, reference store, layer store, and container store. No state is mutated.

Dependencies and integration: used by `docker images` and API list endpoints. It integrates filter parsing, path glob matching for references, rootfs chain accounting, and container image usage counts.

Risks: list output can skip images whose layer disappears between map and get calls. Shared-size calculation can fail on missing shared layers. Reference matching must compare familiar and canonical forms, and invalid glob patterns surface as errors.

Test signals: no direct tests here; daemon image-list tests usually exercise filter and summary behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_prune.go -->
# sources/cloud-native/moby/daemon/images/image_prune.go

Purpose: removes unused images and reports reclaimed space for the legacy image store.

Important APIs and control flow: `ImagePrune` uses an atomic guard to reject concurrent prune operations, validates filters, chooses dangling heads or all images, filters intermediary images, `until`, and labels, then deletes refs or dangling IDs through `ImageDelete` with `PruneChildren`. It records delete responses, computes reclaimed space from deleted layer chain IDs, logs cancellation details, and emits a prune event. `matchLabels` handles positive and negative label filters. `getUntilFromPruneFilters` parses one `until` value.

State and persistence: mutates image, reference, and layer state through `ImageDelete`; reads layer sizes; writes events. The `pruneRunning` atomic flag is transient process state.

Dependencies and integration: integrates filters, timestamp parsing, image delete semantics, layer store maps, daemon events, and conflict/error classification.

Risks: cancellation stops additional deletes but still reports already reclaimed data. `imageDeleteFailed` suppresses conflicts and cancellation/deadline errors as prune misses rather than hard failures. Reclaimed space is estimated from layer records captured before deletion.

Test signals: no direct tests here; prune API and image delete tests are the main coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_pull.go -->
# sources/cloud-native/moby/daemon/images/image_pull.go

Purpose: implements legacy-store image pull, progress streaming, and content lease preservation.

Important APIs and control flow: `PullImage` accepts at most one platform, delegates to `pullImageWithReference`, records metrics, and emits a warning for the special single-arch platform mismatch case. `pullImageWithReference` creates buffered progress channels, starts a progress writer goroutine, adds the containerd namespace, creates a temporary lease with `tempLease`, wraps the content store and image config store so committed digests get leased to the final image, builds a distribution pull config, and calls `distribution.Pull`. `tempLease` reuses an existing lease or creates an expiring temporary lease.

State and persistence: writes image configs, references, layers/content, distribution metadata, final image content leases, temporary leases, progress output, metrics, and image events through distribution callbacks.

Dependencies and integration: integrates containerd namespaces/leases/content, Moby distribution pull, progress formatting, registry auth/meta headers, and image-store lease wrappers from `store.go`.

Risks: temporary lease deletion failures are deferred and ignored by callers. Progress writing runs concurrently and cancels the pull context when output fails. Only one platform is supported. The platform mismatch warning relies on `GetImage`'s special non-nil-image plus NotFound behavior.

Test signals: store lease behavior is covered by `store_test.go`; pull integration tests cover registry behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_push.go -->
# sources/cloud-native/moby/daemon/images/image_push.go

Purpose: implements legacy-store image push with progress streaming and optional platform validation.

Important APIs and control flow: `PushImage` rejects multiple platforms, validates the requested platform by resolving the local image when provided, starts a buffered progress writer goroutine, constructs a distribution push config with schema2 config media type, layer providers from the layer store, upload manager, registry/auth metadata, and calls `distribution.Push`. It waits for progress output and records push metrics.

State and persistence: reads image, reference, distribution metadata, and layer stores; writes progress, registry upload state, metrics, and image events through callbacks.

Dependencies and integration: used by API push paths and depends on Moby distribution push, upload concurrency manager, registry resolver, and progress utilities.

Risks: only one platform is supported. Progress output cancellation can cancel the push context. Platform validation depends on legacy image-store platform semantics.

Test signals: no direct tests here; push integration tests cover registry upload behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_squash.go -->
# sources/cloud-native/moby/daemon/images/image_squash.go

Purpose: creates a new squashed image by replacing the diff between an image and optional parent with a single layer.

Important APIs and control flow: `SquashImage` loads target and optional parent images, obtains the target root layer, streams the diff from the parent chain with `TarStreamFrom`, registers a new layer over the parent chain, copies and rewrites the image rootfs/history, marks intervening history entries as empty layers, appends a squash history entry, marshals the new config, and creates a new image.

State and persistence: reads existing images and layers, writes a new layer and image record. It does not delete or retag the original images.

Dependencies and integration: uses internal image/layer stores and is exposed through the daemon image-service interface for legacy squash support.

Risks: mutating history/rootfs correctness depends on parent ancestry matching the target. The new image is untagged unless a later caller tags it. Layer references must be released after streaming/registering.

Test signals: no direct tests in this subset; squash integration tests are the likely coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_squash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_tag.go -->
# sources/cloud-native/moby/daemon/images/image_tag.go

Purpose: adds or updates a repository tag for an image.

Important APIs and control flow: `TagImage` calls `referenceStore.AddTag` with force enabled, updates the image's last-updated time, and logs a tag event with the familiar tag name.

State and persistence: writes reference store mappings and image metadata; emits an event.

Dependencies and integration: used by import, load, build export, and API tag flows. It depends on distribution references and image-store timestamp support.

Risks: if `SetLastUpdated` fails after the tag is added, the reference mutation remains but the call returns an error. Forced tag replacement can move existing tags.

Test signals: no direct tests here; tag API tests and import/load/build tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_tag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_unix.go -->
# sources/cloud-native/moby/daemon/images/image_unix.go

Purpose: provides Unix implementation of container layer size reporting for the image service.

Important APIs and control flow: `GetLayerFolders` panics because it is Windows-specific. `GetContainerLayerSize` gets the container RW layer, logs and returns zeroes if unavailable, gets RW diff size, returns `-1` for RW size on driver errors, adds parent size when present, and releases the RW layer.

State and persistence: reads graphdriver/layer-store size metadata and releases a layer reference; no state is written.

Dependencies and integration: used by container inspect size reporting on Linux/FreeBSD. Depends on layer-store RW layer APIs and containerd logging.

Risks: errors getting the RW layer are intentionally logged but not returned, preserving historical API behavior. The function returns `-1` for RW size on size errors, which callers must interpret correctly.

Test signals: container inspect tests exercise size paths indirectly; this file has no direct unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_windows.go -->
# sources/cloud-native/moby/daemon/images/image_windows.go

Purpose: provides Windows-specific layer-folder inspection support for image-mounted containers, with a placeholder size implementation.

Important APIs and control flow: `GetContainerLayerSize` currently returns zeros with a TODO. `GetLayerFolders` iterates image rootfs diff IDs, mutates `img.RootFS.DiffIDs` to each prefix, validates OS support, resolves each layer path from the layer store, reverses parent order, then appends the RW layer metadata `dir`.

State and persistence: reads layer paths and RW layer metadata. It mutates the passed image object's `RootFS.DiffIDs` slice while computing paths.

Dependencies and integration: used by Windows container inspect/mount reporting and depends on internal image OS validation plus `layer.GetLayerPath`.

Risks: the in-place `RootFS.DiffIDs` mutation is explicitly marked with a FIXME and can surprise callers if they reuse the image object. Size reporting is not implemented on Windows.

Test signals: no direct tests in this subset; Windows-specific daemon tests would be needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/images_test.go -->
# sources/cloud-native/moby/daemon/images/images_test.go

Purpose: unit tests for platform matching fallback behavior.

Important APIs and control flow: `TestOnlyPlatformWithFallback` constructs an ARM v8 platform and asserts that the matcher accepts the same OS/architecture with no variant, accepts the exact variant, and rejects a different architecture.

State and persistence: no state.

Dependencies and integration: uses OCI platform structs and `gotest.tools` assertions. It validates the matcher used by `GetImage`, pull, and BuildKit local image resolution.

Risks: the test covers only one architecture family and does not assert OS mismatch or different non-empty variants. It still captures the main config-without-variant compatibility rule.

Test signals: direct coverage for `OnlyPlatformWithFallback`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/images_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/imagespec.go -->
# sources/cloud-native/moby/daemon/images/imagespec.go

Purpose: converts Docker container config fields into Docker OCI image config shape for image inspect responses.

Important APIs and control flow: `containerConfigToDockerOCIImageConfig` copies user, env, entrypoint, cmd, volumes, workdir, labels, stop signal, deprecated `ArgsEscaped`, exposed ports as string keys, healthcheck, onbuild, and shell into `dockerspec.DockerOCIImageConfig`.

State and persistence: no state is read or written beyond the supplied config pointer.

Dependencies and integration: used by `ImageInspect` to fill API config data while preserving Docker-specific extensions.

Risks: nil config returns an empty Docker OCI config. Deprecated fields are intentionally carried for compatibility. Port conversion depends on `nat.Port.String()` formatting from API container config.

Test signals: no direct tests here; image inspect tests validate serialized output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/imagespec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/service.go -->
# sources/cloud-native/moby/daemon/images/service.go

Purpose: constructs and implements the legacy `ImageService` backend around image, layer, reference, distribution, content, lease, event, and container stores.

Important APIs and control flow: `ImageServiceConfig` supplies all dependencies. `NewImageService` creates download/upload managers and wraps the image store with lease deletion. Methods expose distribution services, image counts, children, layer creation from containers or images, layer lookup/status/mount IDs, cleanup, storage driver name, layer release, disk usage, layer reference accounting, and runtime concurrency config updates.

State and persistence: owns pointers to persistent stores and transient managers. It writes layer state through create/release, reads image/layer maps for disk usage, and updates manager concurrency.

Dependencies and integration: central hub for daemon image operations, distribution pull/push, builders, container lifecycle, events, and disk usage. It depends on Moby internal image/layer/refstore and containerd content/leases.

Risks: `ReleaseLayer` type-asserts to `layer.RWLayer`, so alternative RW layer implementations must satisfy that concrete internal interface. `ImageDiskUsage` counts only layers referenced by images that are tagged or childless, matching Docker semantics but not all on-disk data. `UpdateConfig` ignores zero values, so zero cannot be used to set concurrency here.

Test signals: behavior is covered broadly by image, container, and daemon tests rather than a single service test.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/store.go -->
# sources/cloud-native/moby/daemon/images/store.go

Purpose: adds content lease management around legacy image and content stores used during pulls and deletes.

Important APIs and control flow: `imageKey` names per-image leases. `imageStoreWithLease.Delete` deletes the matching lease before deleting the image. `imageStoreForPull.Put/Get` delegates image config storage and then calls `updateLease`. `updateLease` creates or reuses a lease named for the image config digest and adds every ingested content digest as a content resource. `contentStoreForPull` tracks committed digests from content writers, including already-existing content. `contentWriter.Commit` records digests on successful or already-existing commits.

State and persistence: mutates containerd leases and content store data, and delegates image config store mutations. It keeps an in-memory per-pull digest list protected by a mutex.

Dependencies and integration: used by `image_pull.go` and `NewImageService`. It integrates containerd leases/content, namespaces, distribution image config stores, and legacy image deletion.

Risks: lease naming is tied to image config digest, so config-digest identity must remain stable. `imageStoreWithLease.Delete` uses `context.TODO` with a stored namespace because the image store interface lacks context. Content writer `AlreadyExists` handling depends on descriptor options being present.

Test signals: `store_test.go` covers lease deletion and digest tracking for successful and already-existing content writes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/store_test.go -->
# sources/cloud-native/moby/daemon/images/store_test.go

Purpose: unit tests for legacy image-store lease wrappers and pull content-store digest tracking.

Important APIs and control flow: `setupTestStores` creates temporary image, content, metadata, and lease stores under a namespace. `TestImageDelete` verifies image delete succeeds without a lease and removes an existing image lease. `TestContentStoreForPull` verifies a committed content writer records its digest and that attempting to write already-existing content also records the digest.

State and persistence: creates temporary filesystem stores and a Bolt metadata DB, then removes them in cleanup. It mutates real local content and lease metadata.

Dependencies and integration: uses containerd local content, metadata DB/lease manager, Moby image FS store, namespaces, bbolt, and `gotest.tools`.

Risks: the temporary directory is created with `os.MkdirTemp("", t.Name())`, so failures before cleanup can leave OS temp state. Tests check core lease behavior but not `imageStoreForPull.updateLease` resource addition end to end.

Test signals: direct coverage for the lease deletion contract and pull digest accounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/info.go -->
# sources/cloud-native/moby/daemon/info.go

Purpose: builds daemon `/info` and `/version` responses from host, daemon, storage, registry, runtime, and configuration state.

Important APIs and control flow: `SystemInfo` gathers raw sysinfo, config, image counts, host/kernel/OS/memory values, registry config, proxy config with masked credentials, NRI/CDI/device info, and then delegates to fill helpers for containers, debug, containerd, API warnings, platform info, driver info, plugins, security options, licensing, address pools, firewall, and devices. `SystemVersion` builds engine component details and delegates platform component population. Utility functions handle tracing, module version caching, host/kernel/memory/OS lookup, env fallback, nil-slice promotion, and device driver enumeration.

State and persistence: reads many daemon fields and host files/proc data; does not mutate daemon state except metrics timers and logs. `moduleVersion` is cached with `sync.OnceValue`.

Dependencies and integration: central to API system endpoints and integrates config, metrics, tracing, registry, platform, sysinfo, logger plugins, SELinux/seccomp/userns/rootless state, containerd, libnetwork, and device drivers.

Risks: most helper errors are logged and suppressed by design, while context cancellation/deadline is intended to propagate through platform helpers. API security warnings depend on normalized daemon hosts. Device driver enumeration can append warnings but should not fail the whole info response.

Test signals: no direct tests in this file; platform parser helpers are tested in `info_unix_test.go`, and system API integration tests cover assembled responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_unix.go -->
# sources/cloud-native/moby/daemon/info_unix.go

Purpose: supplies Unix-specific system info/version details for cgroups, runtimes, rootless mode, storage warnings, and component versions.

Important APIs and control flow: `fillPlatformInfo` fills cgroup driver/version/capabilities, runtimes and statuses, default runtime, runc/containerd/init commits, warnings for unsupported resource controls, rootless warnings, and platform-specific fields. `fillPlatformVersion` appends containerd, runc, init, and rootlesskit/slirp4netns/vpnkit version components when available. Helpers parse init/runtime version output, query rootlesskit, determine security options, rootless/no-new-privileges/cgroup namespace state, populate containerd/runc/init versions, and expose OCI runtime features in runtime status.

State and persistence: reads daemon config, sysinfo, runtime binaries, containerd version RPCs, rootlesskit API, and OS files. It does not persist data.

Dependencies and integration: selected by `!windows` build tags. Integrates system API responses with runc options, rootlesskit client, daemon runtimes config, containerd client, and rootless helper packages.

Risks: external binary `--version` output parsing is format-sensitive, though parser tests cover common cases. Context cancellation must be propagated from containerd/init calls while other discovery errors are logged and ignored. Warning text is user-visible and therefore compatibility-sensitive.

Test signals: `info_unix_test.go` covers `parseInitVersion` and `parseRuntimeVersion`; broader system info tests cover assembled fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_unix_test.go -->
# sources/cloud-native/moby/daemon/info_unix_test.go

Purpose: Unix-only parser tests for extracting version and commit details from init and OCI runtime command output.

Important APIs and control flow: `TestParseInitVersion` checks `tini version` forms with optional git commits and invalid strings. `TestParseRuntimeVersion` checks runc and crun style outputs, commit-only output, and invalid strings.

State and persistence: no state; table-driven pure parser tests.

Dependencies and integration: uses `gotest.tools` assertions and is guarded by `!windows`. It protects helpers used by `fillPlatformInfo` and `fillPlatformVersion`.

Risks: tests cover known output formats, not every runtime implementation. Assertions accept any error text for invalid cases, so exact diagnostics can change.

Test signals: direct coverage for version parsing edge cases that feed system API component details.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_windows.go -->
# sources/cloud-native/moby/daemon/info_windows.go

Purpose: provides Windows stubs for platform-specific info helpers that are Unix-specific elsewhere.

Important APIs and control flow: `fillPlatformInfo` and `fillPlatformVersion` return nil without adding fields. `fillDriverWarnings` is empty. `cgroupNamespacesEnabled`, `Rootless`, and `noNewPrivileges` all return false.

State and persistence: no state is read or written.

Dependencies and integration: selected on Windows to satisfy shared system info code without Unix cgroup/rootless/runtime behavior.

Risks: Windows system info lacks the Unix fields populated in `info_unix.go`, so callers must treat platform-specific fields as optional.

Test signals: compile-time coverage on Windows; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/initlayer/setup_unix.go -->
# sources/cloud-native/moby/daemon/initlayer/setup_unix.go

Purpose: populates the init layer used as a top readonly layer for containers on Linux/FreeBSD.

Important APIs and control flow: `Setup(initLayerFs, uid, gid)` iterates required container mountpoint paths, unlinks any existing path components inside the init layer, creates missing parent directories, creates required directories/files with ownership, and creates `/etc/mtab` as a symlink to `/proc/mounts`.

State and persistence: mutates the init layer filesystem tree by creating directories, files, symlinks, and ownership. It removes stale path entries before recreation.

Dependencies and integration: used during layer initialization for containers and depends on `moby/sys/user` chown helpers plus `unix.Unlink`.

Risks: it unlinks path prefixes under the init layer, so correct path joining is critical. File creation uses mode `0755` for placeholder files. `f.Chown` and `f.Close` errors are not fully checked in sequence.

Test signals: no direct tests here; container creation and rootfs setup integration tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/initlayer/setup_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/inspect.go -->
# sources/cloud-native/moby/daemon/inspect.go

Purpose: implements container and exec inspect responses.

Important APIs and control flow: `ContainerInspect` resolves the container, builds base inspect data, and optionally adds size information outside the container lock. `containerInspect` locks the container, calls `getInspectData`, and fills graphdriver metadata for non-snapshotter containers, tolerating missing metadata for dead containers. `getInspectData` copies host config, legacy links, ulimits, health state, ports, endpoint settings, mount points, image manifest descriptor, and either snapshotter storage or graphdriver name. `ContainerExecInspect` returns exec process state, process config, IO flags, pid, and removal state.

State and persistence: reads container state, host config, network settings, link index, RW layer metadata, image service layer sizes, and exec store. It does not mutate persisted state.

Dependencies and integration: backs API inspect endpoints and integrates daemon container store, config, network endpoint settings, storage driver metadata, snapshotter mode, and exec command store.

Risks: shallow copying host config plus selective deep copies requires care to avoid races. Size calculation is intentionally outside the lock. Missing RW layers are fatal for live non-snapshotter containers but tolerated for dead containers.

Test signals: `inspect_test.go` covers basic `getInspectData` success and dead-container RW-layer tolerance/error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/inspect_test.go -->
# sources/cloud-native/moby/daemon/inspect_test.go

Purpose: unit tests for minimal container inspect data construction and missing RW-layer handling.

Important APIs and control flow: `TestGetInspectData` constructs a minimal container and daemon link index/config store, then verifies `getInspectData` does not error. `TestContainerInspect` skips snapshotter mode, verifies a live container without `RWLayer` errors, then marks it dead and verifies the missing layer is tolerated.

State and persistence: creates in-memory daemon/container structs only.

Dependencies and integration: uses daemon container/network structs, config store, exec store, and `gotest.tools` assertions. It validates behavior in `containerInspect`.

Risks: tests do not exercise network endpoint copying, graphdriver metadata success, size paths, or exec inspect. Snapshotter mode is skipped for the RW-layer expectations.

Test signals: direct coverage for critical missing-RW-layer branch behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/containerimage/pull.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/adapters/containerimage/pull.go

Purpose: implements a BuildKit image source backed by Moby's legacy image/layer stores and containerd content store.

Important APIs and control flow: `Source` exposes the Docker image scheme, parses image identifiers and attributes, resolves local refs from Moby ref/image stores, resolves remote configs with BuildKit/containerd resolver flightcontrol, and creates `puller` source instances. `puller.CacheKey` prefers local config or manifest digest keys and falls back to remote resolution. `Snapshot` reuses local image layers via BuildKit cache refs when possible; otherwise it creates a temporary lease, fetches manifests/configs/layers with containerd handlers, streams download/extract progress, downloads layers through Moby's layer download manager, gets cache refs by diff IDs, leases non-layer content to the ref, and sets optional usage record types. `layerDescriptor` adapts remote descriptors to Moby layer download descriptors. Helpers handle progress status, cache keys from config chain IDs, platform matching, and source policy mutation.

State and persistence: reads Moby image/reference/layer stores, writes containerd content blobs, metadata V2 layer digest mappings, BuildKit cache refs, temporary leases, and possibly triggers garbage collection. It keeps in-memory singleflight/flightcontrol state for resolution.

Dependencies and integration: bridges BuildKit source, solver, cache, sessions, source policies, containerd remotes/content/images/leases, Moby distribution download manager, V2 metadata, and legacy image/layer stores.

Risks: this is lifecycle-heavy code: progress goroutines, temporary leases, cache refs, release callbacks, and background GC must stay ordered. Schema1 manifests are rejected. Local platform matching uses Docker's variant fallback, while remote resolution uses OCI platform filtering. The legacy store cannot represent multi-arch tags well, so cache keys and local reuse must be conservative.

Test signals: no direct tests in this subset. The attempted local `go test` could not run because `go` is not installed in the workspace environment. BuildKit build/pull integration tests are the expected coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/containerimage/pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/localinlinecache/inlinecache.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/adapters/localinlinecache/inlinecache.go

Purpose: lets BuildKit import inline cache metadata from locally stored legacy images before falling back to registry cache import.

Important APIs and control flow: `ResolveCacheImporterFunc` wraps the registry importer and first calls `tryImportLocal` for `attrs["ref"]`. `tryImportLocal` resolves a local reference through the refstore and image store and returns raw image JSON. `localImporter.Resolve` parses inline cache into BuildKit cache manager storage. `importInlineCache` decodes image config, parses `moby.buildkit.cache.v0`, builds descriptors for each diff ID with created/description annotations from non-empty history entries, and calls `v1.ParseConfig`. `parseCreatedLayerInfo` aligns history metadata to non-empty rootfs layers.

State and persistence: reads local image/ref store data only. It constructs in-memory cache manager data for BuildKit; registry fallback may read remote state.

Dependencies and integration: integrates BuildKit remote cache APIs, registry cache importers, session manager, containerd content interfaces, and Moby image/ref stores.

Risks: `parseCreatedLayerInfo` assumes history non-empty entries align with rootfs diff IDs; malformed configs could produce length mismatches later in `importInlineCache`. The local descriptor provider cannot read layer blobs, so it is only suitable for metadata reconstruction.

Test signals: no direct tests here; inline-cache build tests should cover local-vs-registry import behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/localinlinecache/inlinecache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/layer.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/layer.go

Purpose: converts graphdriver snapshots into registered Moby layers for BuildKit cache use.

Important APIs and control flow: `GetDiffIDs` returns existing layer diff chains when a key already maps to a layer. `EnsureLayer` serializes conversion per key, returns existing diff IDs when present, rejects active snapshots, recursively ensures the parent layer, computes diffID and size for the graphdriver ID into a temporary tar-split path, registers the graph ID as a layer with parent chain ID, records the chain ID in Bolt, caches the layer ref, and returns the full diff chain. `getDiffChain` walks parents recursively. `getGraphID` extracts graphdriver cache IDs from layers that expose `CacheID`.

State and persistence: reads/writes snapshot Bolt metadata, temporary tar-split files, layer-store registrations, and in-memory layer refs.

Dependencies and integration: used by the graphdriver BuildKit snapshotter and exporter/differ paths. Depends on layer store graph ID registration and checksum calculation extensions.

Risks: parent chain ID is assigned from a goroutine while another goroutine computes checksum; errors are coordinated by errgroup, but shared variables rely on completion before use. Active snapshots cannot be converted. Correct tar-split cleanup depends on temp directory removal.

Test signals: no direct tests in this subset; BuildKit graphdriver cache/export tests cover conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/leasemanager.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/leasemanager.go

Purpose: wraps a containerd lease manager to tie BuildKit snapshot lease resources to the custom graphdriver snapshotter lifecycle.

Important APIs and control flow: `sLM` delegates create/list/resource operations to the underlying lease manager while tracking `snapshots/default` resources in `byLease` and `bySnapshot` maps. `Delete` removes all tracked refs for a lease after deleting the underlying lease. `AddResource`/`DeleteResource` update tracking. `addRef` optionally loads the snapshot layer and records chain metadata. `delRef` removes reverse refs and removes snapshots when no leases remain.

State and persistence: mutates underlying lease metadata, in-memory ref maps, snapshotter refs, and snapshot Bolt metadata.

Dependencies and integration: created by `NewSnapshotter` and wrapped with a namespace via BuildKit lease utilities. It controls when graphdriver snapshots can be cleaned up.

Risks: the map handling in `addRef`/`delRef` is delicate because lease and snapshot reverse maps must stay symmetric. Silent warnings on failed snapshot removal can leave graphdriver data. This code is central to preventing premature layer removal and storage leaks.

Test signals: no direct tests in this subset; lease lifecycle is covered indirectly through BuildKit cache prune and build cleanup tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/leasemanager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/snapshot.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/snapshot.go

Purpose: implements a BuildKit snapshotter over Moby's graphdriver and layer store for the legacy image-store builder path.

Important APIs and control flow: `NewSnapshotter` opens `snapshots.db`, requires a layer store that can register graph IDs, initializes lease refs, and returns a namespaced lease manager. `Prepare` creates graphdriver active snapshots and records original parent. `getLayer` maps chain IDs or committed snapshot keys to layer refs and caches them. `Stat`, `Mounts`, `Commit`, `View`, `Usage`, and `Close` implement snapshotter behavior, with `Remove` forbidden externally and internal `remove` used by the lease manager. `mountable` memoizes mounts with ref counting and identity mapping.

State and persistence: persists snapshot metadata in Bolt buckets, creates/removes graphdriver layers, caches layer refs, creates temporary RW layers for committed layer mounts, and reads/writes cached usage sizes.

Dependencies and integration: used by `newGraphDriverController`, BuildKit cache manager, Moby graphdriver/layer store, and lease manager. It bridges containerd snapshot APIs to Docker graphdriver semantics.

Risks: external `Remove` is forbidden, so cleanup must flow through lease tracking. Bolt bucket names are raw snapshot keys and chain IDs. Mount release functions must be called by consumers or RW layers/graphdriver mounts can leak. The custom snapshotter has partial implementations such as no-op `Walk` and `Update` delegating to `Stat`.

Test signals: no direct tests in this subset; BuildKit graphdriver mode integration tests are the main coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/builder.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/builder.go

Purpose: exposes a Docker build backend implemented on top of an embedded BuildKit controller.

Important APIs and control flow: `New` creates a request-body handler and controller. `DiskUsage` singleflights BuildKit disk usage and maps records to Docker API cache records. `Prune` validates Docker filters, converts them to BuildKit prune info, streams usage records, and returns reclaimed size and cache IDs. `Build` translates Docker build options into BuildKit frontend attrs, handles upload-request synchronization, cache-from, build args, labels, no-cache, pull mode, platform parsing, network mode, extra hosts, shm size, ulimits, exporters, inline cache, entitlements, solve request, status streaming, aux trace messages, and final image ID emission. Helpers implement gRPC stream proxies, upload rendezvous, extra-host conversion, ulimit conversion, and prune filter conversion.

State and persistence: holds build jobs and cancel functions in memory, streams request bodies through an internal HTTP handler, and relies on the controller for persistent cache/export state.

Dependencies and integration: integrates Docker API build options, BuildKit control API, BuildKit sessions/status/progress, Moby exporters, network options, daemon DNS host-gateway config, and cache prune filters.

Risks: build upload rendezvous has short timeouts and requires matching upload/build IDs. Only one output is supported. Filter conversion accepts a narrow set and maps `id` to regex matching. Status streaming uses a background request with `context.TODO`, so solve cancellation and status cancellation are intentionally decoupled.

Test signals: no direct tests in this subset; builder API and BuildKit integration suites cover behavior. Local `go test` could not be run because `go` is unavailable.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/controller.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/controller.go

Purpose: constructs the embedded BuildKit controller for either containerd snapshotter mode or legacy graphdriver mode.

Important APIs and control flow: `newController` dispatches by `UseSnapshotter`. `newSnapshotterController` creates history and cache stores, a containerd worker with normalized platforms, GC policy, registry hosts, labels, executor/proxy provider, frontends, cache import/export functions, entitlements, content store, lease manager, tracing, and GC callback. `newGraphDriverController` creates local content/metadata stores, custom graphdriver snapshotter and lease manager, cache manager, image source, executor, Moby exporter, cache/history stores, GC policy, worker, frontends, inline/local cache support, and disables BuildKit merge/diff caps for the legacy backend. Helper functions open history DBs, parse GC policy size strings, convert builder entitlements, add labels, and create CDI managers.

State and persistence: creates and owns BuildKit root directories, Bolt DBs, local content stores, cache metadata, history DBs, snapshot metadata, leases, and worker/controller resources. It cleans up opened resources on constructor errors.

Dependencies and integration: deeply integrates BuildKit control/worker/cache/frontend packages, containerd client/content/metadata, Moby graphdriver/layer/image/reference services, exporters, registry hosts, CDI, tracing, and daemon builder config.

Risks: resource cleanup on partial construction is critical because many DBs, proxy providers, and snapshotters are opened. Graphdriver mode uses a custom compatibility stack and explicitly disables capabilities that require the containerd image store. GC policy parsing depends on unit strings and filter conversion from `builder.go`.

Test signals: no direct tests in this subset; BuildKit controller startup/build/prune tests cover behavior. Local `go test` was unavailable due to missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/executor.go

Purpose: provides shared BuildKit executor networking helpers for Docker's libnetwork bridge integration and DNS config conversion.

Important APIs and control flow: `bridgeProvider.New` locates the Docker bridge network and creates an `lnInterface`. `lnInterface.init` creates an endpoint, sandbox, hosts/resolv paths, and joins the endpoint. `Close` asynchronously deletes the sandbox and network state directory. `DialContext` runs dialing inside the sandbox namespace. `getDNSConfig` and `ipAddresses` convert daemon DNS config into BuildKit OCI DNS config.

State and persistence: creates libnetwork endpoints/sandboxes and temporary network state files under the builder root. Cleanup removes sandbox directories asynchronously.

Dependencies and integration: used by Linux executor creation and BuildKit network providers. It integrates BuildKit network interfaces, Docker libnetwork, daemon DNS config, and resource sampling types.

Risks: asynchronous cleanup logs failures but does not block. `Sample` is stubbed. Network initialization happens in a goroutine and callers wait on `ready`, so error propagation depends on the `err` field.

Test signals: no direct tests in this subset; build networking integration tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_linux.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/executor_linux.go

Purpose: constructs the Linux BuildKit runc executor and network/proxy providers.

Important APIs and control flow: `newExecutor` sets up bridge/host/none network providers, removes stale network state, normalizes empty identity mappings to nil, creates a resource monitor, honors `DOCKER_BUILDKIT_RUNC_COMMAND`, optionally creates a proxy provider with host/filtered egress, and constructs `runcexecutor.New` with cgroup, rootless, DNS, AppArmor, CDI, proxy, and network settings. `newExecutorGD` delegates to `newExecutor`. `loopbackFilteredProvider` blocks proxy egress to loopback addresses. `lnInterface.Set` installs a prestart hook invoking `libnetwork-setkey` through the current executable.

State and persistence: writes executor/proxy/network state under the BuildKit root and deletes old network state on startup. It may own and close a proxy provider on failures.

Dependencies and integration: Linux-only integration between BuildKit runcexecutor, resource monitor, proxy provider, libnetwork bridge provider, daemon identity mappings, CDI, and OCI runtime specs.

Risks: loopback filtering requires DNS resolution and may allow hosts that resolve differently later. Environment-based runc override is a testing escape hatch. Prestart hook correctness depends on libnetwork controller IDs and daemon reexec support.

Test signals: no direct tests in this subset; Linux BuildKit build/network/proxy tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_nolinux.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/executor_nolinux.go

Purpose: provides non-Linux graphdriver executor stubs for BuildKit.

Important APIs and control flow: `stubExecutor.Run` and `Exec` return errors stating the BuildKit executor is not implemented for the current `runtime.GOOS`. `newExecutorGD` returns the stub executor with no proxy provider.

State and persistence: no state is read or written.

Dependencies and integration: selected by `!linux` builds to satisfy graphdriver controller construction paths where native executor support is unavailable.

Risks: any non-Linux graphdriver BuildKit execution path will fail at runtime with the stub error. Containerd snapshotter mode has separate controller behavior and may not use this stub.

Test signals: compile coverage on non-Linux platforms; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_nolinux.go -->
