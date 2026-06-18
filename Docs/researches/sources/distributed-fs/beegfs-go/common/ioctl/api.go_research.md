<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/api.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/api.go

Purpose: idiomatic Go API over BeeGFS client ioctls for config file lookup, entry info, stripe-hint file creation, node ping, file state update, and enhanced entry info.

Important APIs/types/functions: `GetConfigFile`, `TrimEntryInfoNullBytes`, `GetEntryInfo`, `CreateFileWithStripeHints`, `PingNode`, `SetFileState`, and `GetEntryInfoV2`.

Control flow: functions open mount/directories/files, build ABI structs from `beegfs.go`, invoke `syscall.Syscall(SYS_IOCTL, ...)`, convert errno to Go errors, and translate raw fields into `beegfs`/`msg` types. `GetEntryInfoV2` chooses parent directory plus filename for non-directories, trims null bytes, handles partial metadata RPC results, validates RST version, and assembles `msg.GetEntryInfoResponse`.

State and persistence: mutates BeeGFS for file creation and file state changes. Other calls read kernel/client state. No Go-level persistence.

Dependencies and integration points: depends on `common/beegfs`, `common/beemsg/msg`, unsafe pointer syscall rules, and ABI structs/constants from `beegfs.go`. It bridges ioctl entry info to BeeMsg RPC-compatible structures.

Risks: feature flag bit checks use expressions like `arg.FeatureFlags&1>>0 == 1`; operator precedence should be audited for intended bit tests. `GetConfigFile` opens mount but does not close the file descriptor. Unsafe pointer lifetimes require `runtime.KeepAlive` in some functions but not all paths. `GetEntryInfoV2` slices arrays by kernel-provided counts without explicit bounds checks beyond fixed field types.

Test signals: `api_test.go` is build-tagged `beegfs` and covers these APIs against a real mounted BeeGFS filesystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/api.go -->
