# sources/distributed-fs/ceph-client/net/netfilter/nf_queue.c

## Purpose

`nf_queue.c` implements the generic kernel side of netfilter packet queueing. It lets one queue backend, normally nfnetlink_queue, register a handler that receives packets whose netfilter verdict is `NF_QUEUE`. The core captures enough skb, hook, device, socket, bridge, and route state so the backend can later reinject the packet through `nf_reinject()`.

## Important APIs, types, and functions

- `nf_queue_handler` is a single global RCU pointer to `struct nf_queue_handler`.
- `nf_register_queue_handler()` and `nf_unregister_queue_handler()` publish and clear the backend handler.
- `nf_queue_entry_get_refs()` takes references on `state->sk`, input/output devices, and bridge physical devices so queued packets can outlive the original hook call.
- `nf_queue_entry_free()` and `nf_queue_entry_release_refs()` drop those references and free the queue entry.
- `nf_queue_nf_hook_drop()` forwards net namespace hook-drop notifications to the registered backend.
- `nf_ip_saveroute()` and `nf_ip6_saveroute()` snapshot LOCAL_OUT route keys for later reroute decisions.
- `__nf_queue()` builds a `struct nf_queue_entry` and calls `qh->outfn(entry, queuenum)`.
- `nf_queue()` decodes the queue number from the verdict and applies queue-bypass/drop policy.

## Control flow

Backends register once with `nf_register_queue_handler()`, which warns if another handler is already present. When a hook returns an `NF_QUEUE` verdict, `nf_queue()` calls `__nf_queue()` with the queue number encoded in the verdict high bits. `__nf_queue()` drops safely with `-ESRCH` if no backend is registered. It chooses extra route-key storage based on address family, handles prefetched skb sockets that need an explicit reference, allocates `struct nf_queue_entry` plus route storage with `GFP_ATOMIC`, forces dst references when present, copies the hook state, initializes bridge physical devices, and holds all needed refs.

For IPv4 and IPv6 LOCAL_OUT packets, the original source, destination, mark, and IPv4 TOS are saved. The backend `outfn` receives ownership of the queue entry; if it returns an error, the core frees the entry and returns the error. `nf_queue()` then either treats `-ESRCH` as accepted when `NF_VERDICT_FLAG_QUEUE_BYPASS` is set, or frees the skb and reports that the packet did not continue synchronously.

## State and persistence behavior

The registered handler is global RCU state. Per-packet queue state is in `struct nf_queue_entry`, which embeds a copy of `struct nf_hook_state`, the skb pointer, hook index, entry size, optional bridge physical devices, and optional route key data. The queue backend is responsible for reinjecting every accepted entry; queued packets do not persist across backend loss unless the backend flushes them. Device and socket refs are held explicitly and released by `nf_queue_entry_free()`.

## Dependencies and integration points

This file integrates with core netfilter hook traversal, nfnetlink_queue style backends, network namespace hook-drop handling, IPv4/IPv6 routing metadata, bridge netfilter physical-device metadata, skb dst management, and socket lifetime helpers. It exports symbols used by queue backends and reinjection code.

## Risks

Reference lifetime is the main risk. Missing a device, bridge device, socket, or dst reference can leave the backend with dangling state; failing to release refs leaks resources. Queueing occurs in atomic context, so allocation failure and dst forcing failure must be handled by dropping. The single-handler design means backend registration conflicts are not supported. Queue bypass only applies when no backend is registered; other queue errors still drop the skb.

## Test signals

Test signals include NFQUEUE operation for IPv4 and IPv6 LOCAL_OUT and forwarded packets, queue-bypass behavior when no backend is loaded, backend `outfn` failure cleanup, reinjection after network device lifetime changes, bridge netfilter packets with physical input/output devices, prefetched skb socket reference handling, and namespace teardown invoking `nf_queue_nf_hook_drop()`.
