# sources/distributed-fs/ceph-client/net/smc/smc_netlink.h

## Purpose
`smc_netlink.h` declares the SMC generic netlink family, shared policies, dump cursor context, and registration lifecycle.

## Important APIs, Types, and Functions
It exposes `smc_gen_nl_family`, `smc_gen_ueid_policy[]`, `struct smc_nl_dmp_ctx`, `smc_nl_dmp_ctx()`, `smc_nl_init()`, and `smc_nl_exit()`. `struct smc_nl_dmp_ctx` has three integer positions for multi-dimensional dump cursors.

## Control Flow
Dump handlers cast `netlink_callback->ctx` through `smc_nl_dmp_ctx()` and use the position array to resume multi-part dumps. Module init and exit register and unregister the generic netlink family through the declared lifecycle calls.

## State and Persistence
The header owns no runtime state. It defines the shape of callback cursor memory used during netlink dump operations and references static family/policy objects in `smc_netlink.c`.

## Dependencies and Integration Points
It depends on netlink and generic netlink headers. It is included by core, IB, ISM, and stats/CLC code that either fills generic netlink messages or registers command handlers.

## Risks
All dump handlers sharing `pos[3]` must agree on index meaning; misuse can skip or repeat objects across multipart dumps. The cast from callback context assumes the context is large enough for `struct smc_nl_dmp_ctx`, matching generic netlink callback storage expectations.

## Test Signals
Multipart dumps with small skb sizes should resume correctly for device lists, link-group lists, and nested link dumps. Build tests should catch family/policy declaration drift.
