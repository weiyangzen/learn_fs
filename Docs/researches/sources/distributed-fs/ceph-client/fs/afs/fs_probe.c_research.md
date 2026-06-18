# sources/distributed-fs/ceph-client/fs/afs/fs_probe.c

Purpose: `fs_probe.c` probes fileserver endpoints to discover responsiveness, preferred address, RTT, YFS support, and capabilities such as FS64, then schedules fast or slow reprobes.

Important APIs and functions: exported functions include `afs_get_endpoint_state()`, `afs_put_endpoint_state()`, `afs_fileserver_probe_result()`, `afs_fs_probe_fileserver()`, `afs_wait_for_fs_probes()`, `afs_fs_probe_timer()`, `afs_probe_fileserver()`, `afs_fs_probe_dispatcher()`, `afs_wait_for_one_fs_probe()`, and `afs_fs_probe_cleanup()`.

Control flow: `afs_fs_probe_fileserver()` creates a new endpoint state, inherits old responsive hints, installs it under the server fs lock, applies address preferences, then sends async GetCapabilities probes to addresses in priority order. Completion records errors, responsive/failed bits, abort codes, YFS/AFS and FS64 flags, RTT, preferred address, and responding state. When all address probes finish, the server enters the slow queue if responsive or fast queue if not, and the timer is scheduled. The dispatcher drains due queues and reschedules work or timer.

State and persistence: `afs_endpoint_state` is refcounted and RCU-freed, storing address list, probe sequence, bitsets, error/abort, RTT, flags, and outstanding count. Server state stores endpoint pointer, address version, service ID, RTT, probe link, and capability flags.

Dependencies and integration points: uses `afs_fs_get_capabilities()` from `fsclient.c`, call-type done hooks, server selection waiters, namespace cleanup, rxrpc peer RTT, address preferences, RCU, timers, locks, and workqueues.

Risks: peer appdata update around `old_alist` deserves review because the local variable is initialized NULL and not visibly assigned before comparison. Superseded probe states and shutdown require careful ref balancing. Error classification controls server availability. Address sets assume unsigned-long capacity.

Test signals: all/mixed/no responsive addresses, YFS and AFS FS64 capability detection, superseded probes with waiters, timeout/signal waits, ENOMEM call allocation, timer cleanup, and fast/slow dispatcher scheduling.
