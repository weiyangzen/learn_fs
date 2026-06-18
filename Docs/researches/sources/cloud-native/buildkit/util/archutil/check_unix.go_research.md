# sources/cloud-native/buildkit/util/archutil/check_unix.go

## Purpose
Unix probe executor for archutil. It gunzips an embedded static probe binary into a temp chroot and runs /check to determine whether binfmt can execute it.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!windows`. Key declarations observed in the file: `withChroot, check`.

## Control Flow, State, And Persistence
check creates a temp directory, writes executable probe bytes, sets SysProcAttr.Chroot, runs /check, and special-cases amd64 exit code 65/66 for v1/v2. State is temporary filesystem only.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are requiring chroot/binfmt permissions and interpreting amd64 variants only up to v2 in this probe path. No direct unit test.
