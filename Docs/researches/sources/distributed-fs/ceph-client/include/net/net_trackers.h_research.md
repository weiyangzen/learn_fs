<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_trackers.h -->
# sources/distributed-fs/ceph-client/include/net/net_trackers.h

## Purpose
`net_trackers.h` aliases optional network object reference trackers for netdevices and network namespaces.

## Important APIs, types, and functions
It typedefs `netdevice_tracker` and `netns_tracker` to `struct ref_tracker *` when the matching CONFIG tracker is enabled, otherwise to empty structs.

## Control flow
Code can declare tracker variables unconditionally and pass them to helpers; enabled builds allocate/free tracker records, disabled builds compile away storage.

## State and persistence
The header stores no state. Runtime tracker state lives in ref_tracker directories on netdevices/net namespaces when enabled.

## Dependencies and integration points
It depends on `<linux/ref_tracker.h>` and CONFIG_NET_DEV_REFCNT_TRACKER / CONFIG_NET_NS_REFCNT_TRACKER. It integrates leak diagnostics with network object lifetimes.

## Risks and test signals
Risks include helpers that assume pointer semantics in disabled builds and mismatched alloc/free pairs in enabled builds. Tests should build with trackers on/off and run leak/refcount diagnostics.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_trackers.h` completely for this pass (18 lines, 424 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_trackers.h -->
