# sources/cloud-native/nydus/contrib/nydusify/pkg/provider/provider_test.go

Purpose: tests provider package defaults for platform parsing, remote construction/auth, source providers/layers, and logging.

Important APIs under test: `ExtractOsArch`, `newDefaultClient`, `DefaultRemoteWithAuth`, `DefaultRemote`, `defaultSourceProvider` methods, `defaultSourceLayer` getters, `DefaultSource`, `defaultLogger.Log`, and `DefaultLogger`.

Control flow and state: tests validate valid/invalid platform strings, TLS client settings, base64 auth parsing and rejection, Docker Hub auth host mapping, source layer ChainID/ParentChainID construction, mismatched layer/diffID errors, parser integration branches for nydus-only and OCI images, and logger closure duration mutation.

Dependencies and integration points: gomonkey patches for parser/remote construction, HTTP transport settings, Docker config credentials, OCI identity ChainID, digest helpers, and nydus utility arch constants.

Risks and test signals: tests avoid real registry pulls/mounts, so `defaultSourceLayer.Mount` is not exercised. Auth parsing splits on `:`, so passwords containing colons are rejected and covered by tests.
