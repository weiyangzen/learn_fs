<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtmultipath.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtmultipath.c

Purpose: Implements multipath support for SUNRPC client transports by managing `rpc_xprt_switch` lists, reference-counted switch lifetime, active/offline counts, switch IDs, sysfs publication, and iterator policies for selecting transports.

Important APIs/types/functions: Switch management APIs include `rpc_xprt_switch_add_xprt()`, `rpc_xprt_switch_remove_xprt()`, `rpc_xprt_switch_get_main_xprt()`, `xprt_switch_alloc()`, `xprt_switch_get()`, `xprt_switch_put()`, `rpc_xprt_switch_set_roundrobin()`, and `rpc_xprt_switch_has_addr()`. Iterator APIs include `xprt_iter_init()`, `xprt_iter_init_listall()`, `xprt_iter_init_listoffline()`, `xprt_iter_rewind()`, `xprt_iter_xchg_switch()`, `xprt_iter_destroy()`, `xprt_iter_xprt()`, and `xprt_iter_get_next()`. Static policies are singular, round-robin, list-all, and list-offline.

Control flow: A switch is allocated with one initial xprt, gets an ID, initializes lock/kref/list/queue counters, creates sysfs switch/xprt objects, and records a network namespace. Adding a transport takes a reference, appends it with RCU list operations if it belongs to the same net namespace, increments total and active counts, and publishes sysfs. Removing a transport updates counts, clears the net when the list becomes empty, deletes from the RCU list, and drops the transport reference. Iterators hold a switch reference and use RCU read-side sections to walk active or offline entries. Round-robin selection advances a cursor and skips transports whose queue length is above the switch average.

State and persistence behavior: `rpc_xprt_switch` maintains `xps_xprt_list`, `xps_nxprts`, `xps_nactive`, `xps_nunique_destaddr_xprts`, `xps_queuelen`, `xps_net`, `xps_iter_ops`, IDA id, kref, and sysfs pointer. Iterators maintain an RCU pointer to the switch, a cursor, and optional override ops. State is memory-only and freed with RCU after kref release.

Dependencies and integration points: Used by RPC clients to select transports, by `xprt.c` for online/offline/delete state changes, and by `sysfs.c` for live management. Depends on Linux RCU list traversal, kref, IDA, atomic counters, SUNRPC address comparison, and xprt refcounting.

Risks: Correctness depends on pairing RCU list updates with `xprt_get()`/`xprt_put()` and on readers taking references before leaving RCU. Active counts must stay in sync with `XPRT_OFFLINE` transitions from `xprt.c` and sysfs; double offline/remove mistakes can skew scheduling. Round-robin queue balancing uses approximate atomic counters and can be unfair under rapidly changing load. `xprt_switch_alloc()` does not visibly handle ID allocation failure before sysfs naming, so low-memory IDA failures merit review.

Test signals: Validate add/remove refcounts and RCU safety, net namespace rejection, active/offline count transitions, main transport lookup, duplicate address detection, singular vs round-robin vs list-all vs list-offline iteration, cursor rewind/exchange, queue-length based skipping, sysfs setup/destroy coupling, and cleanup of switch IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtmultipath.c -->
