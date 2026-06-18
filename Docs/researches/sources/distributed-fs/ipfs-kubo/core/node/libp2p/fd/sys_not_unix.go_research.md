# sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_not_unix.go

Purpose: platform fallback for file descriptor limit detection on systems that are not Linux, Darwin, or Windows. Important API is `GetNumFDs`.

Control flow: under build tag `!linux && !darwin && !windows`, `GetNumFDs` returns `0`.

State and persistence: none.

Dependencies/integration: consumed by resource-manager default limit calculation in `rcmgr_defaults.go`. A return value of zero means the computed `MaxFileDescriptors` default may become zero/half-zero unless config overrides it.

Risks: on unsupported platforms the resource manager cannot infer FD limits and may need explicit config. Test signal is build coverage across platforms rather than unit tests in this repo.
