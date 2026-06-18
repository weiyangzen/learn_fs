# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_cmn.h

## Purpose
`bnx2x_cmn.h` declares the common `bnx2x` driver API and defines shared inline helpers used by the common runtime, main driver, slowpath, link, ethtool, and optional offload paths. It is the public internal interface for NIC load/unload, queue setup, interrupts, memory allocation, netdev callbacks, CNIC integration, RSS, link reporting, filtering, hardware locks, and ring/status-block primitives.

## Important APIs, Types, and Functions
- Allocation macros:
  - `BNX2X_PCI_ALLOC`, `BNX2X_PCI_FALLOC`, and `BNX2X_PCI_FREE` wrap coherent DMA allocation/free for buffers addressed by firmware/hardware.
  - `BNX2X_FREE` frees normal kernel heap pointers and clears them.
- Lifecycle and hardware declarations:
  - `bnx2x_nic_load()`, `bnx2x_nic_unload()`, `bnx2x_chip_cleanup()`, `bnx2x_pre_irq_nic_init()`, `bnx2x_post_irq_nic_init()`, `bnx2x_alloc_mem()`, `bnx2x_free_mem()`, and CNIC variants.
  - MCP and firmware helpers such as `bnx2x_send_unload_req()`, `bnx2x_send_unload_done()`, `bnx2x_fw_command()`, `bnx2x_drv_pulse()`, and `bnx2x_compare_fw_ver()` through related headers/C file use.
- Queue and netdev operations:
  - `bnx2x_setup_queue()`, `bnx2x_setup_leading()`, `bnx2x_set_num_queues()`, `bnx2x_start_xmit()`, `bnx2x_select_queue()`, `bnx2x_tx_int()`, `bnx2x_change_mtu()`, `bnx2x_set_features()`, `bnx2x_tx_timeout()`, `bnx2x_setup_tc()`, and `__bnx2x_setup_tc()`.
- Link and filtering:
  - `bnx2x_initial_phy_init()`, `bnx2x_link_set()`, `bnx2x_force_link_reset()`, `bnx2x_link_test()`, `bnx2x__link_status_update()`, `bnx2x_link_report()`, `bnx2x_get_mf_speed()`, `bnx2x_set_eth_mac()`, `bnx2x_set_rx_mode_inner()`, and VLAN/MAC cleanup helpers.
- Interrupt/status-block inline helpers:
  - `bnx2x_update_rx_prod()` posts RX BD/CQE/SGE producers after a write barrier.
  - `bnx2x_igu_ack_sb_gen()`, `bnx2x_hc_ack_sb()`, `bnx2x_ack_sb()`, `bnx2x_hc_ack_int()`, `bnx2x_igu_ack_int()`, and `bnx2x_ack_int()` abstract HC versus IGU interrupt blocks.
  - `bnx2x_update_fpsb_idx()`, `bnx2x_has_tx_work_unload()`, `bnx2x_tx_avail()`, `bnx2x_tx_queue_has_work()`, `bnx2x_has_tx_work()`, and `bnx2x_has_rx_work()` read ring/status state.
- Ring and object inline helpers:
  - `bnx2x_free_rx_sge()`, NAPI deletion helpers, MSI disable, SGE mask initialization, `bnx2x_reuse_rx_data()`, `bnx2x_set_next_page_rx_bd()`, `bnx2x_free_rx_sge_range()`, and RX memory pool cleanup.
  - `bnx2x_func_start()`, `bnx2x_set_fw_mac_addr()`, `bnx2x_init_vlan_mac_fp_objs()`, `bnx2x_init_bp_objs()`, `bnx2x_init_txdata()`, CNIC ID helpers, `bnx2x_clean_tx_queue()`, `bnx2x_wait_sp_comp()`, `bnx2x_mtu_allows_gro()`, and management flag/link sync helpers.

## Control Flow
This header shapes several key flows:
- RX producer flow: callers replenish RX rings and call `bnx2x_update_rx_prod()`, which writes BD/CQE/SGE producers to USTORM memory only after descriptors and buffers are visible.
- Interrupt acknowledgement flow: callers use `bnx2x_ack_sb()` and `bnx2x_ack_int()` without duplicating HC/IGU differences; the helper derives IGU segment selection for backward-compatible versus normal interrupt modes.
- Queue work detection: NAPI and unload paths use `bnx2x_has_rx_work()`, `bnx2x_tx_queue_has_work()`, and `bnx2x_has_tx_work_unload()` to decide whether to poll, drain, or wait.
- Function start flow: `bnx2x_func_start()` prepares a slowpath function-start command, sets multi-function, BD-mode, network COS, tunnel port, inner RSS, and class-fail parameters, then calls the function state machine.
- Object initialization flow: `bnx2x_init_bp_objs()` and `bnx2x_init_vlan_mac_fp_objs()` connect slowpath objects to DMA ramrod buffers, pending bits, function IDs, client IDs, and credit pools.

## State and Persistence Behavior
- The allocation macros mutate pointer and DMA-address variables by clearing them on free and logging physical/virtual addresses when debug masks enable it.
- Inline helpers mutate fastpath ring producers/consumers, SGE masks, RX buffer metadata, status block acknowledgements, function start ramrod data, slowpath object state, credit pools, and management firmware shared-memory driver flags.
- Hardware-visible persistence occurs through MMIO writes to USTORM producer memory, HC/IGU acknowledgement registers, VLAN ethertype registers in BD mode, and shared-memory driver flags.
- `bnx2x_wait_sp_comp()` observes `bp->sp_state` under `netif_addr_lock_bh()` with memory barriers and waits for slowpath pending bits to clear, creating a synchronization point for filtering/object commands.

## Dependencies and Integration Points
- Includes Linux types, PCI, netdevice, etherdevice, and IRQ headers.
- Includes `bnx2x.h` for the primary state contract and `bnx2x_sriov.h` for SR-IOV declarations.
- Exports common functions implemented in `bnx2x_cmn.c` and functions implemented in other bnx2x compilation units (`bnx2x_main.c`, link, slowpath, stats, DCB, SR-IOV, ethtool, and self-test files).
- Integrates with netdev callbacks, CNIC offload control, firmware ramrods, management firmware shared memory, interrupt controller abstractions, and hardware ring memory.

## Risks
- The allocation/free macros assume the local variable name `bp` exists; using them outside that convention would break compilation or free through the wrong device.
- Ring helpers rely on exact producer/consumer arithmetic and next-page descriptor layout from `bnx2x.h`; any mismatch can corrupt hardware rings.
- Interrupt acknowledgement helpers must choose the correct HC/IGU path and segment, or interrupts can be lost or repeatedly asserted.
- `bnx2x_wait_sp_comp()` can time out if pending bits are not cleared by completion handling; callers must ensure interrupts/completions are still serviced while waiting.
- Inline object initialization encodes chip and multi-function policy; changes can affect MAC/VLAN/RSS credit accounting across PFs/VFs.

## Test Signals
- Compile coverage catches declaration drift between this header and implementation files.
- Runtime tests should verify RX producer updates, NAPI interrupt re-enable, TX drain on unload, function start ramrods, RSS setup, MAC/VLAN filtering, and CNIC/FCoE queue initialization.
- Interrupt-mode tests across HC/IGU and MSI-X/MSI/INTx validate acknowledgement helpers.
- Slowpath stress, including multicast/UC list updates and feature reloads, should not trigger `bnx2x_wait_sp_comp()` timeouts.
- Memory fault injection around coherent allocation and RX/TX buffer allocation should unwind without leaks or stale DMA mappings.
