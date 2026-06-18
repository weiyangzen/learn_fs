# sources/distributed-fs/ceph-client/include/linux/soc/airoha/airoha_offload.h

Purpose: This header defines Airoha network offload integration between Ethernet PPE/NPU providers and WLAN or network consumers. It covers PPE callbacks, NPU DMA descriptors, WLAN command IDs, IRQ helpers, and optional stubs when the Airoha drivers are not enabled.

Important APIs/types/functions: `struct airoha_ppe_dev` carries `setup_tc_block_cb` and `check_skb` operations plus private data. `airoha_ppe_get_dev`/`put_dev` acquire the PPE provider. `struct airoha_npu_rx_dma_desc` and `struct airoha_npu_tx_dma_desc` define packed RX/TX DMA descriptors with bit masks for length, done, packet ID, FOE ID, SID, radio/VAP/frame type, and TXWI data. `enum airoha_npu_wlan_set_cmd` and `enum airoha_npu_wlan_get_cmd` enumerate message IDs for PCIE addresses, descriptors, BA windows, token sizes, counters, DMA addresses, and NPU versions. `struct airoha_npu` conditionally contains device, regmap, per-core spinlocks/work items, IRQs, stats, and operation hooks.

Control flow: Consumers acquire PPE or NPU handles, call inline wrappers, and dispatch through provider operation tables. WLAN setup sends set/get messages, fetches queue addresses, and manages NPU IRQ state. PPE paths can inspect SKBs and attach TC block offload.

State and persistence: Runtime state is in provider-owned `priv`, NPU cores, spinlock-protected memory accesses, IRQ status, DMA rings, firmware/shared memory, and hardware stats. The header itself stores no state.

Dependencies and integration: Includes `skbuff`, `spinlock`, and `workqueue`; uses `struct device`, `regmap`, `gfp_t`, DMA addresses, and optional `CONFIG_NET_AIROHA`/`CONFIG_NET_AIROHA_NPU`. It integrates with netdev TC offload, WLAN datapaths, PPE flow offload, and NPU firmware messaging.

Risks and test signals: Inline wrappers assume operation pointers are valid after successful acquisition. Descriptor packing, endianness, and queue IDs are fragile. Test provider-disabled builds, module builds, SKB offload checks, TC setup, NPU reserved-memory initialization, IRQ enable/disable, DMA ring ownership, and firmware command round trips.
