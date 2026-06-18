# subset-b-004492 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_main.c

## Purpose

`igc_main.c` is the main Linux PCI Ethernet driver body for Intel I225/I226-class 2.5G controllers. It binds PCI IDs to the `igc` driver, allocates and registers the `net_device`, owns the `net_device_ops`, and coordinates the controller lifecycle from probe through open, traffic, reset, power management, PCI error recovery, and remove. It is also the central integration point for queue resources, DMA descriptor rings, NAPI, MSI/MSI-X/legacy interrupts, XDP and AF_XDP zero-copy, PTP timestamp delivery, traffic-control/TSN offloads, wake-on-LAN, filtering, statistics, and hardware register access.

## Important APIs, Types, and Functions

The exported or externally used driver entry points include `igc_open`, `igc_close`, `igc_reset`, `igc_up`, `igc_down`, `igc_reinit_locked`, `igc_update_stats`, `igc_has_link`, `igc_reinit_queues`, `igc_get_hw_dev`, `igc_rd32`, `igc_setup_tx_resources`, `igc_setup_rx_resources`, `igc_free_tx_resources`, `igc_free_rx_resources`, `igc_flush_tx_descriptors`, `igc_get_tx_ring`, `igc_add_nfc_rule`, `igc_del_nfc_rule`, `igc_enable_empty_addr_recv`, `igc_disable_empty_addr_recv`, and the ring enable/disable helpers. The file registers `igc_netdev_ops`, `igc_driver`, `igc_err_handler`, and PM ops, then wires them into `module_init`/`module_exit`.

Core state is carried by `struct igc_adapter`, `struct igc_hw`, `struct igc_ring`, `struct igc_q_vector`, `struct igc_tx_buffer`, `struct igc_rx_buffer`, `struct igc_nfc_rule`, `struct igc_flex_filter`, `struct igc_metadata_request`, and timestamp/TSN state embedded in the adapter and rings. The file relies heavily on descriptor unions such as `union igc_adv_tx_desc` and `union igc_adv_rx_desc`, hardware register macros from the igc headers, and state bits such as `__IGC_DOWN`, `__IGC_RESETTING`, and `__IGC_TESTING`.

Major functional groups are:

- Probe and lifetime: `igc_probe`, `igc_remove`, `igc_init_module`, `igc_exit_module`.
- Netdev lifecycle: `__igc_open`, `igc_open`, `__igc_close`, `igc_close`, `igc_up`, `igc_down`, `igc_reset`, `igc_reinit_locked`, `igc_reset_task`.
- Queue resources: `igc_setup_all_tx_resources`, `igc_setup_all_rx_resources`, `igc_configure_tx_ring`, `igc_configure_rx_ring`, `igc_alloc_q_vector`, `igc_alloc_q_vectors`, `igc_clear_interrupt_scheme`.
- Tx path: `igc_xmit_frame`, `igc_xmit_frame_ring`, `igc_tso`, `igc_tx_csum`, `igc_tx_map`, `igc_clean_tx_irq`, `igc_xdp_init_tx_descriptor`, `igc_xdp_xmit`, `igc_xdp_xmit_zc`.
- Rx path: `igc_clean_rx_irq`, `igc_clean_rx_irq_zc`, `igc_alloc_rx_buffers`, `igc_alloc_rx_buffers_zc`, `igc_build_skb`, `igc_construct_skb`, `igc_process_skb_fields`, `igc_rx_checksum`, `igc_rx_hash`, `igc_rx_vlan`.
- Interrupts and NAPI: `igc_request_irq`, `igc_request_msix`, `igc_intr`, `igc_intr_msi`, `igc_msix_ring`, `igc_msix_other`, `igc_poll`, `igc_irq_enable`, `igc_irq_disable`, `igc_set_itr`, `igc_update_itr`, `igc_update_ring_itr`.
- Filtering and receive mode: `igc_set_rx_mode`, multicast programming, RAR MAC filters, VLAN priority filters, ethertype filters, flex filters, and NFC rule list management.
- TSN and traffic control: `igc_setup_tc`, `igc_tsn_enable_qbv_scheduling`, `igc_tsn_enable_launchtime`, `igc_tsn_enable_cbs`, `igc_tsn_enable_mqprio`, `igc_qbv_scheduling_timer`.
- XDP metadata and AF_XDP: `igc_bpf`, `igc_xsk_wakeup`, `igc_xdp_rx_hash`, `igc_xdp_rx_timestamp`, `igc_xsk_tx_metadata_ops`.
- PM and recovery: `__igc_shutdown`, `__igc_resume`, runtime suspend/resume/idle, system suspend/resume/shutdown, and PCI AER callbacks.

## Control Flow

Module load calls `pci_register_driver`, allowing PCI probe to match one of the IGC/I225/I226 IDs. `igc_probe` enables the PCI memory device, configures DMA, requests BARs, optionally enables PTM, allocates a multiqueue Ethernet device, maps MMIO, copies MAC/PHY ops from the board info, obtains hardware invariants, assigns netdev features, initializes software queues and interrupts, resets hardware, validates NVM if flash is present, reads or accepts the MAC address, initializes timers/work items/PTP/TSN/FPE, resets again, claims hardware control from firmware, and registers the netdev.

Interface open flows through `igc_open` into `__igc_open`: set real queue counts, runtime-PM resume, allocate Tx and Rx descriptor resources, power up and set up the copper link, configure hardware registers and rings, request interrupts, enable NAPI, enable interrupts, start Tx queues, and schedule the watchdog. The `igc_up` path is a related post-reset bring-up path that reconfigures hardware, enables NAPI/interrupts, starts queues, and schedules link handling.

The normal Tx path starts at `ndo_start_xmit` (`igc_xmit_frame`). It pads tiny frames, selects a Tx ring from `skb->queue_mapping`, reserves descriptors, optionally computes TSN launch time and inserts an empty frame, records the first Tx buffer, rejects packets during Qbv transitions or gate closure, enforces `max_sdu`, allocates hardware timestamp slots if requested, handles VLAN flags and preemption padding, emits TSO or checksum context descriptors, maps skb linear/frags to DMA descriptors, applies memory barriers, updates `next_to_use`, and rings the hardware tail. Completion is handled in `igc_clean_tx_irq`, which walks completed descriptors by `next_to_watch`, accounts stats, frees SKBs/XDP frames or completes XSK frames, detects hangs, and wakes stopped queues when descriptors return.

The normal Rx path is NAPI-driven through `igc_poll`. `igc_clean_rx_irq` reads completed Rx descriptors, observes `dma_rmb`, syncs page-backed DMA buffers for CPU, handles inline timestamp headers, handles FPE mPackets, runs XDP if no partial skb is in progress, converts pass traffic into SKBs, handles non-EOP multi-buffer packets, validates headers, applies checksum/hash/VLAN metadata, sends packets to GRO, recycles or frees pages, replenishes descriptors, finalizes XDP TX/redirect, and updates per-ring stats. If a ring is backed by an AF_XDP zero-copy pool, `igc_clean_rx_irq_zc` uses `xsk_buff` buffers and dispatches pass packets via a zero-copy-specific SKB copy path.

Interrupt setup prefers MSI-X. MSI-X has one "other" vector for link/reset/timestamp causes plus queue vectors for NAPI. If MSI-X allocation or request fails, the driver falls back to MSI and then shared legacy interrupt. Interrupt handlers read ICR/EICR-equivalent causes, schedule reset or watchdog work on DRSTA/link events, process timestamp interrupts, write ITR when needed, and schedule NAPI. NAPI completion re-enables ring interrupts.

Close and down paths stop traffic in the opposite order. `igc_down` sets `__IGC_DOWN`, suspends PTP, disables hardware Rx/Tx and interrupts, stops carrier and queues, synchronizes and disables NAPI, deletes timers, snapshots stats, resets hardware if the PCI channel is usable, disables hardware rings, cleans software rings, and stops FPE verification. `__igc_close` then releases firmware control, frees IRQs, and frees descriptor resources.

The watchdog is the slow-path coordinator for link changes, stats, hang detection, allocation failure wakeups, PTP Tx hang checks, and periodic rescheduling. Link-up handling resumes runtime PM, reads speed/duplex, logs flow-control mode, disables EEE for half-duplex, checks downshift, adjusts Tx timeout factors and TSN txtime offsets, handles FPE link state, waits for 1000BASE-T remote receiver OK when needed, turns carrier on, and schedules PHY info refresh. Link-down handling clears speed/duplex, carrier, FPE link state, schedules PHY info refresh, and asks runtime PM to suspend after a delay.

Traffic-control setup routes `TC_SETUP_QDISC_TAPRIO`, `ETF`, `CBS`, and `MQPRIO` to TSN helpers. Taprio/Qbv schedule validation rejects unsupported cycle extensions, future base times on i225, unsupported commands, and repeated gate reopening cases. Saved Qbv state updates adapter `base_time`, `cycle_time`, per-ring gate windows, `max_sdu`, preemption settings, and transition flags. CBS is restricted to the top two queues and enforces enable/disable ordering. MQPRIO requires one traffic class per Tx queue and a priority-preserving mapping.

Suspend/shutdown closes the device if running, clears interrupts, configures wake filters, may power down the PHY, releases firmware control, and disables PCI. Resume restores PCI state, reinitializes interrupts, resets hardware, reclaims firmware control, delivers stored wake packets if present, and reopens the netdev when it was running. PCI error recovery detaches the netdev, downs the adapter, disables PCI, re-enables and resets the slot, then reopens and reattaches.

## State and Persistence Behavior

Persistent hardware state includes PCI config, MMIO registers, descriptor base/tail/head registers, receive address registers, multicast table, wake filters, PTP/TSN registers, NVM-derived MAC address, and PHY state. Runtime state lives mostly in `struct igc_adapter` and its rings: descriptor memory, DMA addresses, `next_to_use/clean/alloc`, NAPI vectors, interrupt masks, per-ring flags, XDP program pointer, AF_XDP pools, timestamp request slots, NFC rule list, stats counters, TSN schedule fields, timers, and work items.

The driver uses memory barriers around descriptor ownership transitions: `wmb` before tail writes on Tx/Rx/XDP paths, `dma_rmb` after seeing Rx descriptor length, and `smp_rmb` before consuming Tx completion status. It uses `u64_stats_sync` for per-ring stats, `spin_lock_irqsave` for PTP timestamp and Qbv gate transition state, mutex protection for NFC rules, RCU for q_vector freeing and XDP program access, RTNL around reset/recovery flows, and atomic state bits for down/reset/test coordination.

The file does not persist configuration to disk. Configuration persists only across driver runtime in kernel memory or in hardware registers until reset/power transition. NVM is read but not written from this file. On reset and reopen, many features are replayed from adapter state into hardware: VLAN mode, MAC/default filters, NFC rules, queues, PTP, TSN, EEE settings, and receive mode.

## Dependencies and Integration Points

This file depends on Linux PCI, DMA mapping, netdevice, NAPI, GRO, skb, XDP, AF_XDP, BPF, PTP, ethtool, traffic-control, runtime PM, hrtimer, timers/workqueues, and MDIO-related infrastructure. Internal igc dependencies include `igc.h`, `igc_hw.h`, `igc_tsn.h`, `igc_xdp.h`, and functions from MAC/base/PHY/NVM/PTP/TSN/FPE/ethtool/LED modules, such as `igc_get_invariants`, `igc_set_eee_i225`, `igc_ptp_init/reset/stop/suspend`, `igc_tsn_offload_apply`, `igc_xdp_set_prog`, `igc_xdp_setup_pool`, `igc_fpe_*`, `igc_led_setup/free`, and MAC/PHY ops stored in `hw->mac.ops` and `hw->phy.ops`.

External integration surfaces include the PCI driver core, `net_device_ops`, ethtool operations, XDP metadata kfunc-style callbacks, AF_XDP metadata callbacks, TC offload callbacks, PM callbacks, PCI error handlers, wake-on-LAN, and the kernel logging/statistics interfaces. Hardware integration is almost entirely through MMIO register reads/writes and coherent DMA descriptor rings.

## Risks and Edge Cases

Descriptor ownership is the highest-risk area. Incorrect barriers, `next_to_*` updates, DMA unmapping, XDP frame lifetime, or AF_XDP completion timing can cause data corruption, leaks, double-free, queue stalls, or device hangs. The XSK timestamp path deliberately holds completions while hardware timestamps are pending, so timestamp loss or lock ordering mistakes can stall zero-copy Tx.

Reset/open/close paths are concurrency-sensitive because watchdog work, interrupt handlers, runtime PM, PCI error recovery, TC reconfiguration, XDP setup, and user-triggered MTU/features changes can intersect. The state bits and RTNL usage reduce the race window, but changes in these paths need testing under repeated reset, suspend, and hot-unplug conditions.

Filter programming has partial-failure risk. `igc_enable_nfc_rule` may add earlier hardware filters before a later filter type fails, and callers need to account for cleanup semantics. Flex filters depend on length alignment, WUFC/WUFC_EXT bit selection, and byte/mask packing; off-by-one errors would produce silent misclassification.

TSN/Qbv behavior is highly stateful. Future base time restrictions differ for i225/i226, launch-time scheduling relies on PTP time and per-ring cycle tracking, gate-closed checks can intentionally drop packets, and schedule transitions are protected by `qbv_tx_lock`. Changes need both functional and timing validation.

Power management and wake paths manipulate receive mode and wake registers after closing the netdev. Regressions can break WoL, runtime suspend, wake packet delivery, or firmware ownership. `igc_rd32` detaches the netdev on all-ones MMIO reads, so callers must tolerate device removal.

## Test Signals

Useful validation includes successful kernel build with the igc driver enabled, modprobe/probe on I225/I226 hardware, `ip link set up/down`, MTU changes including jumbo and XDP-incompatible jumbo rejection, throughput and checksum/TSO/GSO tests, VLAN tag offload tests, RSS distribution, multicast/promiscuous/allmulti receive-mode tests, ethtool stats and register dump sanity, PTP timestamp Tx/Rx tests, suspend/resume and runtime PM tests, wake-on-LAN tests, PCI error injection where available, and hot-unplug or forced MMIO failure tests.

XDP-specific signals include attaching/detaching XDP programs, XDP_PASS/DROP/TX/REDIRECT behavior, `ndo_xdp_xmit`, AF_XDP zero-copy sockets, need-wakeup behavior, XDP metadata hash/timestamp reads, and XSK Tx metadata timestamp/launch-time requests. TSN signals include `tc taprio`, `etf`, `cbs`, and `mqprio` setup success/failure cases, invalid schedule rejection, packet drops for closed gates/max SDU, launch-time behavior around cycle boundaries, FPE preemptible queue behavior, and queue reinit restoring the default schedule.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_nvm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_nvm.c

## Purpose

`igc_nvm.c` implements the small NVM/EEPROM support layer used by the igc hardware abstraction. It provides register-driven EEPROM reads through EERD, reads the permanent MAC address from receive address registers, validates the NVM checksum, and updates the checksum through the configured NVM write operation.

## Important APIs, Types, and Functions

The public functions are `igc_read_nvm_eerd`, `igc_read_mac_addr`, `igc_validate_nvm_checksum`, and `igc_update_nvm_checksum`. The file-private helper `igc_poll_eerd_eewr_done` waits for EERD/EEWR completion. It operates on `struct igc_hw`, especially `hw->nvm`, `hw->nvm.ops`, and `hw->mac.addr/perm_addr`.

Key hardware macros and registers include `IGC_EERD`, `IGC_EEWR`, `IGC_NVM_POLL_READ`, `IGC_NVM_RW_REG_START`, `IGC_NVM_RW_REG_DONE`, `IGC_NVM_RW_ADDR_SHIFT`, `IGC_NVM_RW_REG_DATA`, `IGC_RAL(0)`, `IGC_RAH(0)`, `IGC_RAL_MAC_ADDR_LEN`, `IGC_RAH_MAC_ADDR_LEN`, `NVM_CHECKSUM_REG`, and `NVM_SUM`.

## Control Flow

`igc_read_nvm_eerd` first validates `offset` and `words` against `hw->nvm.word_size`, rejecting zero-length and out-of-bounds requests. For each requested word it builds an EERD command with the word offset and start bit, writes it to `IGC_EERD`, polls for `IGC_NVM_RW_REG_DONE`, and extracts the returned 16-bit word from the EERD data field.

`igc_poll_eerd_eewr_done` loops up to 100000 attempts, reading either `IGC_EERD` or `IGC_EEWR` depending on whether the caller is polling a read or write path. It waits 5 microseconds between attempts and returns `0` when the done bit appears or `-IGC_ERR_NVM` on timeout.

`igc_read_mac_addr` reads RAL0 and RAH0 and decodes six bytes into `hw->mac.perm_addr`, then copies them into the active `hw->mac.addr`. It does not read EEPROM directly; it trusts the MAC address registers already initialized by hardware or earlier init.

`igc_validate_nvm_checksum` reads words `0..NVM_CHECKSUM_REG` through `hw->nvm.ops.read`, accumulates a 16-bit checksum, and requires the final sum to equal `NVM_SUM`. `igc_update_nvm_checksum` sums words before the checksum register, computes `NVM_SUM - checksum`, and writes that value through `hw->nvm.ops.write`.

## State and Persistence Behavior

The file reads persistent NVM contents but only `igc_update_nvm_checksum` writes persistent state, and even that delegates to the NVM ops configured elsewhere. The checksum routines rely on the NVM operation table rather than hard-coding the write mechanism. `igc_read_mac_addr` updates in-memory MAC fields from hardware registers. Polling uses synchronous busy waits and does not maintain state between calls.

## Dependencies and Integration Points

This file includes `igc_mac.h` and `igc_nvm.h` and depends on the low-level register access macros `rd32`/`wr32`, delay helpers, and error constants from the igc hardware layer. `igc_probe` in `igc_main.c` uses NVM validation when flash is present and uses the MAC read op when no platform MAC address is supplied. Hardware-specific invariant setup assigns these functions into `hw->nvm.ops` and `hw->mac.ops`.

## Risks and Edge Cases

The EERD/EEWR polling loop can spin for up to roughly 500 ms per operation in failure cases. Any incorrect `word_size` setup can reject valid reads or allow invalid offsets. `igc_read_nvm_eerd` returns partial data if a later word fails, so callers must honor the return code. Checksum update correctness depends on `hw->nvm.ops.write` being implemented and safe for the platform. `igc_read_mac_addr` reads receive address registers rather than EEPROM words, so it depends on hardware initialization having loaded those registers correctly.

## Test Signals

Validation signals include successful NVM checksum validation during probe, expected failure on deliberately corrupted checksum images, correct MAC address reporting when platform firmware does not provide one, timeout handling when EERD/EEWR completion is blocked, bounds tests for zero words and offset overflow, and checksum update tests on hardware or emulation that supports safe NVM writes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_nvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_nvm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_nvm.h

## Purpose

`igc_nvm.h` declares the NVM helper interface implemented by `igc_nvm.c`. It is the public header used by the igc hardware setup code to expose EEPROM read, MAC address read, checksum validate, and checksum update helpers.

## Important APIs, Types, and Functions

The header declares `igc_read_mac_addr`, `igc_read_nvm_eerd`, `igc_validate_nvm_checksum`, and `igc_update_nvm_checksum`. All functions operate on `struct igc_hw`; `igc_read_nvm_eerd` also takes a word offset/count and output buffer. The header uses the igc signed status type `s32` and integer types such as `u16`, which are supplied by includers through the driver header stack.

## Control Flow

There is no executable control flow in this header. It is protected by `_IGC_NVM_H_` include guards and makes the NVM routines available to files that configure or consume `hw->nvm.ops` and `hw->mac.ops`.

## State and Persistence Behavior

The header owns no state. The declared functions read or update hardware/NVM state via `struct igc_hw`, but persistence behavior is entirely in the implementation and the operation tables wired by hardware-specific code.

## Dependencies and Integration Points

The header is included by `igc_nvm.c` and any igc hardware module that needs to assign these helpers into operation tables or call them directly. It intentionally contains only prototypes, keeping hardware register details in the C file and shared igc headers.

## Risks and Edge Cases

Because the header does not include the defining type headers itself, include ordering must ensure `struct igc_hw`, `s32`, and `u16` are visible. Prototype changes here must stay synchronized with operation table signatures and all call sites.

## Test Signals

Compile coverage is the main signal. Any signature drift should fail builds in modules that include this header or assign the functions into ops tables. Runtime behavior is covered through the `igc_nvm.c` tests and probe-time NVM/MAC flows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_nvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_phy.c

## Purpose

`igc_phy.c` implements PHY-level support for copper igc devices. It handles PHY reset checks, PHY ID discovery, link polling, copper power up/down, autonegotiation advertisement, copper link setup, MDIC and XMDIO register access, GPY register read/write dispatch, and gPHY firmware version reads.

## Important APIs, Types, and Functions

Public functions are `igc_check_reset_block`, `igc_get_phy_id`, `igc_phy_has_link`, `igc_power_up_phy_copper`, `igc_power_down_phy_copper`, `igc_check_downshift`, `igc_phy_hw_reset`, `igc_setup_copper_link`, `igc_write_phy_reg_gpy`, `igc_read_phy_reg_gpy`, and `igc_read_phy_fw_version`. Private helpers include `igc_phy_setup_autoneg`, `igc_wait_autoneg`, `igc_copper_link_autoneg`, `igc_read_phy_reg_mdic`, `igc_write_phy_reg_mdic`, `__igc_access_xmdio_reg`, `igc_read_xmdio_reg`, and `igc_write_xmdio_reg`.

The code operates on `struct igc_hw`, `struct igc_phy_info`, and `struct igc_fc_info`. It uses PHY operation callbacks in `hw->phy.ops` for register access and semaphore acquisition/release. Important registers and bit fields include `IGC_MANC`, `IGC_CTRL`, `IGC_I225_PHPM`, `IGC_MDIC`, `PHY_ID1`, `PHY_ID2`, `PHY_STATUS`, `PHY_CONTROL`, `PHY_AUTONEG_ADV`, `PHY_1000T_CTRL`, `IGC_ANEG_MULTIGBT_AN_CTRL`, `IGC_MMDAC`, `IGC_MMDAAD`, and `IGC_GPHY_VERSION`.

## Control Flow

`igc_check_reset_block` reads the management-control register and reports `IGC_ERR_BLK_PHY_RESET` when firmware has blocked PHY reset. `igc_phy_hw_reset` uses that check, acquires the PHY semaphore, asserts and clears `IGC_CTRL_PHY_RST`, waits for `IGC_PHY_RST_COMP` in `IGC_I225_PHPM`, logs timeout if the completion bit never arrives, then releases the semaphore.

`igc_get_phy_id` reads the standard PHY ID registers, builds `phy->id` from `PHY_ID1` and masked `PHY_ID2`, and stores the revision bits. `igc_phy_has_link` polls `PHY_STATUS`, intentionally reading twice per iteration because link bits may be sticky, and returns a boolean success flag based on whether link was observed before the iteration limit.

Copper link setup starts in `igc_setup_copper_link`, which calls `igc_copper_link_autoneg`, then polls link briefly. Autoneg setup masks `phy->autoneg_advertised` with `phy->autoneg_mask`, defaults to full mask when no advertisement is set, programs 10/100 advertisement bits, 1000 full-duplex bits, 2500 full-duplex bits via MMD register 7.32, and flow-control pause/asymmetric-pause bits according to `hw->fc.current_mode`. It restarts autoneg in `PHY_CONTROL` and optionally waits for completion. Once link is detected, setup configures collision distance and flow control after link up.

MDIC access validates the register offset, writes `IGC_MDIC` with PHY address, register offset, and read/write opcode, then polls `IGC_MDIC_READY` up to `IGC_GEN_POLL_TIMEOUT` with 50 microsecond waits. It returns `-IGC_ERR_PHY` on timeout or MDIC error. GPY access dispatches based on the encoded MMD device address in the offset: normal MDIC accesses are protected by `phy->ops.acquire/release`, while MMD/XMDIO accesses use the `IGC_MMDAC`/`IGC_MMDAAD` address-data sequence.

Power helpers simply clear or set `MII_CR_POWER_DOWN` in `PHY_CONTROL`, with a short delay after power down. `igc_check_downshift` currently records that speed downshift is unsupported by clearing `phy->speed_downgraded`. `igc_read_phy_fw_version` reads `IGC_GPHY_VERSION` and returns zero with a debug message on read failure.

## State and Persistence Behavior

The file mutates PHY hardware registers, PHY info fields (`id`, `revision`, `speed_downgraded`, autoneg advertisement), MAC link-status state indirectly through setup flows, and flow-control advertisement bits. Register changes persist until PHY reset, MAC reset, power transition, or another driver/firmware operation changes them. The code uses PHY semaphores for MDIC and reset paths where required, but XMDIO access is expressed in terms of PHY ops and relies on those ops for necessary serialization.

## Dependencies and Integration Points

This file includes `linux/bitfield.h` and `igc_phy.h`, which includes `igc_mac.h`. It depends on generic MII constants, igc register macros, delay helpers, `FIELD_GET`, low-level register I/O, and higher-level MAC helpers `igc_config_collision_dist` and `igc_config_fc_after_link_up`. It is called from hardware init, reset, link setup, watchdog/link code, and any code using `hw->phy.ops.read_reg/write_reg` for GPY devices.

## Risks and Edge Cases

PHY reset can be blocked by management firmware; this implementation treats reset-block as a nonfatal no-op in `igc_phy_hw_reset`, so callers expecting a physical reset must account for that. MDIC access can timeout or report hardware errors, and offset validation only applies after GPY offsets are stripped to the low register field. Autoneg programming must keep advertisement masks synchronized with supported hardware; unsupported half-duplex 1000/2500 requests are only logged and not programmed. Flow-control advertisement depends on `hw->fc.current_mode`, and invalid values return `-IGC_ERR_CONFIG`. XMDIO access must restore `IGC_MMDAC` to zero; failures in that cleanup path propagate and can leave the address/data function selected.

## Test Signals

Useful tests include PHY ID read during probe, link-up/link-down detection across all supported speeds, autoneg advertisement changes via ethtool, flow-control mode combinations, reset-block scenarios with management firmware, suspend/resume PHY power transitions, MDIC timeout/error injection, MMD/2.5G advertisement reads/writes, and watchdog link messages showing correct speed/duplex/flow-control state. Regression tests should include repeated reset/open/close cycles and link partner changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_phy.h

## Purpose

`igc_phy.h` declares the copper PHY helper interface for the igc driver. It exposes PHY reset, ID, link, power, autoneg/link setup, GPY register access, and firmware-version helpers to the rest of the driver.

## Important APIs, Types, and Functions

The header declares `igc_check_reset_block`, `igc_phy_hw_reset`, `igc_get_phy_id`, `igc_phy_has_link`, `igc_check_downshift`, `igc_setup_copper_link`, `igc_power_up_phy_copper`, `igc_power_down_phy_copper`, `igc_write_phy_reg_gpy`, `igc_read_phy_reg_gpy`, and `igc_read_phy_fw_version`. These functions all operate on `struct igc_hw` except the scalar arguments used for polling and register offsets/data. The header includes `igc_mac.h`, which supplies the hardware structure and shared MAC/PHY definitions used by the prototypes.

## Control Flow

There is no executable control flow in this header. Include guards prevent multiple inclusion, and the declarations let MAC/base/link code wire these helpers into operation tables or call them directly.

## State and Persistence Behavior

The header owns no state. Its declared functions can mutate PHY registers and `struct igc_hw` PHY fields, but those effects are implemented in `igc_phy.c` and through hardware operation callbacks.

## Dependencies and Integration Points

The header is consumed by `igc_phy.c` and other igc modules responsible for hardware initialization, link setup, reset, and power management. Because it includes `igc_mac.h`, it sits in the shared hardware-abstraction header stack rather than being a standalone Linux PHY API header.

## Risks and Edge Cases

Prototype changes must stay aligned with `struct igc_phy_operations` assignments and all call sites. Including `igc_mac.h` from this header couples PHY declarations to MAC definitions; circular include changes in nearby headers can break compilation.

## Test Signals

Compile coverage is the primary signal for this header. Runtime signals come from the implementation: probe-time PHY discovery, link setup, reset, power management, and GPY register access tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_phy.h -->
