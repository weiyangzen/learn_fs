## sources/cloud-native/buildkit/session/sshforward/ssh.go

Purpose: exposes a local Unix socket inside a build that forwards each accepted connection to an SSH agent service registered on a BuildKit session.

Important APIs/types/functions: `DefaultID` is `"default"` and `KeySSHID` is the gRPC metadata key selecting an agent. `SocketOpt` carries ID, UID, GID, and mode for the mounted socket. `MountSSHSocket` creates a temporary directory, listens on `ssh_auth_sock`, applies ownership and permissions, starts an accept loop, and returns path plus cleanup closure. `CheckSSHID` asks the session provider whether an ID is configured.

Control flow: `server.run` uses an errgroup with one goroutine waiting for context cancellation and another accepting listener connections. For each accepted connection it creates an SSH client on `session.Caller.Conn()`, wraps the caller context, adds metadata for the selected id, opens `ForwardAgent`, and runs `Copy` in its own goroutine.

State and persistence: state is a temporary filesystem socket and listener. The cleanup closure closes the listener and removes the socket path; the parent temp directory is removed only on setup error, not in the closer, which may leave an empty temp directory.

Dependencies and integration points: integrates with session `Caller`, generated SSH gRPC stubs, and metadata. This is consumed by executor mount plumbing for `RUN --mount=type=ssh`.

Risks and test signals: accept loop returns errors such as listener close; the caller ignores `s.run` errors because it runs in a goroutine. Per-connection `Copy` errors are also intentionally detached. Socket ownership/mode failures abort setup. Provider tests validate the backing gRPC service path.
