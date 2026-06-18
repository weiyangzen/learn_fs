# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_windows.go

Purpose: supplies Windows named-pipe listener and security descriptor behavior for buildkitd.

Important APIs and flow: `listenFD` rejects fd activation on Windows. `getLocalListener` creates a winio named pipe, defaulting to authenticated users and system read/write access when no descriptor is supplied. `groupToSecurityDescriptor` builds an SDDL string granting administrators and system full access plus read/write access for comma-separated group SIDs resolved by name.

State and dependencies: named-pipe security controls daemon access. Depends on go-winio, Windows-specific blank imports needed by BuildKit, TLS type signatures, and SDDL/SID handling.

Risks and test signals: malformed group names fail daemon startup; overly broad descriptors can expose the daemon. There are no direct tests in this subset for descriptor generation.
