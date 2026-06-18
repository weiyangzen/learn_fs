# sources/distributed-fs/ceph-client/net/tipc/discover.c

## Purpose

`discover.c` drives TIPC bearer peer discovery and link setup request/response exchange. It periodically sends discovery messages on a bearer, performs initial node-address uniqueness trials when the local node has no assigned address, validates incoming discovery traffic, detects duplicate node addresses, and asks `node.c` to create or check peer destinations.

## Important APIs, Types, and Functions

`struct tipc_discoverer` stores bearer identity, destination media address, net namespace, discovery domain, discovered-node count, a reusable discovery skb, timer interval, timer, and spinlock. Public functions are `tipc_disc_create()`, `tipc_disc_delete()`, `tipc_disc_reset()`, `tipc_disc_add_dest()`, `tipc_disc_remove_dest()`, and `tipc_disc_rcv()`. Internal helpers build discovery messages (`tipc_disc_init_msg()`), transmit one-shot messages (`tipc_disc_msg_xmit()`), report duplicate addresses, handle trial address messages, and run the periodic timer.

## Control Flow

Creation allocates the discoverer and reusable request skb, initializes it as `DSC_REQ_MSG`, optionally changes it to `DSC_TRIAL_MSG` for a one-second address trial, starts the timer at `TIPC_DISC_INIT`, attaches the discoverer to the bearer, and returns an initial clone. Timer expiry doubles the interval until fast or slow limits depending on whether links exist, stops when a specific destination node is found, handles trial-period exit by scheduling `tipc_net` work, clones the reusable skb, and transmits it through the bearer.

Receive linearizes the skb, extracts peer capabilities, node ID, suggested address, node signature, network ID, media address, and message type. It rejects corrupt/broadcast media addresses, own-media messages, wrong net IDs, trial-only messages, duplicate own address usage, and out-of-domain peers. Valid candidates are passed to `tipc_node_check_dest()`, which decides whether to respond and whether a duplicate alert is needed. Discovery requests that require a response produce `DSC_RESP_MSG`.

## State and Persistence Behavior

The discoverer persists per bearer while discovery is active. Its reusable skb is mutated for trial and normal phases, `num_nodes` tracks active destinations, and `timer_intv` backs off or resets. Per-net address trial state lives in `tipc_net`: `trial_addr`, `addr_trial_end`, `random`, `net_id`, and legacy address format flags. No state is written to disk.

## Dependencies and Integration Points

The file depends on TIPC core, node, bearer/media address conversion, timers, skbs, and domain helpers. It integrates directly with media adapters via `b->media->addr2msg()` and `msg2addr()`, with bearer transmit via `tipc_bearer_xmit_skb()`, with node identity/address assignment via `tipc_node_try_addr()` and `tipc_node_check_dest()`, and with net work scheduling when a trial address becomes usable.

## Risks and Edge Cases

Discovery is exposed to untrusted LAN/bearer traffic. It must reject malformed media addresses, wrong net IDs, self-originated messages, and duplicate node addresses. Timer and lock ordering matters because delete shuts down the timer while bearer teardown may race receive/reset. Address trial handling is subtle: accepting normal link setup before trial end risks duplicate addresses; failing to switch from trial to request can stall cluster formation.

## Test Signals

Exercise bearer enable/disable, peer appearance/removal, duplicate address injection, network ID mismatch, trial fail messages with new suggestions, and discovery reset after bearer reconfiguration. Packet traces should show `DSC_TRIAL_MSG`, `DSC_TRIAL_FAIL_MSG`, `DSC_REQ_MSG`, and `DSC_RESP_MSG` transitions and interval backoff.
