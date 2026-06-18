# Research: subset-b-000210

Grouped code research for the nydus-snapshotter auth, backend, cache, cgroup, and converter files in this work item. Each section preserves its source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/cri.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/cri.go

Purpose: implements a CRI-backed registry credential provider that captures image pull credentials by installing a proxy ImageService in front of the real CRI image service. It is used as one provider in the registry keychain path.

Important APIs and functions: `DefaultImageServiceAddress` defaults to `/run/containerd/containerd.sock`; package global `credentials []resolver.Credential` stores credential lookup callbacks returned by stargz-snapshotter's CRI keychain; `CRIProvider` implements `AuthProvider` with `String` and `GetCredentials`; `newCRIConn` builds an insecure gRPC client over containerd's dialer with containerd default message sizes and a short max backoff; `AddImageProxy` registers a CRI ImageService proxy on the supplied gRPC server and appends the CRI credential resolver to the global list.

Control flow: `GetCredentials` rejects missing parsers and empty refs, parses the image reference via `parseReference`, then calls each captured CRI credential resolver with `(host, refSpec)`. The first non-empty username or secret is returned as `PassKeyChain`; otherwise the provider reports no credentials for the host. `AddImageProxy` chooses either the configured image service address or the default socket, creates `cri.NewCRIKeychain`, registers its ImageService server into the snapshotter RPC server, and stores the returned resolver callback for later credential reads.

State and persistence: credentials are in-memory only and package-global. There is no persistence and no synchronization around appending or iterating `credentials`; the file comments note it should be embedded in `CRIProvider` and made concurrency safe.

Dependencies and integration points: integrates with containerd CRI over gRPC, containerd dialer defaults, Kubernetes CRI API types, and `github.com/containerd/stargz-snapshotter/service/keychain/cri`. It depends on `parseReference` from `provider.go` and returns `PassKeyChain` from `keychain.go`.

Risks: the global slice can race if `AddImageProxy` and credential lookup run concurrently. Because CRI is pull-time credential capture, restarts lose captured credentials and renewal intentionally excludes CRI. A resolver returning an error aborts the whole provider chain for CRI instead of trying later captured resolvers.

Test signals: `cri_test.go` exercises the no-proxy case, proxy registration, credential capture through `PullImage`, ref mismatches, alternate registries, and digest refs.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/cri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/cri_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/cri_test.go

Purpose: validates that the CRI provider can capture credentials from proxied CRI `PullImage` requests and later return them by image reference.

Important APIs and functions: `MockImageService` implements `runtime.ImageServiceServer` enough to accept `PullImage`; `TestFromImagePull` sets up a downstream mock CRI Unix socket, a proxy CRI Unix socket through `AddImageProxy`, then uses a CRI client to perform image pulls with `runtime.AuthConfig`.

Control flow: the test first asserts `NewCRIProvider().GetCredentials` fails before any proxy is registered. It then starts a mock real ImageService, starts the proxy server registered by `AddImageProxy`, checks that no credentials exist before pulling, sends `PullImage` calls with username/password auth, and checks that later lookups return the captured credentials for matching refs and fail for a wrong tag. It repeats for another registry and a digest-pinned image.

State and persistence: the test exercises the package-global `credentials` slice and the stargz CRI keychain's in-memory capture store. Temporary Unix sockets are under `t.TempDir`; gRPC servers are stopped with defers.

Dependencies and integration points: uses real gRPC servers over Unix sockets, containerd's dialer, Kubernetes CRI API types, and the production `AddImageProxy` path. This is closer to an integration test than a pure unit test.

Risks and gaps: the package global `credentials` is not reset by the test, so test order or repeated runs in the same process can retain state. The test does not run concurrent calls and does not check malformed refs, proxy downstream failure propagation, or resolver error behavior.

Test signals: verifies tag refs, digest refs, multiple registries, empty-before-pull behavior, and wrong-tag miss behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/cri_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/docker.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/docker.go

Purpose: implements a Docker config credential provider that reads credentials from Docker CLI `config.json`, including credential-helper-backed configs through Docker's configfile API.

Important APIs and functions: constants `dockerHost` and `convertedDockerHost` map containerd's Docker Hub host `registry-1.docker.io` back to Docker config's `https://index.docker.io/v1/` key. `DockerProvider` stores a `*configfile.ConfigFile`; `NewDockerProvider` loads the default config from `DOCKER_CONFIG`/home; `CanRenew` marks this provider renewable; `GetCredentials` parses image refs and returns username/password from the loaded config.

Control flow: `GetCredentials` validates request/ref, parses host with `parseReference`, rewrites Docker Hub host when needed, calls `ConfigFile.GetAuthConfig`, rejects incomplete username/password pairs, and returns `PassKeyChain`.

State and persistence: provider state is a loaded Docker config object. The provider does not reload the file for each `GetCredentials`, but renewal creates providers through `renewableProviders`, so new provider instances can reread Docker config on renewal.

Dependencies and integration points: uses Docker CLI config packages and `parseReference`. It participates in the provider order after labels and CRI, and before kubelet/kubesecret through `buildProviders`.

Risks: token-only or helper returns that do not populate both username and password are treated as incomplete. Errors are returned for absence instead of silent nil, which is expected by the provider-chain aggregator but can produce noisy logs. The provider's loaded config can become stale if reused for long periods outside renewal reconstruction.

Test signals: `docker_test.go` verifies empty refs, invalid refs, Docker Hub host conversion, and an arbitrary registry from a synthetic Docker config.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/docker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/docker_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/docker_test.go

Purpose: tests Docker config credential lookup with a temporary `DOCKER_CONFIG` directory.

Important APIs and functions: `setupDockerConfig` writes a `config.json` with base64 `auth` entries for Docker Hub and an extra registry, while saving/restoring the old `DOCKER_CONFIG`. `TestDockerCred` instantiates `NewDockerProvider` and calls `GetCredentials`.

Control flow: the test writes config, asserts empty ref and unparsable `foo` fail, checks Docker Hub lookup through the converted host `registry-1.docker.io/foo:bar`, and checks direct lookup for `reg.docker.alibaba-cloud.com/foo:bar`.

State and persistence: modifies process environment and writes a temp Docker config. Cleanup removes the temp directory and restores the original env var.

Dependencies and integration points: exercises Docker CLI config loading and the production `parseReference` host normalization.

Risks and gaps: no test covers credential helpers, partial username/password records, missing config files, token-only auth, or provider renewal. The environment mutation means tests should avoid parallel execution with other Docker-config-dependent tests.

Test signals: confirms base64 auth decoding through Docker configfile and Docker Hub key compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/docker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/keychain.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/keychain.go

Purpose: defines the basic username/password credential object and orchestrates the ordered registry credential provider chain used by the snapshotter.

Important APIs and functions: `PassKeyChain` holds `Username` and `Password`; `FromBase64` and `ToBase64` encode/decode Docker-style `username:password`; `TokenBase` treats an empty username with non-empty password as a registry token; `renewableProviders` builds the renewal-only provider list; `buildProviders` builds the normal provider list; `GetRegistryKeyChain`, `getRegistryKeyChainFromProviders`, `fetchFromProviders`, `GetKeyChainByRef`, `Resolve`, and `toAuthConfig` expose keychain lookup and go-containerregistry integration.

Control flow: normal lookup checks the global `renewalStore` first. On a miss, it sets `AuthRequest.ValidUntil` to the next renewal tick when renewal is enabled, then iterates providers in priority order: labels, CRI, Docker, kubelet if initialized, and Kubernetes secrets. The first non-nil keychain wins. Renewable providers that return credentials are cached into the renewal store. Errors from failed providers are collected and joined for one warning if no provider succeeds.

State and persistence: provider constructors and `renewalStore` are package-level variables so tests can replace them. Credentials are in-memory only; no file persistence is done here. `PassKeyChain.Resolve` converts to go-containerregistry `authn.Authenticator`.

Dependencies and integration points: integrates with snapshot labels, CRI provider, Docker config, kubelet credential provider plugins, Kubernetes secrets, go-containerregistry authn, and metrics/renewal through `renewal.go`.

Risks: `FromBase64` uses `strings.Split` and therefore rejects passwords containing additional `:` characters; `SplitN` would be more Docker-compatible. Global provider builders and renewal store need careful test restoration. Provider errors are warning-only when no provider succeeds, which avoids hard failing unauthenticated pulls but can mask misconfiguration.

Test signals: label tests cover base64 round trip; renewal tests cover provider ordering, renewable caching, cached lookup, and non-renewable exclusion.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/keychain.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/kubelet.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/kubelet.go

Purpose: implements Kubernetes kubelet credential provider plugin support for registry auth. It reads kubelet credential provider config, executes matching plugin binaries, caches plugin responses according to kubelet cache key semantics, and returns the best matching auth for an image.

Important APIs and functions: `InitKubeletProvider` initializes global `kubeletProvider`; `NewKubeletProvider` loads YAML/JSON config and validates providers; `validateCredentialProvider` enforces name, API version, match images, cache duration, and env constraints; `KubeletProvider.GetCredentials` is the main provider method; helper functions include `evictExpired`, `getCachedCredential`, `bestKeychainMatch`, `computeCacheKey`, `parseRegistry`, `resolveCacheDuration`, `isImageAllowed`, `execPlugin`, and Kubernetes-ported `urlsMatch` helpers.

Control flow: initialization requires non-empty config path and plugin bin dir, reads `CredentialProviderConfig`, rejects empty or duplicate provider definitions, and stores pointers to config providers. Credential lookup parses/normalizes the ref, evicts expired cache entries, tries cache lookup in image, registry, then global order, and checks `ValidUntil` so renewal can demand credentials that survive the next interval. On cache miss, every matching plugin is executed serially. Each response's auth map is folded into an all-keychains map where earlier plugins win overlapping auth keys. Positive TTL responses are cached by image/registry/global key. The returned credential is the most specific registry/path glob match.

State and persistence: global `kubeletProvider` is initialized once under `kubeletProviderMu`. Per-provider cache is an in-memory `map[string]*kubeletCredential` guarded by an RW mutex. Plugin execution inherits the process environment plus configured env vars. No disk persistence is used.

Dependencies and integration points: consumes `k8s.io/kubelet/config/v1` and `credentialprovider/v1` types, executes external plugin binaries, uses `sigs.k8s.io/yaml`, and mirrors kubelet matching/cache semantics. It is included in renewable providers only after `InitKubeletProvider` succeeds.

Risks: plugin execution is serial and uses a hard-coded one-minute timeout. `execPlugin` checks API version but not response kind. Cache entries with zero expiry are removed by eviction and are also treated as no-cache. `bestKeychainMatch` uses reverse alphabetical ordering as a specificity proxy; this works for tested path cases but is not a full path-length comparator. Config provider pointers are taken from the unmarshaled slice; because the slice lives in the provider, the pointers remain valid.

Test signals: `kubelet_test.go` thoroughly covers config validation, plugin execution, no-match/no-auth behavior, provider precedence, path specificity, global initialization, URL glob matching, cache eviction, `ValidUntil`, TTL behavior, cache key types, and registry parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/kubelet.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/kubelet_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/kubelet_test.go

Purpose: unit and integration-style tests for kubelet credential provider plugin loading, validation, matching, execution, and caching.

Important APIs and functions: helpers create temporary plugin binaries and kubelet credential provider config YAML: `setupKubeletProvider`, `buildAuthSection`, `createMockPlugin*`, `createMockCredentialProvider*`, `createMockProviderConfig`, and `setupMockProvider`. Tests cover `NewKubeletProvider`, `validateCredentialProvider`, `GetCredentials`, `InitKubeletProvider`, `urlsMatchStr`, cache eviction, `ValidUntil`, TTL behavior, `computeCacheKey`, and `parseRegistry`.

Control flow: mock plugins are shell scripts that consume stdin and emit a JSON `CredentialProviderResponse`. Tests create configs with match patterns, execute provider calls against image refs, then often remove plugin binaries to prove whether later calls hit cache or re-execute.

State and persistence: uses temp directories for plugin binaries/configs and mutates global `kubeletProvider`, restoring it in relevant tests. Cache behavior is observed through provider calls and direct `provider.cache` inspection in eviction tests.

Dependencies and integration points: exercises real process execution via `exec.CommandContext`, kubelet API structs, YAML marshal/unmarshal, and production URL matching/cache code.

Risks and gaps: shell-script mock plugins make tests Unix-like; there is no Windows equivalent in this file. Tests do not cover plugin timeout, stderr propagation in detail, malformed JSON responses, response kind validation, or concurrent cache access under plugin load.

Test signals: strong coverage for validation failures, first-plugin-wins overlap semantics, most-specific auth matching, no pointer-loop regression, idempotent global init, invalid URL/glob handling, zero/negative/positive TTL semantics, cache key type behavior, and `ValidUntil` bypass of too-short cached credentials.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/kubelet_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/kubesecret.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/kubesecret.go

Purpose: implements a Kubernetes Secret-backed registry credential provider by watching all `kubernetes.io/dockerconfigjson` secrets and searching their Docker config auth entries by registry host.

Important APIs and functions: package globals `kubeSecretListener` and `configMu`; `KubeSecretProvider` implements `AuthProvider` and `RenewableProvider`; `InitKubeSecretListener` builds a Kubernetes client and starts secret synchronization; `KubeSecretListener.addDockerConfig`, `deleteDockerConfig`, `SyncKubeSecrets`, and `GetCredentialsStore` manage the watched Docker config map.

Control flow: initialization is idempotent under `configMu`, optionally checks the kubeconfig path, loads client config with client-go, builds a clientset, and starts a shared informer. The informer lists/watches all namespaces for Docker config JSON secrets, adding/updating parsed Docker config files by namespace/name key and deleting on secret deletion. `GetCredentials` parses the image host and asks the listener for the first config with complete username/password auth.

State and persistence: all watched secret auth data is held in memory in `dockerConfigs`. `configMu` guards the global listener pointer and the map. The Kubernetes API is the persistent source of truth.

Dependencies and integration points: uses client-go `SharedIndexInformer`, corev1 Secret types, Docker configfile parsing, and `parseReference`. It is included in both normal and renewable provider chains because the informer can observe updates.

Risks: `InitKubeSecretListener` assigns the global listener before all setup succeeds, so a failed config/client/sync path can leave a non-nil but partially initialized listener. The kubeconfig existence log message has inverted wording for `os.IsNotExist`. `DeleteFunc` assumes direct objects and does not handle tombstones. It returns the first matching config from map iteration, which is nondeterministic if multiple secrets match the same host.

Test signals: `kubesecret_test.go` manually adds a Docker config secret object, validates provider lookup, direct store lookup, map insertion, deletion, and nil after deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/kubesecret.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/kubesecret_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/kubesecret_test.go

Purpose: verifies the in-memory Docker config parsing and lookup behavior used by the Kubernetes secret provider.

Important APIs and functions: `testDockerConfigJSONFmt` builds a Docker config JSON secret payload; `TestGetCredentialsStore` calls `InitKubeSecretListener`, manually invokes `addDockerConfig`, calls `NewKubeSecretProvider().GetCredentials`, calls `GetCredentialsStore`, and then deletes the config.

Control flow: the test tolerates `InitKubeSecretListener(ctx, "")` failure because local hosts may not have kubeconfig, but still expects `kubeSecretListener` to be non-nil. It then inserts a fake `corev1.Secret` with `.dockerconfigjson` data and checks registry auth retrieval.

State and persistence: uses package-global `kubeSecretListener`; inserted config is removed at the end. It does not reset the whole global listener.

Dependencies and integration points: directly exercises Docker configfile parsing and `KubeSecretProvider.GetCredentials` with production reference parsing.

Risks and gaps: because init errors are ignored and the global listener may persist across tests, the test is sensitive to package-level state. It does not exercise the informer, Kubernetes fake client, update/delete event handlers, missing data keys, invalid config JSON, or multiple matching secrets.

Test signals: confirms a valid dockerconfigjson secret can provide username/password and that deletion removes the store entry.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/kubesecret_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/labels.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/labels.go

Purpose: provides the highest-priority auth provider that reads registry credentials directly from snapshot labels.

Important APIs and functions: `LabelsProvider` implements `String` and `GetCredentials`; `NewLabelsProvider` constructs it. It looks for `label.NydusImagePullUsername` and `label.NydusImagePullSecret`.

Control flow: `GetCredentials` rejects nil labels, then requires non-empty username and secret labels. On success it returns a `PassKeyChain`.

State and persistence: stateless; all data is carried in `AuthRequest.Labels`.

Dependencies and integration points: depends on `pkg/label` label constants and is first in `buildProviders`, so explicit pull labels override CRI, Docker config, kubelet plugins, and Kubernetes secrets. It is excluded from renewal because labels are only available during pull/snapshot operations.

Risks: no nil request guard is present; callers currently construct a non-nil `AuthRequest`. It does not support token-only auth and treats missing labels as errors, which are later aggregated by `fetchFromProviders`.

Test signals: `labels_test.go` checks successful lookup, base64 conversion, missing-label errors, and missing-username errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/labels_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/labels_test.go

Purpose: tests label-sourced credentials and base64 encode/decode helpers.

Important APIs and functions: `TestFromLabels` constructs maps using `label.NydusImagePullUsername` and `label.NydusImagePullSecret`, calls `NewLabelsProvider().GetCredentials`, `PassKeyChain.ToBase64`, and `FromBase64`.

Control flow: the test checks a successful label lookup, verifies encoded `mock:mock`, decodes it back, then checks empty labels and secret-only labels return nil credentials with errors.

State and persistence: no external state; pure unit test.

Dependencies and integration points: exercises `pkg/label` constants and `keychain.go` base64 helpers.

Risks and gaps: no coverage for nil `AuthRequest`, nil labels, empty secret, empty username, invalid base64, colon-containing passwords, or token-based keychains.

Test signals: confirms the label provider's normal success path and basic failure behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/labels_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/provider.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/provider.go

Purpose: defines shared provider interfaces, request metadata, renewal capability, and canonical image reference parsing for all auth providers.

Important APIs and functions: `AuthRequest` carries `Ref`, optional `Labels`, and optional `ValidUntil`; `AuthProvider` requires `GetCredentials` and `String`; `RenewableProvider` adds `CanRenew`; `parseReference` returns containerd `reference.Spec` plus distribution host.

Control flow: `parseReference` first normalizes with `distribution.ParseDockerRef`, then parses the normalized string through containerd's `reference.Parse`, extracts the domain with `distribution.Domain`, and rejects missing hosts.

State and persistence: no mutable state; this is interface and helper code.

Dependencies and integration points: all providers use `AuthRequest` and most use `parseReference`. `ValidUntil` is specifically consumed by `KubeletProvider` to bypass cached plugin credentials that expire before the next renewal.

Risks: provider implementations differ on nil-request handling; `LabelsProvider` assumes non-nil. `parseReference` behavior depends on distribution reference normalization, so short refs are canonicalized before host extraction.

Test signals: no dedicated provider test file is listed, but Docker, CRI, kubelet, Kubernetes secret, and renewal tests exercise ref parsing and interface behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/renewal.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/renewal.go

Purpose: implements the in-memory renewable credential cache and functions used by the snapshotter renewal loop.

Important APIs and functions: global `renewalStore`; `InitCredentialStore`; `GetStoredCredential`; `RenewCredential`; `EvictStaleCredentials`; internal `credentialEntry`; internal concurrency-safe `credentialStore` with `Add`, `Get`, `Remove`, and `Entries`.

Control flow: `InitCredentialStore` replaces the global store with a fresh map and interval. `GetStoredCredential` returns nil if disabled/missing. `RenewCredential` calls `fetchFromProviders` using `renewableProviders()` with a request valid until the next interval, increments success/failure metrics, and returns the refreshed keychain. `EvictStaleCredentials` snapshots entries and removes refs not in the supplied live set only if they are older than half the renewal interval.

State and persistence: credentials live only in process memory under an RW mutex. Each entry records ref, keychain pointer, and `renewedAt`. Metrics are updated on add/remove/renew.

Dependencies and integration points: called by auth lookup in `keychain.go` and by higher-level snapshot renewal code outside this subset. Uses `pkg/metrics/data` gauges/counters and containerd logging.

Risks: `RenewCredential` assumes `renewalStore` is non-nil; callers must initialize before use. `Get` returns the stored keychain pointer directly, so callers could mutate cached credentials. Global store replacement is not synchronized with concurrent users. Per-ref metrics labels can grow if many unique refs are cached, though removal deletes labels.

Test signals: `renewal_test.go` covers provider type assertions, store get/add/remove/upsert/entries/concurrency, renew success/failure, stale eviction with grace period, nil store behavior, and provider-chain cache interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/renewal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/renewal_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/auth/renewal_test.go

Purpose: verifies renewable provider contracts, credential store semantics, renewal behavior, stale eviction, and interaction between provider lookup and the renewal store.

Important APIs and functions: test doubles `mockProvider`, `mockNonRenewableProvider`, and `trackingProvider`; tests for `RenewableProvider` type assertions, `credentialStore` methods, `RenewCredential`, `EvictStaleCredentials`, `GetStoredCredential`, and `getRegistryKeyChainFromProviders`.

Control flow: tests swap globals (`renewableProviders`, `renewalStore`) and restore them with defers. Store tests add/remove/inspect entries. Renewal tests substitute a tracking provider and check call counts and nil/non-nil results. Eviction tests use tiny intervals or normal intervals to test grace behavior. Provider-chain tests verify cached hit, renewable storage, non-renewable no-storage, and nil-store behavior.

State and persistence: in-memory only. The concurrency test runs add/get/entries/remove from 100 goroutines against one store to exercise locking.

Dependencies and integration points: imports real providers for type assertions, so changes to provider renewal membership should update this test.

Risks and gaps: tests do not assert Prometheus metric values or `RenewCredential` with nil `renewalStore`. The tracking provider's `nilNext` path is defined but not heavily used. Global mutation means tests must remain careful about parallelization.

Test signals: strong coverage of store locking and expected renewable-vs-nonrenewable caching behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/auth/renewal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/backend/backend.go -->
# sources/cloud-native/nydus-snapshotter/pkg/backend/backend.go

Purpose: defines the blob storage backend abstraction and factory for nydus converter outputs.

Important APIs and functions: backend type constants `oss`, `s3`, and `localfs`; variable `MultipartChunkSize` defaults to 500 MiB; `Backend` interface defines `Push`, `Check`, `Type`, and `Size`; `NewBackend` dispatches to `newOSSBackend`, `newS3Backend`, or `newLocalFSBackend`.

Control flow: callers pass backend type, raw JSON config, and `forcePush`. Unsupported type returns an error. Implementations upload content-store descriptors and can check/size blobs by digest.

State and persistence: this file has only the multipart-size global. Actual persistence is in local filesystem, OSS, or S3 implementations.

Dependencies and integration points: mirrors the `converter.Backend` interface so converter options can use package backend implementations. Integrates with containerd `content.Store`, OCI descriptors, and digest types.

Risks: `MultipartChunkSize` is mutable package-global, which is convenient for tests/tuning but can affect all backend instances. Factory config is untyped raw JSON; validation is deferred to individual implementations.

Test signals: S3 config has a focused test; localfs and OSS behavior are not directly tested in listed files.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/backend/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/backend/localfs.go -->
# sources/cloud-native/nydus-snapshotter/pkg/backend/localfs.go

Purpose: stores nydus blobs as digest-named files in a local directory backend.

Important APIs and functions: `LocalFSBackend` holds `dir` and `forcePush`; `newLocalFSBackend` parses `{"dir": "..."}; `dstPath` maps blob hex to a path; `Push`, `Check`, `Type`, and `Size` implement `Backend`.

Control flow: `Push` skips existing blobs unless `forcePush` is true, creates the backend directory, opens the descriptor from the content store, creates/truncates the destination file named by digest hex, and copies the full content. `Check` stats the expected file and returns errdefs not found for missing paths or directories. `Size` stats the file.

State and persistence: blobs persist as files under the configured directory. There is no metadata aside from file names and sizes.

Dependencies and integration points: uses containerd content readers and `errdefs.ErrNotFound`. It is selected by `NewBackend("localfs", ...)` and can be used by converter pack/merge paths.

Risks: `path.Join` is used rather than `filepath.Join`; with digest hex this is harmless on Unix but less portable. `os.Create` overwrites existing files when `forcePush` is true and does not use atomic rename, so interrupted writes can leave partial blobs. No digest verification is performed after copy.

Test signals: no listed direct tests for localfs backend.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/backend/localfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/backend/oss.go -->
# sources/cloud-native/nydus-snapshotter/pkg/backend/oss.go

Purpose: implements an Alibaba Cloud OSS backend for uploading and checking nydus blobs as objects.

Important APIs and functions: `OSSBackend` stores object prefix, OSS bucket, and force-push flag; `newOSSBackend` parses endpoint/bucket/access keys/object prefix; `splitFileByPartSize` builds multipart chunks; `push` performs one multipart upload; `Push` retries `push`; `Check`, `Type`, and `Size` implement the backend interface.

Control flow: `newOSSBackend` validates endpoint and bucket, creates an OSS client and bucket handle. `push` reads the blob descriptor from the content store, checks if the object already exists, splits it into parts by `MultipartChunkSize`, initiates multipart upload, uploads parts concurrently with `errgroup`, aborts on part failure, then completes the upload with collected parts. `Push` retries with one-, two-, four-, and eight-second backoff until success or final failure. `Size` reads `Content-Length` from object metadata.

State and persistence: remote objects are named `objectPrefix + digest.Hex()`. There is no local persistent state. Multipart uploads are explicitly aborted on part upload errors.

Dependencies and integration points: uses `github.com/aliyun/aliyun-oss-go-sdk/oss`, containerd content store, errdefs not found, and global multipart size. Converter backends can use it for remote blob storage.

Risks: uploaded parts are appended from a channel and not sorted before `CompleteMultipartUpload`; OSS SDK may require ascending part order. `Push` ignores context cancellation during `time.Sleep` and returns the last error when backoff reaches eight seconds. No test covers multipart chunking, part ordering, retry, or metadata size parsing.

Test signals: no listed tests for OSS backend.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/backend/oss.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/backend/s3.go -->
# sources/cloud-native/nydus-snapshotter/pkg/backend/s3.go

Purpose: implements an S3-compatible backend for uploading nydus blobs, including MinIO-style custom endpoints and configurable checksum algorithm.

Important APIs and functions: `S3Backend` stores object prefix, bucket, endpoint, region, credentials, force flag, and checksum algorithm; `S3Config` maps JSON config; `newS3Backend`, `client`, `existObject`, `Push`, `Check`, `Type`, and `Size`.

Control flow: config parsing defaults endpoint to `s3.amazonaws.com`, scheme to `https`, requires bucket and region, defaults checksum to CRC32 unless `checksum_algorithm` is provided, and validates named algorithms against AWS SDK enum values. Each operation builds an S3 client from default AWS config, then overrides endpoint, region, path-style access, and optional static credentials. `Push` checks existence, skips unless forced, opens the content-store reader, and uploads using AWS transfer manager with `MultipartChunkSize`. `Check` and `Size` use `HeadObject`.

State and persistence: remote objects are named `objectPrefix + digest.Hex()`. Client objects are recreated per operation; no local state persists.

Dependencies and integration points: uses AWS SDK v2 config, credentials, S3 client, and transfermanager. Implements the backend interface consumed by converter paths.

Risks: `client()` uses `context.TODO()` and ignores operation context for config loading. A nil `HeadObjectOutput.ContentLength` would panic in `Size`. `existObject` only maps `awshttp.ResponseError` 404 to not found; other SDK not-found shapes may bubble as errors. Client recreation per call is simple but can be inefficient.

Test signals: `s3_test.go` validates successful config parsing, defaults, and checksum algorithm selection for two positive cases; it does not test missing fields, invalid checksum, client behavior, upload, check, or size.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/backend/s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/backend/s3_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/backend/s3_test.go

Purpose: tests S3 backend config parsing and checksum algorithm defaults/overrides.

Important APIs and functions: `Test_newS3Backend` calls `newS3Backend` with JSON configs and compares the resulting `S3Backend` struct using `reflect.DeepEqual`.

Control flow: the first case omits checksum and expects CRC32 with the configured endpoint, scheme, bucket, region, prefix, and credentials. The second sets `"checksum_algorithm": "SHA256"` and expects the AWS SDK SHA256 enum.

State and persistence: no remote S3 calls are made; tests inspect constructed state only.

Dependencies and integration points: imports AWS S3 checksum enum types and validates JSON tags on `S3Config`.

Risks and gaps: no negative cases for missing bucket/region or invalid checksum. No tests for default endpoint/scheme, `forcePush`, client construction, `HeadObject`, transfer manager upload, or object sizing.

Test signals: confirms the main positive config paths and checksum mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/backend/s3_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cache/manager.go -->
# sources/cloud-native/nydus-snapshotter/pkg/cache/manager.go

Purpose: manages disk cache files for nydus fusedev-style blob caching, including usage accounting and blob cache removal.

Important APIs and functions: suffix constants for image disk, layer disk, chunk map, blob metadata, and v2.1 blob data. `Manager` stores `cacheDir`, `period`, and an event channel; `Opt` includes disabled/cache dir/period/database fields; `NewManager`, `CacheDir`, `CacheUsage`, `RemoveBlobCache`, and `ExtractBlobIDFromFilename`.

Control flow: `NewManager` ensures the cache directory exists and returns a manager. `CacheUsage` builds all possible cache file paths for a blob ID, including backward-compatible unsuffixed and suffixed forms, sums `fs.DiskUsage` for existing paths, and ignores missing files. `RemoveBlobCache` removes chunk maps and metadata before data files, skipping missing files. `ExtractBlobIDFromFilename` strips known suffixes in an order that handles `.blob.data.chunk_map` before shorter suffixes.

State and persistence: cache files live in `cacheDir`; manager state is otherwise simple in-memory configuration. `eventCh`, `period`, `Disabled`, and `Database` are not used in this file, suggesting broader manager behavior is elsewhere or planned.

Dependencies and integration points: integrates with containerd snapshot usage accounting, continuity `fs.DiskUsage`, containerd logging, and cache file names produced by nydusd.

Risks: `RemoveBlobCache` is not atomic and may leave partial state if one removal fails after earlier files are removed. It uses `path.Join`, which assumes Unix-like paths. Cache usage can double-count if alternate legacy/current names are hard links or aliases. Directory traversal is not relevant if blob IDs are trusted digest hex, but arbitrary input would be joined directly.

Test signals: `manager_test.go` tests suffix stripping for many filename forms; usage and deletion are not tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cache/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cache/manager_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/cache/manager_test.go

Purpose: verifies blob ID extraction from cache filenames with known nydus cache suffixes.

Important APIs and functions: `TestExtractBlobIDFromFilename` table-tests `ExtractBlobIDFromFilename`.

Control flow: cases cover plain blob IDs, each known suffix, combined `.blob.data.chunk_map`, real SHA-256-like names, empty input, unknown suffixes, names with unrelated dots, and suffix precedence.

State and persistence: pure function test with no filesystem state.

Dependencies and integration points: uses testify assertions only.

Risks and gaps: no tests cover `NewManager`, `CacheUsage`, or `RemoveBlobCache`, so filesystem behavior, missing-file handling, and deletion order are unverified in this subset.

Test signals: good coverage of filename parsing edge cases and suffix ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cache/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cgroup/cgroup.go -->
# sources/cloud-native/nydus-snapshotter/pkg/cgroup/cgroup.go

Purpose: provides shared cgroup configuration, support detection, mode display, and version-specific factory logic for placing daemon processes in memory-limited cgroups.

Important APIs and functions: `defaultSlice` is `system.slice`; `ErrCgroupNotSupported`; `Config` with `MemoryLimitInBytes`; `DaemonCgroup` interface with `Delete` and `AddProc`; `createCgroup`, `supported`, and `displayMode`.

Control flow: `createCgroup` checks `cgroups.Mode()` and uses v2 implementation for unified mode, otherwise v1 implementation. `supported` rejects only unavailable mode. `displayMode` maps containerd cgroups mode enum to strings.

State and persistence: no mutable state here; actual cgroups are managed by v1/v2 packages under system cgroup filesystem.

Dependencies and integration points: wraps `github.com/containerd/cgroups/v3` and local `pkg/cgroup/v1`/`v2` packages. Used by `manager.go` to create a process manager.

Risks: hybrid mode falls through to v1, which is probably intentional but worth noting. Memory limit semantics differ between v1 and v2; config has only one field. The default slice is hard-coded.

Test signals: no listed tests directly cover cgroup mode selection or display.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cgroup/cgroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cgroup/manager.go -->
# sources/cloud-native/nydus-snapshotter/pkg/cgroup/manager.go

Purpose: exposes a small manager object around a version-specific daemon cgroup.

Important APIs and functions: `Manager` stores name/config/cgroup; `Opt` carries name and config; `NewManager`, `AddProc`, and `Delete`.

Control flow: `NewManager` checks support, logs cgroup mode, creates a v1 or v2 cgroup through `createCgroup`, and returns a manager. `AddProc` and `Delete` forward to the underlying `DaemonCgroup`.

State and persistence: manager holds the created cgroup handle in memory; cgroup state persists in the kernel cgroup filesystem until deleted.

Dependencies and integration points: uses containerd logging and version-specific cgroup packages. Intended callers add daemon PIDs and clean up on shutdown.

Risks: comments require callers to ensure `*Manager` is non-nil; methods will panic on nil receiver or nil `cgroup`. No recovery path exists if cgroup creation partially succeeds.

Test signals: no listed tests for manager construction or process addition/deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cgroup/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cgroup/v1/v1.go -->
# sources/cloud-native/nydus-snapshotter/pkg/cgroup/v1/v1.go

Purpose: implements memory controller cgroup management for cgroup v1.

Important APIs and functions: `Cgroup` wraps `cgroup1.Cgroup`; `generateHierarchy` selects the memory subsystem; `NewCgroup`, `Delete`, and `AddProc`.

Control flow: `NewCgroup` creates Linux resources with memory limit, tries to load an existing `system.slice/name` cgroup, updates it if it has processes, deletes it if empty, then creates a fresh cgroup. `Delete` skips deletion when processes still exist; otherwise deletes. `AddProc` adds a PID to the memory subsystem.

State and persistence: cgroup state lives under the cgroup v1 hierarchy. The wrapper keeps the controller handle.

Dependencies and integration points: uses containerd cgroup1 API, OCI runtime `LinuxResources`, and logging. Called through the shared cgroup factory in non-unified modes.

Risks: `memoryLimitInBytes` is always assigned as a limit pointer, including negative values; v2 treats `-1` specially but v1 does not. Existing cgroups with running processes are reused and updated, which may affect unrelated processes if names collide. Deleting empty existing cgroups before recreation can race with another creator.

Test signals: no listed v1 tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cgroup/v1/v1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cgroup/v2/v2.go -->
# sources/cloud-native/nydus-snapshotter/pkg/cgroup/v2/v2.go

Purpose: implements memory cgroup management for cgroup v2/unified mode.

Important APIs and functions: `defaultRoot` is `/sys/fs/cgroup`; `ErrRootMemorySubtreeControllerDisabled`; `Cgroup` wraps `*cgroup2.Manager`; `readSubtreeControllers`, `NewCgroup`, `Delete`, and `AddProc`.

Control flow: `NewCgroup` creates resource settings with memory max only when `memoryLimitInBytes > -1`, reads root `cgroup.subtree_control`, requires the memory controller to be enabled, creates a manager at `/<slice>/<name>`, logs controllers, and returns the wrapper. `Delete` and `AddProc` are no-ops if manager is nil; otherwise they call cgroup2 manager methods.

State and persistence: cgroup state persists in cgroup v2 filesystem. The wrapper stores only the manager pointer.

Dependencies and integration points: uses containerd cgroup2 API and `golang.org/x/exp/slices`. Selected by shared factory in unified mode.

Risks: requiring memory in root `cgroup.subtree_control` may fail on systems where delegation is arranged differently. The path is hard-coded under `/sys/fs/cgroup`. If memory limit is exactly `-1`, no max is set; values less than `-1` also skip setting due to `> -1` check.

Test signals: no listed v2 tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/cgroup/v2/v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/constant.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/constant.go

Purpose: centralizes media types and annotations used to identify nydus manifests, blobs, bootstrap layers, cache manifests, and source/target relationships.

Important APIs and constants: manifest constants include `ManifestOSFeatureNydus`, `ManifestConfigNydus`, `ManifestArtifactTypeNydus`, `MediaTypeNydusBlob`, and `BootstrapFileNameInLayer`. Layer annotations include fs version, blob marker, blob digest/size, bootstrap marker, source chain/digest, target digest, encrypted blob marker, reference blob IDs, and uncompressed diff ID label.

Control flow: no executable logic.

State and persistence: constants define OCI descriptor annotations and media types persisted into content store manifests/layers and consumed by runtime/conversion logic.

Dependencies and integration points: used by `convert_unix.go`, `reconvert_unix.go`, cache/runtime code outside this subset, and tests that detect nydus blobs/bootstrap layers.

Risks: these string constants are cross-component contracts; changing them would break existing images and runtime detection. Some constants are not used in this subset but may be part of external compatibility.

Test signals: detection helpers and reconvert tests indirectly validate key blob/bootstrap/uncompressed annotation names.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/constant.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/convert_unix.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/convert_unix.go

Purpose: Unix implementation of OCI-to-nydus conversion, nydus blob unpacking, layer merging, manifest rewriting, and containerd converter hooks.

Important APIs and functions: exported functions include `Pack`, `Merge`, `Unpack`, `UnpackEntry`, `IsNydusBlobAndExists`, `IsNydusBlob`, `IsNydusBootstrap`, `LayerConvertFunc`, `ConvertHookFunc`, and `MergeLayers`. Important helpers include `getBuilder`, `ensureWorkDir`, `unpackOciTar`, `unpackNydusBlob`, `seekFileByTarHeader`, `seekFileByTOC`, `seekFile`, `packFromDirectory`, `packFromTar`, `calcBlobTOCDigest`, `makeBlobDesc`, `convertIndex`, `convertManifest`, and `mergeManifestBlobDigests`.

Control flow: `Pack` detects builder features and chooses tar2rafs streaming when available or directory fallback when not. Directory fallback decompresses/unpacks OCI tar input to a temp source directory, runs `nydus-image create`, and streams the generated blob FIFO to `dest`. Tar streaming wires caller input, nydus-image, and output through FIFOs and an errgroup. `UnpackEntry` reads the custom nydus tar-like blob format through TOC first, then legacy reverse tar-header scanning. `Merge` extracts each layer bootstrap and fs-v6 blob metadata, invokes `nydus-image merge`, assembles final bootstrap/metadata tar content if requested, and returns referenced blob digests from builder output. `LayerConvertFunc` converts regular image layers into nydus blob descriptors, using content-store cache labels to skip repeated conversion and optionally pushing to a backend. `ConvertHookFunc` rewrites indexes/manifests after layer conversion. `convertManifest` merges nydus layers into a bootstrap layer, updates manifest layers, GC labels, config rootfs diff IDs/history, optional referrer subject, and optional merged-manifest config media type. `MergeLayers` writes the final bootstrap tar.gz to the content store and constructs blob/bootstrap descriptors.

State and persistence: temp work dirs are created under configured/env/temp base and removed after conversion. Converted blobs, bootstraps, configs, and manifests are persisted in containerd content store. Optional backends persist blob layers remotely. Content labels cache target digests and uncompressed diff IDs. Package buffer pool reuses 1 MiB buffers.

Dependencies and integration points: deeply integrates with containerd content store and image converter hooks, OCI image-spec descriptors/config/history, nydus-image CLI via `tool`, compression libraries, FIFOs, errgroup, backend interface, and label constants. Unix-only due to FIFOs, local readers, and build tag.

Risks: complex goroutine/pipe/FIFO flows can deadlock if close/error propagation regresses; comments emphasize callers must check `Close` on the returned writer. `seekFileByTarHeader` assumes nydus tar layout from tail to head and needs careful bounds. `MergeLayers` receives original blob digests asynchronously; if `Merge` exits early before sending, read ordering matters. The content proxy and pack/unpack paths rely on external `nydus-image` behavior and feature detection. Several branches are hard to unit test without real content store and builder binaries.

Test signals: listed tests cover `mergeManifestBlobDigests`; reconvert tests cover detection-related helpers; feature tests cover builder feature gating. There are no direct tests for full pack/merge/unpack execution in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/convert_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/convert_windows.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/convert_windows.go

Purpose: Windows build-tag stub for converter APIs.

Important APIs and functions: declares Windows versions of `Pack`, `Merge`, `Unpack`, `IsNydusBlobAndExists`, `IsNydusBlob`, `IsNydusBootstrap`, `LayerConvertFunc`, `ConvertHookFunc`, and `MergeLayers`, all of which panic with `"not implemented"`.

Control flow: every function panics immediately.

State and persistence: none.

Dependencies and integration points: preserves package API shape on Windows builds while avoiding Unix-specific implementation. Imports containerd converter/content and OCI types for signature compatibility.

Risks: any Windows consumer that calls converter functionality will crash at runtime. This is acceptable only if Windows builds do not exercise nydus conversion.

Test signals: no Windows tests are listed.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/convert_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/cs_proxy_unix.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/cs_proxy_unix.go

Purpose: provides a Unix-socket HTTP proxy over a content-store reader so `nydus-image unpack` can stream blob data from an already-packed nydus layer without extracting the data file to disk.

Important APIs and functions: `contentStoreProxy` holds socket path and HTTP server; `setupContentStoreProxy` creates a Unix socket and starts the server; `close` shuts down and removes the socket; `parseRangeHeader` parses byte ranges; `contentProxyHandler` serves HEAD and ranged GET responses from the nydus blob entry or raw reader.

Control flow: setup creates a temp socket path under work dir, removes the temp file, listens on Unix socket, and starts `http.Server` with a handler. The handler initializes by trying to seek `EntryBlob` from the nydus layer; if present, total length is the entry size, otherwise full reader size. HEAD returns content length/type. GET requires a `Range` header after `bytes=`, seeks/skips the internal reader to the requested start, resets when reads move backward, copies the requested length, and sets content headers.

State and persistence: proxy state is in-memory plus a temporary Unix socket file. The handler keeps mutable `dataReader` and `curPos` across requests.

Dependencies and integration points: used by `Unpack` when `UnpackOption.Stream` is true to generate a nydus backend config of type `http-proxy`. It relies on `seekFile` from `convert_unix.go`.

Risks: handler state is not protected for concurrent GET requests, so simultaneous range requests can corrupt `curPos`/reader position. `parseRangeHeader` does not support suffix ranges, open-ended `bytes=start-` fails because empty end is parsed as int, and malformed empty ranges return parse errors. Headers are set after writing body in GET, which can be too late for Go's `net/http` to send them as intended.

Test signals: no direct tests for range parsing or proxy behavior are listed.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/cs_proxy_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/merge_unix_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/merge_unix_test.go

Purpose: tests the digest-list reconciliation logic used when building final nydus manifest layer lists after merging bootstraps.

Important APIs and functions: helper `d` creates synthetic SHA256 digests; `TestMergeManifestBlobDigests` table-tests `mergeManifestBlobDigests`.

Control flow: each case passes `nydusBlobDigests` in OCI layer order and `originalBlobDigests` from nydus-image merge output. Expected results preserve all original nydus layer digests, including metadata-only layers missing from builder output, and append chunk-dict-only blobs not already in the layer list.

State and persistence: pure unit test.

Dependencies and integration points: validates a subtle part of `MergeLayers`/`convertManifest` where manifest layers must preserve OCI order while including extra dictionary blobs.

Risks and gaps: does not test full `MergeLayers` descriptor construction, backend sizing, fs version metadata, encryption annotations, or actual nydus-image merge output parsing.

Test signals: specifically guards reverse conversion correctness for metadata-only layers and chunk-dict images.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/merge_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/reconvert_unix.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/reconvert_unix.go

Purpose: implements nydus-to-OCI reconversion helpers and hooks, including a workaround for containerd diff ID calculation on nydus blobs.

Important APIs and functions: `DefaultIndexConvertFunc`, `collectNydusBlobDigests`, `collectFromManifest`, `wrappedStore.Info`, `ReconvertHookFunc`, `LayerReconvertFunc`, and `makeOCIBlobDesc`.

Control flow: `DefaultIndexConvertFunc` wraps containerd's `IndexConvertFuncWithHook` with `ReconvertHookFunc`; before conversion it scans the input descriptor for nydus blob digests and wraps the content store when needed. `wrappedStore.Info` injects `containerd.io/uncompressed` labels for nydus blobs so containerd skips decompression attempts. `ReconvertHookFunc` runs on converted manifests, removes nydus bootstrap layers and their GC labels, removes the corresponding rootfs diff ID when possible, strips the synthetic "Nydus Bootstrap Layer" history entry, writes updated config JSON, updates config GC labels, and writes the updated manifest. `LayerReconvertFunc` skips non-layers and bootstrap layers, unpacks nydus blobs to tar via `Unpack`, recompresses as gzip/zstd/uncompressed, commits to content store with uncompressed label, builds an OCI descriptor, and optionally pushes to backend.

State and persistence: writes converted OCI blobs, configs, and manifests into the content store. Optional backend push persists converted blobs remotely. The wrapped store mutates returned `content.Info.Labels` maps in memory but does not update the underlying store.

Dependencies and integration points: integrates with containerd image converter hooks, platform matching, content store, OCI descriptors/config, gzip/zstd, and conversion constants. Calls `Unpack` from `convert_unix.go`.

Risks: `ReconvertHookFunc` removes a diff ID only when `bootstrapIndex` is within bounds; mismatched config/layer history may remain inconsistent. `LayerReconvertFunc` computes uncompressed digest while writing through the compressor; for gzip/zstd this digester is attached to the compressed stream writer input before compression, so intent is uncompressed tar digest, but code changes here are high-risk. Unsupported compressor values hard fail. Full reconversion depends on external `nydus-image unpack`.

Test signals: `reconvert_unix_test.go` covers scanning nydus blobs, wrapped store label injection, OCI descriptor construction, and hook no-op cases; full layer reconversion is not directly tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/reconvert_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/reconvert_unix_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/reconvert_unix_test.go

Purpose: tests reconversion helper behavior without invoking the external nydus-image binary.

Important APIs and functions: `mockContentStore`, `mockReaderAt`, `TestCollectNydusBlobDigests`, `TestCollectFromManifest`, `TestWrappedStore_Info`, `TestWrappedStore_Info_Error`, `TestMakeOCIBlobDesc`, `TestReconvertHookFunc_NilDescriptor`, and `TestReconvertHookFunc_NonManifestType`.

Control flow: tests build synthetic OCI manifests/indexes in an in-memory content store, scan for nydus blob annotations, verify bootstrap and regular layers are ignored by blob collection, wrap store info calls to inject uncompressed labels for selected digests, build descriptors for compressed target blobs, and ensure the reconvert hook handles nil and non-manifest descriptors.

State and persistence: mock store maps digests to `content.Info` and byte slices. No real content writes or external process execution.

Dependencies and integration points: exercises production JSON reading through `readJSON`, descriptor constants, and reconvert helper logic.

Risks and gaps: the mock store does not implement writer/update paths needed by full `ReconvertHookFunc` manifest rewriting or `LayerReconvertFunc`, so those paths are not covered. No tests for compressor selection, bootstrap removal from a real manifest, config history cleanup, GC label cleanup, or backend pushes.

Test signals: good focused coverage for nydus blob discovery and the content-store info workaround that prevents containerd from decompressing nydus blobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/reconvert_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/tool/builder.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/tool/builder.go

Purpose: wraps the external `nydus-image` CLI for pack, merge, and unpack operations with structured option types and timeout support.

Important APIs and functions: option structs `PackOption`, `MergeOption`, `UnpackOption`; `buildPackArgs`; exported `Pack`, `Merge`, and `Unpack`; helper `packRef`; `isSignalKilled`; internal `outputJSON`.

Control flow: `Pack` delegates to `packRef` for OCI reference mode or builds `nydus-image create` args. It defaults fs version to 6, sets prefetch/whiteout/blob/fs flags, chooses tar-rafs or directory flags based on detected features, adds chunk dict, compressor, alignment, chunk/batch size, encryption, and source path, then runs the command with optional timeout and prefetch patterns on stdin. `Merge` builds `nydus-image merge` args with source bootstraps, blob digests/TOC digests/sizes, chunk dict/parent bootstrap, output JSON, and parses resulting blob IDs into SHA256 digests. `Unpack` builds `nydus-image unpack`, optionally translates a nested backend config file into `--backend-type` and `--backend-config`, or passes a blob path.

State and persistence: external commands read/write paths provided by converter code. `Merge` reads output JSON from disk. Logging goes through logrus logger writers. No in-process persistence.

Dependencies and integration points: used by `convert_unix.go` and `reconvert_unix.go`; depends on `nydus-image` CLI compatibility and feature detection from `feature.go`.

Risks: command argument construction is tightly coupled to nydus-image versions. Timeout detection relies on error text containing `signal: killed`. `Unpack` type-asserts backend config JSON shapes and can panic if `backend` is missing or not a map before the `ok` check on nested access. `Merge` assumes output blob IDs are hex SHA256 strings.

Test signals: no direct builder command tests in listed files; feature tests cover feature-detection inputs that influence `buildPackArgs`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/tool/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/tool/feature.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/tool/feature.go

Purpose: detects which optional `nydus-image create` features are supported by the installed builder and exposes a small feature-set type.

Important APIs and functions: `Feature` and `Features`; constants `FeatureTar2Rafs`, `FeatureBatchSize`, `FeatureEncrypt`, and env var `NYDUS_DISABLE_TAR2RAFS`; set methods `NewFeatures`, `Add`, `Remove`, `Contains`, `Equals`; `GetHelp`; `detectFeature`; `DetectFeatures`.

Control flow: `GetHelp` executes `builder create -h`. `detectFeature` checks exact feature text and, for two-part features like `--type tar-rafs`, accepts help text containing both parts. `DetectFeatures` runs only once process-wide via `sync.Once`, records the required feature set, scans help output, honors `NYDUS_DISABLE_TAR2RAFS`, warns for unsupported features, and returns the detected subset. Later calls with a different required set return an error.

State and persistence: process-global `requiredFeatures`, `detectedFeatures`, `detectFeaturesOnce`, and `disableTar2Rafs`. No disk state.

Dependencies and integration points: called by converter `Pack` before choosing streaming vs directory conversion and optional batch/encryption flags.

Risks: process-wide `sync.Once` means a first call with one builder path/feature set fixes detection for the entire process; using different builders later is unsupported. `disableTar2Rafs` is read at package init and only changed in tests. The two-part detection can produce false positives if help text mentions flag and value separately in unrelated contexts.

Test signals: `feature_test.go` covers set operations, detection across multiple representative help texts, env-based tar2rafs disable, and error on changed required feature sets.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/tool/feature.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/tool/feature_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/tool/feature_test.go

Purpose: tests feature-set operations and builder help parsing for optional nydus-image features.

Important APIs and functions: `TestFeature` covers `Add`, `NewFeatures`, `Remove`, `Contains`, and `Equals`; `TestDetectFeature` checks help-text parsing for tar2rafs, batch-size, encrypt, unsupported old versions, and empty input; `TestDetectFeatures` checks process-wide detection behavior and env-disable handling.

Control flow: tests use hard-coded help text excerpts from multiple nydus-image versions. `TestDetectFeatures` resets package globals and `sync.Once` for isolated cases, then calls `DetectFeatures` with a fake `getHelp` function.

State and persistence: mutates package globals `requiredFeatures`, `detectedFeatures`, `detectFeaturesOnce`, and `disableTar2Rafs`, but only in-process.

Dependencies and integration points: validates logic that gates converter pack behavior without needing an actual `nydus-image` binary.

Risks and gaps: no direct test for `GetHelp` command execution or `buildPackArgs`. Because tests manually reset globals, production behavior with multiple builders/required sets remains intentionally constrained.

Test signals: strong coverage for supported/unsupported feature detection, env-disable semantics, set equality, and changed-required-feature error.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/tool/feature_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/types.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/types.go

Purpose: defines converter option structs, layer/backend abstractions, compression flags, and TOC entry accessors used by pack/merge/unpack code.

Important APIs and types: `Compressor` constants and mask; `ErrNotFound`; `Layer`; converter-local `Backend` interface; `PackOption`, `MergeOption`, `UnpackOption`; `TOCEntry` and methods `GetCompressor`, `GetName`, `GetUncompressedDigest`, `GetCompressedOffset`, `GetCompressedSize`, and `GetUncompressedSize`; `Encrypter` callback type.

Control flow: most types are configuration. `TOCEntry.GetCompressor` decodes compressor bits from flags and errors on unsupported values. `GetName` reads a NUL-terminated 16-byte name. Offset/size/digest methods expose binary TOC fields.

State and persistence: option structs carry work dir, builder path, fs version, chunk dict, prefetch, backend, timeouts, encryption, and merge settings across converter calls. `TOCEntry` maps on-disk nydus blob TOC records.

Dependencies and integration points: used by Unix converter implementation, reconverter, and backend implementations. `PackOption.features` is internal and populated from `tool.DetectFeatures`.

Risks: `PackOption` has a misspelled `BacthSize` comment for `BatchSize`, but field is correct. The converter-local `Backend` duplicates `pkg/backend.Backend`; structural typing keeps it compatible but changes must be mirrored. TOC parsing assumes little-endian 128-byte entries matching nydus-image output.

Test signals: no direct tests for TOC accessors in listed files; conversion code indirectly depends on them for `seekFileByTOC`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/utils.go -->
# sources/cloud-native/nydus-snapshotter/pkg/converter/utils.go

Purpose: provides utility types and functions for tar packaging and content-store JSON read/write operations used by converter hooks.

Important APIs and functions: `File`; `writeCloser` and `newWriteCloser`; `seekReader`; `newSeekReader`; `packToTar`; `readJSON`; and `writeJSON`.

Control flow: `writeCloser.Close` closes the underlying writer once and then runs an action callback, making converter pack writers finish background conversion on close. `seekReader` adapts an `io.ReaderAt` to sequential read/seek operations for tar parsing. `packToTar` streams an `image/` directory and supplied files into tar or tar.gz through an `io.Pipe`. `readJSON` reads descriptor labels and JSON content from a content store. `writeJSON` marshals JSON, computes digest, opens a content writer with a deterministic ref, copies data with labels, closes it, and returns an updated descriptor.

State and persistence: `packToTar` uses goroutine/pipe state only. `writeJSON` persists new JSON blobs into the content store and preserves supplied labels. `writeCloser` tracks close state.

Dependencies and integration points: used throughout manifest/config rewrite paths in `convert_unix.go` and `reconvert_unix.go`.

Risks: `seekReader.Seek` does not support `io.SeekEnd` and does not bounds-check negative positions. `packToTar` uses `filepath.Join` for tar entry names; on Windows this could emit backslashes, though converter Unix paths use it. `writeJSON` does not explicitly handle already-existing content beyond whatever `content.Copy` does.

Test signals: no direct tests in listed files; many converter tests indirectly rely on `readJSON`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/converter/utils.go -->
