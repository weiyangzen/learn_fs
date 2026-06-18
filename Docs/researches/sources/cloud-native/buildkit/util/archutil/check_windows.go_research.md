# sources/cloud-native/buildkit/util/archutil/check_windows.go

## Purpose
Windows archutil probe stub. Since binfmt is unsupported on Windows, check always returns an explanatory error.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `windows`. Key declarations observed in the file: `check`.

## Control Flow, State, And Persistence
No state or persistence; all foreign-arch probes fail through this function on Windows builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is callers must tolerate warnings/errors rather than cross-exec support. Build tags are the test signal.
