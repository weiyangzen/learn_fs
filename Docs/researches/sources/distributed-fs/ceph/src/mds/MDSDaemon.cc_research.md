# sources/distributed-fs/ceph/src/mds/MDSDaemon.cc

## Purpose

`MDSDaemon.cc` implements the top-level Ceph MDS daemon process object. It initializes messenger/monitor/auth/logging/admin-socket integration, receives MDS maps, creates and delegates to an `MDSRankDispatcher` when assigned a rank, handles daemon-level commands and signals, manages shutdown/respawn, and wires authenticated client connections to `Session` objects.

## Important Functions And Control Flow

The constructor initializes timers, GSS keytab environment, beacon, messenger/monitor references, manager/log clients, start time, and an empty `MDSMap`. `init` rejects unsupported Windows daemon mode, logs structure sizes, registers beacon and daemon dispatchers, initializes and authenticates `MonClient`, waits for rotating keys, subscribes to `mdsmap`, sets up the admin socket, initializes timer/beacon state, sets messenger identity to rankless MDS, and schedules periodic `tick`.

`set_up_admin_socket` registers daemon and rank-facing commands. `asok_command` handles daemon-local commands (`status`, `lockup`, `exit`, `respawn`, `heap`, `cpu_profiler`) and delegates all other commands to `mds_rank->handle_asok_command` when active. `dump_status` emits cluster FSID, rank identity, wanted/current state, MDS/OSD map epochs, uptime, sysinfo, and endian.

`handle_mds_map` discards old maps, decodes the new map, validates compatibility, determines this daemon's global id, rank, old/new state, and incarnation, marks removed peer addrs down, initializes `MgrClient` when first added to the FS map, handles rankless standby state, creates `MDSRankDispatcher` when assigned a rank, delegates map processing to the rank dispatcher, and notifies the beacon.

`ms_dispatch2` takes `mds_lock`, drops messages during stop/DNE state, handles core messages, then delegates rank messages. `handle_core_message` filters by peer type and handles monitor maps, MDS maps, snap removals, command messages, OSD map notifications, and legacy monitor commands. `handle_command` authorizes tell commands using session `auth_caps.allow_all` and queues accepted commands through the admin socket.

Shutdown paths are `handle_signal`, `suicide`, and `respawn`. `suicide` marks `stopping`, cancels tick, unregisters admin socket, sets beacon wanted state to DNE, unlocks while waiting for beacon ACK, shuts down beacon/manager, then either shuts down rank or timer/monitor/messenger. `respawn` logs recent messages and `execv`s the current executable path.

## State And Persistence Behavior

`MDSDaemon` persists no metadata directly. It owns runtime identity, map, timer, beacon, clients, and rank dispatcher. Its handling of `MDSMap` controls when rank-level persistent subsystems start or stop. `parse_caps` decodes authenticated cap strings and populates `MDSAuthCaps` for connections and sessions.

## Dependencies And Integration Points

The file integrates `Messenger`, `MonClient`, `MgrClient`, `LogClient`, `Beacon`, `MDSMap`, `MDSRankDispatcher`, `Session`, `Server`, `Locker`, snap components, admin socket, auth keyrings, profiler hooks, and Ceph message types. It is the root dispatcher for the daemon and the owner of `mds_lock`.

## Risks And Test Signals

Risks include lock ordering during shutdown/admin commands, invalid rank transitions, accepting malformed caps, dispatching rank messages while rankless, and failing to respawn on removal or blocklist-related paths. Tests should cover startup auth failures, rotating key timeout, admin socket command delegation, MDS map old/new transitions, removal from map, rank assignment, signal shutdown, session replacement on reconnect, tell-command authorization, and message peer-type filtering.
