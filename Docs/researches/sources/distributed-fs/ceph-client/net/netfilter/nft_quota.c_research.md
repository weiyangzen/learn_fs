
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_quota.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_quota.c

## Purpose

`nft_quota.c` implements nftables quota matching both as a stateful expression and as a named nft object. It counts packet bytes against a configured quota, supports inverted matching, exposes consumed byte counters, supports reset-on-dump, and sends an object notification when a quota object becomes depleted.

## Important APIs, Types, and Functions

`struct nft_quota` contains an atomic quota limit, flags, and an allocated atomic consumed counter. `nft_overquota()` atomically adds `skb->len` and tests the boundary. `nft_quota_do_init()`, `nft_quota_do_dump()`, and `nft_quota_do_destroy()` are shared by expression and object paths. `nft_quota_obj_eval()` adds depletion notification via `nft_obj_notify()`. `nft_quota_clone()` duplicates stateful expression counters.

## Control Flow

Initialization requires `NFTA_QUOTA_BYTES`, rejects quota values above `S64_MAX`, rejects initially consumed values above quota, and rejects userspace setting the depleted flag. Evaluation always increments consumed bytes, then breaks evaluation when over quota XOR inverted. Object evaluation also computes a report condition when consumption reaches quota and sends a single notification guarded by `NFT_QUOTA_DEPLETED_BIT`. Dump optionally resets consumed bytes and clears depletion state.

## State and Persistence Behavior

Quota state persists across packets in atomic counters. Object updates replace quota and flags but leave the existing consumed counter in place. Expression clone allocates a new consumed counter and copies its value, preserving snapshot behavior for transaction cloning. Dump caps reported consumed bytes at quota even though internal consumed may exceed quota.

## Dependencies and Integration Points

The file integrates with nf_tables expression registration, nft object registration, netlink quota attributes, atomic64 counters, and nft object notifications. The expression is marked `NFT_EXPR_STATEFUL`; the object type is `NFT_OBJECT_QUOTA`.

## Risks and Test Signals

Risks include byte counter overflow assumptions, reset races with packet evaluation, notification storms if depleted state is mishandled, and confusing inclusive/exclusive boundary behavior: report at `>= quota`, overquota at `> quota`. Test quota objects and expressions with reset dumps, inverted rules, object update, clone/transaction paths, and packets crossing the quota exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_quota.c -->
