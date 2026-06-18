# sources/distributed-fs/ceph-client/fs/afs/vlclient.c

Purpose: Provides kAFS Volume Location service RPC client stubs for classic AFS VL and YFSVL calls, including VLDB lookup, address lookup, capability probing, endpoint decoding, and cell-name lookup.

Important APIs and functions: `afs_vl_get_entry_by_name_u()` sends `VLGETENTRYBYNAMEU` and returns `struct afs_vldb_entry`. `afs_vl_get_addrs_u()` resolves a server UUID into an IPv4 address list. `afs_vl_get_capabilities()` sends an async probe used by VL server probing. `afs_yfsvl_get_endpoints()` decodes YFS IPv4/IPv6 endpoint arrays. `afs_yfsvl_get_cell_name()` returns a server-reported cell name. Delivery functions use `call->unmarshall` state machines for variable-length replies.

Control flow: Call builders allocate flat AFS calls, fill request XDR, bind the selected cursor peer/service id, issue the RxRPC call, wait for completion for synchronous paths, copy `abort_code`, `error`, and `responded` back into the VL cursor, then release the call. Delivery functions first extract fixed fields, allocate return containers, then iterate variable arrays in bounded chunks. Endpoint decoding validates type tags and element lengths before merging addresses.

State and persistence: Returned VLDB entries carry volume IDs, type availability bits, server UUIDs, server flags, and address versions. Address-list calls fill `struct afs_addr_list` version and merged endpoint peers. The capability probe stores probe context in the call and reports completion through `afs_vlserver_probe_result()`.

Dependencies and integration points: Integrates with `vl_rotate.c` cursors, `volume.c` volume creation/update, AFS XDR protocol structures from `afs_fs.h`, RxRPC call allocation, and address-list merge helpers. YFSVL support feeds modern fileserver endpoint discovery.

Risks: Protocol parsing must strictly cap server/address counts and validate padded strings. Ownership of `ret_vldb`, `ret_alist`, and `ret_str` is transferred only on success; error paths must free partial returns. Cursor feedback is required for failover correctness.

Test signals: VLDB lookup by name and numeric ID, empty or no-media VLDB entries, large endpoint lists, bad endpoint type/length protocol errors, capability probe completion/cancel, and memory allocation failures during reply delivery.
