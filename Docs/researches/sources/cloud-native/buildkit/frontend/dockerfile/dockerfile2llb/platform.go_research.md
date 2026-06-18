# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/platform.go

Purpose: computes build/target platform defaults and injects automatic platform build args.

Important APIs: `platformOpt`, `buildPlatformOpt`, and `defaultArgs`.

Control flow: if target is set but build platforms are absent, build platforms default to the target. If build platforms are absent entirely, default spec is used. If target is absent, target becomes the first build platform and `implicitTarget` is true. `defaultArgs` creates `BUILD*`, `TARGET*`, and `TARGETSTAGE` env entries, applying build arg overrides.

State and persistence: platform opt is in-memory conversion state; default args feed ARG expansion and stage platform resolution.

Dependencies and integration: used early in `convert.go`; depends on containerd platform formatting and LLB env lists.

Risks and test signals: risks include implicit platform behavior, overrides producing inconsistent auto args, and OSVersion/variant formatting. `platform_test.go` covers selection rules.
