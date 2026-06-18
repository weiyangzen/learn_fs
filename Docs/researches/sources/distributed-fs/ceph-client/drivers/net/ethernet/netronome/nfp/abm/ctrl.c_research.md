# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/ctrl.c

## Purpose
`abm/ctrl.c` is the firmware control and telemetry layer for the NFP ABM NIC app. It discovers firmware runtime symbols, validates ABM capabilities, writes RED queue thresholds/actions, reads queue and queue-manager statistics, enables/disables ABM queue management, and updates per-vNIC DSCP priority maps through the NFP net mailbox.

## Important APIs, types, and functions
Symbol names such as `_abi_pci_dscp_num_prio_%u`, `_abi_nfd_out_q_lvls_%u%s`, and `_abi_nfdqm%u_stats%s` define the firmware ABI. `nfp_abm_ctrl_find_addrs()` discovers capabilities and runtime symbols. `__nfp_abm_ctrl_set_q_lvl()` and `nfp_abm_ctrl_set_q_lvl()` write RED thresholds. `__nfp_abm_ctrl_set_q_act()` and `nfp_abm_ctrl_set_q_act()` write actions. `nfp_abm_ctrl_read_q_stats()` and `nfp_abm_ctrl_read_q_xstats()` read basic and extended stats. `nfp_abm_ctrl_qm_enable()`/`disable()` send PF mailbox commands. `nfp_abm_ctrl_prio_map_update()` writes a packed priority map into the vNIC mailbox and triggers reconfiguration.

## Control flow
ABM app init calls `nfp_abm_ctrl_find_addrs()`, which derives the PCIe PF id, reads optional firmware values for RED support, number of bands/priorities, and action mask, computes priority map size and DSCP mask, validates power-of-two geometry, and locates queue level/stat symbols if RED is supported. Per-vNIC allocation calls `nfp_abm_ctrl_read_params()` to derive `queue_base` and validate mailbox size. Qdisc/classifier paths then call threshold/action/map update helpers. Stats paths compute queue ids from band, queue base, and queue number and read firmware symbols or vNIC RX stats depending on priority support.

## State and persistence
The control layer caches firmware capability values in `struct nfp_abm`: `red_support`, `num_prios`, `num_bands`, `action_mask`, `prio_map_len`, `dscp_mask`, and runtime-symbol pointers. It also caches current thresholds/actions and clears `threshold_undef` when levels are set. Hardware/firmware state is updated through runtime-symbol writes and mailbox commands; it is not persistent across firmware reset.

## Dependencies and integration points
This file depends on NFP CPP access, runtime symbol lookup/read/write APIs, PF optional symbol reads, NFP ABI mailbox constants, `struct nfp_net` mailbox helpers, and ABM data structures in `main.h`. It is used by ABM qdisc, classifier, vNIC init, stats, and eswitch mode code.

## Risks and edge cases
Firmware ABI names and exact symbol sizes are strict; mismatches fail init or RED support. Queue id calculation combines band with `NFP_NET_MAX_RX_RINGS` and per-vNIC `queue_base`, so queue geometry changes must match firmware. `nfp_abm_ctrl_stat_basic()` reads normal vNIC stats when there is no priority split, but runtime symbols when per-band stats exist. Optional firmware symbols default some values, so unsupported firmware must be distinguished from invalid geometry. Mailbox size validation is required before priority map updates.

## Test signals
Tests should cover firmware with and without RED support, one-band and multi-band configurations, invalid non-power-of-two capabilities, missing or wrong-sized runtime symbols, threshold/action no-op caching, mailbox priority map writes and failures, stat reads for per-band and non-per-band modes, QM enable/disable mailbox commands, and vNIC queue-base calculations.
