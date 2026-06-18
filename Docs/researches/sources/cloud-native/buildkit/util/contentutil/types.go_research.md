# sources/cloud-native/buildkit/util/contentutil/types.go

## Purpose
types.go belongs to package contentutil and supports the BuildKit utility/source-policy area represented by its directory. Key declarations: RegisterContentPayloadTypes.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `RegisterContentPayloadTypes`.

## Control Flow, State, And Persistence
Build tags: none. Important dependencies: github.com/containerd/containerd/v2/core/remotes. Control flow is local to the declarations above and holds no persistent state unless noted by its package-level maps, globals, or content/database handles.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/remotes`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks and tests should be interpreted at package level: generated files risk schema drift, platform shims risk build-tag coverage, and utility files rely on adjacent tests or integration paths.
