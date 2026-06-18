<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/config.go -->
# sources/cloud-native/buildkit/frontend/dockerui/config.go

## Purpose
dockerui client configuration and build-context entrypoints that parse gateway opts, read Dockerfiles, load .dockerignore, expose build args/labels/cache/SBOM settings, and construct local contexts. The file has 576 lines and belongs to package `dockerui`.

## Important APIs, Types, and Functions
Important symbols: `Config`, `Client`, `SBOM`, `Source`, `ContextOpt`, `validateMinCaps`, `NewClient`, `BuildOpts`, `GatewayClient`, `init`, `buildContext`, `ReadEntrypoint`, `MainContext`, `NamedContext`, `IsNoCache`, `DockerIgnorePatterns`, `DefaultMainContext`, `WithInternalName`, `dockerIgnorePatterns`.

## Control Flow
NewClient validates gateway capabilities, snapshots BuildOpts, init parses all frontend options into Config fields, and methods lazily build context state, read Dockerfile/.dockerignore through LLB solves, and expose no-cache/named-context decisions.

## State and Persistence
Client caches BuildOpts, dockerignore bytes/name under a mutex, buildContext through flightcontrol.CachedGroup, parsed config fields in memory, and local session ID overrides. It persists nothing itself; LLB solves and gateway refs carry external state.

## Dependencies and Integration Points
Dependencies: Dockerfile linter rules/config; BuildKit LLB state/options; BuildKit gateway client/result APIs; wrapped error reporting; platform/test filesystem helpers; Docker ignore pattern parsing.
Integrated with gateway/client BuildOpts, LLB source construction, exporter metadata, frontend inputs, named contexts, .dockerignore, and source-date-epoch behavior.

## Risks and Edge Cases
Risks include subtle frontend option compatibility, cache import parsing across old/new APIs, .dockerignore caching races, capability-gated behavior, and errors masked while probing optional Dockerignore files.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerui/build_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/config.go -->
