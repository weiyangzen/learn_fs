# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_eth.c

## Purpose
`airoha_eth.c` is the main platform Ethernet driver for Airoha EN7581/AN7583-class SoCs. It initializes front-end switch/packet-engine registers, QDMA RX/TX rings, hardware forwarding buffers, interrupts, NAPI, per-GDM net_devices, DSA metadata, ethtool statistics, and traffic-control offloads for ETS, HTB, matchall police, and PPE flower rules.

## Important APIs, Types, and Functions
The file relies on private types from `airoha_eth.h`: `struct airoha_eth`, `struct airoha_qdma`, `struct airoha_queue`, `struct airoha_irq_bank`, `struct airoha_tx_irq_queue`, `struct airoha_gdm_port`, `struct airoha_hw_stats`, and SoC data/ops structures. Major functions cover MMIO helpers, front-end setup (`airoha_fe_init()` and helpers), QDMA RX/TX ring setup and cleanup, RX/TX NAPI, `airoha_irq_handler()`, netdev ops, DSA/PPE helpers, TC offload helpers, platform probe/remove, and SoC matching through `of_airoha_match`.

## Control Flow
Probe allocates `struct airoha_eth`, obtains SoC data, sets a 32-bit DMA mask, maps `fe` registers, gets reset controls, allocates a dummy threaded-NAPI net_device, initializes hardware and PPE, enables NAPI for QDMA queues, scans child `airoha,eth-mac` nodes, allocates GDM net_devices, and registers them. Open enables VIP/IFC forwarding, DSA STAG behavior, frame length, QDMA DMA, and PSE forwarding. Stop disables forwarding, resets TX subqueues, and when the final QDMA user stops, disables QDMA DMA and cleans TX rings.

RX allocates coherent descriptors and page-pool fragments, programs ring registers, and refills descriptors. RX IRQs disable per-ring interrupts and schedule NAPI. `airoha_qdma_rx_process()` consumes done descriptors, validates length/source port, builds or extends an skb, attaches DSA metadata, sets hash/PPE information, submits to GRO, and refills the ring. TX maps skb data/frags into QDMA descriptors with QoS, checksum, TSO, DSA, front-end port, and meter metadata; TX completion NAPI drains hardware completion queues, unmaps DMA, completes BQL, frees skbs, returns descriptors, and wakes shared netdev queues.

TC offload maps ETS to hardware scheduler/weights, HTB to egress TRTCM meters and extra queue IDs, matchall police to ingress meters, and flower to PPE callbacks.

## State and Persistence Behavior
Runtime state is in `struct airoha_eth` and child QDMA/GDM structures: MMIO bases, reset handles, SoC ops, state bits, QDMA queues, IRQ masks, page pools, coherent rings, hardware-forwarding buffers, netdevs, DSA metadata, PPE state, hardware counter snapshots, QDMA user counts, and per-port QoS bitmaps. No state is persisted to disk. Device tree persists port topology and MAC addresses; missing MACs are replaced with random addresses. Hardware counters are folded into software 64-bit stats and then cleared.

## Dependencies and Integration Points
The file depends on platform devices, OF, reset controls, reserved memory, coherent DMA, page_pool, NAPI, skbuff, DSA, dst metadata, ethtool, phylib ethtool helpers, traffic-control offload APIs, flow blocks, BQL, and private headers `airoha_regs.h` and `airoha_eth.h`. It integrates with `airoha_ppe.o` for PPE init/deinit, CPU-port programming, flow offload callbacks, and skb checks. Compatible strings are `airoha,en7581-eth`, `airoha,an7583-eth`, and child `airoha,eth-mac`.

## Risks and Edge Cases
RX scattered frames keep a partial `q->skb` across descriptors, so malformed descriptor sequences, invalid source ports, allocation failures, or too many fragments must free pages and partial skbs correctly. TX uses `dma_map_single()` for both linear data and `skb_frag_address()` fragments, which is worth reviewing against normal `skb_frag_dma_map()` expectations. Shared hardware queues require broad wakeups to avoid stalls. TC offload has strict hardware layout limitations and tick-dependent rate calculations. `airoha_qdma_init_qos_stats()` appears to program both CPU and forwarded counter configs through `REG_CNTR_CFG(i << 1)`, which may deserve review for a missing `+ 1`.

## Test Signals
Build with `CONFIG_NET_AIROHA`, `CONFIG_NET_AIROHA_NPU`, `CONFIG_NET_DSA`, `CONFIG_DEBUG_FS`, and `COMPILE_TEST` combinations. Runtime tests should cover probe/remove, reset handling, RX/TX on LAN/WAN GDM ports, jumbo MTU, checksum/TSO, DSA MTK tags, PPE hit/unbind paths, page-pool recycling, shared-QDMA open/stop, BQL stop/wake, ethtool MAC/RMON stats, hardware counter folding, and TC ETS/HTB/matchall/flower offloads including unsupported-action validation.
