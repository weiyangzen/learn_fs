# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_acct.c

## Purpose
`nfnetlink_acct.c` implements the nfnetlink accounting subsystem. It lets userspace create named packet/byte counters with optional packet or byte quotas, retrieve and optionally zero counters, delete counters, and receive overquota multicast events. Other netfilter modules can hold references to accounting objects and update them per packet.

## Important APIs, Types, and Functions
The main object is `struct nf_acct`, containing atomic packet/byte counters, flags, name, refcount, RCU list node, and optional quota data. Per-net state is `struct nfnl_acct_net`.

nfnetlink callbacks are `nfnl_acct_new()`, `nfnl_acct_get()`, `nfnl_acct_del()`, dump helpers `nfnl_acct_dump()`, `nfnl_acct_start()`, `nfnl_acct_done()`, and formatter `nfnl_acct_fill_info()`. Exported module APIs are `nfnl_acct_find_get()`, `nfnl_acct_put()`, `nfnl_acct_update()`, and `nfnl_acct_overquota()`.

## Control Flow, State, and Persistence
Creation requires a non-empty `NFACCT_NAME`. Existing names honor `NLM_F_EXCL`; replace resets counters and clears overquota if quota is enabled. New objects validate quota flags so only packet or byte quota is selected, store optional initial counter values, set refcount to one, and append to the per-net RCU list.

Get either starts a dump with optional flag mask/value filtering or sends one named object. `NFNL_MSG_ACCT_GET_CTRZERO` atomically exchanges counters with zero and clears overquota state after reporting old values. Delete without a name attempts to delete every object; named delete removes one object only when `refcount_dec_if_one()` proves no external user holds it.

Runtime users call `nfnl_acct_find_get()` under RCU, which also pins the module, then `nfnl_acct_update()` to increment atomic counters. `nfnl_acct_overquota()` compares the selected counter with the stored quota, sets the overquota bit once, and multicasts an overquota report on `NFNLGRP_ACCT_QUOTA`.

## Dependencies and Integration Points
The subsystem registers under `NFNL_SUBSYS_ACCT`, uses per-net generic storage, RCU lists, atomic64 counters, refcounts, and nfnetlink multicast/unicast helpers. Consumers are nftables/xt accounting integrations that resolve named counters and call the exported update/quota APIs.

## Risks and Test Signals
Risks include quota flag validation, refcount deletion races, counter zeroing memory ordering, RCU traversal during namespace exit, overquota event suppression after the first event, and module refcount balance. Tests should cover create/replace/exclusive behavior, byte and packet quotas, counter dump with filtering, get-and-zero semantics, delete while referenced, namespace teardown with live references, and overquota multicast listener behavior.
