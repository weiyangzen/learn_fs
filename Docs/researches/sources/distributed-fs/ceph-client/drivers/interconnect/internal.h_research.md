# sources/distributed-fs/ceph-client/drivers/interconnect/internal.h

Purpose: private interconnect framework header defining internal path and request structures.

Important APIs/types/functions: `struct icc_req` records node, consumer device, enabled flag, tag, average bandwidth, peak bandwidth, and request hlist linkage. `struct icc_path` stores path name, hop count, and flexible request array. It declares internal `icc_get()` and `icc_debugfs_client_init()`.

Control flow: `core.c` allocates paths with one request per hop and attaches requests to each node's `req_list`; aggregation walks those lists.

State and persistence: `icc_path` and `icc_req` are the persistent per-consumer state from get to put.

Dependencies/integration: used by core, debugfs client, and KUnit.

Risks and test signals: test flexible-array allocation, hlist attach/detach, tag propagation, disabled request aggregation, and cleanup after failed path creation.
