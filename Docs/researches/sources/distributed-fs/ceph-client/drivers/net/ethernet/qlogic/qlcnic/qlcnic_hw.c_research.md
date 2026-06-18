# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hw.c

## Purpose

`qlcnic_hw.c` implements low-level 82xx-oriented hardware access and control-plane helpers for the QLogic qlcnic Ethernet driver. It translates CRB and memory offsets into BAR0 windowed accesses, arbitrates PCIe semaphores, sends firmware request descriptors through TX ring 0, manages station/multicast/MAC-learning filter programming, configures offloads such as RSS/LRO/coalescing/VXLAN-related receive modes indirectly through firmware, and exposes suspend/resume/shutdown hooks used by the main PCI driver.

This file is the bridge between higher-level netdev lifecycle code and device-specific firmware/register mechanisms. Most exported functions are invoked through `struct qlcnic_hardware_ops` or `struct qlcnic_nic_template` assignments in `qlcnic_main.c`.

## Important APIs, Types, And Functions

- `struct qlcnic_ms_reg_ctrl` captures the register set and address/window state needed for 64-bit MS memory agent reads/writes.
- `crb_128M_2M_map[]` and `crb_hub_agt[]` encode the 128M internal CRB address space to 2M BAR0 window mappings for 82xx hardware.
- `qlcnic_pcie_sem_lock()` and `qlcnic_pcie_sem_unlock()` acquire/release hardware semaphores, optionally writing ownership to an ID register.
- `qlcnic_ind_rd()` and `qlcnic_ind_wr()` provide chip-family aware indirect register reads/writes.
- `qlcnic_send_cmd_descs()` queues raw command descriptors on TX ring 0 after checking firmware attachment and descriptor availability.
- MAC filter helpers (`qlcnic_82xx_sre_macaddr_change()`, `qlcnic_nic_add_mac()`, `qlcnic_nic_del_mac()`, `qlcnic_flush_mcast_mac()`, `qlcnic_82xx_free_mac_list()`) synchronize software MAC lists with firmware.
- `qlcnic_set_multi()` and `__qlcnic_set_multi()` implement multicast/promiscuous programming and driver/RX MAC-learning toggles.
- `qlcnic_prune_lb_filters()` and `qlcnic_delete_lb_filters()` age or remove learned filters.
- Runtime firmware configuration helpers cover loopback, physical port ID, coalescing, hardware LRO, bridged mode, RSS, IP address notifications, link event subscription, MTU, and LEDs.
- Register/memory helpers (`qlcnic_82xx_hw_read_wx_2M()`, `qlcnic_82xx_hw_write_wx_2M()`, `qlcnic_pci_mem_read_2M()`, `qlcnic_pci_mem_write_2M()`) implement direct/windowed CRB and memory-agent access.
- `qlcnic_82xx_shutdown()` and `qlcnic_82xx_resume()` provide power-management integration.

## Control Flow

Hardware register access first classifies an address as directly mapped or windowed. Direct addresses are read/written through BAR0. Windowed addresses acquire `ahw->crb_lock`, grab the CRB window lock, program `CRB_WINDOW_2M`, access the indirect aperture, and release both locks.

Firmware command submission is descriptor based. Callers fill `struct qlcnic_nic_req`, cast it to `struct cmd_desc_type0`, and submit it with `qlcnic_send_cmd_descs()`. The helper uses TX ring 0, stops and restarts the queue around low descriptor availability, advances `tx_ring->producer`, and rings the producer doorbell. Most commands in this file are asynchronous request descriptors, not synchronous mailbox calls.

MAC filter programming flows from netdev state into firmware. `qlcnic_set_multi()` dispatches to SR-IOV VF handling or `__qlcnic_set_multi()`, which ensures station and broadcast filters, computes the receive miss mode, flushes/re-adds multicast filters, handles unicast overflow by enabling accept-all, and toggles MAC-learning modes when accept-all is required.

Memory access uses either direct OCM windowing or the MS memory agent. The memory-agent path rejects unaligned/out-of-range addresses, programs low/high/control registers, polls `TA_CTL_BUSY`, then reads or writes the 64-bit halves.

## State And Persistence Behavior

State touched here includes `adapter->mac_list`, learned filter hash tables, `adapter->flags`, `adapter->ahw->coal`, link/beacon/port identity fields, and feature-related bits such as `adapter->rx_csum`. Device-persistent state lives in firmware-visible registers, hardware semaphores, board ROM, descriptor rings, and firmware-programmed MAC/offload settings.

The file uses `ahw->crb_lock`, `ahw->mem_lock`, TX queue locks, and filter spinlocks to serialize shared hardware windows and mutable filter tables.

## Dependencies And Integration Points

The implementation depends on `qlcnic.h`, `qlcnic_hdr.h`, PCI BAR mappings, firmware descriptor layouts, Linux netdev feature APIs, VLAN/multicast lists, MMIO accessors, and chip-family predicates. It integrates with `qlcnic_main.c` through hardware/nic operation tables, with `qlcnic_io.c` through learned filter updates, and with firmware initialization through ROM and memory access helpers.

## Risks

- `qlcnic_config_bridged_mode()` toggles `QLCNIC_BRIDGE_ENABLED` even when firmware command submission fails, risking software/firmware state divergence.
- Control-plane descriptor commands depend on TX ring 0 and `__QLCNIC_FW_ATTACHED`; saturated queues or stale state can block configuration.
- Failed MAC add/delete commands can desynchronize software lists from firmware filters.
- Windowed CRB and memory-agent access require strict locking; bypasses can corrupt the active window.
- `qlcnic_82xx_hw_read_wx_2M()` returns `-1` for invalid offsets without setting `*err`.
- LRO feature changes are not fully transactional around `netdev->features`.

## Test Signals

Exercise probe/start logs, board-type detection, MTU changes, promisc/allmulti/multicast transitions, `ethtool -C`, LRO/RSS toggles, LED/beacon commands, suspend/resume, firmware reset recovery, and error logs for semaphore timeouts, invalid CRB offsets, failed memory-agent operations, and firmware command submission failures.
