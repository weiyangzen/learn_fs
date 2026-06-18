# sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_unix.go

Purpose: returns the process file descriptor limit on Linux and Darwin. Important API is `GetNumFDs`.

Control flow: under build tag `linux || darwin`, it calls `unix.Getrlimit(unix.RLIMIT_NOFILE, &l)` and returns the current soft limit, or `0` on error.

State and persistence: reads kernel process limits only.

Dependencies/integration: depends on `golang.org/x/sys/unix` and feeds resource-manager default `MaxFileDescriptors` in `rcmgr_defaults.go`.

Risks: returning zero on `Getrlimit` failure may produce overly strict defaults; normal Unix platforms should provide a valid soft limit. No direct tests.
