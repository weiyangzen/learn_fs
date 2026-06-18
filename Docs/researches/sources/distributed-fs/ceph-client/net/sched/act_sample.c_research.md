# sources/distributed-fs/ceph-client/net/sched/act_sample.c

## Purpose

`act_sample.c` implements the tc packet sampling action. It randomly sends selected packets and metadata to the psample subsystem while returning the configured tc control action for the original packet.

## Important APIs, types, and functions

`tcf_sample_init()` parses `TCA_SAMPLE_PARMS`, required sample `RATE`, required `PSAMPLE_GROUP`, and optional truncation size, then obtains a `psample_group` reference and stores it under RCU. `tcf_sample_act()` performs random sampling with `get_random_u32_below()`, builds `psample_metadata`, copies an optional tc user cookie, and calls `psample_sample_packet()`. `tcf_sample_dev_ok_push()` decides whether ingress MAC headers may be temporarily pushed. Offload hooks expose `FLOW_ACTION_SAMPLE` and transfer a psample group reference.

## Control flow

Runtime updates stats and reads the action result. If a psample group exists and the random draw hits, it fills ingress and egress ifindexes depending on tc direction. On ingress for Ethernet-like devices it temporarily pushes the MAC header so psample sees the full frame, copies the action cookie under RCU, sets truncation length, samples the packet, and then restores the skb data pointer.

## State and persistence

Persistent state includes sample rate, psample group number, truncation flag/size, and an RCU-protected `psample_group` reference. Cleanup drops the group reference. Packet cookies are stored in the common tc action and read transiently.

## Dependencies and integration points

The module integrates tc actions with `net/psample`, flow offload, netdevice ARP type checks, tc cookies, and per-net action registration.

## Risks and edge cases

Rate zero is rejected; missing group/rate is invalid. Temporary ingress header push must be balanced, and tunnel/none device types are excluded from that push. Cookie copying is bounded by `TC_COOKIE_MAX_SIZE`. Sampling is probabilistic, so tests must account for randomness or use rate 1.

## Test signals

Use sample rate 1 for deterministic psample events, verify group reference lifecycle, truncation size, user cookie propagation, ingress/egress ifindexes, ingress MAC-header restoration, invalid rate/group handling, and offload conversion.
