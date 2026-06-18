# sources/distributed-fs/ceph-client/fs/lockd/mon.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/mon.c` implements the in-kernel client for the Network Status Monitor service (`rpc.statd`). It registers and unregisters monitored peers, caches NSM handles, matches reboot notifications, tracks local NSM state, and provides XDR for NSM MON/UNMON calls. The source was read as a complete 581-line file.

## Important APIs, Types, and Functions

Important public functions are `nsm_monitor`, `nsm_unmonitor`, `nsm_get_handle`, `nsm_reboot_lookup`, and `nsm_release`. Internal helpers include `nsm_create`, `nsm_mon_unmon`, `nsm_lookup_hostname`, `nsm_lookup_addr`, `nsm_lookup_priv`, `nsm_init_private`, `nsm_create_handle`, and NSM XDR encoders/decoders. Global state includes `nsm_local_state`, `nsm_use_hostnames`, and `nsm_lock`.

## Control Flow

`nsm_get_handle` validates hostnames, searches the per-net handle list by hostname or address depending on `nsm_use_hostnames`, and creates a handle with a unique private cookie if not found. `nsm_monitor` chooses the monitor name, creates a loopback TCP RPC client to `rpc.statd`, sends `NSMPROC_MON`, and updates `nsm_local_state` from the response. `nsm_unmonitor` sends `NSMPROC_UNMON` only when the final non-sticky reference is being released. Reboot lookup matches the private cookie returned by statd to an existing handle.

## State and Persistence Behavior

Handles are refcounted and stored on `lockd_net->nsm_handles`. Each handle stores monitor name, peer name/address, monitored/sticky flags, unique private cookie, and printable address buffer. The local NSM state is global in memory and changes when statd reports a different state.

## Dependencies and Integration Points

This file integrates with `host.c` host allocation/destruction and reboot notification, `netns.h` per-net storage, SUNRPC client transport to loopback statd, XDR stream helpers, and the NLM callback procedure number for `NLMPROC_NSM_NOTIFY`.

## Risks and Edge Cases

If statd is unavailable, monitoring fails and client lock acquisition can fail. Hostnames containing `/` are rejected to protect statd database paths. Private cookies use timestamp plus kernel pointer and are exposed only to local loopback statd, but stale or duplicated cookies could misattribute reboot state. `nsm_use_hostnames` changes cache matching semantics.

## Test Signals

Use statd integration tests for monitor/unmonitor, simulated reboot notifications, per-net handle isolation, hostname-vs-address matching, invalid hostname rejection, statd connection refused/rebind handling, refcount release tests, and XDR encode/decode fuzzing for NSM responses.
