## sources/cloud-native/soci-snapshotter/fs/artifact_fetcher.go

Purpose: fetches SOCI artifacts from local store or remote registry and stores/labels them locally.

Important APIs/types/functions: `Fetcher`, `artifactFetcher`, `orasBlobStore`, `newRemoteBlobStore`, `Resolve`, `Fetch`, `FetchRange`, `doInitialFetch`, `newArtifactFetcher`, `FetchSociArtifacts`, and helper error redaction.

Control flow: remote blob store resolves descriptors with registry blob headers and supports ranged GETs. `artifactFetcher.Fetch` tries local store first, resolves size when descriptor size is zero, then fetches remote. `FetchSociArtifacts` fetches and decodes an index, opens a store batch, stores and GC-labels index if remote, then concurrently fetches/stores each zTOC and labels GC refs.

State and persistence: writes artifacts to local SOCI/content store and applies GC labels; reads remote registry content.

Dependencies and integration: ORAS remote/content APIs, containerd reference/docker localhost handling, SOCI store/index encoding, fs remote URL helpers, internal HTTP redaction.

Risks and test signals: `GetContentWithRange` returns an error wrapping a possibly nil `err` for bad status. Concurrent blob fetch labels depend on stable loop index capture. Tests cover ref construction, local-vs-remote fetching, size resolve, store digest errors, remote store plain HTTP, and corrupted artifact failures.
