# sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_windows.go

Purpose: Windows-specific file descriptor/handle limit placeholder. Important API is `GetNumFDs`.

Control flow: under build tag `windows`, returns `math.MaxInt`.

State and persistence: none.

Dependencies/integration: feeds resource-manager FD limit defaults. The high value avoids Unix-style FD limiting on Windows where the same rlimit mechanism is not available.

Risks: can make FD-derived resource limits effectively unbounded on Windows unless other limits constrain behavior. No direct tests.
