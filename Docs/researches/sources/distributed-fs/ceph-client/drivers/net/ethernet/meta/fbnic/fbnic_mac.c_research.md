# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mac.c

## Purpose
`fbnic_mac.c` programs the Meta FBNIC ASIC MAC-side hardware and exposes the MAC operation table used by PCI, phylink, ethtool stats, pause storm protection, and sensor readers. It initializes AXI request sizing, queue manager defaults, RX/TX packet buffers, flow-control/drop/ECN thresholds, and MAC link-up/link-down behavior.

## Important APIs, Types, And Functions
The public entry points are `fbnic_mac_init()`, `fbnic_mac_get_fw_settings()`, `fbnic_mac_ps_protect_to_config()`, `fbnic_mac_ps_protect_handler()`, and `fbnic_mac_check_tx_pause()`. The file instantiates `static const struct fbnic_mac fbnic_mac_asic`, whose hooks include register init, link event/status, prepare, stats readers, link transitions, and sensor reads. Internal initializers include `fbnic_mac_init_axi()`, `fbnic_mac_init_qm()`, `fbnic_mac_init_rxb()`, and `fbnic_mac_init_txb()`.

## Control Flow
Probe calls `fbnic_mac_init()`, which assigns the ASIC vtable and runs register initialization. RXB setup either preserves already-enabled FIFO sizing, warning when smaller than expected, or programs cut-through, base/size, credits, pause, drop, ECN, calendar, DRR weights, and endian/FCS registers. TXB setup initializes internal queues, TSO/CSO behavior, packet size limits, calendars, weighted scheduling, and SOP protection before enabling TCAM load.

Link detection clears stale PCS status, clears link interrupts, reads lane-lock status according to AUI/FEC mode, then advances the PMD training state machine. Link-up programming enables pause generation and pause storm protection, releases MAC clock resets, and enables RX/TX. Link-down asserts MAC clock resets and disables pause. Firmware settings map firmware speed/FEC capability fields into driver AUI/FEC enums.

## State And Persistence
Persistent driver state includes `fbd->mac`, `fbd->pmd_state`, `fbd->end_of_pmd_training`, and `fbd->ps_timeout`. Statistics are kept as software deltas using old register snapshots in `struct fbnic_stat_counter`; RSFEC/PCS narrow counters are accumulated after clear-on-read accesses. Hardware state persists in FBNIC CSR registers for queue manager, packet buffers, MAC command config, PCS interrupt masks, pause storm timers, and TCAM enable state.

## Dependencies And Integration Points
This file depends on CSR definitions from `fbnic_csr.h` via `fbnic.h`, register access helpers, firmware mailbox helpers for TSENE sensor reads, `fbnic_net` state for FEC, and phylink callers in `fbnic_phylink.c`. PCI service work invokes pause storm handling, ethtool stats code reaches the stats hooks, and phylink calls prepare/get_link/link_up/link_down through the vtable.

## Risks
Many values are hardware-policy constants: FIFO partitioning, queue credits, calendar slots, and TX/RX thresholds. Wrong values can cause packet loss, BMC starvation, or flow-control deadlocks. PMD training relies on `jiffies` timing and barriers; races can report carrier before training is stable or leave it stuck initializing. Pause storm protection is only active when TX pause is enabled and a nonzero timeout exists, so config transitions must preserve the interrupt mask and timer reset behavior.

## Test Signals
Useful signals include successful probe register initialization, phylink carrier only after the four-second PMD training delay, correct FEC/AUI reporting from firmware modes, pause storm interrupt count increments and resets, ethtool MAC/RMON/FEC counter deltas, and sensor read success/failure paths including timeout and firmware error handling.
