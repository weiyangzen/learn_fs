# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_cmn.c

## Purpose
`bnx2x_cmn.c` implements the common runtime body of the `bnx2x` driver: fast-path RX/TX processing, NAPI polling, IRQ setup, queue sizing, queue memory allocation, NIC load/unload, CNIC/FCoE queue bring-up, link reporting, RSS setup, netdev feature changes, MTU changes, PM suspend/resume, and several hardware context/coalescing helpers. It is the bridge between netdev callbacks and the lower-level hardware, firmware, slowpath, and link-management modules.

## Important APIs, Types, and Functions
- Queue and NAPI setup:
  - `bnx2x_calc_num_queues()` clamps requested/default RSS queues and forces a single queue in kdump.
  - `bnx2x_set_num_queues()` computes Ethernet plus CNIC queue counts.
  - `bnx2x_set_real_num_queues()` publishes real TX/RX queue counts to netdev, accounting for FCoE.
  - `bnx2x_add_all_napi()`, `bnx2x_add_all_napi_cnic()`, enable/disable helpers, and `bnx2x_poll()` wire NAPI to fastpath rings.
- TX completion and transmit:
  - `bnx2x_tx_int()` consumes hardware TX completions, frees descriptors/SKBs via `bnx2x_free_tx_pkt()`, completes BQL accounting, and wakes stopped queues when descriptors become available.
  - `bnx2x_start_xmit()` maps SKB data/frags, builds start/parse/data BDs, handles checksum/TSO/tunnel offloads, rings the doorbell, and stops the queue when descriptor space drops below `MAX_DESC_PER_TX_PKT`.
  - Helper paths include `bnx2x_xmit_type()`, `bnx2x_pkt_req_lin()`, `bnx2x_tx_split()`, parse-BD checksum/GSO helpers, and `bnx2x_select_queue()`.
- RX receive and aggregation:
  - `bnx2x_rx_int()` consumes completed CQEs up to NAPI budget, handles slowpath ramrod CQEs, normal packets, errors, VLAN tags, RX checksum, RX hash, PTP timestamps, and TPA start/stop.
  - `bnx2x_tpa_start()` and `bnx2x_tpa_stop()` manage LRO/GRO aggregation bins and SGE fragments.
  - `bnx2x_alloc_rx_data()`, `bnx2x_alloc_rx_sge()`, `bnx2x_fill_frag_skb()`, `bnx2x_build_skb()`, and `bnx2x_gro_receive()` implement buffer allocation and GRO handoff.
- Interrupts:
  - `bnx2x_enable_msix()`, `bnx2x_enable_msi()`, `bnx2x_setup_irqs()`, `bnx2x_req_msix_irqs()`, `bnx2x_free_irq()`, and `bnx2x_msix_fp_int()` manage MSI-X/MSI/INTx selection and fastpath scheduling.
  - `bnx2x_netif_start()` and `bnx2x_netif_stop()` sequence NAPI and interrupt enable/disable.
- Load/unload:
  - `bnx2x_nic_load()` is the main open/load path. It initializes queue state, allocates memory, negotiates MCP load, initializes hardware/function objects, requests IRQs, sets queues/RSS/MAC/VLAN/RX mode/PTP/link/DCB, starts TX, starts timers, and optionally loads CNIC.
  - `bnx2x_nic_unload()` is the main close/unload path. It marks management state, stops VF/CNIC/TX/timers/stats, drains TX, closes VF or PF chip resources, disables interrupts/NAPI, squeezes objects, frees SKBs/rings/memory, updates MCP state, and handles parity recovery flags.
  - `bnx2x_load_cnic()` brings up CNIC/FCoE-related queues after base NIC load.
- Memory management:
  - `bnx2x_alloc_mem_bp()`/`bnx2x_free_mem_bp()` allocate long-lived arrays for fastpaths, slowpath objects, stats, TX queues, MSI-X table, and ILT.
  - `bnx2x_alloc_fp_mem_at()`/`bnx2x_free_fp_mem_at()` allocate and free per-queue status blocks, TX rings, RX rings, CQ rings, SGE rings, and initial RX buffers.
  - `bnx2x_alloc_fw_stats_mem()`/`bnx2x_free_fw_stats_mem()` manage the firmware statistics request/data DMA buffer.
- Link, features, and misc:
  - `bnx2x_link_report()`, `__bnx2x_link_report()`, `bnx2x_get_mf_speed()`, and PHY lock helpers report carrier and speed/duplex/flow-control state.
  - `bnx2x_rss()` and `bnx2x_init_rss()` program RSS configuration through PF slowpath or VF/PF mailbox.
  - `bnx2x_setup_tc()` and `__bnx2x_setup_tc()` configure traffic classes and priority-to-COS mapping.
  - `bnx2x_change_mac_addr()`, `bnx2x_change_mtu()`, `bnx2x_fix_features()`, `bnx2x_set_features()`, `bnx2x_tx_timeout()`, `bnx2x_suspend()`, and `bnx2x_resume()` implement netdev/PM-facing callbacks.
  - `bnx2x_set_ctx_validation()`, `bnx2x_update_coalesce_sb_index()`, `bnx2x_get_c2s_mapping()`, and `bnx2x_schedule_sp_rtnl()` provide shared hardware/context utilities.

## Control Flow
Open/load flow:
1. `bnx2x_nic_load()` sets opening state, resets link-report cache, prepares ILT for PFs, zeroes fastpaths while preserving NAPI/TPA allocations, sizes RX buffers, allocates base and per-FP memory, allocates firmware stats memory, and initializes VF state if needed.
2. It updates real netdev queues, sets initial TC mapping, adds/enables NAPI, marks PF load, asks MCP for a load code or uses `bnx2x_load_count` when there is no MCP, checks firmware compatibility, initializes function objects and hardware.
3. It initializes pre-IRQ state, requests interrupts, performs post-IRQ init, initializes slowpath objects and SR-IOV, starts the function, sends `LOAD_DONE`, configures coalescing, sets up leading and nondefault queues, initializes RSS, configures MAC/VLAN/RX mode/PTP/link/DCB, starts TX, starts the periodic timer, loads CNIC if enabled, waits for slowpath completion, and returns open.

Receive flow:
1. An MSI-X fastpath interrupt disables the status block interrupt and schedules NAPI.
2. `bnx2x_poll()` completes TX first for all COS queues, then calls `bnx2x_rx_int()` if RX work exists.
3. `bnx2x_rx_int()` reads CQEs with an `rmb()` after the completion marker, dispatches slowpath events, TPA start/stop, or normal RX. Normal RX either copies tiny jumbo-mode packets or replaces the RX buffer, builds an SKB, sets protocol/hash/checksum/VLAN/timestamp metadata, and submits through GRO.
4. Producers are written back to firmware with `bnx2x_update_rx_prod()`, which uses a write barrier before posting producer values.

Transmit flow:
1. `bnx2x_start_xmit()` selects the TX queue from `skb_get_queue_mapping()`, checks descriptor availability, determines checksum/GSO/tunnel type, linearizes packets that violate firmware fetch limits, maps the linear segment, and builds start plus parse BDs.
2. For E2/E3 tunnel or checksum offloads it fills E2 parse descriptors and optional second parse descriptors; for E1x it fills E1x parse descriptors. It maps fragments into data BDs, records total packet size, updates BQL, increments packet producer, issues write barriers, updates doorbell producer, writes the doorbell, and optionally stops the queue.
3. `bnx2x_tx_int()` later observes hardware consumer status, frees all BDs/SKBs for completed packets, updates consumers, and wakes the queue under TX lock when space returns.

Unload flow:
1. `bnx2x_nic_unload()` marks OS/MFW state disabled, handles recovery special cases, changes state away from open before disabling TX, notifies VFs and CNIC, stops TX and timers, saves stats, drains TX unless in recovery, and closes VF or PF chip resources.
2. It squeezes remaining slowpath objects, clears SP state, frees SKBs/SGEs/TPA pools/FP memory/CNIC memory/base memory, marks closed, updates management version, and sets/reset recovery gate flags based on parity attentions.

## State and Persistence Behavior
- Mutates long-lived `struct bnx2x` fields: `state`, queue counts, `port.pmf`, `nic_stopped`, `cnic_loaded`, `force_link_down`, `last_reported_link`, `fw_seq`, `fw_drv_pulse_wr_seq`, `rx_ring_size`, `fw_stats_*`, `sp_state`, `sp_rtnl_state`, `lin_cnt`, PTP state, and multi-function config.
- Maintains per-queue producers/consumers for TX packets/BDs, RX BDs/CQEs/SGEs, status block indices, NAPI state, and TPA aggregation bins.
- Allocates and frees DMA-coherent descriptor/status/statistics rings and maps/unmaps SKB/page data for device DMA.
- Persists state into hardware and management firmware via MMIO registers, doorbells, shared-memory driver flags, OS driver state, load/unload commands, pulse mailbox, coalescing memory, RSS/classification ramrods, and link/DCB configuration.
- Uses memory barriers around hardware-owned rings and status blocks: `smp_rmb()` after TX status reads, `rmb()` after RX CQE completion markers/status-block reads, and `wmb()` before posting RX/TX producers and doorbells.

## Dependencies and Integration Points
- Linux networking: netdev queues, NAPI, GRO, VLAN acceleration, checksum offload, GSO/TSO, BQL, traffic classes, carrier state, feature negotiation, MTU changes, TX timeout, and PM hooks.
- Linux PCI/DMA/IRQ APIs: coherent allocations, streaming DMA mapping, MSI-X/MSI/INTx requests, power states, and config space.
- Driver internals: `bnx2x.h`, `bnx2x_cmn.h`, `bnx2x_init.h`, `bnx2x_sp.h`, link/PHY functions, stats, DCB, SR-IOV/VF-PF mailbox, CNIC interface, PTP helpers, and management firmware commands.
- Hardware firmware: status blocks, slowpath ramrods, RSS configuration, function state transitions, MCP load/unload protocol, shared memory, DCBX, AFEX, FCoE/iSCSI queues, and coalescing RAM.

## Risks
- Ordering bugs around status blocks, CQE markers, producer writes, or doorbells can cause missed interrupts, stale packet metadata, descriptor corruption, or permanent TX queue stalls.
- Error unwind in `bnx2x_nic_load()` spans many partially initialized subsystems; missing one cleanup step can leak DMA memory, leave NAPI registered, or keep MCP state inconsistent.
- TPA/GRO aggregation state depends on correct SGE replacement and page reference handling; allocation failures and DMA mapping failures must preserve ring consistency.
- TX offload descriptor construction is chip-generation dependent and handles VLANs, tunnels, IPv4/IPv6, TCP/UDP, GSO, and timestamping. Small mistakes can produce bad packets or firmware fetch violations.
- Queue shrinking after allocation failures moves fastpath/TX structures; bugs can leave stale pointers or mismatched queue indices.
- Multi-function, SR-IOV, CNIC/FCoE, storage-only personality, and recovery modes all change queue counts and cleanup behavior, increasing cross-feature regression risk.

## Test Signals
- Build tests across SR-IOV, DCB, PTP, FCoE/CNIC, and non-SR-IOV configs.
- Probe/open/close/reload cycles, including forced allocation failures where possible, validate load error paths and queue shrinking.
- RX/TX traffic under checksum, TSO/GSO, VLAN, VXLAN/Geneve encapsulation, jumbo MTU, LRO/GRO_HW, RSS, and multi-COS modes.
- Interrupt mode coverage for MSI-X multi-vector, single MSI-X fallback, MSI, and INTx.
- Stress tests for NAPI budget exhaustion, TX queue stop/wake, MTU/feature changes while running, suspend/resume, TX timeout recovery, parity recovery, and CNIC/FCoE load/unload.
- Hardware counters and netdev stats should show no RX checksum spikes, TX timeouts, DMA mapping leaks, or persistent stopped queues during sustained traffic.
