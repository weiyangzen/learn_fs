# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/initialize.go

Purpose: sends the management request that mirrors the BeeGFS root metadata inode.

Important APIs/types/functions: `MirrorRootInode`.

Control flow: obtains the management client and calls `MirrorRootInode` with an empty request.

State and persistence: mutates cluster metadata mirroring state for the root inode.

Dependencies and integration points: uses backend global management client and management protobuf API.

Risks: no local preflight checks; callers must ensure buddy groups and cluster state are appropriate. Errors are returned directly.

Test signals: no direct tests. Mock tests could verify request dispatch and error propagation.
