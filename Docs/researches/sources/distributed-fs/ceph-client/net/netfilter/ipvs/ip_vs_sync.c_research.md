# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sync.c

## Purpose
Implements IPVS master/backup connection synchronization over multicast UDP. Master threads batch selected IPVS connection state into version 0 or version 1 sync messages; backup threads receive, validate, decode, and create or update local connection entries.

## Important APIs, Types, and Functions
Wire structs include `ip_vs_sync_conn_v0`, `ip_vs_sync_v4`, `ip_vs_sync_v6`, `ip_vs_sync_mesg_v0`, and `ip_vs_sync_mesg`. `ip_vs_sync_conn()` is the public sender for connection sync, with `ip_vs_sync_conn_v0()` for legacy format. `ip_vs_sync_conn_needed()` rate-limits syncs by state, thresholds, refresh period, retries, and persistence mode. `ip_vs_process_message()` and `ip_vs_process_message_v0()` receive messages. `ip_vs_proc_sync_conn()` parses one v1 connection, and `ip_vs_proc_conn()` creates or updates the IPVS connection. `start_sync_thread()` and `stop_sync_thread()` manage kernel threads, sockets, queues, and daemon state. `ip_vs_sync_net_init()` and `ip_vs_sync_net_cleanup()` initialize per-netns locks and stop daemons.

## Control Flow
On the master, protocol/state changes call `ip_vs_sync_conn()`. It skips one-packet connections, checks sync policy, computes message length including sequence options and persistence data, appends the connection to the current per-thread buffer, and queues full buffers for the master thread. Master threads dequeue buffers or flush old current buffers and send them with `kernel_sendmsg()`. On the backup, receive threads wait on UDP socket queues, read datagrams, validate size and sync ID, parse v1 or v0 format, validate protocol state, resolve persistence engines when PE data is present, then update or create IPVS connection entries and bind destinations if available.

## State and Persistence
Per-netns state includes master and backup configs, sync state flags, thread arrays, master per-thread queues, current sync buffers, locks, thread mask, and socket buffers. Sync message state is transient, but decoded backup connections persist in the IPVS connection table. Version 1 preserves IPv6, fwmark, timeout, persistence engine name/data, and sequence options; version 0 is IPv4 only and loses some template/fwmark fidelity.

## Dependencies and Integration Points
Depends on kernel sockets, multicast group join APIs, kthreads, delayed work, RCU connection/destination lookup, IPVS sysctls, persistence engine registry, protocol registry, and connection table allocation. It is controlled by IPVS daemon configuration and integrates with active connection state transitions in protocol handlers.

## Risks
The file combines wire-format parsing, socket lifecycle, and connection-table mutation, so bounds checks and lock ordering are critical. Version 1 optional parameter parsing must reject duplicate, oversized, mandatory unknown, or truncated parameters. Master queue growth is bounded by sysctls but allocation happens in atomic context. Backup destination binding assumes homogeneous pools for synced services. Thread startup holds RTNL and sync mutex with careful trylock ordering; error cleanup must stop partially started threads and release sockets. Multicast MTU and `sync_maxlen` determine message fragmentation risk.

## Test Signals
Run master/backup daemons with IPv4 and IPv6 multicast, multiple sync ports, sync ID filtering, version 0 and version 1 modes, TCP/SCTP/UDP state changes, persistence templates with SIP PE data, sequence options, fwmark services, daemon start/stop races, malformed datagrams, queue pressure, socket send `EAGAIN`, backup without preexisting services, and netns cleanup while daemons are running.
