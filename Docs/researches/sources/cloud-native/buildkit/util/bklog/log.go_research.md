# sources/cloud-native/buildkit/util/bklog/log.go

## Purpose
BuildKit logging bridge. It installs BuildKit/containerd log functions, stores logrus entries in context, and adds OpenTelemetry trace/span IDs when present.

## Important APIs, Types, And Functions
Package: `bklog`. Build tags: `none`. Key declarations observed in the file: `init, WithLogger, GetLogger, TraceLevelOnlyStack`.

## Control Flow, State, And Persistence
init overrides containerd/log globals. WithLogger stores a context value; GetLogger prefers that value, then containerd log, then package default. TraceLevelOnlyStack only calls debug.Stack when trace logging is enabled.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/log, github.com/sirupsen/logrus`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are global logger mutation, context value type assertions, and logging cost at trace level. No local tests.
