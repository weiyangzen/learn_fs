# sources/distributed-fs/ceph-client/fs/smb/server/server.h

## Purpose
Declares ksmbd global server configuration, server state constants, configuration accessors, control work queue entry points, and inline state predicates.

## Important APIs, Types, and Functions
- Server states: `SERVER_STATE_STARTING_UP`, `SERVER_STATE_RUNNING`, `SERVER_STATE_RESETTING`, and `SERVER_STATE_SHUTTING_DOWN`.
- Config string indices: `SERVER_CONF_NETBIOS_NAME`, `SERVER_CONF_SERVER_STRING`, and `SERVER_CONF_WORK_GROUP`.
- `struct ksmbd_server_config` contains global feature flags, state, signing policy, protocol range, TCP/IPC settings, share faked capabilities, domain SID, auth mechanisms, connection/request limits, config strings, durable scavenger task pointer, and bind-interface policy.
- `extern struct ksmbd_server_config server_conf` exposes the global config.
- Setters/getters manage NetBIOS name, server string, and workgroup.
- Inline predicates `ksmbd_server_running()` and `ksmbd_server_configurable()` use `READ_ONCE()` on `server_conf.state`.
- `server_queue_ctrl_init_work()` and `server_queue_ctrl_reset_work()` schedule server control actions.

## Control Flow
Configuration code updates `server_conf` while the server is configurable. Request/transport code can cheaply check `ksmbd_server_running()`. IPC or management code schedules start/reset work through the declared control functions.

## State and Persistence
`server_conf` is process-global kernel module state and is not persistent across module unload. String fields are heap-owned by `server.c`. State reads are lockless snapshots.

## Dependencies and Integration Points
The header includes `smbacl.h` for `struct smb_sid`. It is included by server implementation, IPC/config management, procfs stats, and protocol negotiation code that reads feature flags and protocol bounds.

## Risks and Edge Cases
- Global mutable configuration requires careful synchronization by writers; the header only provides lockless read predicates.
- Consumers that read multiple fields may observe a mixed snapshot during reset.
- `ksmbd_server_configurable()` treats states numerically, so state enum ordering is part of the ABI between header and implementation.

## Test Signals
Compile and run management/config tests that set names/workgroup, start/reset the server, check state predicates during transitions, and verify procfs/sysfs readers behave under concurrent reset.
