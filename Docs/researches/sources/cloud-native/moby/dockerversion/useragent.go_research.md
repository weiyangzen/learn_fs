# sources/cloud-native/moby/dockerversion/useragent.go

## Purpose
Builds Docker daemon User-Agent strings, including daemon version metadata and optional upstream client context.

## Important APIs and Types
Defines `WithUpstreamUserAgent`, `DockerUserAgent`, `getDaemonUserAgent`, `getUpstreamUserAgent`, and `escapeStr`. Uses a private context key and `sync.Once` cache for daemon metadata.

## Control Flow, State, and Persistence
`DockerUserAgent` appends optional extra `useragent.VersionInfo` entries to the cached daemon UA, then appends `UpstreamClient(...)` if present in context. `getDaemonUserAgent` includes Docker version, Go runtime, git commit, kernel version when available, OS, and architecture. `escapeStr` escapes comment delimiters and backslashes, preserves tabs, and drops other control bytes.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on build-time variables in `version_lib.go`, `pkg/parsers/kernel`, and `pkg/useragent`. It is used for daemon-originated HTTP requests and preserving upstream caller attribution. Risks include header injection if sanitization regresses, stale cached version data in tests, and dropped kernel version on probe failure. `useragent_test.go` covers metadata, upstream comments, escaping, and control-character removal.
