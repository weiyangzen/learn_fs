# sources/distributed-fs/moosefs/mfschunkserver/masterconn.c

## Purpose
`masterconn.c` implements the chunkserver's singleton connection to the MooseFS master. It handles nonblocking connect, auth, registration, periodic reports, master-issued chunk operations, replication commands, idle checksum/block queries, reload/reconnect, and graceful unregister.

## Important APIs and control flow
The central `masterconn` struct tracks socket mode, poll position, input/output queues, master address, timeout, version, registration state, connection counter, and auth challenge data. Initialization loads `chunkserverid.mfs`, reads config, connects to the master, and registers main-loop hooks.

On connection, `masterconn_sendregister()` sends version, listen address, timeout, chunkserver id, and disk-space counters. `masterconn_master_ack()` drives registration: it validates master version and metadata id, stores assigned id/meta id, starts `hdd_get_chunks_begin(1)`, sends labels when supported, streams chunk batches with register type 61, and marks complete with type 62. Auth challenge ACKs compute an MD5 response around the configured auth code.

The poll loop assembles framed packets, dispatches handlers for create/delete/version/duplicate/truncate/chunkop/replication/status/checksum commands, drains output packets with `writev`, sends idle NOPs, and closes on timeout or socket errors.

## State, persistence, and dependencies
Persistent identity lives in `chunkserverid.mfs`; metadata-id mismatches against persisted or HDD-discovered ids are fatal. HDD queues feed space, error, damaged, lost, new, changed, and nonexistent reports. Master commands are delegated to `job_*` background work and guarded by `busychunk`; callback packets are dropped if their connection counter is stale.

Dependencies include `hddspacemgr`, `bgjobs`, `busychunks`, `csserv`, `main`, `cfg`, `sockets`, `datapack`, `random`, `md5`, `mfsalloc`, and protocol constants.

## Risks and test signals
Test registration state transitions, metadata mismatch exits, auth-required cases, reconnect on config reload, labels changes, disconnect during chunk listing, stale job callbacks after reconnect, periodic report queues, packet length fuzzing, and graceful unregister timeout.
