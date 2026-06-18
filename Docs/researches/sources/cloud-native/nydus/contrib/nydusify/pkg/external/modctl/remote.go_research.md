# sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/remote.go

Purpose: remote-image variant of modctl handling, reading model layer tar contents directly from a registry and producing external backend plus file attribute metadata.

Important APIs/types/functions: `RemoteInterface`, `RemoteHandler`, `FileCrcList`, `FileCrcInfo`, `NewRemoteHandler`, `initRemoteHandler`, `Handle`, `GetModelConfig`, `GetLayers`, `setManifest`, `backend`, `handle`, and `hackFileWrapper`.

Control flow: constructor creates a default remote and initializes the manifest. `Handle` processes manifest layers concurrently with limit 10 and five retries per layer, accumulating file attributes under a mutex. `handle` obtains a `ReadSeekCloser` for a layer, parses tar file offsets, reads optional CRC annotations, applies environment-controlled file mode hacks, and maps files to blob indexes/digests/sizes/chunk sizes. `GetModelConfig` pulls and unmarshals model config.

State and persistence: handler stores manifest and converted blob metadata in memory. It reads remote registry data only; no durable local files are written. `HACK_FILE` and `HACK_MODE` environment variables mutate emitted file modes.

Dependencies and integration points: provider default remotes, CloudNativeAI model spec, snapshotter external backend attributes, tar parsing shared with local modctl, retry helpers, logrus, and OCI annotations.

Risks and test signals: the goroutine loop closes over `idx` and `layer`; modern Go per-iteration semantics reduce risk, but compatibility matters. `io.Copy` result in `setManifest` is not checked. File attribute ordering can vary due to concurrent append.
