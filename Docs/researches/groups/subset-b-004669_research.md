# subset-b-004669 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_sriov.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_sriov.c

## Purpose
`wx_sriov.c` implements the PF-side SR-IOV control plane shared by Wangxun PF drivers. It enables and disables PCI SR-IOV, allocates per-VF state, configures VMDq pool layout, handles PF/VF mailbox requests, applies VF MAC/VLAN/multicast/MACVLAN/link policy, and broadcasts PF link state changes to active VFs.

## Important APIs, Types, and Functions
Public exports are `wx_disable_sriov()`, `wx_pci_sriov_configure()`, `wx_msg_task()`, `wx_disable_vf_rx_tx()`, `wx_ping_all_vfs_with_link_status()`, and `wx_set_all_vfs()`. Internal setup helpers include `__wx_enable_sriov()`, `wx_alloc_vf_macvlans()`, `wx_sriov_clear_data()`, and `wx_sriov_reinit()`. Mailbox handlers include `wx_vf_reset_msg()`, `wx_rcv_msg_from_vf()`, `wx_set_vf_mac_addr()`, `wx_set_vf_multicasts()`, `wx_set_vf_vlan_msg()`, `wx_set_vf_macvlan_msg()`, `wx_negotiate_vf_api()`, `wx_get_vf_queues()`, `wx_get_vf_link_state()`, `wx_get_fw_version()`, and `wx_update_vf_xcast_mode()`.

## Control Flow
`wx_pci_sriov_configure()` dispatches zero VF requests to disable and positive requests to `wx_pci_sriov_enable()`. Enable rejects active custom RXFH configuration, initializes VF state, sets VMDq/SR-IOV flags, programs VT count, resets traffic classes through `setup_tc()`, then calls `pci_enable_sriov()`. Disable refuses assigned VFs, calls `pci_disable_sriov()`, clears shared state, and reinitializes queues.

At runtime `wx_msg_task()` scans every configured VF for reset, message, and ack events. A VF reset replays PF VLAN, L2 receive mode, TX/RX enable, MAC filter, mailbox clear-to-send, and response payload. Normal messages are rejected until clear-to-send is established, then routed by opcode and acknowledged or nacked. Link state changes mark the VF not clear-to-send, ping it, and update VF TX/RX enable registers.

## State and Persistence Behavior
State is runtime-only in `struct wx`: `num_vfs`, `vfinfo`, `vf_mvs`, `mv_list`, `ring_feature[RING_F_VMDQ]`, PF flags, default priority, and hardware filter tables/registers. Hardware settings persist only until reset/remove. No disk persistence exists. The clear-to-send bit is the mailbox gate used to keep VFs from configuring before PF reset setup completes.

## Dependencies and Integration Points
The file depends on `wx_type.h` register definitions and `struct wx`, common hardware filter helpers (`wx_add_mac_filter`, `wx_del_mac_filter`, `wx_set_vfta`, `wx_set_rx_mode`), mailbox helpers from `wx_mbx.h`, PCI SR-IOV core APIs, rtnl/netdev TC APIs, VLAN definitions, and PF driver callbacks such as `wx->setup_tc`. PF drivers wire it through `.sriov_configure`, interrupt mailbox causes, and link notifications.

## Risks and Edge Cases
`__wx_enable_sriov()` leaks `vfinfo` if `wx_alloc_vf_macvlans()` fails unless callers unwind with `wx_sriov_clear_data()`. `wx_write_qde()` clears bits using `reg &= qde << i`; for `qde == 0` this clears the whole local register value, so queue disable behavior should be reviewed against hardware intent. Mailbox message sizes reuse the maximum mailbox buffer even for short replies. Promiscuous PF VLAN sharing has subtle cleanup logic that must preserve other pool membership. The shared-vector special case for seven `ngbe` VFs affects interrupt allocation.

## Test Signals
Exercise SR-IOV enable/disable with 0, 1, maximum, assigned, and failed `pci_enable_sriov()` cases; verify RXFH blocking. Test VF reset mailbox handshake, MAC set denial after PF-set MAC, VLAN add/remove with PF promiscuous mode, multicast hash programming, MACVLAN exhaustion, xcast transitions, and link enable/disable. Reset and remove tests should verify `vfinfo`, MACVLAN lists, VMDq offsets, RSC flags, and VF TX/RX enable registers are restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_sriov.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_sriov.h

## Purpose
`wx_sriov.h` declares the shared PF SR-IOV interface for Wangxun PF drivers and defines small mailbox event encoding helpers for VF enable events.

## Important APIs, Types, and Functions
The header defines `WX_VF_ENABLE_CHECK()`, `WX_VF_NUM_GET()`, and `WX_VF_ENABLE` for encoding or extracting a VF enable event mask. It declares PF lifecycle and mailbox functions: `wx_disable_sriov()`, `wx_pci_sriov_configure()`, `wx_msg_task()`, `wx_disable_vf_rx_tx()`, `wx_ping_all_vfs_with_link_status()`, and `wx_set_all_vfs()`.

## Control Flow
There is no runtime control flow in the header. PF drivers include it to connect PCI `.sriov_configure`, mailbox interrupt causes, device down/up paths, and link notification paths to the implementation in `wx_sriov.c`.

## State and Persistence Behavior
The header owns no storage. It describes functions that manipulate `struct wx` runtime fields and PF/VF hardware registers. Its macros assume the VF id is encoded in bits 0-5 and the enable flag in bit 31.

## Dependencies and Integration Points
It requires `struct wx`, `struct pci_dev`, and `bool` to be visible from including translation units. It is included by `ngbe`, `txgbe`, MDIO/AML/IRQ code, and any PF code that services SR-IOV or VF mailbox state.

## Risks and Edge Cases
The event macros silently truncate VF ids to six bits, matching up to 64 VFs; callers must not use them for larger VF ranges. Header declarations need to stay in sync with exported symbols in `wx_sriov.c` or PF modules will fail to link.

## Test Signals
Build all PF drivers with SR-IOV enabled, verify `.sriov_configure` resolves, and exercise mailbox interrupt paths that call `wx_msg_task()` and link paths that call `wx_ping_all_vfs_with_link_status()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_type.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_type.h

## Purpose
`wx_type.h` is the central shared hardware and software data model for Wangxun Ethernet drivers. It defines register offsets, bitfields, descriptors, packet type decoding constants, mailbox/host-interface command structures, queue/ring structures, statistics, PF/VF state, feature flags, and MMIO access helpers consumed by PF and VF drivers.

## Important APIs, Types, and Functions
Key data types include `struct wx`, `struct wx_ring`, `struct wx_q_vector`, `struct wx_ring_container`, `struct wx_mbx_info`, `struct wx_mac_info`, `struct wx_eeprom_info`, `struct vf_data_storage`, `struct vf_macvlans`, descriptor unions `wx_tx_desc`/`wx_rx_desc`, `struct wx_tx_buffer`, `struct wx_rx_buffer`, and PTP/statistics containers. Enumerations classify MAC/media/eeprom/reset/flow-control/state/flag/ring-feature values. Inline helpers include `rd32m()`, `wr32m()`, `rd64()`, `rd32ptp()`, `wr32ptp()`, `rd32_wrap()`, `phylink_to_wx()`, and `wx_rx_pg_order()`.

## Control Flow
The header has no standalone control flow, but it defines the state and register vocabulary used by all control paths. PF probe initializes `struct wx`, reset paths program registers defined here, fast paths consume descriptor and ring definitions, PTP uses timestamp register wrappers, and SR-IOV/VF paths use `vf_data_storage` and mailbox constants.

## State and Persistence Behavior
Most state is memory-resident driver state with device lifetime or netdev-open lifetime. Hardware register definitions map to persistent device state until reset or power cycle. `struct wx` is the aggregation point for PCI/MMIO identity, link state, phylink/PTP, queue arrays, MSI-X vectors, RSS, MAC/VLAN filters, SR-IOV VF data, Flow Director callbacks, and service work. There is no filesystem persistence.

## Dependencies and Integration Points
The header depends on Linux networking, VLAN, phylink, PTP, DIM, bitfield, and IP headers. It integrates every Wangxun module in this subset: `libwx` hardware/mailbox/library code, `ngbe`, `ngbevf`, and `txgbe`. Its MMIO macros assume `wx->hw_addr` has been ioremapped and that callers provide required locking around shared hardware access.

## Risks and Edge Cases
Because this is a broad register contract, incorrect masks or offsets affect many features. `struct wx` mixes PF-only and VF-only fields; call sites must respect device mode. Fixed queue arrays sized to 64 require queue count validation. `rd32ptp()`/`wr32ptp()` apply a MAC-type offset that must match hardware generation. VF state is indexed by `num_vfs`, so SR-IOV teardown must clear `num_vfs` before freeing `vfinfo`.

## Test Signals
Compile all Wangxun drivers using the header, run sparse/lockdep/bounds checks on ring and VF indexes, exercise reset/open/close/PTP/SR-IOV paths, and verify descriptor layout and register offsets against hardware documentation or working silicon. Endianness-sensitive descriptor and host-interface structures need packet-path and firmware-command tests on little-endian systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf.c

## Purpose
`wx_vf.c` implements shared VF-side low-level hardware and PF mailbox operations. It resets a VF, stops VF queues, negotiates mailbox API version, requests MAC/VLAN/multicast/MACVLAN/LPE/link/FW/queue configuration from the PF, and derives link status from PF notifications or VF status registers.

## Important APIs, Types, and Functions
Exports include `wx_init_hw_vf()`, `wx_reset_hw_vf()`, `wx_stop_adapter_vf()`, `wx_set_rar_vf()`, `wx_update_mc_addr_list_vf()`, `wx_update_xcast_mode_vf()`, `wx_get_link_state_vf()`, `wx_set_vfta_vf()`, `wx_get_mac_addr_vf()`, `wx_get_fw_version_vf()`, `wx_set_uc_addr_vf()`, `wx_rlpml_set_vf()`, `wx_negotiate_api_version()`, `wx_get_queues_vf()`, and `wx_check_mac_link_vf()`. Internal helpers perform posted mailbox write/read and VF register clearing.

## Control Flow
Reset starts by stopping queues and masking interrupts, backing up MSI-X vector state from `b4_addr` when available, asserting `WX_VXCTRL_RST`, waiting for reset completion, restoring vector state, enabling AML BME if needed, clearing VF RX descriptor controls, enabling mailbox timeouts, then sending `WX_VF_RESET` to the PF. The PF response either supplies the permanent MAC or nacks when no administrator-assigned MAC exists.

Configuration APIs format mailbox commands and either post fire-and-forget requests or wait for PF replies. Link checking first consumes PF mailbox notifications (`WX_PF_NOFITY_VF_LINK_STATUS` or `WX_PF_CONTROL_MSG`), then falls back to polling `WX_VXSTATUS` and translating speed bits through `wx_speed_lookup_vf`.

## State and Persistence Behavior
Runtime state includes `wx->mac.addr`, `wx->mac.perm_addr`, `wx->mac.mc_filter_type`, VF API level in `wx->vfinfo->vf_api`, mailbox timeout, link/speed/notify flags, and queue limits returned by the PF. Hardware register state is reset and reprogrammed across VF reset/open; no state is persisted to disk.

## Dependencies and Integration Points
The file depends on VF register macros from `wx_vf.h`, mailbox routines from `wx_mbx.h`, common hardware helpers, `struct wx` from `wx_type.h`, netdev multicast lists, and Linux PCI/MMIO primitives. It is consumed by `wx_vf_common.c` and concrete VF drivers such as `ngbevf`.

## Risks and Edge Cases
Mailbox APIs assume the PF honors API 1.3 semantics for xcast and queue queries; older PFs return errors. `wx_update_mc_addr_list_vf()` caps multicast hashes at 28 despite `WX_MAX_VF_MC_ENTRIES` being 30. Reset depends on the PF being up and able to answer; timeout returns `-EBUSY`. Link status can be stale if PF notifications are missed and hardware status polling races module link transitions.

## Test Signals
Test VF probe with PF up/down, no assigned MAC, random MAC fallback, mailbox API negotiation failure, queue count validation, multicast overflow, VLAN add/remove ack/nack, UC filter list clear/add, xcast mode on old API, and link notifications for up/down/notify-down. Reset tests should verify MSI-X vector save/restore and AML BME programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf.h

## Purpose
`wx_vf.h` defines the VF register map, descriptor-control bitfields, RSS/interrupt/queue constants, link-speed extraction helpers, and exported VF mailbox/hardware API declarations shared by Wangxun VF drivers.

## Important APIs, Types, and Functions
The header defines control registers (`WX_VXSTATUS`, `WX_VXCTRL`, `WX_VXMRQC`), VF interrupt registers (`WX_VXICR`, `WX_VXIMS`, `WX_VXIMC`, `WX_VXITR`, `WX_VXIVAR`), RX/TX descriptor registers, buffer-size encoding macros (`wx_buf_len`, `wx_hdr_sz`, `wx_buf_sz`), link extraction macros (`WX_PFLINK_STATUS`, `WX_PFLINK_SPEED`, `WX_VXSTATUS_SPEED`), and `struct wx_link_reg_fields`. It declares low-level VF functions implemented in `wx_vf.c`.

## Control Flow
The header has no executable control flow. VF reset, open, queue setup, mailbox commands, and link checks use these offsets and masks to program device state and interpret PF messages.

## State and Persistence Behavior
It owns no storage. The constants describe VF MMIO register state and exported functions mutate runtime `struct wx` state and hardware registers.

## Dependencies and Integration Points
It assumes `struct wx`, `struct net_device`, and kernel integer/bitfield macros are available. It is included by VF low-level code, VF common lifecycle code, VF queue configuration code, and concrete VF modules.

## Risks and Edge Cases
Encoding helpers convert descriptor counts and buffer sizes into hardware fields; incorrect counts or unsupported values can produce zero encodings. Constants cap VF queues at four TX/RX queues, while some concrete VFs choose lower limits. Register comments and array ranges must match silicon.

## Test Signals
Compile VF drivers, run VF reset/open with queue counts at boundaries, verify RSS key/RETA programming uses `WX_VXMRQC` correctly, and validate interrupt vector mapping and ITR writes for MSI-X VF configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_common.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_common.c

## Purpose
`wx_vf_common.c` provides shared netdev/PCI lifecycle for Wangxun VF drivers. It handles suspend/resume/remove, MSI-X request, API negotiation, reset, receive-mode programming, TX/RX configuration, MAC address changes, link watchdog, open/close, and VF service work.

## Important APIs, Types, and Functions
Exports are `wxvf_suspend()`, `wxvf_shutdown()`, `wxvf_resume()`, `wxvf_remove()`, `wx_request_msix_irqs_vf()`, `wx_negotiate_api_vf()`, `wx_reset_vf()`, `wx_set_rx_mode_vf()`, `wx_configure_vf()`, `wx_set_mac_vf()`, `wxvf_watchdog_update_link()`, `wxvf_open()`, `wxvf_close()`, and `wxvf_init_service()`. Internal flow is split across `wx_configure_rx_vf()`, `wxvf_up_complete()`, `wxvf_down()`, `wxvf_reinit_locked()`, `wxvf_reset_subtask()`, `wxvf_link_config_subtask()`, and `wxvf_service_task()`.

## Control Flow
VF probe code initializes service work here, then open allocates resources, programs RX mode/TX/RX rings, requests MSI-X IRQs, sets real queue counts, enables NAPI/interrupts, starts queues, and schedules service. Link updates are driven by misc interrupts setting `WX_FLAG_NEED_UPDATE_LINK`; service work queries PF/hardware link and toggles carrier. Reset errors set `WX_FLAG_NEED_DO_RESET`, causing the service task to reinitialize under RTNL and `reset_lock`. Close stops service, queues, NAPI, resets the VF, frees IRQs/resources, and cleans rings.

## State and Persistence Behavior
State lives in `struct wx`: service timer/work, flags, reset state bitmap, MSI-X entries, queue vectors, rings, mailbox lock, link/speed, MAC addresses, and allocated resources. Suspend/resume detach or attach the netdev and tear down/recreate interrupt scheme without storing anything persistently.

## Dependencies and Integration Points
The file depends on low-level VF commands from `wx_vf.c`, queue programming from `wx_vf_lib.c`, common ring/resource helpers from `wx_lib.h`, mailbox locking, Linux PCI PM, netdevice carrier and queue APIs, NAPI, timers, workqueues, and IRQ APIs. Concrete VF drivers reuse these functions in netdev ops and PCI PM hooks.

## Risks and Edge Cases
`wx_request_msix_irqs_vf()` calls `wx_reset_interrupt_capability()` on queue IRQ request failure, which may surprise caller cleanup paths. Reset reinit ignores failures from `wx_request_msix_irqs_vf()` during service reset. Receive mode always attempts xcast, multicast, and UC mailbox updates; mailbox failure is not propagated from `ndo_set_rx_mode`. Close and reset both call `wx_reset_vf()`, so PF availability affects teardown latency.

## Test Signals
Open/close repeatedly, suspend/resume with netdev up and down, inject MSI-X request failures, force PF mailbox reset/loss, and verify carrier messages for link transitions. Test MAC change ack/nack, receive mode transitions for promisc/allmulti/multicast, and service reset after PF ping loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_common.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_common.h

## Purpose
`wx_vf_common.h` declares the shared VF lifecycle, netdev operation helpers, and service hooks implemented by `wx_vf_common.c`.

## Important APIs, Types, and Functions
Declarations cover PCI PM/remove/shutdown (`wxvf_suspend`, `wxvf_shutdown`, `wxvf_resume`, `wxvf_remove`), interrupt setup (`wx_request_msix_irqs_vf`), mailbox/reset/configuration (`wx_negotiate_api_vf`, `wx_reset_vf`, `wx_set_rx_mode_vf`, `wx_configure_vf`), netdev operations (`wx_set_mac_vf`, `wxvf_open`, `wxvf_close`), link service (`wxvf_watchdog_update_link`), and service initialization (`wxvf_init_service`).

## Control Flow
There is no executable flow. Concrete VF drivers wire these helpers into `net_device_ops`, PCI PM ops, shutdown, and remove handlers.

## State and Persistence Behavior
No state is declared here. The functions operate on runtime `struct wx`, `struct pci_dev`, `struct device`, and `struct net_device` state.

## Dependencies and Integration Points
The header integrates concrete VF modules such as `ngbevf` with shared libwx VF behavior. It relies on including files to provide type declarations for kernel PCI, device, and netdevice structures plus `struct wx`.

## Risks and Edge Cases
Any signature mismatch between this header and exported implementation breaks all VF modules. Adding a new VF lifecycle behavior requires keeping concrete driver netdev/PCI hooks synchronized with the shared API.

## Test Signals
Build `ngbevf` with this header and verify all netdev ops and PM hooks resolve. Probe/remove and suspend/resume tests should cover each declared entry point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_lib.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_lib.c

## Purpose
`wx_vf_lib.c` contains shared VF queue and interrupt register programming. It configures MSI-X vector mapping, interrupt throttle registers, unicast filter mailbox updates, TX rings, RX rings, packet-split/RSS type registers, RSS key and indirection table, and RX buffer replenishment for VF drivers.

## Important APIs, Types, and Functions
Exports are `wx_write_eitr_vf()`, `wx_configure_msix_vf()`, `wx_write_uc_addr_list_vf()`, `wx_setup_psrtype_vf()`, `wx_setup_vfmrqc_vf()`, `wx_configure_tx_vf()`, and `wx_configure_rx_ring_vf()`. Internal helpers include `wx_set_ivar_vf()`, `wx_configure_tx_ring_vf()`, and `wx_configure_srrctl_vf()`.

## Control Flow
Open/configure code calls `wx_configure_msix_vf()` to map each RX/TX ring to a queue vector and assign the misc interrupt vector. TX configuration disables each queue, programs descriptor base/head/tail, enables PCIe relaxed ordering, optionally configures head writeback, clears software buffers, enables the queue, and polls for enable. RX configuration disables the queue, programs descriptor base/head/tail, resets software buffer indexes, sets SRRCTL/drop/buffer sizes, enables VLAN/RSC/descriptor merge bits, enables the queue, and allocates receive buffers.

## State and Persistence Behavior
The file mutates ring runtime fields (`tail`, `next_to_clean`, `next_to_use`, `next_to_alloc`, buffer arrays), `wx->rss_key`, `wx->rss_indir_tbl`, `wx->eims_enable_mask`, and `wx->eims_other`. Hardware register programming persists until reset or close. No disk persistence exists.

## Dependencies and Integration Points
It depends on `wx_vf.h` register definitions, `wx_lib.h` ring helpers (`wx_disable_rx_queue`, `wx_enable_rx_queue`, `wx_alloc_rx_buffers`, `wx_desc_unused`), PCI capability helpers, RSS key generation, netdev UC list APIs, and low-level mailbox UC update from `wx_vf.c`. `wx_vf_common.c` calls these routines during VF open/configure.

## Risks and Edge Cases
RSS setup divides over `wx->num_rx_queues`; zero queues would break RETA generation, so earlier queue setup must be valid. TX enable polling failures only log errors. UC filter programming ignores individual mailbox failures and returns only the count attempted. RX ring configuration enables RSC unconditionally, then optionally descriptor merge, which must match shared feature flags and buffer sizes.

## Test Signals
Validate MSI-X vector layout for one and multiple queue vectors, TX/RX ring enable polling, head writeback on/off, RX descriptor initialization, RSS key/RETA contents for queue counts 1-4, UC filter clear and add list behavior, and packet receive after reset/open cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_lib.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_lib.h

## Purpose
`wx_vf_lib.h` declares the shared VF interrupt, RSS, UC filter, TX, and RX ring configuration helpers used by VF lifecycle code.

## Important APIs, Types, and Functions
It declares `wx_write_eitr_vf()`, `wx_configure_msix_vf()`, `wx_write_uc_addr_list_vf()`, `wx_setup_psrtype_vf()`, `wx_setup_vfmrqc_vf()`, `wx_configure_tx_vf()`, and `wx_configure_rx_ring_vf()`.

## Control Flow
No runtime flow exists in the header. `wx_vf_common.c` invokes these functions during VF open, receive-mode updates, and hardware configuration.

## State and Persistence Behavior
The header owns no state. Declared functions program VF MMIO registers and update `struct wx` ring/RSS/interrupt state.

## Dependencies and Integration Points
It requires `struct wx`, `struct wx_q_vector`, `struct wx_ring`, and `struct net_device` declarations from surrounding headers. Concrete VF drivers normally do not include it directly; shared VF common code does.

## Risks and Edge Cases
Header/API drift would break VF builds. Because all functions operate on fully initialized queue/ring structures, callers must run common interrupt and resource setup first.

## Test Signals
Build VF modules and run open/configure paths that call every declared function. Static analysis should verify no function is declared but unused in supported configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/Makefile

## Purpose
The `ngbe` Makefile builds the Wangxun GbE PF driver module when `CONFIG_NGBE` is enabled.

## Important APIs, Types, and Functions
It declares `obj-$(CONFIG_NGBE) += ngbe.o` and composes `ngbe.o` from `ngbe_main.o`, `ngbe_hw.o`, `ngbe_mdio.o`, and `ngbe_ethtool.o`.

## Control Flow
Kbuild uses this file during kernel build. There is no runtime control flow, but object ordering determines which compilation units are linked into the PF module.

## State and Persistence Behavior
No runtime state or persistence is present. Build state is controlled by Kconfig and generated object files.

## Dependencies and Integration Points
The module depends on shared `libwx` objects from the parent Wangxun build and kernel networking/PCI infrastructure. It intentionally excludes `ngbevf`, which has a separate Makefile.

## Risks and Edge Cases
Adding a new `ngbe` source file requires updating `ngbe-objs`. If `CONFIG_NGBE` is disabled, neither PF nor the separate VF object listed under its Makefile is built by this directory entry.

## Test Signals
Run kernel/module builds with `CONFIG_NGBE=m` and `CONFIG_NGBE=y`; verify all referenced symbols from `libwx` resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_ethtool.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_ethtool.c

## Purpose
`ngbe_ethtool.c` installs ethtool operations for the GbE PF driver and implements the `ngbe`-specific ring-size setter that safely reconfigures rings while preserving shared `wx` ethtool behavior.

## Important APIs, Types, and Functions
The main public function is `ngbe_set_ethtool_ops()`. The local `ngbe_set_ringparam()` clamps and aligns TX/RX descriptor counts, handles running and stopped devices, and uses `ngbe_down()`, `wx_set_ring()`, `wx_configure()`, and `ngbe_up()` to apply changes. `ngbe_ethtool_ops` delegates most operations to shared `wx_ethtool` helpers for link settings, WOL, stats, pause, coalesce, channels, RSS, message level, and PTP stats.

## Control Flow
During probe `ngbe_set_ethtool_ops()` assigns `netdev->ethtool_ops`. Ring changes acquire `wx->reset_lock`, set `WX_STATE_RESETTING`, update counts directly if the netdev is down, or allocate temporary rings, bring the device down, swap ring counts through `wx_set_ring()`, reconfigure, and bring it back up. The reset flag and mutex are cleared at exit.

## State and Persistence Behavior
Descriptor counts are persisted only in driver runtime fields `wx->tx_ring_count`, `wx->rx_ring_count`, and per-ring `count` until module unload/reset. Ettool WOL and other settings go through shared helpers and hardware registers.

## Dependencies and Integration Points
The file depends on shared `wx_ethtool`, `wx_lib`, and `wx_hw` helpers plus `ngbe_down()`/`ngbe_up()` from `ngbe_main.c`. It integrates with the kernel ethtool netlink/ioctl surface.

## Risks and Edge Cases
Temporary ring allocation failure leaves old rings active. Running ring changes are disruptive and depend on `ngbe_down()`/`ngbe_up()` fully restoring link, interrupts, and phylink. The file uses shared `WX_MIN/MAX_TXD/RXD` constants rather than `NGBE_*` min/max names, so those shared constants must remain compatible.

## Test Signals
Run `ethtool -g/-G` with min, max, unaligned, unchanged, and allocation-failure cases; repeat while interface is up/down and with traffic. Verify queue counts, interrupts, and phylink recover after ring changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_ethtool.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_ethtool.h

## Purpose
`ngbe_ethtool.h` exposes the `ngbe` PF ethtool setup hook.

## Important APIs, Types, and Functions
It declares `ngbe_set_ethtool_ops(struct net_device *netdev)`.

## Control Flow
There is no runtime flow in the header. Probe code calls the declared function before registering the netdev.

## State and Persistence Behavior
No state is stored here. The implementation assigns the netdev's ethtool operation table.

## Dependencies and Integration Points
It requires `struct net_device` to be declared by including translation units and links `ngbe_main.c` to `ngbe_ethtool.c`.

## Risks and Edge Cases
The header must stay synchronized with the implementation. Missing inclusion in probe would leave the device without driver-specific ethtool operations.

## Test Signals
Build `ngbe` and verify `ethtool` operations are available after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_hw.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_hw.c

## Purpose
`ngbe_hw.c` contains GbE PF hardware-specific reset, EEPROM checksum, and SFP power-control routines layered on top of shared `wx` hardware helpers.

## Important APIs, Types, and Functions
Exports are `ngbe_eeprom_chksum_hostif()`, `ngbe_sfp_modules_txrx_powerctl()`, and `ngbe_reset_hw()`. Internal `ngbe_reset_misc()` runs common misc reset and powers down GPIO-controlled SFP modules.

## Control Flow
Probe calls `ngbe_reset_hw()` after management/flash readiness checks. Reset stops the adapter, optionally triggers a LAN reset for non-MDI MAC types and polls completion, resets misc hardware, clears hardware counters, reads the permanent MAC, initializes receive addresses, and re-enables PCI bus mastering. EEPROM checksum sends a host-interface command and checks firmware mailbox status for pass/fail.

## State and Persistence Behavior
The file updates hardware reset state, GPIO output state, counters, MAC receive address registers, and `wx->mac.perm_addr`/`num_rar_entries`. SFP power state persists in GPIO until changed or reset. No disk persistence exists.

## Dependencies and Integration Points
It depends on `wx_stop_adapter()`, `wx_reset_misc()`, `wx_clear_hw_cntrs()`, `wx_get_mac_addr()`, `wx_init_rx_addrs()`, host-interface command helpers, PCI APIs, and `ngbe_type.h` register constants. It is used by `ngbe_probe()`, resume, and reset paths.

## Risks and Edge Cases
LAN reset polling uses a fixed timeout and a hard-coded status register in the poll call. GPIO power control semantics are inverted (`0` is on), so wrong boolean use can power down optics. EEPROM checksum validation depends on firmware status magic values.

## Test Signals
Test probe/reset on MDI and RGMII/SFP variants, GPIO-controlled modules, failed host-interface checksum, LAN reset timeout, permanent MAC read, and post-reset traffic. Verify SFP power toggles during down/up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_hw.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_hw.h

## Purpose
`ngbe_hw.h` declares the GbE PF hardware helper API used by probe, reset, and module power paths.

## Important APIs, Types, and Functions
It declares `ngbe_eeprom_chksum_hostif()`, `ngbe_sfp_modules_txrx_powerctl()`, and `ngbe_reset_hw()`.

## Control Flow
No executable flow exists. `ngbe_main.c` calls these routines during probe, resume, reset, and link/module transitions.

## State and Persistence Behavior
The header owns no state. Implemented functions manipulate `struct wx` and hardware registers.

## Dependencies and Integration Points
It requires `struct wx` from shared headers and binds `ngbe_main.c` to `ngbe_hw.c`.

## Risks and Edge Cases
Prototype drift breaks module linkage. Since power control uses a boolean with hardware-inverted semantics, callers must use the API consistently instead of writing GPIO directly.

## Test Signals
Build and run reset/probe paths that call all declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_main.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_main.c

## Purpose
`ngbe_main.c` is the main PCI/netdev driver for Wangxun GbE PF devices. It matches PCI IDs, initializes `struct wx`, configures netdev features, handles probe/remove/suspend/resume/shutdown, opens and closes the interface, manages interrupts, service work, phylink, PTP, SR-IOV, and traffic-class reconfiguration.

## Important APIs, Types, and Functions
Important routines include `ngbe_probe()`, `ngbe_remove()`, `ngbe_open()`, `ngbe_close()`, `ngbe_up()`, `ngbe_down()`, `ngbe_setup_tc()`, `ngbe_suspend()`, `ngbe_resume()`, `ngbe_dev_shutdown()`, `ngbe_irq_enable()`, `ngbe_intr()`, `ngbe_msix_misc()`, `ngbe_misc_and_queue()`, `ngbe_request_irq()`, and `ngbe_request_msix_irqs()`. The `ngbe_netdev_ops` table delegates most packet/filter operations to shared `wx` helpers.

## Control Flow
Probe enables PCI memory, sets DMA mask, requests BARs, allocates netdev/`struct wx`, ioremaps BAR0, caps total VFs to seven, initializes shared software state, waits for flash, checks management firmware, resets hardware, validates EEPROM, configures WOL, reads EEPROM version, installs MAC filter, initializes service/interrupt scheme, initializes MDIO/phylink, registers netdev, and stores drvdata. Open controls hardware, allocates rings, configures the device, requests IRQs, connects PHY, sets queue counts, starts PTP, and calls `ngbe_up()`. Down/close stop phylink, notify VFs, disable queues/interrupts, update stats, reset filters/PTP, clean rings, free IRQs/resources, and release hardware.

## State and Persistence Behavior
Runtime state includes `wx` queues, flags, service timer/work, WOL bits, phylink/PHY pointers, interrupt scheme, PTP state, SR-IOV state, EEPROM id string, and netdev feature flags. Hardware state includes MAC/VLAN filters, GPIO, interrupts, queues, wake filters, and PF reset-done bit. WOL can affect device wake behavior across system sleep, but driver state is rebuilt on probe/resume.

## Dependencies and Integration Points
The file integrates with PCI core, netdev ops, phylink/MDIO, ethtool setup, shared `wx` library, PTP, mailbox/SR-IOV, WOL, and kernel PM. `.sriov_configure` points to `wx_pci_sriov_configure()`, and misc interrupts call `wx_msg_task()`.

## Risks and Edge Cases
Probe has many error labels; resource ownership across devm allocations, manual BAR requests, interrupt scheme, phylink, and allocated `rss_key`/`mac_table` needs failure-path coverage. `ngbe_disable_device()` notifies VFs and disables VF TX/RX only when `num_vfs` is nonzero. Shared-vector handling for seven VFs changes interrupt behavior. Suspend/resume must coordinate with WOL and netdev running state.

## Test Signals
Probe/remove all supported device IDs and subsystem variants, including GPIO-controlled SFP and NCSI/WOL variants. Test open/close with traffic, MSI-X/MSI/legacy interrupts, SR-IOV enable with seven VFs, mailbox interrupts, suspend/resume with WOL on/off, TC changes while up/down, PTP PPS events, and error injection in flash/management/reset/MDIO/register_netdev paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_mdio.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_mdio.c

## Purpose
`ngbe_mdio.c` implements MDIO bus access and phylink MAC callbacks for the GbE PF driver. It supports internal MDI-style PHY register access and external RGMII/Clause 22/Clause 45 access through shared MDIO helpers, then uses phylink to manage link state.

## Important APIs, Types, and Functions
Public entry point is `ngbe_mdio_init()`. Internal helpers are `ngbe_phy_read_reg_internal()`, `ngbe_phy_write_reg_internal()`, `ngbe_phy_read_reg_c22()`, `ngbe_phy_write_reg_c22()`, `ngbe_mac_config()`, `ngbe_mac_link_down()`, `ngbe_mac_link_up()`, and `ngbe_phylink_init()`. `ngbe_mac_ops` supplies phylink callbacks.

## Control Flow
Probe calls `ngbe_mdio_init()`, which allocates a devm MDIO bus, sets read/write callbacks and phy mask, enables Clause 45 callbacks for RGMII, registers the bus, finds the first PHY, initializes link fields, and creates a phylink instance. On link up, phylink configures flow control, writes LAN speed, sets MAC TX speed/enable, refreshes RX config and watchdog registers, updates `wx->speed`, resets PTP cycle counter if active, and notifies VFs. Link down sets unknown speed, resets PTP cycle counter, and notifies VFs.

## State and Persistence Behavior
State lives in devm MDIO bus resources, `wx->phydev`, `wx->phylink`, link/speed/duplex fields, phylink config, flow-control registers, MAC speed registers, and PTP timing state. No disk persistence exists.

## Dependencies and Integration Points
It depends on Linux MDIO/PHY/phylink APIs, shared `wx` MDIO helpers (`wx_phy_read/write_reg_mdi_c22/c45`), PTP helpers, SR-IOV link notifications, and `ngbe_type.h` speed/register constants.

## Risks and Edge Cases
Internal MDIO reads return `0xffff` for nonzero PHY addresses instead of an error, which can mask address bugs. `ngbe_mac_config()` is empty, so all MAC changes occur in link-up/down. The PHY mask excludes addresses 4-31, assuming PHY address below 4. Phylink fixed TX delay comment must match board design.

## Test Signals
Test MDIO discovery on MDI and RGMII hardware, Clause 22/45 reads/writes, no-PHY failure, link up/down at 10/100/1000, pause negotiation, PTP reset on link transitions, and VF link notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_mdio.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_mdio.h

## Purpose
`ngbe_mdio.h` declares the GbE PF MDIO/phylink initialization entry point.

## Important APIs, Types, and Functions
It declares `ngbe_mdio_init(struct wx *wx)`.

## Control Flow
The header has no executable flow. `ngbe_probe()` calls the declaration after interrupt-scheme initialization and before netdev registration.

## State and Persistence Behavior
No state is stored here. The implementation initializes MDIO, PHY, and phylink runtime state.

## Dependencies and Integration Points
It requires `struct wx` and connects `ngbe_main.c` with `ngbe_mdio.c`.

## Risks and Edge Cases
Prototype drift or missing inclusion would prevent the PF probe path from initializing PHY/link management.

## Test Signals
Build `ngbe` and verify probe calls MDIO initialization and handles `-ENODEV` when no PHY is discovered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_type.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_type.h

## Purpose
`ngbe_type.h` defines GbE PF device IDs, subsystem IDs, register constants, queue/descriptor limits, interrupt masks, EEPROM/firmware constants, and public `ngbe` driver entry points.

## Important APIs, Types, and Functions
It lists supported WX1860 PCI IDs and subsystem identifiers for SFP/RJ45/OCP/GPIO variants. It defines flash/load, EEPROM checksum/version, GPIO, misc interrupt, PHY config, LAN speed, queue count, MSI-X, RAR, table-size, descriptor, and VF-limit constants. It declares `ngbe_driver_name`, `ngbe_down()`, `ngbe_up()`, and `ngbe_setup_tc()`.

## Control Flow
There is no executable control flow. Probe, reset, MDIO, IRQ, and ethtool code consume these constants to choose hardware behavior and resource limits.

## State and Persistence Behavior
No memory is allocated. Constants describe hardware register state and default runtime limits for `struct wx` initialization.

## Dependencies and Integration Points
It includes Linux types and netdevice declarations, and is included by every `ngbe` source file. Shared `wx` helpers rely on limits initialized from these constants.

## Risks and Edge Cases
Incorrect PCI/subsystem IDs affect device binding and board-specific GPIO/NCSI/WOL behavior. Queue and VF limits must stay consistent with hardware pool allocation and SR-IOV code. Interrupt masks must align with hardware bit definitions or events can be missed.

## Test Signals
Compile and probe all listed IDs, verify subsystem-specific type detection, interrupt causes, descriptor ring limits, maximum VFs, and EEPROM version/checksum handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/Makefile

## Purpose
The `ngbevf` Makefile builds the Wangxun 1GbE VF driver object when `CONFIG_NGBE` is enabled.

## Important APIs, Types, and Functions
It declares `obj-$(CONFIG_NGBE) += ngbevf.o` and builds `ngbevf.o` from `ngbevf_main.o`.

## Control Flow
Kbuild consumes this file at build time only. There is no runtime logic.

## State and Persistence Behavior
No runtime state or persistence is present.

## Dependencies and Integration Points
The object links against shared `libwx` VF/common code. The use of `CONFIG_NGBE` ties the VF module build to the same config symbol as the PF driver.

## Risks and Edge Cases
If Kconfig expects a separate VF option, this Makefile does not provide one. Adding VF support files requires updating `ngbevf-objs`.

## Test Signals
Build with `CONFIG_NGBE=m/y` and verify `ngbevf` links and loads with its shared dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/ngbevf_main.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/ngbevf_main.c

## Purpose
`ngbevf_main.c` is the concrete PCI/netdev wrapper for Wangxun GbE virtual functions. It matches VF PCI IDs, allocates and initializes `struct wx`, wires shared VF common operations into netdev/PM hooks, initializes mailbox/reset state, registers the netdev, and delegates most runtime behavior to `libwx`.

## Important APIs, Types, and Functions
Important routines are `ngbevf_probe()`, `ngbevf_remove()`, `ngbevf_sw_init()`, and `ngbevf_set_num_queues()`. `ngbevf_netdev_ops` maps open/close to `wxvf_open()`/`wxvf_close()`, transmit to `wx_xmit_frame()`, validation to `eth_validate_addr()`, and MAC set to `wx_set_mac_vf()`. PCI PM uses `wxvf_suspend()` and `wxvf_resume()`.

## Control Flow
Probe enables PCI memory, sets DMA mask, requests BARs, allocates a one-queue netdev, maps BAR0, installs ethtool and netdev ops, then calls `ngbevf_sw_init()`. Software init runs `wx_sw_init()`, initializes mailbox parameters and lock, resets the VF through the PF, negotiates API 1.3, obtains or randomizes a MAC, sets queue/ITR/ring/work limits, and installs the queue-count callback. Probe then enables minimal features, initializes service and interrupt scheme, queries firmware version, registers the netdev, stores drvdata, and stops TX queues until open.

## State and Persistence Behavior
Runtime state is in `struct wx`: mailbox, VF API, MAC, ring counts, one TX/RX queue, interrupt scheme, service timer/work, firmware id string, and allocated `vfinfo`/RSS/MAC tables from shared init. No persistence beyond PCI/device state; all state is rebuilt on probe or VF reset.

## Dependencies and Integration Points
It depends on shared `wx_type`, `wx_hw`, `wx_lib`, `wx_mbx`, `wx_vf`, `wx_vf_common`, and `wx_ethtool` APIs. The VF depends on a functioning PF for reset, mailbox API negotiation, MAC assignment, queue configuration, link notifications, and MAC/VLAN filter programming.

## Risks and Edge Cases
If the PF is down or in reset, software init fails after allocations and must clean up correctly. Random MAC assignment occurs when PF provides none, but PF-side policy may still reject later MAC changes. Only one TX/RX queue and one MSI-X vector are configured, so queue-query results above one are not used here. Feature set is minimal compared to PF.

## Test Signals
Probe/remove with PF up/down, no assigned MAC, random MAC fallback, mailbox timeout, firmware version query failure, interrupt scheme failure, and netdev registration failure. Exercise open/close, MAC change, suspend/resume, link update, and PF reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/ngbevf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/ngbevf_type.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/ngbevf_type.h

## Purpose
`ngbevf_type.h` defines PCI device IDs and resource defaults for the Wangxun GbE VF driver.

## Important APIs, Types, and Functions
The header lists VF device IDs corresponding to WX1860 variants, and constants for one MSI-X vector, one RX/TX queue, 128 default TX/RX descriptors, and TX/RX work limits of 256.

## Control Flow
No executable control flow exists. The PCI ID table and VF software initialization consume these constants.

## State and Persistence Behavior
No state is stored. Constants become runtime limits in `struct wx` during probe.

## Dependencies and Integration Points
It is included by `ngbevf_main.c` and pairs with PF-supported VF device IDs.

## Risks and Edge Cases
Missing or incorrect device IDs prevent VF binding. Queue/vector limits must remain consistent with `ngbevf_set_num_queues()` and shared VF queue programming.

## Test Signals
Probe all listed VF IDs and validate queue/vector/ring defaults after `ngbevf_sw_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/ngbevf_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/Makefile

## Purpose
The `txgbe` Makefile builds the Wangxun 10/25/40GbE PF driver module when `CONFIG_TXGBE` is enabled.

## Important APIs, Types, and Functions
It declares `obj-$(CONFIG_TXGBE) += txgbe.o` and composes the module from `txgbe_main.o`, `txgbe_hw.o`, `txgbe_phy.o`, `txgbe_irq.o`, `txgbe_fdir.o`, `txgbe_ethtool.o`, and `txgbe_aml.o`.

## Control Flow
Kbuild uses this file only at build time. Object inclusion controls which TXGBE subsystems are linked: main PCI/netdev, hardware reset/checksum, PHY, IRQ, Flow Director, ethtool, and AML module/link support.

## State and Persistence Behavior
No runtime state or persistence is present.

## Dependencies and Integration Points
The module links against shared `libwx` sources and TXGBE headers. `txgbe_phy.o` is not part of this work item but is required by `txgbe_main.c` and `txgbe_irq.c`.

## Risks and Edge Cases
Adding source files without updating `txgbe-objs` causes unresolved symbols. Removing `txgbe_phy.o` would break PHY initialization and link IRQ handling.

## Test Signals
Build with `CONFIG_TXGBE=m/y` and verify all TXGBE objects and shared `libwx` symbols link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_aml.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_aml.c

## Purpose
`txgbe_aml.c` handles AML-family TXGBE module GPIO interrupts, firmware host-interface PHY/module commands, module EEPROM reads, SFP/QSFP capability decoding, link setup, and phylink MAC callbacks for 10/25/40G AML devices.

## Important APIs, Types, and Functions
Exports are `txgbe_gpio_init_aml()`, `txgbe_gpio_irq_handler_aml()`, `txgbe_test_hostif()`, `txgbe_read_eeprom_hostif()`, `txgbe_set_phy_link()`, `txgbe_identify_module()`, `txgbe_setup_link()`, and `txgbe_phylink_init_aml()`. Internal helpers include host-interface command builders, `txgbe_sfp_to_linkmodes()`, `txgbe_qsfp_to_linkmodes()`, `txgbe_get_mac_link()`, `txgbe_reconfig_mac()`, and phylink callbacks.

## Control Flow
AML up calls `txgbe_setup_link()`, which clears link interface/support masks, sets `WX_FLAG_NEED_MODULE_RESET`, and schedules service work. The service task later calls `txgbe_identify_module()`, which checks module-present GPIO, asks firmware for module info, validates SFP/QSFP identifiers, converts module EEPROM fields into phylink supported/advertising/interface masks, and sets `WX_FLAG_NEED_LINK_CONFIG`. A later service pass calls `txgbe_set_phy_link()` to send selected speed/autoneg/duplex to firmware. GPIO IRQs mask GPIO interrupts, detect module reset pins, set module-reset work, acknowledge EOI, and unmask.

## State and Persistence Behavior
Runtime state lives in `struct txgbe`: `link_support`, `advertising`, `link_interfaces`, and `link_port`, plus `struct wx` flags, speed, phylink, GPIO, flow-control, MAC registers, and PTP cyclecounter state. Firmware link configuration persists in device firmware/hardware until changed or reset. Module EEPROM reads are transient.

## Dependencies and Integration Points
The file depends on `wx_host_interface_command()`, phylink fixed-link APIs, GPIO/MMIO registers from shared and TXGBE type headers, PTP reset helpers, SR-IOV VF link notifications, and TXGBE hardware helpers such as `txgbe_enable_sec_tx_path()`. Ettool module EEPROM operations call `txgbe_read_eeprom_hostif()`.

## Risks and Edge Cases
`txgbe_read_eeprom_hostif()` copies four bytes per rounded dword into `data`, which assumes the caller buffer can hold rounded length. Unsupported modules return errors and leave link config pending. AML fixed-link phylink is driven by hardware status rather than an external PHY, so stale port status can misreport link. `txgbe_phylink_init_aml()` should destroy phylink if `phylink_set_fixed_link()` fails.

## Test Signals
Test SFP and QSFP module insertion/removal GPIO IRQs, unsupported module IDs, passive/active DAC, SR/LR/ER/CR speeds, 10/25/40G link setup, firmware command failures, module EEPROM page reads, PTP reset on link change, and VF link notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_aml.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_aml.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_aml.h

## Purpose
`txgbe_aml.h` declares AML-family TXGBE GPIO, firmware host-interface, module, link, EEPROM, and phylink helper functions.

## Important APIs, Types, and Functions
It declares `txgbe_gpio_init_aml()`, `txgbe_gpio_irq_handler_aml()`, `txgbe_test_hostif()`, `txgbe_read_eeprom_hostif()`, `txgbe_set_phy_link()`, `txgbe_identify_module()`, `txgbe_setup_link()`, and `txgbe_phylink_init_aml()`.

## Control Flow
There is no executable flow. `txgbe_main.c`, `txgbe_irq.c`, and `txgbe_ethtool.c` call these APIs for AML probe, link service, GPIO IRQ handling, and module EEPROM access.

## State and Persistence Behavior
The header owns no state. Implementations mutate `struct wx`, `struct txgbe`, firmware, GPIO, MAC, and phylink state.

## Dependencies and Integration Points
It requires declarations for `struct wx`, `struct txgbe`, `struct txgbe_hic_i2c_read`, and `irqreturn_t` from included context. It links AML-specific code into the generic TXGBE driver.

## Risks and Edge Cases
Callers must gate AML-only routines by MAC type where appropriate; SP devices do not need GPIO/module firmware paths. Prototype drift affects multiple compilation units.

## Test Signals
Build TXGBE and exercise AML probe/open/link/ethtool EEPROM paths, plus SP devices where AML hooks should be skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_aml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_ethtool.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_ethtool.c

## Purpose
`txgbe_ethtool.c` installs TXGBE ethtool operations and implements TXGBE-specific link settings, ring resizing, Flow Director rule get/set/delete, RX NFC reporting, and module EEPROM page reads.

## Important APIs, Types, and Functions
Public functions are `txgbe_get_link_ksettings()` and `txgbe_set_ethtool_ops()`. Local Flow Director helpers include `txgbe_get_ethtool_fdir_entry()`, `txgbe_get_ethtool_fdir_all()`, `txgbe_flowspec_to_flow_type()`, `txgbe_add_ethtool_fdir_entry()`, `txgbe_del_ethtool_fdir_entry()`, `txgbe_update_ethtool_fdir_entry()`, `txgbe_match_ethtool_fdir_entry()`, `txgbe_get_rxnfc()`, and `txgbe_set_rxnfc()`. `txgbe_get_module_eeprom_by_page()` proxies module EEPROM reads to AML firmware.

## Control Flow
Probe assigns the ethtool ops table. Ring resizing follows the same reset-lock/down/up pattern as `ngbe`, but calls `txgbe_down()`/`txgbe_up()`. RX NFC get paths report rule count, a single rule, or all rule locations from the sorted hlist. Rule insert validates perfect-filter mode, ring/VF target, location bounds, flow type, and one-mask-per-port constraint, computes the ATR perfect hash, optionally programs hardware if the netdev is running, then inserts the software rule. Delete erases hardware when needed and removes the software node under `fdir_perfect_lock`.

## State and Persistence Behavior
State includes runtime ring counts, reset state, `txgbe->fdir_filter_list`, `fdir_filter_count`, `fdir_mask`, and link mode masks in `struct txgbe`. Perfect filters are stored in memory and restored after Flow Director reinitialization; they are not persisted across driver unload.

## Dependencies and Integration Points
It depends on shared `wx_ethtool` helpers, TXGBE Flow Director programming, AML EEPROM access, phylink linkmode helpers, ethtool RX NFC APIs, and shared ring reset helpers.

## Risks and Edge Cases
Hardware supports only one perfect-filter mask per port; users must delete all rules to change masks. Rule duplicate detection uses bucket hash plus action, so different raw flows with the same bucket/action can be treated as duplicates. `ring_cookie` VF/ring mapping must match SR-IOV queue layout. Module EEPROM reads are only supported when `WX_FLAG_SWFW_RING` is set.

## Test Signals
Test `ethtool -k/-S/-g/-G/-n/-N`, perfect rule add/delete/list for TCP/UDP/SCTP/IPV4, drop and queue actions, VF queue actions, mask mismatch, duplicate rules, interface down/up restoration, and module EEPROM page reads on AML devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_ethtool.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_ethtool.h

## Purpose
`txgbe_ethtool.h` declares TXGBE ethtool setup and custom link-ksettings retrieval.

## Important APIs, Types, and Functions
It declares `txgbe_get_link_ksettings()` and `txgbe_set_ethtool_ops()`.

## Control Flow
No executable flow exists. Probe calls `txgbe_set_ethtool_ops()`, and the ethtool ops table calls `txgbe_get_link_ksettings()` for link reporting.

## State and Persistence Behavior
No state is stored. Implementations read `struct wx` and `struct txgbe` runtime link state and install an ethtool ops pointer.

## Dependencies and Integration Points
It requires `struct net_device` and `struct ethtool_link_ksettings` declarations from included context. It connects `txgbe_main.c` with `txgbe_ethtool.c`.

## Risks and Edge Cases
Prototype drift can break the TXGBE module. Non-SP link reporting depends on AML link masks populated by module identification.

## Test Signals
Build TXGBE and run `ethtool` link queries on SP and AML devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_fdir.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_fdir.c

## Purpose
`txgbe_fdir.c` implements TXGBE Flow Director support. It computes ATR signature and perfect-filter hashes, samples TCP transmit flows for signature filters, programs input masks and perfect filters, erases filters, initializes Flow Director hardware, restores software rules after reconfiguration, and frees rule state.

## Important APIs, Types, and Functions
Exports are `txgbe_atr_compute_perfect_hash()`, `txgbe_atr()`, `txgbe_fdir_set_input_mask()`, `txgbe_fdir_write_perfect_filter()`, `txgbe_fdir_erase_perfect_filter()`, `txgbe_configure_fdir()`, and `txgbe_fdir_filter_exit()`. Internal helpers include `txgbe_atr_compute_sig_hash()`, `txgbe_fdir_check_cmd_complete()`, `txgbe_fdir_add_signature_filter()`, `txgbe_fdir_enable()`, `txgbe_init_fdir_signature()`, `txgbe_init_fdir_perfect()`, and `txgbe_fdir_filter_restore()`.

## Control Flow
TX ATR sampling runs from transmit context: it decodes packet type, accepts TCP IPv4/IPv6 outer or tunnel flows, skips FIN packets, samples SYN or every configured interval, builds inverted receive-side input/common hash dwords, and programs a signature filter to the queue associated with the interrupt vector. Perfect-filter ethtool paths compute masks and hashes before calling `txgbe_fdir_write_perfect_filter()`. Driver configuration disables the secure RX path, initializes either signature or perfect mode, restores saved perfect rules, then re-enables secure RX.

## State and Persistence Behavior
Hardware state includes Flow Director hash keys, control registers, input mask registers, flex-byte config, hash/cmd registers, and programmed filters. Software state for perfect rules lives in `struct txgbe` and is freed on close through `txgbe_fdir_filter_exit()`. Signature ATR rules are generated dynamically and not stored as per-rule software state.

## Dependencies and Integration Points
The file depends on packet type decoding from `wx_type.h`, TX ring/buffer state, Flow Director register definitions from `txgbe_type.h`, secure RX path helpers, ethtool rule management, and transmit fast path callback `wx->atr` installed by `txgbe_sw_init()`.

## Risks and Edge Cases
IPv6 perfect masking is explicitly unsupported. Command completion polling uses a 100 microsecond total timeout, so slow hardware can produce errors. ATR assumes TX and RX queues are CPU-paired. Perfect filter restore skips rules whose target ring is now out of range. Mask validation is strict and hardware supports only one mask per port.

## Test Signals
Test ATR insertion for TCP IPv4/IPv6, tunnel and non-tunnel packets, SYN and sample-rate paths, and FIN skip. Test perfect filter add/delete/restore, mask validation, queue/drop actions, command timeout injection, secure RX path disable/enable, and ring-count changes with existing filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_fdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_fdir.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_fdir.h

## Purpose
`txgbe_fdir.h` declares TXGBE Flow Director hash, ATR, mask, filter programming, configuration, and cleanup APIs.

## Important APIs, Types, and Functions
It declares `txgbe_atr_compute_perfect_hash()`, `txgbe_atr()`, `txgbe_fdir_set_input_mask()`, `txgbe_fdir_write_perfect_filter()`, `txgbe_fdir_erase_perfect_filter()`, `txgbe_configure_fdir()`, and `txgbe_fdir_filter_exit()`.

## Control Flow
There is no executable flow. TXGBE software init installs `txgbe_atr()` and `txgbe_configure_fdir()` callbacks, while ethtool code calls the mask/filter APIs.

## State and Persistence Behavior
The header owns no state. Implementations operate on `struct wx`, `struct wx_ring`, `struct wx_tx_buffer`, and `union txgbe_atr_input` hardware/software Flow Director state.

## Dependencies and Integration Points
It requires TXGBE ATR types from `txgbe_type.h` and shared ring types. It connects transmit path, ethtool RX NFC, and device configuration paths to Flow Director programming.

## Risks and Edge Cases
Callers must hold appropriate locks for perfect-filter list operations; the low-level functions only program hardware. API misuse can program filters while the device is down or before Flow Director mode is initialized.

## Test Signals
Build TXGBE and run transmit ATR plus ethtool perfect-filter operations that reach every declared function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_fdir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_hw.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_hw.c

## Purpose
`txgbe_hw.c` implements TXGBE hardware reset, EEPROM checksum validation, thermal sensor threshold initialization, and secure TX path enable/disable.

## Important APIs, Types, and Functions
Exports are `txgbe_disable_sec_tx_path()`, `txgbe_enable_sec_tx_path()`, `txgbe_validate_eeprom_checksum()`, and `txgbe_reset_hw()`. Internal helpers are `txgbe_init_thermal_sensor_thresh()`, `txgbe_calc_eeprom_checksum()`, and `txgbe_reset_misc()`.

## Control Flow
Probe and reset call `txgbe_reset_hw()`: stop adapter, optionally assert LAN reset for non-copper media, wait for flash load after LAN software reset, reset misc state and thermal thresholds, program AML BME/RSC free control, clear counters, read permanent MAC, initialize receive address registers, and set PCI master. EEPROM validation first performs a fast read test, calculates checksum over the NVM image with AML I2C pointer range masked to `0xffff`, reads stored checksum, and compares.

## State and Persistence Behavior
Runtime state includes `wx->mac.sensor`, `wx->mac.perm_addr`, `wx->mac.num_rar_entries`, and EEPROM parameters. Hardware state includes secure TX disable bit, thermal sensor registers, LAN reset state, counters, RAR/MTA, AML BME/RSC control, and PCI bus mastering. No filesystem persistence.

## Dependencies and Integration Points
The file depends on shared `wx_stop_adapter()`, `wx_check_flash_load()`, `wx_reset_misc()`, `wx_clear_hw_cntrs()`, `wx_get_mac_addr()`, `wx_init_rx_addrs()`, NVM read helpers, MMIO helpers, PCI APIs, and TXGBE register constants. AML link-up code calls secure TX helpers.

## Risks and Edge Cases
Checksum calculation initializes the output by accumulating into caller-provided `*checksum`; callers must pass a zeroed value, as `txgbe_validate_eeprom_checksum()` does. Thermal sensors are only configured for SP physical port 0. Failed `phylink_set_fixed_link()` in AML code can leave phylink allocated, but that is outside this file. Reset behavior differs by media type and AML/SP generation.

## Test Signals
Test checksum success/failure and read errors, AML NVM masking, reset on copper/fiber/backplane/AML devices, thermal threshold programming on port 0 vs other ports, secure TX path disable polling timeout, and post-reset MAC address/filter initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_hw.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_hw.h

## Purpose
`txgbe_hw.h` declares TXGBE hardware helper APIs for secure TX path control, EEPROM checksum validation, and hardware reset.

## Important APIs, Types, and Functions
It declares `txgbe_disable_sec_tx_path()`, `txgbe_enable_sec_tx_path()`, `txgbe_validate_eeprom_checksum()`, and `txgbe_reset_hw()`.

## Control Flow
No executable flow exists. Probe/reset/link code calls these functions from `txgbe_main.c` and `txgbe_aml.c`.

## State and Persistence Behavior
The header owns no state. Implementations mutate `struct wx` and hardware registers.

## Dependencies and Integration Points
It requires `struct wx` from shared headers and binds TXGBE main/AML code to `txgbe_hw.c`.

## Risks and Edge Cases
Secure TX helpers must be paired correctly around MAC reconfiguration; callers need to handle polling failures from disable.

## Test Signals
Build TXGBE and exercise reset, EEPROM validation, and AML link-up secure TX paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_irq.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_irq.c

## Purpose
`txgbe_irq.c` implements TXGBE interrupt enablement, queue MSI-X IRQ request, and a nested misc IRQ domain for link, GPIO/module, PTP, and VF mailbox causes.

## Important APIs, Types, and Functions
Exports are `txgbe_irq_enable()`, `txgbe_request_queue_irqs()`, `txgbe_free_misc_irq()`, and `txgbe_setup_misc_irq()`. Internal pieces include `txgbe_request_link_irq()`, `txgbe_request_gpio_irq()`, `txgbe_misc_irq_domain_map()`, `txgbe_misc_irq_handle()`, `txgbe_misc_irq_thread_fn()`, and `txgbe_del_irq_domain()`.

## Control Flow
Open calls `txgbe_setup_misc_irq()` first, creating an irq_domain, mapping hardware sub-IRQs, requesting the top-level threaded misc IRQ, then requesting nested link and optional AML GPIO IRQs. Queue IRQs are requested separately for MSI-X queue vectors. The top-half reads ISB cause registers; in MSI-X mode it handles VF mailbox immediately and wakes the thread. In MSI/legacy mode it also schedules queue NAPI and captures misc causes. The thread dispatches link and GPIO causes through nested IRQs, handles PTP PPS events, and re-enables misc interrupts.

## State and Persistence Behavior
Runtime state is in `struct txgbe`: misc irq domain/chip, top-level irq, link/gpio virqs, and cached `eicr`. `wx->misc_irq_domain` records setup state. Hardware interrupt enable masks persist until disabled or reset. No disk persistence.

## Dependencies and Integration Points
It depends on Linux irqdomain/threaded IRQ APIs, shared queue interrupt handler `wx_msix_clean_rings`, PTP PPS handling, SR-IOV `wx_msg_task()`, TXGBE PHY link IRQ handler from `txgbe_phy`, AML GPIO handler, and shared interrupt enable helpers.

## Risks and Edge Cases
`txgbe_free_misc_irq()` assumes setup completed and frees GPIO only for non-SP devices; callers must avoid double-free on partial setup. VF mailbox handling in MSI-X mode re-enables misc interrupts before threaded sub-IRQ handling. Nested IRQ mappings must be disposed on all failure paths. Legacy/MSI top-half schedules only q_vector 0.

## Test Signals
Test MSI-X, MSI, and legacy interrupt modes; queue IRQ request failure unwinding; misc domain setup failure; link IRQ, AML GPIO module IRQ, VF mailbox, PTP PPS, and shared interrupt not-ours paths. Verify open/close repeatedly does not leak virqs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_irq.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_irq.h

## Purpose
`txgbe_irq.h` declares TXGBE interrupt setup, enable, queue IRQ request, and misc IRQ teardown APIs.

## Important APIs, Types, and Functions
It declares `txgbe_irq_enable()`, `txgbe_request_queue_irqs()`, `txgbe_free_misc_irq()`, and `txgbe_setup_misc_irq()`.

## Control Flow
There is no executable flow. `txgbe_main.c` calls these functions during open/up/close/error unwinding.

## State and Persistence Behavior
The header owns no state. Implementations mutate `struct wx`, `struct txgbe`, IRQ domain state, and hardware interrupt masks.

## Dependencies and Integration Points
It requires `struct wx` and `struct txgbe` declarations. It connects `txgbe_main.c` to `txgbe_irq.c`.

## Risks and Edge Cases
The header lacks an include guard, so repeated inclusion is safe only because it contains prototypes. Adding definitions would require a guard. Prototype drift affects TXGBE build.

## Test Signals
Build TXGBE with warnings enabled and exercise open/close paths that call every declared function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_main.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_main.c

## Purpose
`txgbe_main.c` is the main PCI/netdev driver for Wangxun 10/25/40GbE PF devices. It initializes shared `wx` state plus TXGBE-private state, configures netdev features and UDP tunnel offloads, handles probe/remove/shutdown, open/close/up/down/reset, service work, SR-IOV, PTP, Flow Director, phylink/PHY setup, and traffic-class changes.

## Important APIs, Types, and Functions
Important routines include `txgbe_probe()`, `txgbe_remove()`, `txgbe_open()`, `txgbe_close()`, `txgbe_up()`, `txgbe_down()`, `txgbe_reset()`, `txgbe_disable_device()`, `txgbe_setup_tc()`, `txgbe_do_reset()`, `txgbe_reinit_locked()`, `txgbe_service_task()`, `txgbe_module_detection_subtask()`, `txgbe_link_config_subtask()`, `txgbe_udp_tunnel_sync()`, `txgbe_sw_init()`, and `txgbe_init_type_code()`. `txgbe_netdev_ops` delegates common packet/filter/timestamp operations to shared `wx` helpers.

## Control Flow
Probe enables PCI memory, configures DMA/BAR/MMIO, caps total VFs to 63, installs ethtool/netdev/UDP tunnel ops, initializes `wx`, waits for flash and management firmware, resets hardware, sets feature flags, validates EEPROM checksum, installs default MAC filter, initializes service and interrupt scheme, builds EEPROM id, tests firmware host interface, allocates `struct txgbe`, initializes Flow Director state, initializes PHY/phylink, registers netdev, stores drvdata, stops TX queues, and checks PCIe bandwidth. Open allocates resources, configures hardware, sets up misc and queue IRQs, sets real queue counts, starts PTP, and completes up. Down/close disable traffic, stop link, notify VFs, reset, clean rings, free IRQs/resources, clear FDIR filters, and release hardware.

## State and Persistence Behavior
`struct wx` stores shared netdev, queues, flags, SR-IOV, PTP, RSS, Flow Director callbacks, service work, and link state. `struct txgbe` stores PHY/link/IRQ-domain/FDIR private state. Hardware state includes MAC, queues, interrupts, Flow Director, UDP tunnel ports, PF reset-done, GPIO/PHY, and firmware link settings. No disk persistence exists; EEPROM and module state are read from hardware/firmware.

## Dependencies and Integration Points
The file integrates PCI core, netdev, UDP tunnel NIC offload, ethtool, `libwx` hardware/library/PTP/mailbox/SR-IOV helpers, TXGBE hardware/PHY/AML/IRQ/FDIR subsystems, and kernel phylink. `.sriov_configure` points to `wx_pci_sriov_configure()`.

## Risks and Edge Cases
Probe error unwinding spans manual resources, devm resources, interrupt scheme, service work, PHY, and private TXGBE state. `txgbe_close_suspend()` frees resources without freeing IRQs, relying on suspend/shutdown context. FDIR filters are freed on close, so user rules do not survive close/open. AML and SP paths diverge for phylink, GPIO, RSC, TX head writeback, and firmware. VF notification during disable uses `wx_set_all_vfs()` after clearing `clear_to_send`.

## Test Signals
Probe/remove all supported SP/AML IDs, EEPROM checksum fail, firmware mismatch, PHY init fail, register_netdev fail, MSI-X/MSI/legacy interrupts, open/close with traffic, UDP tunnel port programming, TC changes, reset while up/down, SR-IOV max VFs, Flow Director mode/rules, PTP, AML module insertion/link setup, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_main.c -->
