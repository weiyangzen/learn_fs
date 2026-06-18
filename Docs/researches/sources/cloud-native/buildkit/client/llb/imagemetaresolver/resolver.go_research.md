# sources/cloud-native/buildkit/client/llb/imagemetaresolver/resolver.go

Purpose: default client-side image metadata resolver for LLB image states, resolving image config bytes and digests from registries.

Important APIs/types/functions: `WithDefault` is an image option that attaches `Default()` resolver. `New` creates an `imageMetaResolver` with Docker resolver, BuildKit user-agent, content buffer, cache, locker, and optional default platform. `Default` uses `sync.Once`. `ResolveImageConfig` resolves config via `imageutil.Config`, caches by ref plus platform, and serializes concurrent same-ref resolution with a locker.

Control flow: resolution starts a tracing span, locks by ref, chooses platform from resolver default or request option, checks cache, calls registry image config resolution, stores digest/config, and returns the original ref plus resolved digest/config.

State and persistence: in-memory singleton cache for `Default` and per-resolver cache map. No disk persistence.

Dependencies/integration points: containerd remotes/docker resolver, BuildKit content buffer, imageutil, tracing, version user-agent, `llb.ImageMetaResolver`, and source resolver options.

Risks/test signals: cache key appends `platforms.FormatAll` without separator, which is probably acceptable but worth awareness. Lock is by ref only, so concurrent different-platform resolutions for same ref serialize. Default resolver has process-wide cache. No direct tests in this file; `resolver_test.go` covers the LLB resolver interface with a fake resolver.
