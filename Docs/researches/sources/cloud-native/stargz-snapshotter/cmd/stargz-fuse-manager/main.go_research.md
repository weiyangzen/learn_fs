# sources/cloud-native/stargz-snapshotter/cmd/stargz-fuse-manager/main.go

Purpose: Entrypoint for the detached FUSE manager process used by the snapshotter daemon.

Important APIs: `init` registers two fusemanager configuration functions, and `main` calls `fusemanager.Run`.

Control flow: The first config function derives filesystem options from the manager config using `fsopts.ConfigFsOpts` and returns `service.WithFilesystemOptions`. The second config function builds keychain configuration, enforces that CRI keychain listen path is separated from the FUSE manager server when needed, optionally creates a dedicated CRI gRPC server/socket, configures credential functions, serves the CRI socket, and returns `service.WithCredsFuncs`.

State and persistence: Removes and binds Unix sockets for CRI keychain when configured. Metadata persistence is delegated to fsopts and bbolt opener from manager context.

Dependencies and integration: Integrates fusemanager, service options, keychainconfig, fsopts, gRPC, and Unix sockets. This mirrors parts of daemon in-process setup for detached manager mode.

Risks: Boolean precedence in the CRI listen-path validation relies on Go `&&` before `||`; it rejects empty listen path when keychain is enabled and any listen path equal to manager address. Socket removal can remove stale paths.

Test signals: No direct tests; behavior is configuration/integration heavy.
