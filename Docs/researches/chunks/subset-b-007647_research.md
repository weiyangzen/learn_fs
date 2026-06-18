# sources/distributed-fs/lustre-release/lnet/lnet/api-ni.c lines 9907-10725

## Chunk Scope

This chunk is the final portion of `lnet/lnet/api-ni.c`. It closes the generic-netlink command surface for LNet configuration and then defines exported/local helpers for NI identity enumeration, peer-local checks, ping-based peer interrogation, metadata discovery, and peer discovery status. The source file ends at line 10725, so there is no later code in this file beyond this chunk.

## Purpose

The code in this range ties LNet kernel state to two external control surfaces:

- Generic netlink: command registration through `lnet_genl_ops`, multicast group names through `lnet_mcast_grps`, and the `lnet_family` descriptor used by earlier show/dump/doit handlers.
- Kernel/exported API helpers: `LNetDebugPeer()`, `LNetIsPeerLocal()`, `LNetFetchNIDs()`, `LNetGetId()`, `lnet_discover_nid_metadata()`, and `LNetGetPeerDiscoveryStatus()`.

The ping/discovery helpers implement the active network probes behind earlier ioctl and generic-netlink handlers. They allocate a ping buffer, bind it as an LNet memory descriptor, issue a GET against `LNET_RESERVED_PORTAL` using `LNET_PROTO_PING_MATCHBITS`, wait for reply/unlink events, validate the ping reply format, and return peer NIDs or metadata in `genradix`/caller buffers.

## Important APIs, Types, and Functions

- `lnet_numa_cmd()` parses a scalar-list netlink request, extracts a `range` integer, and updates global `lnet_numa_range` under `lnet_net_lock(LNET_LOCK_EX)`.
- `lnet_mcast_grps[]` declares netlink multicast group names: `ip2net`, `net`, `peer`, `route`, `ping`, `discover`, `cpt-of-nid`, `dbg-recov`, `fault`, `routing`, `buffers`, and `numa`.
- `lnet_genl_ops[]` maps LNet command IDs to handlers. Dump commands wire `.start`, `.dumpit`, and `.done`; mutating commands use `GENL_ADMIN_PERM` and `.doit`.
- `lnet_family` is the `struct genl_family` registered earlier by `lnet_lib_init()` and unregistered by `lnet_lib_exit()`. It enables parallel ops and network namespace support.
- `LNetDebugPeer()` wraps `lnet_debug_peer()` for an exported process-id API.
- `LNetIsPeerLocal()` checks whether a given NID matches a local NI in `the_lnet.ln_nets`.
- `LNetFetchNIDs()` iterates local NIs, optionally filtering by net ID, and calls a caller-provided callback for each NID.
- `LNetGetId()` returns the NID/PID for the local NI at a caller-provided ordinal index, optionally skipping large-NID interfaces when `large_nids` is false.
- `struct ping_data` holds asynchronous ping state: result code/length, reply flag, unlink flag, MD handle, and completion object.
- `lnet_ping_event_handler()` is the MD event callback used by both ping paths. It records reply length or error status, notes unlink completion, and wakes waiters on unlink or send failure.
- `LNetGetForce()` manually builds and sends an LNet GET through a caller-selected `struct lnet_ni`, bypassing normal routing selection.
- `lnet_dump_nid_metadata()` is a failure-injection/test helper that validates poisoned metadata entries when `CFS_FAIL_TEST_PING_MD` is active.
- `lnet_discover_nid_metadata()` is exported for kernel-space metadata discovery. It sends a forced ping over the NI matching the target net and extracts trailing `struct lnet_nid_metadata` from the returned ping buffer.
- `lnet_ping()` is the general ping helper used by earlier ioctl and netlink paths. It sends `LNetGet()`, parses the returned `struct lnet_ping_info`, and appends discovered process IDs to `struct lnet_genl_ping_list`.
- `lnet_discover()` invalidates cached peer NIDs, optionally forces ping/push, runs peer discovery, reacquires the possibly replaced peer NI, and exports the discovered peer NI list into `struct lnet_genl_ping_list`.
- `LNetGetPeerDiscoveryStatus()` returns the inverse of `lnet_peer_discovery_disabled`.

## Control Flow

`lnet_numa_cmd()` follows the command-handler pattern used earlier in the file: validate that the netlink request has attributes, require a scalar-list top-level payload, scan `LN_SCALAR_ATTR_VALUE` entries, and use `nla_extract_val()` for the integer. The actual global write is short and locked with the LNet net lock.

The netlink family tables are static dispatch metadata. Earlier initialization registers `lnet_family` with generic netlink; from then on, requests route to the handlers named here. The `LNET_CMD_PING` entry is noteworthy because both dump and create-style command paths use the same command ID but route through different callbacks from earlier chunks.

Local NI query helpers are simple locked iterations over `the_lnet.ln_nets` and each `net_ni_list`. `LNetIsPeerLocal()` uses the current-net lock and returns as soon as it finds a matching NID. `LNetFetchNIDs()` uses `ln_api_mutex`, calls the provided callback for each matching NI, and aborts only on negative callback return. `LNetGetId()` asserts LNet is initialized, walks the same topology under the net lock, decrements the caller's index across eligible NIs, and fills `struct lnet_processid` with `the_lnet.ln_pid`.

The ping flows are asynchronous but made synchronous for their callers through `struct completion`:

1. Allocate a bounded ping buffer no larger than `LNET_PING_BUFFER_MAX` because larger buffers may fail on InfiniBand transports.
2. Bind an LNet MD with `umd_threshold = 2`, `LNET_MD_TRUNCATE`, user pointer set to `struct ping_data`, and `lnet_ping_event_handler()` as the event callback.
3. Send a GET to `LNET_RESERVED_PORTAL` and `LNET_PROTO_PING_MATCHBITS`.
4. Wait for completion up to the caller's timeout, unlink the MD if needed, and wait for the unlink event to avoid freeing a live MD buffer.
5. Require a reply, validate byte count, magic, feature bits, and expected total size, including large-NID-aware sizing.
6. Extract either peer process IDs (`lnet_ping()`) or metadata mappings (`lnet_discover_nid_metadata()`).
7. Drop the ping buffer reference through `kref_put(..., lnet_ping_buffer_free)`.

`LNetGetForce()` is the special send path used only by metadata discovery in this chunk. It allocates a message, locks the MD CPT resource, validates that the MD exists, has threshold remaining, and is not attached to a match entry, attaches the MD, fills the GET header including return wire handle cookies, overrides source NID/PID with the chosen NI and global LNet PID, then calls the LND `lnd_send()` callback directly. Send failure finalizes the message with `msg_no_resend = true`; the function still returns 0 after handing the message to LNet finalization.

`lnet_discover()` is peer-state oriented rather than raw ping oriented. It looks up or creates a peer NI by NID under the net lock, clears `LNET_PEER_NIDS_UPTODATE`, optionally sets `LNET_PEER_FORCE_PING | LNET_PEER_FORCE_PUSH`, invokes `lnet_discover_peer_locked()`, then releases and re-finds the peer NI because discovery may replace the peer object. It then iterates all peer NIs with `lnet_get_next_peer_ni_locked()` and stores process IDs in a `GENRADIX` list.

## State and Persistence Behavior

The code mutates in-memory kernel state only; there is no on-disk persistence in this chunk.

- `lnet_numa_range` is a module/global tunable updated from netlink under the exclusive net lock.
- `lnet_family` is static registration metadata used for the lifetime between `lnet_lib_init()` and `lnet_lib_exit()`.
- Local NI lists live in `the_lnet.ln_nets`; this chunk reads them under either `lnet_net_lock_current()` or `ln_api_mutex` depending on API context.
- Ping operations allocate transient `struct lnet_ping_buffer` objects and MD handles. Completion and unlink flags ensure the buffer is not freed until MD activity has stopped.
- `lnet_discover()` mutates peer runtime state flags inside `struct lnet_peer` and repopulates the caller's transient `genradix` output list. Peer reference counts are explicitly decremented on all exit paths that own a reference.
- `LNetGetPeerDiscoveryStatus()` reads the global discovery-disable flag and exposes it as enabled/disabled status.

## Dependencies and Integration Points

This chunk depends on Linux generic netlink (`genl_ops`, `genl_family`, `genl_multicast_group`, `sk_buff`, `genl_info`, `nlattr` parsing), Linux synchronization (`mutex`, spin locks, completions, krefs), and Lustre/LNet infrastructure (`the_lnet`, net/resource locks, NID conversion helpers, ping-buffer helpers, peer table helpers, LND send callbacks, and `GENRADIX` storage).

Earlier code in the same file declares `struct lnet_genl_ping_list` and the prototypes for `lnet_ping()`/`lnet_discover()`, registers/unregisters `lnet_family`, and calls these helpers from ioctl and netlink handlers. The normal ping helper is used by legacy `IOC_LIBCFS_PING_PEER` and generic-netlink ping dumps. `lnet_discover()` is used by legacy `IOC_LIBCFS_DISCOVER` and generic-netlink discover/create operations. `lnet_discover_nid_metadata()` is also triggered from the generic-netlink ping dump path under failure injection and is exported for LND/kernel callers.

The metadata path integrates with ping-target construction earlier in the file, where metadata is appended after NI status entries and `LNET_PING_FEAT_METADATA` is set when supported. This chunk validates that feature bit, locates metadata after `pi_ni[n_ids]`, bounds the mapping count by `lnet_interfaces_max`, and copies only `lnet_size_of_metadata(count)` bytes to the caller.

## Risks and Edge Cases

- `lnet_numa_cmd()` defaults `range` to zero when no `range` key is present in a non-empty scalar list. That means malformed but type-valid commands can reset the global NUMA range without an explicit value.
- `LNetFetchNIDs()` invokes arbitrary callback code while holding `ln_api_mutex`. Callers must avoid callbacks that re-enter APIs requiring the same mutex or that block for long periods.
- `LNetGetId()` uses nested list traversal and only breaks out of the inner loop after finding an entry; because `index` is unsigned and already decremented, outer-loop continuation does not overwrite the result, but the traversal still continues unnecessarily after success.
- `LNetGetForce()` returns 0 even when the transport send callback returns a negative error after finalizing the message. Callers must rely on ping event/completion status for send failure, not the immediate return value, except for allocation/MD-validation errors.
- Ping reply parsing is sensitive to size calculations for small versus large NIDs. The code bounds buffers to 3960 bytes, clamps requested IDs to `lnet_interfaces_max`, validates minimum header and entry sizes, and recomputes expected size after seeing the returned count.
- Metadata extraction assumes the returned ping layout matches local parsing helpers and that `num_nid_mappings` is both nonzero and not larger than `lnet_interfaces_max`; peers with no metadata or unsupported feature bits fail with `-EPROTO`.
- `lnet_discover()` deliberately releases and reacquires the peer NI after discovery because discovery can replace peer objects. Any future change that keeps using the old `lpni` after discovery would risk stale peer state.
- Netlink command tables expose multiple admin-capable mutators. Handler permission flags and attribute validation are the main guardrails; dispatch-table mistakes can expose a mutating operation without `GENL_ADMIN_PERM`.

## Test Signals

Useful test/validation signals for this chunk include:

- Generic-netlink family registration succeeds during `lnet_lib_init()` and unregisters cleanly during `lnet_lib_exit()`.
- `lnetctl` or equivalent netlink clients can route commands for `ping`, `discover`, `numa`, `buffers`, `routing`, `fault`, and other IDs to the expected handlers.
- NUMA configuration tests should check empty payload (`-ENOMSG`), wrong top-level type (`-EINVAL`), valid `range`, and no-`range` default behavior.
- Local-NI API tests should cover `LNetIsPeerLocal()` for present and absent NIDs, `LNetFetchNIDs()` callback error propagation, network filtering, and `LNetGetId()` with and without large NIDs.
- Ping tests should cover invalid `LNET_NID_ANY`, oversized requested count clamping, timeout/unlink behavior, malformed magic, short replies, missing `LNET_PING_FEAT_NI_STATUS`, and large-NID reply sizing.
- Discovery tests should verify peer-state invalidation, forced ping/push flags, peer replacement after discovery, and correct population/freeing of `genradix` output lists.
- Failure-injection signal `CFS_FAIL_TEST_PING_MD` exercises metadata poison/validation paths and should catch mismatches in `lnet_dump_nid_metadata()`.
