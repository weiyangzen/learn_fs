# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_common.c

## Purpose
`fm10k_common.c` implements hardware-generic helpers shared by PF and VF flows: PCIe capability discovery, invariant initialization, start/stop queue control, hardware statistic delta handling, queue statistic binding, and host readiness detection.

## Important APIs, types, and functions
Exports include `fm10k_get_bus_info_generic`, `fm10k_get_invariants_generic`, `fm10k_start_hw_generic`, `fm10k_disable_queues_generic`, `fm10k_stop_hw_generic`, `fm10k_read_hw_stats_32b`, `fm10k_update_hw_stats_q`, `fm10k_unbind_hw_stats_q`, and `fm10k_get_host_state_generic`. Static helpers compute MSI-X vector count and handle 48-bit stat deltas/base updates.

## Control flow
Bus info reads PCI config capability/status/control words and maps width, speed, and payload fields into `hw->bus_caps` and `hw->bus`. Invariants clear the DGLORT map and record max MSI-X vectors. Queue disable clears TX/RX enable bits for each queue, flushes, and polls until all queues report disabled or timeout. Stats update reads owner IDs before and after queue counters to avoid attributing deltas across queue ownership changes, then updates base and count fields. Host-state logic processes the mailbox, checks queue 0, mailbox timeout/state, DGLORT map availability, optionally requests lport map, and reports whether host is ready.

## State and persistence behavior
The file mutates `struct fm10k_hw` bus fields, `hw->mac.dglort_map`, `max_msix_vectors`, `tx_ready`, `get_host_state`, and queue stat bases/counts. It writes persistent hardware queue enable state and reads hardware counters that may advance independently. It treats removed hardware (`hw_addr == NULL`) as a special state to avoid MMIO writes.

## Dependencies and integration points
It depends on `fm10k_common.h`, fm10k register definitions, PCI config read hooks, mailbox operations, MAC operations, and queue/stat structures from `fm10k_type.h`. PCI probe/reset/open/close paths use these generic operations through hardware operation tables.

## Risks
Queue disable timeout handling is hardware-sensitive; failing to disable rings can leave DMA active during reset. Stats attribution depends on owner ID stability and base updates; mistakes produce negative/wrapped counters or cross-queue leakage. `fm10k_get_host_state_generic` can request resets on mailbox timeout or unexpected TX disable, so false positives disrupt link. Removed-device checks must prevent invalid MMIO.

## Test signals
Signals include correct PCIe bus reporting, successful reset/open/close, queue disable without timeout, stable per-queue and VF/PF counters under traffic and reset, host-ready transitions after mailbox/lport setup, and no MMIO warnings after hot-unplug.
