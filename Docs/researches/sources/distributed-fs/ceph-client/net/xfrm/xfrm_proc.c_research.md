# sources/distributed-fs/ceph-client/net/xfrm/xfrm_proc.c

## Purpose

`xfrm_proc.c` exposes per-network-namespace XFRM statistics through `/proc/net/xfrm_stat` when XFRM statistics are enabled. It is a small reporting bridge from per-CPU Linux MIB counters to the procfs seq-file interface used by administrators, tests, and monitoring tools.

## Important APIs, Types, and Functions

`xfrm_mib_list[]` maps printable counter names to `LINUX_MIB_XFRM*` indexes. It covers inbound errors, replay/sequence errors, state/policy mismatches, outbound bundle/state/policy errors, forwarding header errors, acquire errors, direction errors, IPTFS errors, and outbound queue-space failures.

`xfrm_statistics_seq_show()` refreshes device-offload-backed state counters with `xfrm_state_update_stats(net)`, batches per-CPU SNMP counters through `snmp_get_cpu_field_batch_cnt()`, and prints each name/value pair. `xfrm_proc_init()` creates `xfrm_stat` under `net->proc_net`; `xfrm_proc_fini()` removes it.

## Control Flow

The per-net XFRM policy initialization path calls `xfrm_statistics_init()` in `xfrm_policy.c`, which allocates per-CPU `linux_xfrm_mib` storage and then calls `xfrm_proc_init()`. Reading `/proc/net/xfrm_stat` invokes the single seq-file show callback. Namespace teardown calls `xfrm_proc_fini()` before freeing the per-CPU counters.

## State and Persistence Behavior

This file does not own long-lived protocol state beyond the proc entry. It reads `net->mib.xfrm_statistics`, which is allocated per net namespace elsewhere. Values are snapshots of per-CPU counters at read time, after an explicit state stats update so packet-offload state counters are folded into visible statistics.

## Dependencies and Integration Points

Dependencies are procfs, seq_file, SNMP MIB helpers, and `net/xfrm.h`. It integrates with `xfrm_policy.c` under `CONFIG_XFRM_STATISTICS`; without that config this file is not part of the runtime reporting path.

## Risks and Edge Cases

The printed counter list must stay aligned with the MIB enum definitions. Missing a newly added counter reduces observability; misordering or wrong indexes would make `/proc/net/xfrm_stat` misleading. `xfrm_proc_init()` returns `-ENOMEM` if proc entry creation fails, which causes XFRM per-net initialization to unwind.

## Test Signals

Check that `/proc/net/xfrm_stat` exists in each eligible namespace, contains all expected `Xfrm*` names, and counters move after replay failures, missing states, policy blocks, queue drops, or IPTFS errors. Namespace creation/destruction tests should show no procfs leaks.
