# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc.h

Purpose: Shared internal header for ENETC drivers. It defines core data structures, ring helpers, feature flags, SI/private state, active offloads, exported function prototypes, CBDR helpers, and conditional QoS stubs used by PF, VF, ENETC4, ethtool, QoS, and PTP code.

Important types and APIs: Defines TX/RX software buffer descriptors, skb private control block, LSO metadata, ring statistics, XDP data, descriptor-ring resources, `struct enetc_bdr`, `struct enetc_cbdr`, `struct enetc_si`, `struct enetc_int_vector`, `struct enetc_ndev_priv`, classifier rule storage, PSFP capabilities, active offload flags, and interrupt coalescing modes. Inline helpers handle ring index wraparound, unused descriptor counts, RX descriptor addressing with optional extension descriptors, SI private-data alignment, PF detection, pseudo-MAC detection, CBDR DMA data allocation, and conditional PTP clock selection.

Control flow and state: The header encodes ring lifecycle assumptions used by `enetc.c`: `next_to_use`, `next_to_clean`, and `next_to_alloc` track producer/consumer and page reuse state; active offload flags drive timestamping, Qbv/Qci/Qbu, checksum, and LSO behavior; XDP reserves TX rings from the same TX ring array; `ENETC_TX_DOWN` and one-step timestamp bits coordinate queue state and serialized timestamp work.

Dependencies and integration points: Pulls in PCI, netdevice, DMA mapping, skb, ethtool, NTMP, VLAN, phylink, DIM, XDP, and ENETC hardware headers. The prototypes link the common core to variant-specific PF/VF/ENETC4 modules, ethtool code, CBDR/NTMP code, and optional QoS implementation.

Risks: Structure fields define ownership and cacheline-sensitive state, so changes can affect performance and concurrency. Descriptor count helpers assume one slot remains unused. XDP TX queue reservation reduces stack-visible TX queues and must stay consistent with `enetc_num_stack_tx_queues()`. Conditional QoS stubs return success for PSFP enable/disable when QoS is disabled, which callers must interpret carefully.

Test signals: Compile matrix for QoS enabled/disabled, PTP timer variants, PF/VF/ENETC4; ring index wrap tests; XDP queue reservation tests; descriptor extended-mode RX timestamp tests; and ABI/build checks for all exported prototypes.
