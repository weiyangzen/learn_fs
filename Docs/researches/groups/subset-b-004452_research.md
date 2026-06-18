# subset-b-004452 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/phy.c

## Purpose
`phy.c` is the e1000e copper PHY service layer. It hides MDIO/Kumeran/HV/BM page-access details behind the PHY operation callbacks used by the e1000e MAC-specific code, and it owns most link setup, autonegotiation, forced speed/duplex, power-state, polarity, cable-length, reset, and PHY identification behavior for M88, IGP, IFE, BM, 82577/82578/82579, and related Intel PHYs.

## Important APIs, types, and functions
The exported functions populate the `struct e1000_phy_operations` style call sites declared in `phy.h`: MDIC access (`e1000e_read_phy_reg_mdic`, `e1000e_write_phy_reg_mdic`), per-PHY wrappers (`*_m88`, `*_igp`, `*_bm`, `*_bm2`, `*_hv`), Kumeran access (`e1000e_read_kmrn_reg*`, `e1000e_write_kmrn_reg*`), link setup (`e1000e_copper_link_setup_m88`, `e1000e_copper_link_setup_igp`, `e1000_copper_link_setup_82577`, `e1000e_setup_copper_link`), forced mode helpers (`e1000e_phy_force_speed_duplex_setup` and per-PHY force functions), state queries (`e1000e_get_phy_info_*`, polarity checks, downshift checks, cable length helpers), reset helpers, wake-register access, and `e1000e_determine_phy_address`. Static helpers cover autoneg wait/setup, BM/HV page routing, wake-register opcode access, and HV debug registers.

## Control flow
Normal copper bring-up runs through per-family setup, then `e1000e_setup_copper_link`. If `hw->mac.autoneg` is set, `e1000_copper_link_autoneg` masks `phy->autoneg_advertised` by `autoneg_mask`, programs MII advertisement and flow-control bits, restarts autoneg, optionally waits, and marks `mac.get_link_status`. If forced mode is requested, the selected `phy->ops.force_speed_duplex` updates both PHY BMCR and MAC CTRL state. Link status is then polled with sticky-safe double reads of `MII_BMSR`; when up, MAC collision distance and flow-control reconciliation run.

Register access flow depends on PHY family. M88 uses direct MDIC after semaphore acquisition. IGP selects `IGP01E1000_PHY_PAGE_SELECT` for high offsets. BM and HV encode page/register in synthetic offsets, choose PHY address 1 or 2, select pages, and special-case wake page 800 through address/data opcodes. HV pages below `HV_INTC_FC_PAGE_START` use vendor debug address/data ports.

## State and persistence behavior
This file mutates persistent driver state in `hw->phy` (`id`, `revision`, `type`, `addr`, `retry_enabled`, `speed_downgraded`, cable metrics, polarity, MDI-X, receiver status, original master/slave mode), `hw->mac` (`get_link_status`, forced speed/duplex effects), and `hw->fc.current_mode`. Hardware state persists in PHY pages, MDIC registers, Kumeran registers, `CTRL`, `PHY_CTRL`, wake-control bits, and power-down/LPLU settings. Semaphore callbacks bracket most MDIO operations; locked variants assume the caller already owns that synchronization.

## Dependencies and integration points
The implementation depends on `e1000.h` for `struct e1000_hw`, `er32`/`ew32`, `e1e_rphy`/`e1e_wphy`, error codes, MAC/PHY enums, and flow-control helpers. Linux MII constants and `FIELD_GET`/`FIELD_PREP` drive register bit extraction. MAC-specific files install these functions into operation tables and call them during probe, reset, open, suspend/resume, link change, ethtool diagnostics, and WoL setup.

## Risks
The major risks are hardware sequencing and concurrency. Page selection and `hw->phy.addr` are mutable global PHY access state, so missing semaphore coverage or incorrect use of locked variants can send MDIO transactions to the wrong page/address. Some status registers are sticky and require double reads; removing those reads can create false link states. BM wake-register access temporarily modifies wake enable bits and must restore them on all paths. Forced speed changes intentionally disable flow control and rewrite MAC CTRL; regressions can break half-duplex, MDI/MDIX, or autoneg behavior. Several paths return success when reset is blocked, which is intentional but easy to misread.

## Test signals
Useful signals include successful probe PHY ID/type detection, link-up/down across autoneg and forced 10/100/1000 modes, MDI/MDIX behavior, cable-length/polarity reporting through ethtool, suspend/resume and WoL wake-filter retention, absence of MDIC timeout/debug messages, and no regressions in PCH/BM/HV-specific reset and power-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/phy.h

## Purpose
`phy.h` is the public PHY interface and register-definition header for e1000e PHY support. It exposes the copper PHY helper functions implemented in `phy.c` and defines the family-specific PHY register offsets, page-encoding helpers, and bit masks needed by e1000e MAC implementations.

## Important APIs, types, and functions
The declarations cover reset blocking, PHY identification, address discovery, generic and family-specific register read/write functions, Kumeran accessors, link setup, forced speed/duplex, LPLU, polarity, downshift, cable length, PHY info, power up/down, BM wake-register access, HV page access, and 82577-specific helpers. The macros define `E1000_MAX_PHY_ADDR`, IGP page selection and AGC constants, BM/HV page and wake opcodes, Kumeran masks, IFE controls, and 82577 status/control/diagnostic masks.

## Control flow
This header does not implement runtime control flow, but it encodes key access conventions used by `phy.c`. `BM_PHY_REG(page, reg)` builds synthetic offsets containing page and register numbers. `BM_PHY_REG_PAGE` and `BM_PHY_REG_NUM` decode those offsets. The constants decide whether register access is direct MDIC, page-selected IGP/BM, wake-register opcode based, or HV debug-port based.

## State and persistence behavior
The header defines hardware register state, not storage. Its masks are used to mutate persistent PHY state such as wake enable bits, LPLU, SmartSpeed, Kumeran control, MDI/MDIX mode, polarity, speed, link status, and cable length. Because the macros define how page state is encoded, any mismatch with silicon expectations persists as wrong hardware programming.

## Dependencies and integration points
`phy.h` depends on `struct e1000_hw`, `enum e1000_phy_type`, `s32`, `u16`, `u32`, `bool`, and bit helpers from the e1000e/Linux include stack. It is included by e1000e source files that need PHY operations and by MAC-specific setup files that assign function pointers.

## Risks
The main risk is silent hardware misprogramming from incorrect constants. Register pages overlap by PHY family, and the BM/HV page encoding uses upper offset bits; a wrong shift or mask can access a valid but unintended PHY register. Prototype changes have broad blast radius because these functions are operation-table entry points.

## Test signals
Compile coverage across e1000e MAC variants is the first signal. Runtime signals include correct PHY type detection, link setup on each supported family, WoL register access on BM/HV PHYs, and ethtool PHY diagnostics matching expected speed, polarity, MDI-X, and cable length values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/ptp.c

## Purpose
`ptp.c` implements e1000e PTP Hardware Clock support for devices with hardware timestamp capability. It adapts e1000e SYSTIM/TIMINCA registers to the Linux PHC API through `ptp_clock_info`, `cyclecounter`, and `timecounter` operations.

## Important APIs, types, and functions
The PHC callbacks are `e1000e_phc_adjfine`, `e1000e_phc_adjtime`, `e1000e_phc_gettimex`, `e1000e_phc_settime`, and `e1000e_phc_enable`. When `CONFIG_E1000E_HWTS` is enabled, `e1000e_phc_getcrosststamp` and `e1000e_phc_get_syncdevicetime` provide ART/device cross timestamps. Lifecycle functions are `e1000e_ptp_init` and `e1000e_ptp_remove`; overflow maintenance is handled by delayed work `e1000e_systim_overflow_work`.

## Control flow
Initialization exits early unless `FLAG_HAS_HW_TIMESTAMP` is set. It copies the static `ptp_clock_info`, names the clock from the permanent MAC address, selects `max_adj` from `hw->mac.type` and the `TSYNCRXCTL` clock-source bit, optionally enables cross timestamp support on ART-capable systems, initializes delayed overflow work, schedules it, and registers the PHC. PHC operations take `adapter->systim_lock`, read or adjust the timecounter, and write TIMINCA when frequency changes.

## State and persistence behavior
Persistent driver state includes `adapter->ptp_clock`, `ptp_clock_info`, `ptp_delta`, `tc`, `cc`, and the delayed work item. Hardware state is in TIMINCA, SYSTIM, RX/TX timestamp registers, and cross timestamp latches. `adjfine` changes the hardware increment value and records the requested delta; `settime` reinitializes the software timecounter base without directly rewriting all hardware time registers.

## Dependencies and integration points
The file depends on the Linux PTP clock framework, timecounter/cyclecounter helpers, spinlocks, delayed work, and e1000e helpers such as `e1000e_get_base_timinca` and `e1000e_read_systim`. It integrates with probe/remove, timestamp ioctl paths, ethtool timestamp reporting elsewhere, and optional x86 ART cross timestamp support.

## Risks
The code explicitly notes non-monotonic SYSTIM readings, so lock coverage and timecounter conversion are critical. Wrong `max_adj` selection can allow invalid frequency adjustments for a clock source. Cross timestamp support has a short polling timeout and hardware latch dependency. Registering delayed work before PHC registration means remove paths must always cancel work for timestamp-capable devices.

## Test signals
Signals include PHC registration/removal logs, `ptp4l`/`phc2sys` frequency and time adjustment behavior, stable `gettimex64` readings, successful cross timestamp calls on ART-capable systems, overflow work rescheduling, and clean driver unload without delayed work or PHC leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/regs.h

## Purpose
`regs.h` defines e1000e memory-mapped register offsets and indexed-register macros. It is the low-level address map used by the driver for MAC control, descriptor rings, interrupts, statistics, flow control, wake/manageability, RSS, and PTP timestamping.

## Important APIs, types, and functions
The file contains macros rather than functions. Important groups include device control/status (`E1000_CTRL`, `E1000_STATUS`, `E1000_CTRL_EXT`), MDIO/PHY (`E1000_MDIC`, `E1000_PHY_CTRL`, `E1000_KMRNCTRLSTA`), RX/TX queue register macros (`E1000_RDBAL`, `E1000_RDLEN`, `E1000_TDBAL`, `E1000_TXDCTL`, etc.), interrupt registers, hardware statistics counters, receive address/VLAN/multicast tables, manageability registers, RSS tables, and PTP registers (`E1000_TSYNCRXCTL`, `E1000_TSYNCTXCTL`, `E1000_SYSTIM*`, `E1000_TIMINCA`, cross timestamp registers).

## Control flow
No runtime control flow exists here. The indexed queue macros encode hardware layout differences between the first four queues and later queues. Callers use these offsets through e1000e register access macros such as `er32` and `ew32`.

## State and persistence behavior
The definitions address persistent device MMIO state. Some counters are read-to-clear, some registers are write-only or read-only, and some control bits alter persistent hardware behavior across reset or power states. Comments identify access direction for many registers but enforcement is in the call sites.

## Dependencies and integration points
Every e1000e module that touches hardware registers depends on this address map. The PTP code uses the timestamp offsets, PHY code uses MDIC/Kumeran/manageability-related registers, ring setup uses queue macros, and stats/ethtool code use counter offsets.

## Risks
Incorrect offsets are high-impact because reads and writes may still hit valid MMIO locations with unrelated side effects. Queue macros must match hardware generation layout. Read-to-clear counters and timestamp latches require call-site care; using them for flushes or debug dumps can destroy state.

## Test signals
Signals include successful device probe, queue bring-up, interrupt delivery, stats accuracy, PTP operation, wake/manageability behavior, RSS programming, and absence of MMIO faults or unexpected counter resets during ethtool register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/Makefile

## Purpose
This Makefile defines the kernel build composition for the Intel fm10k Ethernet Switch Host Interface driver.

## Important APIs, types, and functions
The key build target is `obj-$(CONFIG_FM10K) += fm10k.o`. The `fm10k-y` object list includes main, common, PCI, netdev, ethtool, PF/VF, mailbox, SR-IOV, and TLV implementation files. Optional objects are `fm10k_debugfs.o` under `CONFIG_DEBUG_FS` and `fm10k_dcbnl.o` under `CONFIG_DCB`.

## Control flow
There is no runtime flow. Kbuild links listed objects into the `fm10k` module/built-in object when `CONFIG_FM10K` is enabled, and conditionally includes debugfs/DCB support based on kernel config.

## State and persistence behavior
No runtime state is stored here. Build configuration controls which driver features exist in the resulting binary, which indirectly affects runtime interfaces such as debugfs and DCB netlink ops.

## Dependencies and integration points
The Makefile integrates with Linux Kbuild and the driver source layout. The object list must match symbols declared in `fm10k.h` and referenced by fm10k main/PCI/netdev code.

## Risks
Omitting a required object causes unresolved symbols or missing runtime functionality. Including optional files without their configs would break builds where dependent kernel APIs are disabled. Reordering is generally low risk, but missing common/PF/VF/mailbox/TLV objects would be fatal.

## Test signals
Build `CONFIG_FM10K=m` and `=y` with and without `CONFIG_DEBUG_FS`/`CONFIG_DCB`. Confirm `modinfo`, module load, and optional debugfs/DCB interfaces match the selected config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k.h

## Purpose
`fm10k.h` is the central private driver header for fm10k. It defines queue/ring data structures, interface state, feature flags, SR-IOV data, MAC/VLAN work items, fast-path helpers, and cross-file function prototypes.

## Important APIs, types, and functions
Important types include `struct fm10k_ring`, `fm10k_ring_container`, `fm10k_q_vector`, `fm10k_ring_feature`, `fm10k_iov_data`, `fm10k_macvlan_request`, and `struct fm10k_intfc`. It defines queue descriptor bounds, jumbo limits, ITR defaults, state/flag bit enums, TX/RX buffer structures, queue stat structures, ftag metadata, and skb control block layout. Inline helpers include mailbox locking, descriptor status testing, descriptor-unused calculation, and debug/DCB stubs when configs are disabled.

## Control flow
The header wires subsystem boundaries. PCI/probe code owns `fm10k_intfc`, netdev code owns ring resources and open/close, ethtool code reads and mutates rings/RSS/coalescing, IOV code manages VFs, and service/macvlan work uses state bits and workqueue declarations. Atomic bit flags coordinate reset, service scheduling, link state, stats updates, and MAC/VLAN work.

## State and persistence behavior
`struct fm10k_intfc` is the persistent per-device state: VLAN bitmap, netdev/pci pointers, rings, q_vectors, MSI-X entries, `iov_data`, hardware stats, mailbox lock, MMIO pointers, timers/work, RSS tables, encapsulation ports, MAC/VLAN queue, debugfs dentries, DCB pause state, GLORT resources, and VID. Rings persist DMA addresses, descriptor memory, counters, queue indexes, VLAN/QoS, and NAPI associations.

## Dependencies and integration points
The header includes Linux netdevice, PCI, VLAN, RCU, cpumask, and Ethernet helpers plus fm10k PF/VF hardware headers. It is included by essentially every fm10k source file and is the contract among main, PCI, netdev, ethtool, debugfs, DCB, and SR-IOV modules.

## Risks
Layout changes can affect cache alignment, fast-path performance, and assumptions in ethtool/debugfs/stat collection. State-bit changes can introduce reset/service races. `skb->cb` use must fit kernel skb control buffer constraints. Optional stubs must match real function signatures exactly. RCU-protected members such as L2 acceleration and `iov_data` need matching lifetime rules.

## Test signals
Compile coverage with optional configs, open/close stress, queue count changes, stats updates under traffic, SR-IOV enable/disable, debugfs entry lifecycle, DCB setup, RSS changes, and lockdep/RCU diagnostics are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_common.c

## Purpose
`fm10k_common.c` implements hardware-generic helpers shared by PF and VF flows: PCIe capability discovery, invariant initialization, start/stop queue control, hardware statistic delta handling, queue statistic binding, and host readiness detection.

## Important APIs, types, and functions
Exports include `fm10k_get_bus_info_generic`, `fm10k_get_invariants_generic`, `fm10k_start_hw_generic`, `fm10k_disable_queues_generic`, `fm10k_stop_hw_generic`, `fm10k_read_hw_stats_32b`, `fm10k_update_hw_stats_q`, `fm10k_unbind_hw_stats_q`, and `fm10k_get_host_state_generic`. Static helpers compute MSI-X vector count and handle 48-bit stat deltas/base updates.

## Control flow
Bus info reads PCI config capability/status/control words and maps width, speed, and payload fields into `hw->bus_caps` and `hw->bus`. Invariants clear the DGLORT map and record max MSI-X vectors. Queue disable clears TX/RX enable bits for each queue, flushes, and polls until all queues report disabled or timeout. Stats update reads owner IDs before and after queue counters to avoid attributing deltas across queue ownership changes, then updates base and count fields. Host-state logic processes the mailbox, checks queue 0, mailbox timeout/state, DGLORT map availability, optionally requests lport map, and reports whether host is ready.

## State and persistence behavior
The file mutates `struct fm10k_hw` bus fields, `hw->mac.dglort_map`, `max_msix_vectors`, `tx_ready`, `get_host_state`, and queue stat bases/counts. It writes persistent hardware queue enable state and reads hardware counters that may advance independently. It treats removed hardware (`hw_addr == NULL`) as a special state to avoid MMIO writes.

## Dependencies and integration points
It depends on `fm10k_common.h`, fm10k register definitions, PCI config read hooks, mailbox operations, MAC operations, and queue/stat structures from `fm10k_type.h`. PCI probe/reset/open/close paths use these generic operations through hardware operation tables.

## Risks
Queue disable timeout handling is hardware-sensitive; failing to disable rings can leave DMA active during reset. Stats attribution depends on owner ID stability and base updates; mistakes produce negative/wrapped counters or cross-queue leakage. `fm10k_get_host_state_generic` can request resets on mailbox timeout or unexpected TX disable, so false positives disrupt link. Removed-device checks must prevent invalid MMIO.

## Test signals
Signals include correct PCIe bus reporting, successful reset/open/close, queue disable without timeout, stable per-queue and VF/PF counters under traffic and reset, host-ready transitions after mailbox/lport setup, and no MMIO warnings after hot-unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_common.h

## Purpose
`fm10k_common.h` declares fm10k generic hardware helpers and provides guarded MMIO write macros shared by PF/VF/common code.

## Important APIs, types, and functions
It declares PCI config and register reads, generic bus/invariant/start/stop/stats/host-state functions, and defines `FM10K_REMOVED`, `fm10k_write_reg`, `fm10k_write_sw_reg`, `fm10k_write_flush`, `fm10k_update_hw_base_32b`, and `fm10k_unbind_hw_stats_32b`.

## Control flow
The write macros use `READ_ONCE` on `hw->hw_addr` or `hw->sw_addr`, skip writes when the device mapping has been removed, and issue `writel` to DWORD-indexed register arrays. `fm10k_write_flush` performs a safe control-register read to flush prior posted writes.

## State and persistence behavior
The macros mutate device MMIO state but do not store state themselves. The helper macros update stat base fields in memory. Removed-device detection is a persistent safety convention used throughout the driver after surprise removal or teardown.

## Dependencies and integration points
The header includes `fm10k_type.h` for hardware structures and register constants. It is included by `fm10k_common.c` and lower-level PF/VF code that needs safe MMIO access.

## Risks
The register index unit is DWORDS, not bytes; passing byte offsets would write the wrong registers. `FM10K_REMOVED` only checks pointer presence, not device health. The 32-bit stat base macro assumes caller has already computed a valid delta.

## Test signals
Build coverage, hot-unplug/surprise-removal tests, queue start/stop flush behavior, and statistics consistency validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_dcbnl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_dcbnl.c

## Purpose
`fm10k_dcbnl.c` exposes limited IEEE DCBNL support for fm10k PF devices. It supports traffic-class priority mapping with strict priority only and PFC state tracking.

## Important APIs, types, and functions
The DCBNL ops are `fm10k_dcbnl_ieee_getets`, `fm10k_dcbnl_ieee_setets`, `fm10k_dcbnl_ieee_getpfc`, `fm10k_dcbnl_ieee_setpfc`, `fm10k_dcbnl_getdcbx`, and `fm10k_dcbnl_setdcbx`, collected in `fm10k_dcbnl_ops`. The exported `fm10k_dcbnl_set_ops` installs the ops only for PF MACs.

## Control flow
ETS get reports eight traffic classes, no CBS, zero bandwidth weights, strict TSA, and the current netdev priority-to-TC map. ETS set rejects nonzero shaping bandwidth and non-strict TSA, derives the required TC count from `prio_tc`, calls `fm10k_setup_tc` if TC count changes, and writes priority mappings. PFC get/set reads and writes `interface->pfc_en`; when running, PFC changes update RX drop enable state.

## State and persistence behavior
Persistent state is in netdev TC mappings and `interface->pfc_en`. Hardware queue mapping is updated indirectly through `fm10k_setup_tc`, and pause/drop behavior is updated through `fm10k_update_rx_drop_en`.

## Dependencies and integration points
This file depends on `CONFIG_DCB`, Linux DCBNL structs, netdev TC helpers, and fm10k PF setup paths. `fm10k.h` provides a no-op stub when DCB is disabled.

## Risks
The implementation intentionally rejects bandwidth shaping and non-IEEE DCBX modes; user tooling expecting full DCB support may fail. TC changes can reconfigure queue layout, so error propagation from `fm10k_setup_tc` matters. PFC changes affect packet drops only when propagated to running hardware.

## Test signals
Use `dcb`/`lldptool` or equivalent netlink calls to verify strict ETS only, priority mapping changes, PFC enable storage, PF-only ops installation, and queue/drop behavior after changing TC count while the interface is up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_dcbnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_debugfs.c

## Purpose
`fm10k_debugfs.c` creates debugfs views for fm10k descriptor rings. It exposes per-q_vector directories and per-ring files that dump TX or RX descriptor contents through seq_file.

## Important APIs, types, and functions
Important functions include descriptor seq operations (`fm10k_dbg_desc_seq_start`, `next`, `stop`, TX/RX `show`), `fm10k_dbg_desc_open`, q_vector lifecycle (`fm10k_dbg_q_vector_init`, `fm10k_dbg_q_vector_exit`), interface lifecycle (`fm10k_dbg_intfc_init`, `fm10k_dbg_intfc_exit`), and driver root lifecycle (`fm10k_dbg_init`, `fm10k_dbg_exit`). `dbg_root` stores the root dentry.

## Control flow
Driver init creates a root directory named after `fm10k_driver_name`. Interface init creates a PCI-name child directory. Each q_vector init creates `q_vector.NNN` and files for each TX/RX ring. Opening a descriptor file selects TX or RX seq ops based on whether the ring pointer is before the RX ring array in the q_vector allocation, then seq iteration walks descriptor indexes from zero to `ring->count - 1`.

## State and persistence behavior
Persistent debugfs state is held in `dbg_root`, `interface->dbg_intfc`, and `q_vector->dbg_q_vector`. The files read live descriptor memory and ring metadata; they do not snapshot or lock descriptor contents. Entries are removed recursively on q_vector, interface, and driver teardown.

## Dependencies and integration points
The file depends on `CONFIG_DEBUG_FS`, Linux debugfs and seq_file APIs, and ring/q_vector layout from `fm10k.h`. Stubs in `fm10k.h` remove this feature when debugfs is disabled.

## Risks
Descriptor dumps can race with queue teardown or DMA updates unless lifecycle ordering prevents open files from outliving rings. The TX/RX selection relies on q_vector ring memory layout. Output is privileged mode `0600`, but still exposes DMA addresses and descriptor contents.

## Test signals
With debugfs enabled, load/unload the module and open/close interfaces while checking directory creation/removal. Read TX/RX descriptor files before and after ring allocation, under traffic, and during interface teardown with lockdep/KASAN enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_ethtool.c

## Purpose
`fm10k_ethtool.c` implements the fm10k ethtool control and diagnostics surface: stats strings/data, register dumps, pause parameters, message level, ring sizing, interrupt coalescing, RSS hash fields/key/indirection table, mailbox self-test, private flags, channels, and timestamp info hook.

## Important APIs, types, and functions
The file defines `struct fm10k_stats` descriptors and stat arrays for netdev, interface, PF, mailbox, and queues. Core callbacks include `fm10k_get_strings`, `fm10k_get_sset_count`, `fm10k_get_ethtool_stats`, `fm10k_get_regs`, `fm10k_get_regs_len`, `fm10k_get_drvinfo`, pause get/set, ringparam get/set, coalesce get/set, RSS field get/set, `fm10k_mbx_test`, `fm10k_self_test`, RETA/RSS key get/set, channel get/set, and `fm10k_set_ethtool_ops`.

## Control flow
Stats collection updates driver stats, then walks descriptor arrays and optional PF/queue stats in the same order as string generation. Register dumps branch on PF vs VF and emit fixed register blocks; length macros must match dump logic and are guarded by `BUG_ON` in sub-block helpers. Ring resizing clamps and aligns requested counts, serializes through `__FM10K_RESETTING`, and if running, allocates replacement resources before swapping them into live rings across a down/up cycle. RSS field changes validate supported field combinations and rewrite MRQC when UDP RSS toggles. RSS table/key setters validate queue indexes and write changed entries. Channel changes update RSS limit and delegate queue remapping to `fm10k_setup_tc`.

## State and persistence behavior
Ettool operations read and mutate `fm10k_intfc` counters, ring counts, ITR settings, q_vector ITR fields, RSS flags, `reta`, `rssrk`, `rx_pause`, message level, and ring feature limits. Hardware state changes include descriptor resources, MRQC, RETA, RSSRK, pause/drop behavior, and queue layout. Self-test uses mailbox `test_result` and mailbox TX/process paths.

## Dependencies and integration points
The file depends on Linux ethtool APIs, vmalloc, netdev state, fm10k ring resource functions, mailbox TLV helpers, reset/open/close paths, and register definitions. It is installed by `fm10k_set_ethtool_ops` during netdev setup.

## Risks
String/data count ordering must stay exact or ethtool stats become corrupt. Register dump length macros must be updated with dump changes. Ring resizing is high risk because it reallocates DMA resources while preserving old resources on failure. UDP RSS can reorder fragmented UDP packets, and the code warns when enabling it. Mailbox self-test can time out if mailbox processing is blocked. Channel changes interact with DCB traffic-class mapping.

## Test signals
Run `ethtool -S`, `-d`, `-g/-G`, `-c/-C`, `-x/-X`, `-l/-L`, `--show-priv-flags`, `-t`, and pause operations on PF and VF devices. Verify stats counts match strings, register dump lengths match, traffic survives ring/channel changes, RSS distribution changes as requested, and mailbox self-test passes for VFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_iov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_iov.c

## Purpose
`fm10k_iov.c` implements PF-side SR-IOV support for fm10k: VF mailbox message handling, VF reset/event processing, VF resource allocation and teardown, DGLORT/lport setup, default MAC/VLAN assignment, VF stats, and netdev VF configuration NDOs.

## Important APIs, types, and functions
Static mailbox handlers include `fm10k_iov_msg_error` and `fm10k_iov_msg_queue_mac_vlan`; `iov_mbx_data` registers TLV handlers. Runtime entry points are `fm10k_iov_event`, `fm10k_iov_mbx`, `fm10k_iov_suspend`, `fm10k_iov_resume`, `fm10k_iov_update_pvid`, `fm10k_iov_disable`, `fm10k_iov_configure`, `fm10k_iov_update_stats`, and NDO helpers for VF MAC, VLAN, bandwidth, config, and stats.

## Control flow
VF MAC/VLAN mailbox requests are validated against VF enabled state, PF-assigned VLAN, locked MAC, multicast permission, and selected VID before calling hardware VLAN ops or queueing MAC requests to the PF switch manager. `fm10k_iov_event` handles VFLR by reading reset bits, resetting resources, and reconnecting VF mailboxes. `fm10k_iov_mbx` processes VF mailboxes under the PF mailbox lock, drains the upstream SM mailbox, resets invalid lports or timed-out mailboxes, checks SM mailbox space, and rotates `next_vf_mbx` to avoid starvation. Configure paths disable existing SR-IOV when safe, allocate `iov_data`, initialize PF/VF mailboxes, resume hardware resources, and enable PCI SR-IOV.

## State and persistence behavior
Persistent state lives in `interface->iov_data`, each `fm10k_vf_info`, mailbox state, VF GLORT/lport resources, VF stats arrays, PF/VF VLAN and MAC settings, VF rate limits, and `next_vf_mbx`. The pointer is freed with `kfree_rcu`; readers use RCU in event/mailbox paths. Hardware state includes DGLORT maps, VF lports, VLAN tables, queues, AER completion-abort mask, and PCI SR-IOV VF enablement.

## Dependencies and integration points
The file depends on `fm10k_pf.h`, `fm10k_vf.h`, TLV/mailbox helpers, PCI SR-IOV APIs, netdev VF NDOs, RCU, and hardware operation tables under `hw->iov`, `hw->mac`, and `hw->mbx`. It integrates with service task mailbox polling, reset/suspend/resume, netdev admin commands, and stats update.

## Risks
SR-IOV cannot be safely modified while VFs are assigned; the code logs and preserves current VF count. VF mailbox floods can starve the PF switch-manager mailbox, so backpressure handling and `next_vf_mbx` fairness matter. VLAN/MAC validation is security-sensitive because rogue VFs must not receive unauthorized traffic. RCU lifetime and mailbox locking must be preserved. The resume path masks PCIe completer abort reporting because VF reads of unowned queues can otherwise destabilize platforms.

## Test signals
Enable/disable varying VF counts, attempt changes while VFs are assigned, exercise VF FLR, mailbox traffic, MAC/VLAN/multicast requests, PF-assigned VLAN enforcement, VF rate limits, stats reads, suspend/resume, and AER behavior. Watch for mailbox timeout counters, SM mailbox full counters, stale MAC/VLAN queue entries, and RCU/lockdep warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_iov.c -->
