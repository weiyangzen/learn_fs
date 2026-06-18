# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/procfs/procfs.go

## Purpose
Discovers local BeeGFS client mounts and parses `/proc/fs/beegfs*` client state, including config, management/meta/storage node connection info, filesystem UUID, and mountpoint mapping from `/proc/mounts`.

## Important APIs, Types, And Functions
Exports `GetBeeGFSClientsConfig`, `Client`, `Node`, `Peer`, `MountPoint`, `ErrEstablishingConnections`, and `GetBeeGFSClients`. Internal parsing helpers include `parseClient`, `parseClientFsUUIDFile`, `parseClientConfigFile`, `parseClientNodesFile`, `parseNodes`, `getBeeGFSMounts`, and `parseMounts`.

## Control Flow
`GetBeeGFSClients` parses BeeGFS mounts from `/proc/mounts`, optionally runs `df -t beegfs` to force client/server connections, walks `/proc/fs/<fstype>` directories, parses each client directory, and filters by FS UUID and/or mount paths. `parseClient` reads config and node files, derives client ID from directory name, associates mountpoint using `cfgFile`, and reads `fs_uuid`. `parseNodes` incrementally parses node headers, root markers, and semicolon-separated connection lines.

## State And Persistence
No local persistence. It reads kernel procfs state and may trigger connection establishment through `df`. Returned structs are snapshots.

## Dependencies And Integration Points
Used by `node/ping` and BeeRemote startup validation. Depends on Linux `/proc/mounts`, `/proc/fs/beegfs*`, external `df`, zap-compatible logger, and common BeeGFS NIC aliases/types.

## Risks And Edge Cases
Errors while walking procfs or parsing individual clients are logged and ignored, which favors partial discovery over hard failure. `parseNodes` assumes a node header was seen before `Root:` or `Connections:`; malformed files could panic on nil `current`. It handles only aliases compatible with `fmt.Sscanf("%s [ID: %d]")`. Mount parsing rejects BeeGFS mounts without `cfgFile`. `ForceConnections` shells out to `df`, so environment/path and command behavior matter.

## Test Signals
`procfs_test.go` covers config parsing, node parsing, and mount parsing with representative successful inputs. Gaps include malformed node files, missing `cfgFile`, filesystem UUID filtering, procfs walk error handling, and `ForceConnections` failure.
