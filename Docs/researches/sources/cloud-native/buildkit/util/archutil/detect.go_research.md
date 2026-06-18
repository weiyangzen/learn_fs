# sources/cloud-native/buildkit/util/archutil/detect.go

## Purpose
Runtime platform support detector. It reports native platform plus Linux foreign architectures that can execute probe binaries through binfmt/QEMU.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `none`. Key declarations observed in the file: `CacheMaxAge, SupportedPlatforms, WarnIfUnsupported, nativePlatform, linux, amd64vector, printPlatformWarning`.

## Control Flow, State, And Persistence
SupportedPlatforms caches results under a mutex for CacheMaxAge, probes each architecture with arch-specific supported functions, adds amd64 variants and arm v6 aliases, and WarnIfUnsupported logs validation failures without dropping candidates.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/platforms, github.com/moby/buildkit/util/bklog, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale cache, environment-dependent binfmt behavior, and warning text based on error substrings. Tests are mostly build/integration dependent; probe binaries and assembly fixtures are generated inputs.
