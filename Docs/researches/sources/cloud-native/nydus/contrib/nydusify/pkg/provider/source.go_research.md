# sources/cloud-native/nydus/contrib/nydusify/pkg/provider/source.go

Purpose: provides default source image abstraction for build systems that need manifest, config, and mountable OCI source layers.

Important APIs/types/functions: `SourceLayer`, `SourceProvider`, `defaultSourceProvider`, `defaultSourceLayer`, `Manifest`, `Config`, `Layers`, `Mount`, getters, `ExtractOsArch`, and `DefaultSource`.

Control flow: `DefaultSource` validates `linux/arch`, creates a parser, parses the remote image, rejects Nydus-only or missing OCI images, and returns a provider for the OCI image. `Layers` pairs manifest layers with config diff IDs, computes ChainIDs incrementally, and creates layer objects with mount dirs keyed by ChainID. `Mount` pulls a layer with retry, unpacks targz to the mount dir, and returns an `oci-directory` mount plus cleanup function.

State and persistence: layers unpack into work-dir subdirectories and are removed by the returned cleanup. Provider stores parsed image and remote pointer.

Dependencies and integration points: parser, remote registry pull, OCI identity ChainID, containerd mount type, nydus utils unpack/retry, and buildkit-like source consumers.

Risks and test signals: layer/diffID mismatch is rejected. Mount cleanup depends on caller invoking the returned function. Only Linux amd64/arm64-like supported arches are accepted.
