## sources/cloud-native/soci-snapshotter/benchmark/stargz_utils.go

Purpose: benchmark utilities for launching/stopping stargz snapshotter and pulling images through it.

Important APIs/types/functions: `StargzProcess` stores command/socket/root/log file handles. `StartStargz` starts the binary and waits for socket creation. `StopProcess` kills the command, removes socket/root, and unmounts snapshots. `StargzRpullImageFromRegistry` pulls with `WithPullSnapshotter("stargz")`.

Control flow: mirrors SOCI process startup: create output dir and logs, start command, poll socket for up to 15 seconds, then return process metadata.

State and persistence: writes snapshotter stdout/stderr files and manages the stargz root directory and Unix socket.

Dependencies and integration: containerd client, snapshotter pull options, benchmark framework resolver, and OS mount cleanup.

Risks and test signals: fixed startup wait, ignored kill/unmount errors, and possible leaks on partial startup failure. No direct tests here.
