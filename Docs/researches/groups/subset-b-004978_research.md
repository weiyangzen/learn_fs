# subset-b-004978 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_rx.h

This header defines the receive-side DPMAIF packet information table (PIT) contract for the MediaTek T7xx WWAN data path. Its `struct dpmaif_pit` is the packed hardware descriptor consumed by `t7xx_hif_dpmaif_rx.c`, and the bitfield macros decode packet length, buffer identifiers, continuation state, packet type, channel/network metadata, checksum state, and queue completion fields.

The exported API covers RX queue setup and teardown (`t7xx_dpmaif_rxq_init`, `t7xx_dpmaif_rxq_free`, `t7xx_dpmaif_rx_clear`, `t7xx_dpmaif_rx_stop`), buffer allocation/release for BAT and fragment rings (`t7xx_dpmaif_bat_alloc`, `t7xx_dpmaif_bat_free`, `t7xx_dpmaif_rx_buf_alloc`, `t7xx_dpmaif_rx_frag_alloc`, `t7xx_dpmaif_bat_rel_wq_alloc`, `t7xx_dpmaif_bat_wq_rel`), interrupt entry (`t7xx_dpmaif_irq_rx_done`), and NAPI polling (`t7xx_dpmaif_napi_rx_poll`). Control flow is hardware-driven: DL interrupts schedule NAPI, PIT descriptors identify packet fragments and destination netif, and the RX implementation replenishes DMA buffers through BAT rings.

State is maintained by the associated `dpmaif_ctrl`, `dpmaif_rx_queue`, and `dpmaif_bat_request` structures declared in `t7xx_hif_dpmaif.h`. The header itself persists no data, but its descriptor layout is persistent ABI between host driver and modem hardware. Dependencies include Linux bitfield helpers, endian-safe descriptor access in the implementation, DMA buffer accounting, NAPI, and the WWAN netdev callback path. Risks are descriptor layout drift, malformed continuation chains, out-of-range buffer IDs, packet type confusion between IPv4/IPv6, and starvation if BAT refill fails. Test signals include RX with fragmented packets, checksum metadata, queue-done interrupt masks, BAT exhaustion/replenishment, NAPI budget limits, and modem reset while RX descriptors are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_tx.c

This file implements the T7xx DPMAIF uplink transmit ring. It converts SKBs from WWAN netdevs into hardware DRB descriptors, maps linear and paged SKB data for DMA, pushes descriptor counts to the device, and releases DMA mappings and SKBs after hardware advances the read index.

Important functions are `t7xx_dpmaif_tx_send_skb`, `t7xx_dpmaif_tx_thread_init`, `t7xx_dpmaif_tx_thread_rel`, `t7xx_dpmaif_irq_tx_done`, `t7xx_dpmaif_txq_init`, `t7xx_dpmaif_txq_free`, `t7xx_dpmaif_tx_stop`, and `t7xx_dpmaif_tx_clear`. Internally, `t7xx_dpmaif_add_skb_to_ring` writes one message DRB plus one payload DRB per linear/frag segment; `t7xx_txq_burst_send_skb` batches up to `DPMAIF_SKB_TX_BURST_CNT`; `t7xx_do_tx_hw_push` updates the hardware DRB count; and `t7xx_dpmaif_tx_done` handles UL completion work.

Control flow splits into two asynchronous lanes. Producers enqueue SKBs on `tx_skb_head` and wake `dpmaif_ctrl->tx_thread`; the thread resumes runtime PM, disables PCIe deep sleep, waits for the sleep lock, fills DRBs, and notifies hardware. Completion interrupts call `t7xx_dpmaif_irq_tx_done`, which schedules ordered work per TXQ to read the hardware read index, unmap payload buffers, free SKBs at the last descriptor, restore TX budget, clear done status, and unmask interrupts.

State is ring-based and protected by `tx_lock`, atomics, and workqueue/kthread sequencing: `drb_wr_idx`, `drb_rd_idx`, `drb_release_rd_idx`, `tx_budget`, `tx_processing`, `que_started`, `drb_base`, and `drb_skb_base`. DMA coherent DRB memory is hardware-visible; the software sidecar records SKB ownership and mapping details. Dependencies include `t7xx_dpmaif_ul_*` register helpers, `t7xx_pci_disable_sleep`/`enable_sleep`, runtime PM, `sk_buff` fragment APIs, and the netdev callback `state_notify`.

Risks include ring index corruption, budget underflow, DMA leak on partial mapping failure, unsupported `frag_list` payloads, sleeping/resource-lock races, descriptors left with continuation bits set, and queue-stop waiting only on `tx_processing`. Test signals should cover large fragmented SKBs, DMA mapping failure injection, TX queue full/wake notifications, completion interrupt storms, runtime suspend/resume during TX, modem exception cleanup, and stop/clear while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_tx.h

This header defines the DPMAIF transmit descriptor ABI for T7xx. `struct dpmaif_drb` is a packed 16-byte descriptor union: payload descriptors carry low/high DMA address words, while message descriptors carry per-packet metadata. `struct dpmaif_drb_skb` is the software shadow entry used to remember SKB ownership, DMA address, length, descriptor index, fragment/message flags, and last-descriptor state.

The exported API is the TX half consumed by DPMAIF control and netdev code: send SKB, initialize/release the TX kthread, initialize/free per-queue rings, handle TX-done interrupts, and stop/clear TX state. `DPMAIF_TX_DEFAULT_QUEUE` documents that normal traffic uses queue 0 in the current implementation.

State is maintained by `dpmaif_tx_queue` in the shared DPMAIF header, while this header defines the bit layout (`DRB_HDR_DATA_LEN`, `DRB_HDR_CONT`, `DRB_HDR_DTYP`, `DRB_MSG_CHANNEL_ID`, checksum flags, and count fields) required to build descriptors. Dependencies are Linux bitfield/endian helpers in the implementation, hardware register helpers, DMA mapping, and CCCI/WWAN metadata carried in SKB control blocks. Risks are hardware ABI mismatch, incorrect continuation semantics, and descriptor count accounting changes not reflected in `t7xx_skb_drb_cnt`. Tests should validate descriptor words for linear and fragmented SKBs, queue-0 default behavior, and error paths that free mapped buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_mhccif.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_mhccif.c

This file implements the host side of the modem-host cross-core interrupt facility (MHCCIF). It masks/unmasks device-to-host software interrupts, acknowledges status bits, and routes the MHCCIF PCIe interrupt into modem and PM handling.

The key APIs are `t7xx_mhccif_init`, `t7xx_mhccif_read_sw_int_sts`, `t7xx_mhccif_mask_set`, `t7xx_mhccif_mask_clr`, `t7xx_mhccif_mask_get`, and `t7xx_mhccif_h2d_swint_trigger`. The primary handler pair is `t7xx_mhccif_isr_handler` and `t7xx_mhccif_isr_thread`; the top half only wakes the threaded handler, while the thread reads status, acknowledges suspend/resume/deep-sleep-lock interrupts, completes PM waiters, and invokes `t7xx_pci_mhccif_isr` for modem events.

State is mostly hardware register state under `base_addr.mhccif_rc_base`, plus completions in `t7xx_pci_dev`. Dependencies include `t7xx_reg.h` register offsets and bits, PCIe MAC interrupt registration, and modem/FSM logic. Risks include lost interrupts if status is acked before software observes all relevant bits, incorrect mask changes across suspend/resume, and completion wakeups for stale PM requests. Test signals include port-enumeration interrupts, exception interrupts, suspend/resume ACKs, deep sleep lock ACKs, and mask readback after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_mhccif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_mhccif.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_mhccif.h

This header exposes MHCCIF register-control helpers and defines `D2H_SW_INT_MASK`, the set of modem-originated software interrupts handled by the T7xx driver. The mask includes exception stages, port enumeration, PM ACKs, and asynchronous MD/AP handshake bits.

Its functions are thin register operations around mask set/clear/get, status read, initialization, and host-to-device software interrupt triggering. Integration points include `t7xx_pci.c` for PM, `t7xx_modem_ops.c` for exception/handshake routing, and `t7xx_state_monitor.c` for FSM events. The header has no persistent state, but it defines the interrupt contract that controls persistent modem lifecycle state. Risks are missing a new bit in `D2H_SW_INT_MASK` or triggering the wrong H2D channel. Tests should verify mask programming, status filtering, and all H2D/D2H channels used by reset, exception, port enumeration, and PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_mhccif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_modem_ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_modem_ops.c

This file orchestrates the T7xx modem lifecycle above PCIe, CLDMA, DPMAIF, port proxy, and the FSM. It handles MHCCIF modem interrupts, RGU reset interrupts, ACPI/PCI reset entry points, exception handshakes, runtime feature exchange, AP/MD core handshakes, and modem initialization/exit.

Important APIs include `t7xx_pci_mhccif_isr`, `t7xx_clear_rgu_irq`, `t7xx_reset_device`, `t7xx_md_event_notify`, `t7xx_md_exception_handshake`, `t7xx_md_reset`, `t7xx_md_init`, and `t7xx_md_exit`. Internal helpers parse runtime feature queries, send HS1/HS3 control messages, parse HS2 data, dispatch port enumeration, switch CLDMA queue configuration, and run exception stages (`HIF_EX_INIT`, `HIF_EX_CLEARQ_DONE`, `HIF_EX_ALLQ_RESET`).

Control flow starts in `t7xx_md_init`: allocate modem context, allocate MD/AP CLDMA controllers, initialize FSM, initialize CCMNI/DPMAIF netdev data path, initialize CLDMA, allocate the port proxy, append `FSM_CMD_START`, then register MHCCIF and RGU interrupt handling. During operation, MHCCIF status is accumulated under `exp_lock`; exception, port enumeration, and async handshake bits are converted into FSM events or workqueue jobs. Exception recovery stops/clears CLDMA queues, resets ports after a delay, acknowledges modem stages via H2D interrupts, and restarts CLDMA after all queues reset.

State resides in `struct t7xx_modem`: CLDMA controllers, `core_md` and `core_ap` feature/handshake state, `exp_id`, `exp_lock`, `handshake_wq`, FSM pointer, port proxy, and reset flags. Dependencies are ACPI `_RST`/`MRST._RST` or `pci_reset_function`, PCIe MAC interrupt controls, MHCCIF, CLDMA, port proxy/control messages, CCMNI, and FSM notifiers. Risks include handshake timeout, stale `exp_id` bits, reset while workqueues are active, malformed runtime feature payloads, port enumeration version mismatch, and duplicated reset paths from sysfs, PMIC/RGU, and fastboot. Test signals include HS1/HS2/HS3 success and error events, MD/AP async handshakes, PLDR/FLDR/fastboot reset paths, modem exception stage timing, RGU interrupt behavior, and initialization rollback at each failure label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_modem_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_modem_ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_modem_ops.h

This header defines the modem lifecycle data model. `enum hif_ex_stage` names exception handshake phases; `struct mtk_runtime_feature` models feature negotiation records; `struct t7xx_sys_info` tracks per-core runtime feature state and control port; `struct t7xx_modem` aggregates CLDMA controllers, FSM, port proxy, handshake work, exception state, and reset flags; and `enum reset_type` distinguishes FLDR, PLDR, and fastboot reset.

Its functions are the public modem operations used by PCI, MHCCIF, FSM, and reset paths. State is long-lived for the PCI device lifetime and is reset during modem reprobe and exception recovery. Dependencies include CLDMA, PCI, workqueues, spinlocks, and port/FSM types. Risks are ABI drift in feature record parsing, unclear ownership of the modem context because it is devm-allocated but has explicit workqueue teardown, and concurrent reset/exit paths. Tests should exercise initialization rollback, state transitions, exception handshakes, and reset type selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_modem_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_netdev.c

This file adapts the T7xx DPMAIF data path to Linux WWAN netdevs. It registers WWAN rtnl operations, creates per-IP-mux network devices, starts/stops NAPI around netdev users, transmits IP packets through DPMAIF TX, receives DPMAIF SKBs into GRO, and reacts to modem state changes.

Important functions include `t7xx_ccmni_init`, `t7xx_ccmni_exit`, `t7xx_ccmni_open`, `t7xx_ccmni_close`, `t7xx_ccmni_start_xmit`, `t7xx_ccmni_recv_skb`, and the WWAN link callbacks `t7xx_ccmni_wwan_newlink`/`dellink`. The modem-state notifier registers with the FSM and starts WWAN operations when `MD_STATE_READY`; exception/stopped states stop TX, run `t7xx_dpmaif_md_state_callback`, disable NAPI, and drop carrier.

Control flow for TX checks MTU and CCCI headroom, stores `netif_idx` in the SKB control block, and enqueues to the default DPMAIF TX queue. RX gets `netif_idx` and `rx_pkt_type` from DPMAIF, selects the registered `t7xx_ccmni` instance, sets IPv4/IPv6 protocol, and passes the SKB to `napi_gro_receive`. Queue-state callbacks stop or wake netdev TX queues on DPMAIF full/IRQ notifications.

State is in `struct t7xx_ccmni_ctrl`: DPMAIF control, per-link netdev pointers, callbacks, FSM notifier, NAPI pointers attached to a dummy netdev, registration flag, and reference counts. Dependencies include Linux WWAN rtnl core, netdev/NAPI/GRO, runtime PM, DPMAIF RX/TX, FSM, and CCCI header sizing. Risks include null default netdev access in queue-state callbacks, NAPI reference imbalance, registering links before modem readiness, SKB headroom drops, and queue wakeups after modem state changes. Test signals include default link creation, manual link add/delete, open/close refcounting, IPv4/IPv6 RX, TX queue full/wake, MTU changes, suspend/resume, and exception/stopped modem transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_netdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_netdev.h

This header defines CCMNI netdev state for T7xx. `struct t7xx_ccmni` is per WWAN link and stores the link index, usage count, netdev, and controller pointer. `struct t7xx_ccmni_ctrl` owns the DPMAIF control object, up to `NIC_DEV_MAX` link instances, callbacks, modem state, FSM notifier, dummy NAPI netdev, RX NAPI array, and NAPI user count.

Constants set the default link count, maximum links, MTU ceiling, watchdog timeout, and NAPI poll budget. The API is `t7xx_ccmni_init`/`t7xx_ccmni_exit`, called from modem init/exit. Persistent state is tied to the PCI device and is cleaned during modem exit. Dependencies include DPMAIF, netdevice, PCI, and FSM types. Risks are array bounds on link IDs, mismatch between `CCMNI_MTU_MAX` and hardware MTU, and NAPI pointers becoming invalid if DPMAIF queues are torn down first. Tests should cover link ID bounds, MTU settings, notifier registration lifetime, and init failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pci.c

This file is the PCI driver for MediaTek T7xx 5G WWAN modems. It probes supported PCI IDs, maps BARs, configures 64-bit DMA, initializes PCIe ATR/MHCCIF/modem state, exposes sysfs mode/debug controls, registers MSI-X interrupts, and implements system/runtime PM and reset/reprobe flows.

Important APIs exported to other T7xx modules are `t7xx_mode_update`, `t7xx_pci_pm_init_late`, `t7xx_pci_pm_exp_detected`, PM entity register/unregister, `t7xx_pci_disable_sleep`, `t7xx_pci_enable_sleep`, `t7xx_pci_sleep_disable_complete`, `t7xx_pci_reprobe_early`, and `t7xx_pci_reprobe`. Internal control flows include sysfs writes to `t7xx_mode` for PLDR/fastboot reset, `t7xx_debug_ports` for debug port creation, suspend/resume handshakes via MHCCIF, MSI-X request/free, and probe/remove lifecycle.

State is held in `struct t7xx_pci_dev`: interrupt callbacks, mapped register bases, modem pointer, PM entity list, completions for initialization, PM ACK, and sleep lock, runtime PM state, sleep-disable reference count, device mode, and debug-port visibility. The PM flow disables ASPM low power, invokes registered entity callbacks, sends MD/AP suspend or resume requests, waits for ACKs, handles D3/L2/L3/exception resume states, and reenables interrupts/resource locks.

Dependencies include PCI core, runtime/system PM, MSI-X, DMA masks, PCIe MAC register helpers, MHCCIF, modem/FSM operations, sysfs, and vendor/device IDs. Risks include underflowing `sleep_disable_count`, timeout paths leaving ASPM disabled or IRQs masked, double `pm_runtime_allow` behavior, reset/reprobe races with sysfs and runtime PM, failed IRQ partial cleanup, and resume state misclassification. Test signals include probe failure injection at each init stage, runtime suspend/resume, system suspend/resume/thaw/restore, L2/L3/exception resume registers, sysfs reset/fastboot writes, debug port toggling, and remove after partially initialized modem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pci.h

This header defines the central T7xx PCI device context and PM entity interface. `struct t7xx_addr_base` stores mapped PCIe MAC, external register, translation, infracfg, and MHCCIF bases. `struct t7xx_pci_dev` is the shared object passed through modem, CLDMA, DPMAIF, and port layers. `struct md_pm_entity` lets internal hardware modules register suspend/resume callbacks with an ID.

Control-flow contracts include interrupt callback arrays indexed by `enum t7xx_int`, device modes exposed through sysfs and reset flows, sleep-disable acquire/release APIs, PM entity registration, and reprobe helpers. State persists for the PCI device lifetime and is guarded by mutexes, spinlocks, atomics, and completions. Dependencies are PCI core, completions, IRQ callbacks, and `t7xx_reg.h`. Risks are callback array misuse, PM entity ID collisions, sleep-lock imbalance, and mode reads outside `T7XX_MODE_LAST`. Tests should cover PM entity duplicate/unregister behavior, mode transitions, and concurrent sleep disable/enable users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pcie_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pcie_mac.c

This file programs the T7xx PCIe MAC registers. Its main responsibilities are address translation region (ATR) setup, host interrupt enable/disable, per-interrupt mask manipulation, interrupt status clearing, and MSI-X configuration.

`t7xx_pcie_mac_atr_cfg` writes ATR source, translation, and parameter registers for selected ports; `t7xx_pcie_mac_atr_init` disables old ATR tables, programs BAR2 register translation and transparent device DMA windows, and stores the device register translation address. `t7xx_pcie_mac_interrupts_en`/`dis` toggle host interrupt control; `t7xx_pcie_mac_clear_int`, `t7xx_pcie_mac_set_int`, and `t7xx_pcie_mac_clear_int_status` operate on EXT_INT masks/status; `t7xx_pcie_set_mac_msix_cfg` writes the MSI-X vector count.

State is hardware register state plus `base_addr.pcie_dev_reg_trsl_addr`. Dependencies are `t7xx_reg.h`, PCI BAR mappings, and callers in PCI, MHCCIF, and modem RGU paths. Risks include wrong ATR alignment/size, programming a translation window before BARs are mapped, using a mask bit outside EXT_INT range, and interrupt enable order during resume. Test signals include BAR2 register reads through translated windows, DMA path validation, interrupt mask/status readback, RGU/MHCCIF interrupt delivery, and suspend/resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pcie_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pcie_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pcie_mac.h

This header exposes PCIe MAC helpers and the `IREG_BASE(t7xx_dev)` accessor for internal PCIe MAC registers. It defines the integration surface used by PCI probe/resume, modem reset/RGU handling, and MHCCIF interrupt setup.

The API covers global interrupt enable/disable, ATR initialization, individual interrupt mask set/clear, interrupt status clear, and MSI-X count programming. It has no own persistent state, but callers rely on it to update hardware state that gates all T7xx interrupts and register translations. Dependencies are `struct t7xx_pci_dev` and `enum t7xx_int`. Risks are unsafe calls before BAR mapping or after remove, and interrupt masking mismatches between hardware and callback arrays. Tests should verify interrupt delivery and register access after probe, resume, and reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pcie_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port.h

This header defines the CCCI logical port abstraction used by the T7xx CLDMA control plane. `enum port_ch` lists AP/MD channel IDs for control, AT, MBIM, ADB, modem logs, loopback, status, MIPC, and DSS ports. `struct port_ops` is the per-port behavior table. `struct t7xx_port_conf` maps TX/RX channels to CLDMA queues and WWAN port type. `struct t7xx_port` stores runtime channel state, sequence numbers, RX queue, usage count, waitqueue, task, and WWAN or relay-channel backend.

The exported functions allocate SKBs with CCCI/control headroom, enqueue received SKBs, get per-port MTU from CLDMA queue configuration, and send raw, CCCI-wrapped, or control SKBs. State is per-port and initialized by `t7xx_port_proxy.c`; persistence lasts across normal modem operation and is reset during exception/reprobe. Dependencies include CLDMA, WWAN core, SKB queues, waitqueues, spinlocks, and PCI device context. Risks are channel ID collisions after masking to low 8 bits, sequence-number drift, RX queue overflow, and use of a port after proxy reconfiguration. Tests should cover each configured port type, enabled/disabled channels, exception queues, and CCCI header construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_ctrl_msg.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_ctrl_msg.c

This file implements the T7xx control port protocol. It parses modem control messages, translates exception and handshake messages into FSM events, handles port enumeration payloads, and runs a kernel thread that drains the control port RX queue.

Important functions are `t7xx_port_enum_msg_handler`, `control_msg_handler`, `fsm_ee_message_handler`, `port_ctl_send_msg_to_md`, `port_ctl_rx_thread`, `port_ctl_init`, and `port_ctl_uninit`. Port enumeration validates head/tail patterns and version, then enables or disables channels through `t7xx_port_proxy_chl_enable_disable`. Exception messages recognize MD exception check/pass/ack IDs and append FSM events such as HS2 and exception pass events.

State resides in the control port RX SKB list, its thread pointer, channel enable flags, and FSM event queue. Dependencies are CCCI/control headers from `t7xx_port_proxy.h`, `t7xx_state_monitor`, port proxy channel controls, and SKB queueing. Risks include malformed control payload lengths, stale control thread during uninit, port enumeration version mismatch, queue overflow returning `-ENOBUFS`, and control messages arriving after modem state changed. Test signals include HS1/HS2/HS3, MD exception/pass/ack, bad enumeration pattern/version, channel enable/disable messages, control thread stop, and RX backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_ctrl_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_proxy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_proxy.c

This file owns the T7xx CCCI port proxy. It declares normal and early port configurations, allocates the flexible-array proxy, initializes per-port runtime state, maps channels and CLDMA queues to ports, wraps outbound SKBs in CCCI/control headers, dispatches inbound CLDMA SKBs to the right port ops, and toggles debug/fastboot port configurations.

Important functions include `t7xx_port_proxy_init`, `t7xx_port_proxy_set_cfg`, `t7xx_proxy_debug_ports_show`, `t7xx_port_proxy_uninit`, `t7xx_port_proxy_reset`, `t7xx_port_send_skb`, `t7xx_port_send_ctl_skb`, `t7xx_port_proxy_recv_skb`, `t7xx_port_proxy_recv_skb_from_dedicated_queue`, `t7xx_port_proxy_md_status_notify`, and `t7xx_port_proxy_chl_enable_disable`. The normal configuration exposes AT, MBIM, control, AP control, and optionally debug ports; the early configuration exposes fastboot on a dedicated AP queue.

Control flow for RX reads the CCCI channel from the SKB, rejects packets when the modem state is invalid, finds the matching port by low channel ID and CLDMA path, checks sequence numbers, strips the CCCI header, and calls the port-specific `recv_skb`. If a port returns backpressure, the header is restored and the caller can retry. TX chooses normal or exception CLDMA queues based on FSM modem state and refuses non-log traffic in exception state.

State includes the `port_proxy` channel lists, queue lists, `cfg_id`, `port_count`, each port's sequence counters, channel enable flag, RX queues, and control/WWAN/relay resources. Dependencies are CLDMA, FSM, WWAN port ops, trace port ops under debugfs, SKB APIs, and CCCI protocol definitions. Risks include channel mapping collisions, dropping valid packets before port enumeration, sequence warning only rather than recovery, debug port lifetime races, and sending on unavailable exception queues. Test signals include normal vs early config switching, debug port toggles, RX dispatch for each channel, backpressure retry, invalid channel drops, sequence wraparound, and modem-state TX gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_proxy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_proxy.h

This header defines the CCCI proxy protocol and proxy data structure. `struct port_proxy` indexes ports by RX channel and by CLDMA queue. `struct ccci_header` and `struct ctrl_msg_header` are the on-wire message headers. Macros define CCCI status fields, control message IDs, exception magic values, and port enumeration payload fields/patterns.

The exported API initializes/uninitializes/reset ports, switches configuration, toggles debug ports, dispatches RX SKBs, handles dedicated early queues, publishes modem-state notifications, parses port enumeration, and enables/disables channels. State is owned by the proxy allocated in `t7xx_port_proxy.c` and points into modem/port structures. Dependencies include CLDMA, modem ops, port ops, WWAN debugfs conditionals, and hardware CCCI framing. Risks include packed protocol assumptions without explicit struct packing, endian handling mistakes, invalid flexible-array sizing, and control message ID drift. Tests should validate header encoding/decoding, enumeration parsing, and proxy reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_proxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_trace.c

This file implements the optional modem trace/debug port using relayfs/debugfs. It creates relay buffers under the T7xx WWAN debugfs directory, writes received modem log SKBs to the relay channel, and tears the channel down when the modem leaves usable states or the debug port is hidden.

The key functions are `t7xx_trace_create_buf_file_handler`, `t7xx_trace_remove_buf_file_handler`, relay `subbuf_start`, `t7xx_trace_port_recv_skb`, `t7xx_trace_port_uninit`, and `t7xx_port_trace_md_state_notify`. `t7xx_trace_port_ops` exposes these as a `port_ops` implementation. Control flow is mostly RX-only: incoming SKBs are written to the relay channel and consumed; state notifications close the relay channel when the modem is stopped/exceptional.

State is per-port `relaych` plus debugfs dentries managed by relayfs. Dependencies include CONFIG_WWAN_DEBUGFS, relayfs, debugfs directory access from `wwan_get_debugfs_dir`, and port proxy debug toggling. Risks include relay buffer allocation failure, lost trace data when the relay channel is absent, debugfs lifetime races, and high-volume logs consuming memory (`32 * 128 KiB`). Test signals include debug port sysfs toggling, modem ready/exception/stopped transitions, relay file creation/removal, and RX logging under sustained load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_wwan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_wwan.c

This file adapts T7xx CCCI ports to Linux WWAN character ports. It implements the `wwan_port_ops` start/stop/tx callbacks, creates/removes WWAN ports for AT/MBIM/ADB/MIPC/fastboot-like channels, queues received SKBs to userspace, and applies modem-state/channel-enable flow control.

Important functions include `t7xx_port_wwan_start`, `t7xx_port_wwan_stop`, `t7xx_port_wwan_tx`, `t7xx_port_fastboot_tx`, `t7xx_port_ctrl_tx`, `t7xx_port_wwan_create`, `t7xx_port_wwan_init`, `t7xx_port_wwan_uninit`, `t7xx_port_wwan_recv_skb`, `t7xx_port_wwan_enable_chl`, `t7xx_port_wwan_disable_chl`, and `t7xx_port_wwan_md_state_notify`. `wwan_sub_port_ops` is the exported port-ops table consumed by the proxy.

Control flow opens/closes ports by incrementing usage and toggling channel state. TX paths allocate or use SKBs supplied by WWAN core, apply fastboot/control special cases, and call `t7xx_port_send_skb` or raw send. RX enqueues to the port queue or forwards to `wwan_port_rx`; channel disable calls `wwan_port_txoff`, while enable calls `wwan_port_txon`. State is `chan_enable`, `usage_cnt`, `wwan_port` pointer, RX queue, and thread/waitqueue state in `struct t7xx_port`. Dependencies include WWAN core, CCCI port proxy, CLDMA send, and FSM modem-state notifications. Risks include userspace writes during disabled channels, RX queue overflow/backpressure, WWAN port removal while file descriptors are open, and special-case fastboot path mismatches. Tests should cover open/close, blocking writes, enable/disable, modem exception/stopped transitions, fastboot TX, control TX, and RX queue limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_port_wwan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_reg.h

This header is the T7xx hardware register and bitfield map. It defines MHCCIF base offsets and H2D/D2H channels, PCIe chip/ATR/PM/status/interrupt registers, device stages and link-kernel events, host events, EXT_INT IDs, and DPMAIF UL/DL/AO register offsets and masks.

The file has no functions, but it is the dependency root for PCIe MAC programming, MHCCIF, PCI PM, modem reset, DPMAIF TX/RX, and FSM boot-stage handling. Persistent behavior is hardware register state: writing these offsets changes interrupt delivery, address translation, ASPM/deep-sleep state, DPMAIF queues, BAT/PIT/DRB rings, and modem lifecycle status.

Risks are high because constants are hardware ABI. Notable concerns include duplicate `MISC_RESET_TYPE_PLDR` definition, similar mask names (`MKS` vs `MSK` typo in one DLQ timeout macro), bitfield width assumptions, and coupling to register translation math in PCIe MAC/PCI code. Test signals include register readback after init, ATR access, MHCCIF interrupt exchange, PM resource status polling, DPMAIF queue setup, and suspend/resume across all documented device stages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_state_monitor.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_state_monitor.c

This file implements the T7xx modem finite-state monitor. It owns the FSM kernel thread, command queue, event queue, notifiers, modem state broadcasting, boot/start/stop/exception routines, and the bridge between hardware interrupts and modem lifecycle transitions.

Important APIs are `t7xx_fsm_init`, `t7xx_fsm_uninit`, `t7xx_fsm_reset`, `t7xx_fsm_append_cmd`, `t7xx_fsm_append_event`, `t7xx_fsm_clr_event`, `t7xx_fsm_recv_md_intr`, `t7xx_fsm_get_md_state`, `t7xx_fsm_broadcast_state`, and notifier register/unregister. Internal routines handle stopped/stopping/start/pre-start/ready states, wait for expected events with timeouts, process LK stage events from PCIe device status, run exception handshake through `t7xx_md_exception_handshake`, disable DRM through MHCCIF, and complete synchronous commands.

Control flow is command-driven: callers append `FSM_CMD_START`, `PRE_STOP`, or `STOP`; the FSM thread dequeues commands, transitions `curr_state`, waits for hardware/FSM events, broadcasts `md_state`, and completes waiting commands. Interrupt paths append events through `t7xx_fsm_recv_md_intr`, which converts CCIF exception or port enumeration IRQs into state-machine input. Notifiers, including CCMNI and port proxy, receive `MD_STATE_*` transitions.

State includes `curr_state`, `md_state`, command/event lists, waitqueues, spinlocks, notifier list, exception flag, and `event_id`/data payloads. Dependencies include modem ops, MHCCIF, PCI PM exception notification, port proxy state notification, and register-stage definitions. Risks include command/event queue leaks, timeouts that leave waiters incomplete, races between reset and event delivery, notifier mutation during broadcast, and boot-stage assumptions. Test signals include start path to READY, pre-stop/stop, exception flow, port enumeration during init/stopped, command wait completion, event clearing, reset flushing, notifier register/unregister, and forced timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_state_monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_state_monitor.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_state_monitor.h

This header defines the modem FSM contract. Enums describe FSM control states, asynchronous event IDs, command IDs, exception reasons, modem IRQ sources, and externally broadcast modem states. `struct t7xx_fsm_ctl` stores the current state, queues, waitqueues, locks, notifier list, thread, and modem pointer. `struct t7xx_fsm_event`, `struct t7xx_fsm_command`, and `struct t7xx_fsm_notifier` model queued input and observer callbacks.

The API lets other T7xx modules append commands/events, clear events, broadcast state, reset/init/uninit the FSM, receive modem interrupts, query MD state, and register/unregister notifiers. State persists for modem lifetime and is reset on reprobe. Dependencies include completions, krefs, list heads, spinlocks, waitqueues, and modem forward declarations. Risks include misuse of command flags, event data ownership mistakes, notifier lifetime issues, and callers assuming a stable `md_state` without locking. Tests should cover each enum transition, command completion, event payload freeing, and notifier behavior across reset/uninit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_state_monitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/wwan_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/wwan_core.c

This file is the Linux WWAN framework core. It creates shared WWAN devices under the `wwan` class, exposes control ports as character devices or GNSS devices, provides `wwan_create_port`/`wwan_remove_port` and RX/TX helpers for drivers, and registers an rtnetlink `wwan` link type for data-plane netdevs.

Important APIs exported to drivers are `wwan_create_port`, `wwan_remove_port`, `wwan_port_rx`, `wwan_port_txon`, `wwan_port_txoff`, `wwan_port_get_drvdata`, `wwan_register_ops`, `wwan_unregister_ops`, and debugfs helpers under CONFIG_WWAN_DEBUGFS. Internally it manages minors with IDA, WWAN device IDs, port naming, AT-port terminal ioctl stubs, GNSS wrapping for NMEA ports, character file operations, and rtnl link create/delete/fill/validate callbacks.

Control flow for ports begins with `wwan_create_dev`, which reuses or creates a parent `wwanN` device with reference counting under `wwan_register_lock`; `wwan_create_port` then allocates a `wwan_port`, registers a char device or GNSS device, and stores driver data. User open starts the driver port once per start count, read blocks on RX SKB queue, write fragments userspace data into SKBs with required headroom and `frag_len`, and poll reports RX/TX/hangup. Data links are created through rtnetlink using `IFLA_PARENT_DEV_NAME` and `IFLA_WWAN_LINK_ID`; optional default link creation forges a netlink message and calls rtnl helpers.

State includes global class/major/IDAs/debugfs, per-WWAN-device refcount/ops/context/debugfs, per-port ops/start count/flags/RX queue/waitqueue/termios, and rtnl netdev private `link_id`. Dependencies include netdevice/rtnetlink, char device registration, GNSS, debugfs, SKB queues, uaccess, termios, and WWAN UAPI. Risks include refcount mistakes around shared WWAN devices, ops removal racing file operations, fragmented write memory growth, ioctl compatibility, default link creation failure being non-fatal, and child netdev cleanup ordering. Test signals include concurrent port create/remove, open/read/write/poll blocking and nonblocking behavior, AT ioctls, GNSS NMEA path, rtnl link add/delete, default link creation, ops unregister with active links, and debugfs ref helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/wwan_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/wwan_hwsim.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/wwan_hwsim.c

This file implements a WWAN hardware simulator for framework testing. It creates synthetic devices under a `wwan_hwsim` class, registers WWAN rtnl ops for dummy data links, creates AT and optional NMEA ports, and exposes debugfs controls to create/destroy devices and ports.

Important pieces are `wwan_hwsim_dev_new`/`dev_del`, `wwan_hwsim_port_new`/`port_del`, debugfs write handlers for `devcreate`, `destroy`, and `portcreate`, the AT emulator start/tx parser, optional NMEA timer emulator, netdev setup/xmit, and module init/exit. Control flow uses a dedicated workqueue for deletion because debugfs callbacks cannot synchronously remove the file currently being used. Initial module load creates `devices` simulated devices, two AT ports per device, and an NMEA port when GNSS is enabled.

State includes global simulator device list/index, per-device port list/index/debugfs dentries/work item, and per-port WWAN port pointer/debugfs dentry/work item plus AT parser or NMEA timer state. Dependencies include WWAN core, debugfs, workqueues, timers, GNSS conditionals, SKB APIs, netdevice, and ARPHRD_NONE point-to-point netdev setup. Risks include list lifetime races, deletion work ordering, debugfs files outliving objects, simulator count bounds, AT parser incompleteness, NMEA timer running after stop, and init failure leaking previously created devices if early loops partially succeed. Test signals include module load/unload, devices parameter bounds, debugfs create/destroy, concurrent deletion, AT echo/OK behavior, NMEA periodic output, rtnl link creation, and cleanup after init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/wwan_hwsim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/xen-netback/Makefile

This Makefile builds the Xen network backend module. It maps `CONFIG_XEN_NETDEV_BACKEND` to `xen-netback.o` and composes the module from `netback.o`, `xenbus.o`, `interface.o`, `hash.o`, and `rx.o`.

There is no runtime control flow or persistent state in the file, but it is the integration point that ensures the hash support researched here is linked with the netback data plane, Xenbus lifecycle, interface code, and RX handling. Dependencies are kernel kbuild and the configuration symbol. Risks are omitted object files causing unresolved symbols or dead feature code, and build changes that split hash/control functionality without updating this list. Test signals are `CONFIG_XEN_NETDEV_BACKEND=m/y` builds, module load, and symbol resolution for functions declared in `common.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/common.h -->
# sources/distributed-fs/ceph-client/drivers/net/xen-netback/common.h

This header is the shared private interface for Xen netback. It defines queue state, VIF state, grant-copy/map bookkeeping, stats, multicast controls, RSS/hash configuration, backend Xenbus state, and prototypes shared across `netback.c`, `rx.c`, `interface.c`, `xenbus.c`, and `hash.c`.

Important types include `struct pending_tx_info`, `struct xenvif_rx_meta`, `struct xenvif_copy_state`, `struct xenvif_queue`, `struct xenvif_hash_cache_entry`, `struct xenvif_hash_cache`, `struct xenvif_hash`, `struct backend_info`, and `struct xenvif`. The queue structure is central: it owns TX/RX rings, event channel IRQs, NAPI, RX kthread, grant tables, pending/dealloc rings, credit shaping state, copy operations, and per-queue stats. `struct xenvif` aggregates queues, frontend features, multicast state, hash state, Xenbus watches, control ring, debugfs, and netdev.

Control flow is declared rather than implemented: allocation/free, ring mapping/unmapping, data/control connection, NAPI scheduling, TX action, RX kthread, dealloc kthread, carrier control, multicast, zero-copy callbacks, hash configuration, and debug dumping. State persistence follows Xen frontend/backend lifetime and Xenstore state; grant references, rings, event channels, and queue memory must be paired with disconnect/free. Dependencies include Xen netif/grant/xenbus/page APIs, Linux netdev/NAPI/SKB/debugfs, timers, waitqueues, and multicast/ether helpers. Risks include queue/ring index misuse, grant leak, frontend rogue behavior, hash mapping bounds, multicast list lifetime, zerocopy callback races, and feature negotiation mismatches. Test signals include multi-queue connect/disconnect, split vs shared event channels, grant map/copy failure, TX/RX traffic with SG/GSO/checksum, RX stalls, credit limiting, multicast controls, hash control operations, and module unload under active frontend traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/hash.c -->
# sources/distributed-fs/ceph-client/drivers/net/xen-netback/hash.c

This file implements Xen netback RSS/hash support. It computes Toeplitz hashes for frontend packets, caches computed hashes, validates and applies frontend control requests for hash algorithm, flags, key, and indirection mapping, and exposes debugfs hash information.

Important functions are `xenvif_set_skb_hash`, `xenvif_set_hash_alg`, `xenvif_get_hash_flags`, `xenvif_set_hash_flags`, `xenvif_set_hash_key`, `xenvif_set_hash_mapping_size`, `xenvif_set_hash_mapping`, `xenvif_dump_hash_info`, `xenvif_init_hash`, and `xenvif_deinit_hash`. Internal helpers add/find/flush entries in an RCU-protected bounded cache and compute new hashes from selected IPv4/IPv6 address and TCP port tuples.

Control flow for data packets parses flow dissector output, checks configured algorithm and flags, chooses L3 or L4 tuple data, finds or computes the Toeplitz value, optionally maps it through the active indirection table to a queue-related value, and sets or clears `skb->hash`. Control operations copy key and mapping data from frontend grant references with `gnttab_batch_copy`, validate sizes/queue IDs, maintain double-buffered mapping arrays, and flush cached hash values when the key changes.

State is in `vif->hash`: algorithm, flags, key, mapping selector, mapping size/arrays, and optional hash cache protected by spinlock/RCU. Dependencies include `common.h`, Xen grant copy APIs, Linux flow dissector, Toeplitz helpers from `xen/interface/io/netif.h`, RCU lists, vmalloc/kfree, SKB hash helpers, and debugfs seq output. Risks include accepting invalid grant data, off/len overflow, two-page mapping copy edge cases, stale cache after mapping changes, cache eviction sequence wrap, unsupported protocols clearing hashes, and mapping entries >= queue count. Test signals include each hash flag combination, IPv4/IPv6 TCP and non-TCP packets, NONE vs TOEPLITZ algorithm, key length zero/max, grant copy failure, mapping boundary/off overflow, queue-count validation, cache hit/eviction behavior, and debugfs output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/xen-netback/hash.c -->
