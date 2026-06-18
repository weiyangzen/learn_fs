## sources/distributed-fs/beegfs/client_module/source/app/App.c

### Purpose
Implements the BeeGFS client kernel module application lifecycle: configuration loading, network/interface setup, local node identity, buffer/store allocation, inode-operation table setup, component construction/start/stop/join, mount sanity checks, and runtime update helpers.

### Important APIs, Types, and Functions
- `__App_probe_sockDomain` checks IPv6 socket/connect behavior and falls back to `AF_INET` when IPv6 is unavailable.
- `App_init` initializes all `App` fields to safe defaults, initializes lists/mutexes/counters, and records the owned `MountConfig`.
- `App_uninit` destructs components/stores/nodes/filters/config in reverse-ish order, disables logging before tearing down dependencies, frees inode op tables and fsUUID, and uninitializes locks/lists.
- `App_run` initializes data objects, inode operations, components, logs startup info, starts threads, waits briefly for management initialization, and performs mount sanity checks.
- `App_stop` stops components, optionally disables connection retries for unmount, joins components, and logs completion.
- `__App_initDataObjects` builds config, validates management host, decides socket domain, loads net/TCP-only/interface/RDMA/preferred-node filters, creates stores/mappers/state stores/node stores/local node, preallocates buffer stores, and creates ack/inode/statfs stores.
- `__App_initInodeOperations` allocates per-app Linux `inode_operations` tables and populates callbacks based on kernel feature macros and config flags for xattrs/ACLs.
- `App_updateLocalInterfaces`, `App_cloneLocalNicList`, `App_cloneLocalRDMANicList`, `App_findAllowedInterfaces`, and `App_findAllowedRDMAInterfaces` manage NIC discovery and propagation to node objects.
- `App_cloneFsUUID` and `App_updateFsUUID` manage filesystem UUID with a mutex.
- `__App_initLocalNodeInfo` discovers NICs, generates a client alias from PID/time/hostname truncated to 32 chars, and constructs the local node.
- `__App_initComponents`, `__App_startComponents`, `__App_stopComponents`, `__App_joinComponents`, and `__App_waitForComponentTermination` manage `DatagramListener`, `InternodeSyncer`, `AckManager`, and optional `Flusher`.
- `__App_logInfos` logs version, client ID, NICs, filters, preferred nodes, and ACL/xattr warnings.
- `__App_mountServerCheck` temporarily disables retries, waits for management init, stats root metadata and storage free space, then restores retry setting.
- `App_getVersionStr` returns compile-time `BEEGFS_VERSION`.

### Control Flow and State
Lifecycle is staged: `App_init` zeroes/initializes fields; `App_run` calls data setup, inode op setup, component setup/start, and mount verification; `App_stop` terminates and joins background threads; `App_uninit` frees resources. The `App` object owns most client-module runtime state: config/logger, filters, preferred node lists, local node, node stores, target/buddy mappers, target state stores, buffer stores, ack/inode/statfs caches, components, inode operation tables, lock counters, retry flags, benchmark mode, socket domain, RDMA NIC list, and fsUUID.

### Dependencies and Integration Points
Includes many kernel BeeGFS components: config/logging, sockets/NIC filters, target/buddy mappers, target state stores, node stores, ack manager, datagram listener, internode syncer, flusher, filesystem operations, remoting, inode ref store, buffer store, statfs cache, and kernel xattr APIs. It is the central integration point between mount configuration, networking, protocol state, and Linux VFS operation tables.

### Risks and Edge Cases
`App_updateFsUUID` overwrites `this->fsUUID` without freeing the previous value, so repeated updates can leak. `__App_logInfos` builds an extended NIC string in a fixed 1024-byte buffer with repeated `snprintf`/`strcpy`; many NICs can truncate and possibly produce confusing logs, though `snprintf` bounds the temporary. Initialization has many early returns; cleanup relies on `App_uninit` tolerating partially initialized state. `__App_initLocalNodeInfo` allocates `alias` without checking for allocation failure before `strncpy`. Component stop/join assumes thread self-termination proceeds; blocking join can hang unmount if a component never exits. `connRetriesEnabled` is `volatile bool` but not otherwise synchronized.

### Test Signals
Primary signals are kernel-module build/load/mount/unmount tests, mount sanity check failures, config parser tests, and VFS operation integration tests. Focused tests should exercise partial-initialization cleanup, IPv6 fallback, interface filtering, xattr/ACL feature combinations, repeated fsUUID updates, and component termination timeouts.
