## sources/cloud-native/moby/daemon/listeners/listeners_windows.go

Purpose: Initializes Windows daemon API listeners for TCP, named pipes, and Unix sockets.

Important APIs: `Init(proto, addr, socketGroup string, tlsConfig *tls.Config)` supports `tcp`, `npipe`, and `unix`. `getSecurityDescriptor(additionalUsersAndGroups []string)` builds an SDDL DACL from default administrator/system permissions plus optional user/group read-write ACEs.

Control flow and state: `socketGroup` is treated as a comma-separated list of additional users/groups. TCP uses `sockets.NewTCPSocket`. Named pipes resolve SIDs and call `winio.ListenPipe` with message mode and 64 KiB buffers. Unix sockets use Windows go-connections support with the additional principals. Unsupported protocols return a Windows-specific error.

Dependencies and integration points: Uses `Microsoft/go-winio`, Docker go-connections sockets, Windows SID lookup, and TLS for TCP.

Risks: Security descriptor construction is access-control sensitive. Any unresolvable extra principal fails listener creation. Named pipe message mode is required for `CloseWrite`, so changing it can break HTTP over npipe semantics.

Test signals: No direct tests in this subset.
