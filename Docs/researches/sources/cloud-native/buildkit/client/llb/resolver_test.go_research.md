# sources/cloud-native/buildkit/client/llb/resolver_test.go

Purpose: tests image metadata resolver integration with image states.

Important APIs/types/functions: `TestImageMetaResolver`, `TestImageResolveDigest`, and fake `testResolver.ResolveImageConfig`.

Control flow: fake resolver returns config JSON with a working directory and digest. First test verifies resolver laziness before marshal, platform propagation from marshal constraints, source identifier without digest rewrite, and state directory from image config. Second test enables `ResolveDigest(true)` and verifies source identifier includes the resolved digest.

State and persistence: fake resolver records called/platform fields in memory.

Dependencies/integration points: `Image`, `WithMetaResolver`, `ResolveDigest`, `WithImageConfig`, source resolver opts, platform formatting.

Risks/test signals: catches resolver platform propagation and digest pinning regressions. Fake config omits broader image config fields, so env/user behavior is not covered here.
