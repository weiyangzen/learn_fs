# sources/cloud-native/stargz-snapshotter/fusemanager/fusemanager.go

## Purpose
Provides the fusemanager executable entrypoints and process supervisor helpers. It can run the server in the foreground, self-spawn a detached manager process, and start the manager from another process.

## Important APIs, Types, And Functions
`Run` is the public entrypoint. `parseFlags` defines version, action, socket, fusestore, log level, and log path flags. `startNew` self-invokes the executable in the background. `waitUntilReady` polls status once through the global `address`. `runFuseManager` hosts the Unix socket gRPC server. `StartFuseManager` launches a separate fusemanager binary if the socket is absent.

## Control Flow
`run` handles version printing and dispatches `-action start` to self-spawn; otherwise it runs the server. The server removes stale socket files, listens on Unix socket, registers `Server`, serves in a goroutine, waits for SIGINT/SIGTERM or serve error, stops gRPC, and closes the fuse manager. `StartFuseManager` checks socket and executable paths, invokes the binary with `-action start`, and waits for it to finish.

## State And Persistence
State comes from package-level flag variables and process state. Persistent mount state is configured through `fusestore-path` and managed in `service.go`/`fusestore.go`.

## Dependencies And Integration
Depends on grpc, logrus, Unix signals, process execution, version metadata, and the generated protobuf server registration. It is the operational boundary for running fuse manager outside the main daemon.

## Risks And Test Signals
Risks include stale sockets, file descriptor/log file handling, `waitUntilReady` doing only one status call, global flag state in tests, and subprocess lifecycle ambiguity. Unit tests in this subset focus on the gRPC behavior rather than CLI process behavior.
