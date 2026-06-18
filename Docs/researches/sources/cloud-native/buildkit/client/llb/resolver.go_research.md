# sources/cloud-native/buildkit/client/llb/resolver.go

Purpose: defines image metadata resolver options for LLB image sources.

Important APIs/types/functions: `WithMetaResolver` attaches an `ImageMetaResolver` to `ImageInfo`. `ResolveDigest` controls whether resolver output should rewrite image refs to digest-pinned refs. `WithLayerLimit` and `WithImageChecksum` set image source attrs. `ImageMetaResolver` aliases `sourceresolver.ImageMetaResolver`.

Control flow: these are option setters consumed by `Image` in `source.go`; actual resolution happens asynchronously during state marshal/value lookup.

State and persistence: options mutate per-image `ImageInfo` during state construction; no persistence here.

Dependencies/integration points: `source.go` image construction, sourceresolver interfaces, digest attrs, and image meta resolver implementations.

Risks/test signals: option combinations affect source identity and cache safety. `resolver_test.go` covers metadata resolver invocation and digest-pinning behavior.
