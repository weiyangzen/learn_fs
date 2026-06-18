# sources/cloud-native/buildkit/util/appdefaults/appdefaults_unix.go

## Purpose
Unix default paths and user-scoped BuildKit locations. It derives sockets, root/config paths, CNI config, CDI dirs, and trace socket location from XDG or HOME environment variables.

## Important APIs, Types, And Functions
Package: `appdefaults`. Build tags: `!windows`. Key declarations observed in the file: `UserAddress, EnsureUserAddressDir, UserRoot, UserConfigDir, TraceSocketPath`.

## Control Flow, State, And Persistence
UserAddress/UserRoot/UserConfigDir parse colon-separated XDG paths and fall back to system defaults. EnsureUserAddressDir creates buildkit under XDG_RUNTIME_DIR with 0700 sticky permissions using os.OpenRoot.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are environment-dependent paths and permission errors. Platform build tags split Linux, non-Linux Unix, and Windows defaults; no local tests.
