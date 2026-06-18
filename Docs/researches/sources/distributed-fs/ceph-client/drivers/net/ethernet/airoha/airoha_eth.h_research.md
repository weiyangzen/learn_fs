# sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_eth.h

## Purpose
`airoha_eth.h` is the shared internal interface for the Airoha Ethernet driver family. It defines QDMA ring sizing, GDM port constants, PPE flow-table geometry, hardware-offload table layouts, runtime device structures, MMIO helper wrappers, and exported cross-file entry points used by the main Ethernet, NPU, PPE, and debugfs code.

## Important APIs, types, and constants
- `AIROHA_MAX_*`, `TX_DSCP_NUM`, `RX_DSCP_NUM()`, `PPE_*_NUM_ENTRIES`, and `PPE_ENTRY_SIZE` define queue, descriptor, MTU, and hardware offload table dimensions.
- `struct airoha_queue`, `struct airoha_tx_irq_queue`, and `struct airoha_qdma` model TX/RX descriptor rings, interrupt completion queues, NAPI state, page-pool RX buffers, and per-QDMA MMIO state.
- `struct airoha_gdm_port` links a netdev to a QDMA, hardware GDM id, stats, QoS channel bitmap, DSA metadata, and CPU/forwarded TX counters.
- `struct airoha_foe_entry` and related `airoha_foe_*` structs encode the PPE forwarding/offload entry formats for bridge, IPv4, DS-Lite, and IPv6 routes. Bitfields such as `AIROHA_FOE_IB1_BIND_*` and `AIROHA_FOE_IB2_*` define hardware control words.
- `struct airoha_flow_table_entry` is the software shadow for offloaded flows, with rhashtable nodes, L2 subflow lists, stats, cookie, hash, type, and embedded FOE entry.
- `struct airoha_ppe`, `struct airoha_eth_soc_data`, and `struct airoha_eth` are the central device objects spanning FE registers, QDMA blocks, PPE state, NPU RCU pointer, resets, ports, and SoC-specific callbacks.
- MMIO helpers `airoha_rr()`, `airoha_wr()`, `airoha_rmw()` and wrappers such as `airoha_fe_rr()` and `airoha_qdma_wr()` standardize register access.
- Exported prototypes include PPE lifecycle/offload functions (`airoha_ppe_init()`, `airoha_ppe_deinit()`, `airoha_ppe_setup_tc_block_cb()`), flow-entry helpers, and optional debugfs initialization.

## Control flow and integration
This header is not executable by itself. It establishes the contracts used by `airoha_ppe.c`, `airoha_npu.c`, debugfs, and the Ethernet datapath. The main driver allocates `struct airoha_eth`, populates SoC data and ports, initializes QDMA/GDM state, then calls into PPE helpers using the declared APIs. PPE code uses the FOE layout definitions to translate tc/netfilter flow rules into hardware table entries. NPU and WLAN offload users reach the PPE through `struct airoha_ppe_dev`.

## State and persistence behavior
All state described here is volatile kernel runtime state: rings, NAPI, rhashtables, DMA buffers, stats, and RCU-managed NPU pointers. The header defines no persistent on-disk or firmware state. Hardware state persists only until reset/power-cycle and is represented through MMIO register writes elsewhere.

## Dependencies and integration points
The header depends on Linux networking, DSA, debugfs, page-pool/NAPI patterns, reset controls, and `linux/soc/airoha/airoha_offload.h`. It is tightly coupled to `airoha_regs.h` and to the PPE/NPU implementation files. DSA support and debugfs are conditional through kernel configuration.

## Risks and edge cases
The FOE structs are hardware ABI layouts; packing, field order, endian conversions, or `PPE_ENTRY_SIZE` changes can break offload silently. Queue sizes and descriptor-count macros must remain consistent with hardware limits. RCU access to `eth->npu`, spinlocks around queue/flow state, and stats synchronization are core correctness points. SoC version helpers currently encode specific EN7581/EN7583 behavior.

## Test signals
Useful validation includes compile coverage with Airoha Ethernet/PPE/NPU configs, boot/probe on EN7581/EN7583, QDMA RX/TX traffic, DSA port traffic, flowtable offload add/delete/stats, debugfs entry dumps, lockdep/RCU checks, and ethtool/netdev stats stability under traffic.
