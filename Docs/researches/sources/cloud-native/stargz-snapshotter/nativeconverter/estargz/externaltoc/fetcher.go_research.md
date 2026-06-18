# sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/externaltoc/fetcher.go

Purpose: Provides a remote eStargz decompressor hook that fetches an external TOC blob from a companion TOC image in a registry.
Important APIs/types/functions: `NewRemoteDecompressor`, `fetchTOCBlob`, and `fetchTOCBlobFromManifest`. It uses containerd remote resolvers/fetchers, Docker registry hosts, platform manifest fetching, OCI descriptors, and the shared `getTOCReference` suffix convention.
Control flow: the decompressor lazily constructs a Docker resolver constrained to the expected host, resolves `<image>-esgztoc`, fetches the platform manifest, scans manifest layers for the `containerd.io/snapshot/stargz/layer.digest` annotation that matches the requested layer digest, and returns the fetched TOC bytes.
State and persistence: no local persistence or cache is implemented; each lazy decompressor invocation can resolve and fetch the manifest/blob again.
Dependencies and integration points: pairs directly with `converter.go`'s external TOC image layout and integrates with stargz snapshotter source registry hosts plus containerd remote fetch APIs.
Risks: only supports the hard-coded `-esgztoc` location and default platform manifest lookup. Host mismatch is treated as an error, which is good for safety but limits unusual resolver setups. Missing annotations return a generic `TOC not found`, and manifest caching is noted as a TODO.
Test signals: no direct tests in this subset; integration coverage is implied by external TOC integration tests that pull `--estargz-external-toc` images.
