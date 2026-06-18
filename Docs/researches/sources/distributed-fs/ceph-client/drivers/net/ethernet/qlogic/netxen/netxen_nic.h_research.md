# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic.h

Purpose: Central NetXen NIC driver header. It defines driver versioning, descriptor layouts, ring/context structures, firmware command ABI, board/flash constants, adapter state, minidump structures, function pointer hooks, lock helpers, and exported cross-file prototypes.

Important APIs and types: TX/RX descriptors include `cmd_desc_type0`, `rcv_desc`, and `status_desc` plus bitfield access macros for status and LRO completions. Host ring types include `nx_host_tx_ring`, `nx_host_rds_ring`, `nx_host_sds_ring`, and `netxen_recv_context`. Firmware context ABI types include `nx_hostrq_rx_ctx_t`, `nx_cardrsp_rx_ctx_t`, `nx_hostrq_tx_ctx_t`, and `nx_cardrsp_tx_ctx_t`. `struct netxen_adapter` is the main per-device object, combining PCI/netdev pointers, hardware context, ring configuration, callbacks, stats, firmware state, work items, coalescing config, and minidump state. Exported prototypes connect init, main, hardware, context, firmware, RX/TX, and ethtool modules.

Control flow: The header defines the contracts used by runtime files: main/init code allocates `netxen_adapter`, setup code fills callbacks and ring counts, context code allocates hardware rings and issues firmware context commands, data path uses descriptor macros, and ethtool reads/modifies fields through exported functions.

State and persistence behavior: Runtime persistent state is concentrated in `struct netxen_adapter`: link state, firmware version, flags/state bits, reset ownership, stats, ring counts, context IDs, DMA addresses, work items, MAC/IP lists, and minidump buffers. Flash/ROM constants identify persistent firmware and board data regions, but this header only names them.

Dependencies and integration points: Includes Linux PCI/netdevice/SKB/firmware/ethtool headers plus `netxen_nic_hdr.h` and `netxen_nic_hw.h`. It is the shared ABI between all NetXen source files and firmware CRB/CDRP interfaces.

Risks: Many structures are hardware/firmware ABI with explicit endian fields and alignment requirements; changing layout is dangerous. The header contains large sets of magic constants for board revisions, flash offsets, firmware commands, dump commands, and descriptor bitfields. Function pointers in `netxen_adapter` make revision-specific behavior indirect; setup must initialize them before use. `netxen_tx_avail()` relies on ring counters and a memory barrier.

Test signals: Compile all NetXen objects together, probe supported board revisions, create/destroy contexts, exercise TX/RX descriptors, firmware command paths, minidump setup/dump, ethtool operations, ring resize, and reset flows. Static checks should pay special attention to endian annotations and packed/aligned structure sizes.
