# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/ping.go

## Purpose
Pings management, metadata, and storage nodes through a BeeGFS client mount using the BeeGFS ping-node ioctl. It resolves an eligible local mount and streams per-node ping results and per-node errors.

## Important APIs, Types, And Functions
Exports `PingConfig`, `PingResult`, `PingError`, and `PingNodes`. The core work is a goroutine inside `PingNodes` that resolves target nodes and runs worker goroutines invoking `ioctl.PingNode`.

## Control Flow
`PingNodes` gets the management FS UUID, scans local BeeGFS client mounts via `procfs.GetBeeGFSClients`, filters by optional mountpoint and UUID, chooses the first equivalent mount, and loads the node store. The returned goroutine builds `toPing` from explicit IDs or all eligible nodes, chooses worker count based on `Parallel`, sorts nodes by type and numeric ID, sends them to workers, and closes result/error channels after workers finish.

## State And Persistence
No durable state. It emits transient ping timings and counters. It uses channel buffering of one for results and errors, and worker count from global Viper config when parallel.

## Dependencies And Integration Points
Integrates management gRPC (`GetFsUUID`), local `/proc/fs/beegfs` parsing, node store, BeeGFS ioctl ping, Viper global config, and zap logging.

## Risks And Edge Cases
If an ioctl error occurs in a worker, that worker sends an error and returns, leaving remaining queued nodes for other workers only; with a single worker, later nodes are skipped. Error channel buffer is one, so if multiple workers send errors before a caller drains, workers can block. The function treats the first matching client as equivalent, relying on earlier UUID filtering.

## Test Signals
No direct tests. Coverage should include mount discovery failure, explicit missing node IDs, sorted scheduling, parallel worker error behavior, and conversion of null-padded ioctl strings.
