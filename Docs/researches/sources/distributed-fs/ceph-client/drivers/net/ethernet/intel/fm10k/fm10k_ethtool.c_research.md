# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_ethtool.c

## Purpose
`fm10k_ethtool.c` implements the fm10k ethtool control and diagnostics surface: stats strings/data, register dumps, pause parameters, message level, ring sizing, interrupt coalescing, RSS hash fields/key/indirection table, mailbox self-test, private flags, channels, and timestamp info hook.

## Important APIs, types, and functions
The file defines `struct fm10k_stats` descriptors and stat arrays for netdev, interface, PF, mailbox, and queues. Core callbacks include `fm10k_get_strings`, `fm10k_get_sset_count`, `fm10k_get_ethtool_stats`, `fm10k_get_regs`, `fm10k_get_regs_len`, `fm10k_get_drvinfo`, pause get/set, ringparam get/set, coalesce get/set, RSS field get/set, `fm10k_mbx_test`, `fm10k_self_test`, RETA/RSS key get/set, channel get/set, and `fm10k_set_ethtool_ops`.

## Control flow
Stats collection updates driver stats, then walks descriptor arrays and optional PF/queue stats in the same order as string generation. Register dumps branch on PF vs VF and emit fixed register blocks; length macros must match dump logic and are guarded by `BUG_ON` in sub-block helpers. Ring resizing clamps and aligns requested counts, serializes through `__FM10K_RESETTING`, and if running, allocates replacement resources before swapping them into live rings across a down/up cycle. RSS field changes validate supported field combinations and rewrite MRQC when UDP RSS toggles. RSS table/key setters validate queue indexes and write changed entries. Channel changes update RSS limit and delegate queue remapping to `fm10k_setup_tc`.

## State and persistence behavior
Ettool operations read and mutate `fm10k_intfc` counters, ring counts, ITR settings, q_vector ITR fields, RSS flags, `reta`, `rssrk`, `rx_pause`, message level, and ring feature limits. Hardware state changes include descriptor resources, MRQC, RETA, RSSRK, pause/drop behavior, and queue layout. Self-test uses mailbox `test_result` and mailbox TX/process paths.

## Dependencies and integration points
The file depends on Linux ethtool APIs, vmalloc, netdev state, fm10k ring resource functions, mailbox TLV helpers, reset/open/close paths, and register definitions. It is installed by `fm10k_set_ethtool_ops` during netdev setup.

## Risks
String/data count ordering must stay exact or ethtool stats become corrupt. Register dump length macros must be updated with dump changes. Ring resizing is high risk because it reallocates DMA resources while preserving old resources on failure. UDP RSS can reorder fragmented UDP packets, and the code warns when enabling it. Mailbox self-test can time out if mailbox processing is blocked. Channel changes interact with DCB traffic-class mapping.

## Test signals
Run `ethtool -S`, `-d`, `-g/-G`, `-c/-C`, `-x/-X`, `-l/-L`, `--show-priv-flags`, `-t`, and pause operations on PF and VF devices. Verify stats counts match strings, register dump lengths match, traffic survives ring/channel changes, RSS distribution changes as requested, and mailbox self-test passes for VFs.
