# sources/distributed-fs/ceph-client/net/smc/smc_netlink.c

## Purpose
`smc_netlink.c` defines and registers the SMC generic netlink family. It maps SMC netlink commands to dump and administrative handlers implemented across core, IB, ISM, CLC, and stats modules.

## Important APIs, Types, and Functions
The file defines `smc_gen_ueid_policy`, `smc_gen_nl_ops[]`, `smc_gen_nl_policy`, global `smc_gen_nl_family`, and lifecycle functions `smc_nl_init()` and `smc_nl_exit()`. Operations include system info, SMC-R link groups, SMC-R links, SMC-D link groups, SMC-D devices, SMC-R devices, stats, fallback stats, UEID dump/add/remove/flush, SEID dump/enable/disable, and handshake-limitation dump/enable/disable.

## Control Flow
`smc_nl_init()` registers `smc_gen_nl_family`. User-space generic netlink commands dispatch through `smc_gen_nl_ops[]`; unprivileged dumps call `dumpit` functions, while mutating UEID/SEID/handshake-limitation operations require `GENL_ADMIN_PERM`. `smc_nl_exit()` unregisters the family.

## State and Persistence
This file stores static registration metadata and a UEID string policy. The data returned or mutated by handlers lives in other modules. Generic netlink registration is runtime kernel state only.

## Dependencies and Integration Points
It includes Linux module/list/ctype/mutex/if/SMC APIs and local core, ISM, IB, CLC, stats, and netlink headers. `smc_gen_nl_family` is used by dump helpers in `smc_core.c`, `smc_ib.c`, and `smc_ism.c` when constructing messages.

## Risks
Command permissions must remain correct because several operations mutate negotiation identity or limitations. `maxattr` is intentionally small with a reject policy for command-level attrs, while per-operation policies are attached where needed; incorrect policy updates can reject valid user-space requests or accept malformed ones. Adding new commands requires updating `resv_start_op` and policy coverage.

## Test Signals
Use `genl` or SMC tooling to dump every command, attempt admin-only operations as unprivileged and privileged users, fuzz attrs for UEID commands, verify netns-aware dumps, and unload/reload the module without family registration leaks.
