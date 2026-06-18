# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-trans.h

Purpose: Defines the public/common transport-layer ABI, host command structures, RX buffer wrappers, transport configuration/state, debug/DRAM/PNVM structures, TX queue state, reset helpers, and PCIe registration hooks.

Important APIs and types: Key types include `struct iwl_rx_packet`, `struct iwl_device_cmd`, `struct iwl_device_tx_cmd`, `struct iwl_host_cmd`, `struct iwl_rx_cmd_buffer`, `struct iwl_trans_config`, `struct iwl_trans_txq_scd_cfg`, `struct iwl_trans_rxq_dma_data`, `struct iwl_pnvm_image`, `enum iwl_trans_state`, `struct iwl_trans_debug`, `struct iwl_txq`, `struct iwl_trans_info`, and `struct iwl_trans`. Inline helpers cover RX payload length, response freeing, RX page stealing/freeing, RB sizes, TXQ enable configs, memory read/write wrappers, reset scheduling, firmware-error notification, SW reset, top-reset support, and device-id extraction.

Control flow: Callers configure `trans->conf`, enter an opmode, start hardware/firmware, wait for alive, send host commands/TX, handle errors through `iwl_trans_fw_error()`, and stop/leave/free. Inline reset helpers set status bits and queue the restart worker.

State and persistence: `struct iwl_trans` is the central runtime state for firmware status, device info, debug buffers, PNVM/reduce-power flags, restart work, opmode pointer, and transport-private storage. TX queues hold DMA descriptors, SKBs, locks, watchdog timers, overflow queues, and byte-count tables.

Dependencies and integration points: Pulls in debug, config, firmware image/API headers, opmode definitions, and Linux firmware/lock/page APIs. It is the high-fanout contract between MVM/opmode code and PCIe backend code.

Risks: ABI fields are shared across many modules and backends. Command data flags impose ordering restrictions for NOCOPY/DUP chunks. RX buffer page ownership can leak or double-free if `_page_stolen` protocol is mishandled. Status bits drive concurrency-sensitive reset and firmware-error behavior. TX queue windows differ between hardware and software.

Test signals: Build all users, host command DMA chunk tests, RX response ownership tests, reset scheduling concurrency, TX queue watchdog/freeze/reclaim behavior, debug dump allocation, PNVM image chunk limits, and top-reset support matrix by device family/RF ID.
