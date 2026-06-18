# subset-b-004420 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_pf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_pf.c

## Purpose
Implements the ENETC rev 4.x physical-function PCI driver. It discovers NETC/ENETC4 port capabilities, configures SI/VSI resources, initializes NTMP command access, creates the PF netdev, wires phylink/MDIO, and handles generation-specific MAC filtering, VLAN promiscuity, loopback, pause, speed, and graceful MAC stop/start.

## Important APIs, Types, and Functions
Important entry points are `enetc4_pf_probe`, `enetc4_pf_remove`, `enetc4_pf_init`, `enetc4_pf_netdev_create`, `enetc4_link_init`, and the `enetc4_ndev_ops` netdev operations. Capability and resource setup is split across `enetc4_get_port_caps`, `enetc4_default_rings_allocation`, `enetc4_set_si_msix_num`, and `enetc4_configure_port_si`. MAC receive-mode programming uses `enetc4_psi_do_set_rx_mode`, `enetc4_pf_set_uc_exact_filter`, MAFT helpers, and hash-filter fallback. Phylink callbacks are `enetc4_pl_mac_config`, `enetc4_pl_mac_link_up`, and `enetc4_pl_mac_link_down`.

## Control Flow
Probe calls generic `enetc_pci_probe`, verifies PF-only register blocks, reads revision and driver data, initializes `struct enetc_pf`, programs MAC addresses, creates the NTMP CBDR, configures port/SI defaults, gets SI capabilities, allocates and registers a netdev, then creates debugfs. Link-up control programs port speed, RGMII/RMII fixed speed when in-band autoneg is absent, half-duplex flow control, pause thresholds, and enables RX/TX. Link-down performs graceful RX and TX stops with polling for empty MAC queues.

## State and Persistence
Persistent hardware state includes primary MAC registers, SI ring counts, MSI-X allocation registers, VLAN/MAC promiscuity bits, PM/IF mode registers, port speed, pause thresholds, MAFT entries, RSS key/table, and NTMP command ring registers. Software state is stored in `struct enetc_pf` capabilities and `num_mfe`, `struct enetc_si` workqueue and NTMP user, and `struct enetc_ndev_priv` speed/offload/link data.

## Dependencies and Integration Points
Depends on generic ENETC PCI/SI setup in `enetc.c`, common PF helpers in `enetc_pf_common.c`, register definitions in `enetc4_hw.h` and `enetc_hw.h`, NTMP functions from `ntmp.c`, phylink, MDIO bus helpers, clocks, debugfs, and the driver-data table selecting `enetc4_pf_ethtool_ops` or PPM ethtool ops. It expects `netc_blk_ctrl.c` platform initialization to have configured NETCMIX/IERB before PCI child probing on i.MX NETC systems.

## Risks
Risk concentrates around resource partitioning math for rings/MSI-X, MAFT update windows, async receive-mode work running during teardown, pseudo-MAC handling, link-down graceful-stop timeouts, and different register layouts between ENETC4 PF and PPM devices. `cancel_work` rather than `cancel_work_sync` in destroy depends on workqueue teardown ordering.

## Test Signals
Useful signals are PF probe/remove, link mode matrix tests for RGMII/RMII/SGMII/XGMII/USXGMII, `ip link set promisc/allmulti`, unicast list overflow to hash fallback, VLAN filter toggling, loopback feature toggling, ethtool RSS operations through NTMP, debugfs MAFT visibility, suspend/resume after NETC block reinit, and traffic tests around link down/up transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_cbdr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_cbdr.c

## Purpose
Provides control buffer descriptor ring support for ENETC command operations. Rev 1 hardware uses `struct enetc_cbdr` and `struct enetc_cbd`; ENETC4 delegates command-ring setup and RSS table access to the NTMP library.

## Important APIs, Types, and Functions
Exports `enetc_setup_cbdr`, `enetc_teardown_cbdr`, `enetc_send_cmd`, `enetc_clear_mac_flt_entry`, `enetc_set_mac_flt_entry`, `enetc_set_fs_entry`, `enetc_get_rss_table`, `enetc_set_rss_table`, `enetc4_setup_cbdr`, `enetc4_teardown_cbdr`, `enetc4_get_rss_table`, and `enetc4_set_rss_table`. Internal helpers include `enetc_clean_cbdr`, `enetc_cbd_unused`, and `enetc_cmd_rss_table`.

## Control Flow
Legacy setup allocates coherent descriptors, enforces 128-byte DMA alignment, writes CBDR base/length/cache attributes, initializes producer/consumer indices, and enables the ring. `enetc_send_cmd` copies a command descriptor to the next slot, updates PIR, busy-waits for CIR under contexts that may hold RTNL, copies writeback data, and cleans completed descriptors. RFS and RSS commands allocate aligned command data buffers, populate descriptor class/cmd fields, send, and free DMA data.

## State and Persistence
Software ring state tracks `next_to_clean`, `next_to_use`, DMA base, ring size, register pointers, and owning DMA device. Hardware state persists in CBDR mode/base/length/PIR/CIR registers and in command-programmed tables such as MAC filters, RFS entries, and RSS indirection. ENETC4 stores equivalent command-ring state in `si->ntmp_user`.

## Dependencies and Integration Points
Used by PF, VF, ethtool RX classification, RSS, and QoS/PSFP command paths. It depends on ENETC register accessors, `enetc_cbd_alloc_data_mem` and `enetc_cbd_free_data_mem` from common driver code, and NTMP functions for rev 4 table management.

## Risks
Risks include missing synchronization around callers using the legacy ring, fixed busy-wait timeouts, unaligned DMA rejection, descriptor status masking that only logs command status during cleaning, and RSS count assumptions requiring a full hardware table. ENETC4 wrappers require NTMP user initialization before ethtool RSS operations.

## Test Signals
Probe should fail cleanly on allocation or alignment failure. Exercise MAC exact filters, ethtool RXNFC RFS rules, RSS get/set, CBDR timeout injection, and teardown after failed mid-probe command setup. Command errors should produce warnings without leaving stale descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_cbdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ethtool.c

## Purpose
Implements ethtool operations for ENETC PFs, VFs, ENETC4 PFs, and ENETC4 PPM devices. It provides register dumps, statistics strings/data, RSS configuration, RX flow classification, coalescing, timestamp capability reporting, phylink settings, WOL delegation, pause controls, and MAC Merge preemption support.

## Important APIs, Types, and Functions
Main exported symbols are `enetc_pf_ethtool_ops`, `enetc4_pf_ethtool_ops`, `enetc4_ppm_ethtool_ops`, `enetc_vf_ethtool_ops`, `enetc_set_ethtool_ops`, `enetc_set_rss_key`, `enetc_mm_commit_preemptible_tcs`, and `enetc_mm_link_state_update`. Key internals include `enetc_get_regs`, `enetc_get_ethtool_stats`, `enetc_get_rxfh`, `enetc_set_rxfh`, `enetc_set_rxnfc`, `enetc_set_cls_entry`, `enetc_get_ts_info`, `enetc_get_mm`, and `enetc_set_mm`.

## Control Flow
Stats flow builds string counts from SI rings plus PF-only port/MAC counters, selecting rev1 or rev4 register sets and optional pMAC/QBU counters. RSS operations access PF RSS key registers and dispatch table get/set through `si->ops`, which maps to legacy CBDR or NTMP. RXNFC inserts/deletes RFS rules by translating ethtool flow specs into `struct enetc_cmd_rfse` CBDR commands and mirroring rule state in `priv->cls_rules`. Coalesce changes update private interrupt settings and restart the netdev if running. MAC Merge operations serialize with `mm_lock`, program `PFPMR`, `MMCSR`, and preemptible TC registers, and poll verification when needed.

## State and Persistence
Persistent state includes hardware counters, RSS key and indirection table, RFS table entries, interrupt coalescing registers, PHC association, wakeup enable state, pause negotiation through phylink, and MAC Merge registers. Software mirrors classification rules, interrupt moderation mode, RX DIM enablement, `active_offloads`, preemptible traffic classes, and last known speed.

## Dependencies and Integration Points
Integrates with ethtool core, phylink, PHY WOL APIs, PTP qoriq devices, ENETC CBDR/NTMP RSS ops, netdev flow classifier state, and revision-specific register maps. PF/VF selection happens indirectly through `si->drvdata->eth_ops` in `enetc_set_ethtool_ops`.

## Risks
Risks include string/stat count drift, incorrect rev1/rev4 counter selection, byte-order quirks in RFS MAC matches, stale software `cls_rules` after failed hardware commands, netdev restart side effects during coalesce updates, PHC lookup assumptions by PCI devfn, and MAC Merge workaround behavior depending on link partner timing.

## Test Signals
Run `ethtool -S`, `-d`, `-x`, `-X`, RXNFC add/delete/list, coalescing get/set with device running, PTP timestamp info with and without PHC, WOL through PHY, pause settings through phylink, and `ethtool --show-mm/--set-mm` on QBU-capable hardware. Compare stat counts with `get_sset_count` and verify rev4 pseudo-MAC counters skip unavailable MAC blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_hw.h

## Purpose
Defines the core ENETC hardware ABI: PCI IDs, SI/port/global register offsets, descriptor formats, command descriptor formats, TSN/PSFP structures, mailbox definitions, stats register names, and register accessors with the LS1028A MDIO erratum workaround.

## Important APIs, Types, and Functions
Important types are `struct enetc_hw`, `union enetc_tx_bd`, `union enetc_rx_bd`, `struct enetc_cbd`, `struct enetc_cmd_rfse`, TSN command data structures such as `tgs_gcl_data`, `streamid_conf`, `sfi_conf`, `sgi_table`, `sgcl_conf`, and `fmi_conf`, plus mailbox structures and enums. Important inline helpers include `enetc_rd`, `enetc_wr`, `enetc_port_rd`, `enetc_port_wr`, `enetc_port_rd_mdio`, `enetc_get_primary_mac_addr`, `enetc_load_primary_mac_addr`, VLAN BDR enable helpers, `enetc_set_bdr_prio`, and time conversion helpers.

## Control Flow
This header has mostly declarative control flow. Its active logic wraps MMIO accesses. Normal register reads take a read side of `enetc_mdio_lock` only when static key `enetc_has_err050089` is enabled; MDIO register accessors take a write lock to exclude concurrent non-MDIO access. 64-bit stat reads use native `ioread64` or a high/low/high retry sequence on 32-bit systems.

## State and Persistence
The file defines persistent hardware state layout: SI mode/capability registers, BDR registers, CBDR registers, VF/PF mailbox registers, port MAC/VLAN/filter/QBU/QBV/PSFP registers, global revision registers, TX/RX descriptor bit fields, and CBDR command classes. `struct enetc_hw` stores MMIO base pointers for SI, port, and global blocks.

## Dependencies and Integration Points
Included throughout the ENETC driver and indirectly by PF, VF, MDIO, ethtool, QoS, CBDR, and PTP paths. It exposes erratum symbols defined by `enetc_mdio.c` and `enetc_pci_mdio.c`, and it shares command descriptor definitions with QoS and ethtool classification code.

## Risks
This is hardware ABI. Any offset, mask, endian type, or descriptor field mistake can silently corrupt packet DMA, command execution, timestamping, TSN scheduling, or filtering. Erratum locking misuse can reintroduce dropped MDIO transactions or cause lockdep failures when hot accessors are called without `enetc_lock_mdio`.

## Test Signals
Compile coverage across PF/VF/rev1/rev4/QoS/PTP configs, register dumps matching datasheets, traffic with TX/RX descriptors on 32-bit and 64-bit builds, MDIO stress with ERR050089 enabled, RSS/RFS/CBDR command tests, Qbv/Qbu/PSFP offloads, and endian-sensitive packet offload validation are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ierb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ierb.c

## Purpose
Implements the LS1028A ENETC Integrated Endpoint Register Block platform driver. It fixes boot-time IERB FIFO/buffer parameters that are copied into ENETC PFs after FLR and are read-only from PF space.

## Important APIs, Types, and Functions
Exports `enetc_ierb_register_pf`. Internal components are `struct enetc_ierb`, `enetc_ierb_write`, `enetc_ierb_probe`, the OF match table for `fsl,ls1028a-enetc-ierb`, and the platform driver registration.

## Control Flow
Probe allocates driver state, maps the IERB resource, sets the free buffer depletion threshold, and stores drvdata. A PF later calls `enetc_ierb_register_pf`, which maps the PCI function to an ENETC port, defers if the platform driver is not ready, calculates TX byte credit, TX memory allocation, and RX credit from `ENETC_MAC_MAXFRM_SIZE`, then writes the per-port IERB registers.

## State and Persistence
Persistent state is IERB hardware configuration: transmit byte credit, transmit memory byte allocation, receive initial credits, and global free-memory depletion threshold. Software state only stores the mapped IERB base pointer. Values survive as platform register state and influence PF behavior after FLR.

## Dependencies and Integration Points
Depends on `enetc_pf_to_port`, ENETC max frame constants, platform device probing, and the PF probe path in `enetc_pf.c` that locates this device by compatible string. The header provides a no-op/stub path when the driver is disabled.

## Risks
Risks include PF probing before IERB readiness, stale device trees that omit the IERB node, port-number mapping errors, and hard-coded formulas that assume the jumbo/preemption memory recommendations remain valid. Misprogramming can cause FIFO depletion, frame drops, or RX lock-up under jumbo and preemption traffic.

## Test Signals
Probe ordering should handle `-EPROBE_DEFER`; PF probe should warn but continue on missing unavailable IERB. Validate register writes against LS1028A datasheet recommendations, jumbo frame traffic, frame preemption traffic, FLR behavior, and multi-port contention under high RX/TX load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ierb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ierb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ierb.h

## Purpose
Declares the optional ENETC IERB registration hook used by the rev1 PF driver to program LS1028A IERB resources before normal PF setup.

## Important APIs, Types, and Functions
The sole API is `enetc_ierb_register_pf(struct platform_device *pdev, struct pci_dev *pf_pdev)`. When `CONFIG_FSL_ENETC_IERB` is enabled it is an external symbol; otherwise it is an inline stub returning `-EOPNOTSUPP`.

## Control Flow
Runtime control flow is compile-time selected. Enabled builds call into `enetc_ierb.c`; disabled builds let callers receive an unsupported error without adding conditional compilation at call sites.

## State and Persistence
The header owns no state. It represents a build-time dependency edge between PF probing and platform IERB programming.

## Dependencies and Integration Points
Includes PCI and platform-device declarations. Used by `enetc_pf.c` during PF probe and by `enetc_ierb.c` for the implementation signature.

## Risks
The main risk is callers treating `-EOPNOTSUPP` as fatal on configurations where the platform driver is intentionally absent. Prototype drift would break module builds or stubs.

## Test Signals
Build with `CONFIG_FSL_ENETC_IERB=y/m` and disabled. PF probe should defer only when an enabled IERB node exists but is not yet ready; disabled builds should compile and warn/continue from the PF path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ierb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_mdio.c

## Purpose
Implements ENETC external/internal MDIO controller accesses for Clause 22 and Clause 45 PHY transactions, plus allocation of a minimal `struct enetc_hw` for standalone MDIO PCI devices and definition of the LS1028A MDIO erratum lock.

## Important APIs, Types, and Functions
Exports `enetc_mdio_write_c22`, `enetc_mdio_write_c45`, `enetc_mdio_read_c22`, `enetc_mdio_read_c45`, `enetc_hw_alloc`, and `enetc_mdio_lock`. Internal helpers are `enetc_mdio_rd`, `enetc_mdio_wr`, `enetc_mdio_is_busy`, and `enetc_mdio_wait_complete`.

## Control Flow
Each transaction programs `ENETC_MDIO_CFG` for external MDIO defaults and Clause 22/45 mode, waits for busy clear, writes the port/device control fields, optionally writes the Clause 45 register address, then writes data or triggers a read and waits again. Read errors return `0xffff` to match MDIO absent-device semantics. `enetc_hw_alloc` devm-allocates a hardware wrapper with only the port register base set.

## State and Persistence
Hardware state includes MDIO configuration, control, address, and data registers. The controller clock divide and hold/negative-edge settings are programmed on every transaction. Software state lives in `struct enetc_mdio_priv` via the selected `mdio_base` and ENETC hardware pointer. `enetc_mdio_lock` is global state used by accessor wrappers when ERR050089 is active.

## Dependencies and Integration Points
Used by PF common code for port/internal MDIO buses and by the PCI MDIO driver. It relies on `enetc_port_rd_mdio` and `enetc_port_wr_mdio`, which take the erratum write lock when active. Integrates with Linux `mii_bus`, OF MDIO registration, phylink/PCS creation, and standalone central EMDIO probing.

## Risks
Clock divider values are fixed; incorrect board clocks could violate MDIO timing. Busy polling timeout is 10 ms. Returning `0xffff` hides read errors by design but can mask wiring issues. Erratum locking requires all non-MDIO register accesses to use the matching accessors.

## Test Signals
Probe PHYs through port MDIO, internal PCS MDIO, and PCI central MDIO; test Clause 22 and 45 reads/writes, absent PHY reads, timeout/error injection, concurrent MDIO plus packet traffic on LS1028A erratum hardware, and phylink link mode negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_msg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_msg.c

## Purpose
Implements PF-side mailbox handling for messages from VFs to the PF, currently focused on VF requests to manage the primary MAC address.

## Important APIs, Types, and Functions
Exports `enetc_msg_psi_init` and `enetc_msg_psi_free`. Internal functions include `enetc_msg_psi_msix`, `enetc_msg_task`, `enetc_msg_alloc_mbx`, `enetc_msg_free_mbx`, and interrupt mask helpers.

## Control Flow
Initialization requests the SI message MSI-X vector, sets the PSI message interrupt vector register, initializes work, allocates a coherent receive mailbox for each active VF, writes mailbox DMA addresses to hardware, and enables message-received interrupts. The IRQ disables MR interrupts and schedules work. Work loops over pending VF bits, calls `enetc_msg_handle_rxmsg` in `enetc_pf.c`, writes the completion code and W1C receive bit, then re-arms interrupts once no messages remain. Free cancels work, disables interrupts, frees mailboxes, clears hardware addresses, and releases the IRQ.

## State and Persistence
Persistent hardware state is the mailbox receive DMA address registers, PSI interrupt routing, interrupt enable/disable state, and message receive/status registers. Software state is `pf->rxmsg[]`, `pf->msg_task`, and the IRQ name.

## Dependencies and Integration Points
Used only when SR-IOV VFs are enabled by `enetc_sriov_configure`. It depends on PF state from `enetc_pf.h`, DMA coherent allocation, PCI MSI-X vector allocation done earlier, and command decoding in `enetc_pf.c`.

## Risks
Mailbox count must match active VF count. Message buffers are trusted enough to parse command headers after DMA writeback, so malformed or unsupported commands need robust status handling. Races around disabling SR-IOV are handled by `cancel_work_sync`, but interrupt masking/rearming order is critical.

## Test Signals
Enable and disable SR-IOV, set VF MAC from inside a VF, attempt unsupported mailbox command types, remove PF while VFs are active, inject mailbox allocation failures, and confirm interrupts re-arm after bursts of VF messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pci_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pci_mdio.c

## Purpose
Provides a PCI driver for standalone ENETC/NETC central external MDIO controllers and enables/disables the LS1028A ERR050089 static-key workaround for affected devices.

## Important APIs, Types, and Functions
Important functions are `enetc_pci_mdio_probe`, `enetc_pci_mdio_remove`, `enetc_emdio_enable_err050089`, and `enetc_emdio_disable_err050089`. It defines the exported static key `enetc_has_err050089` and matches Freescale ENETC MDIO plus NETC EMDIO PCI IDs.

## Control Flow
Probe maps BAR0, allocates an `enetc_hw`, allocates an MDIO bus with `enetc_mdio_priv`, assigns Clause 22/45 read/write callbacks, performs FLR, enables PCI memory access, requests the BAR, increments the erratum static key for affected ENETC MDIO devices, registers the OF MDIO bus, and stores the bus as drvdata. Remove unregisters the bus, decrements the workaround key, unmaps registers, releases the region, and disables the PCI device.

## State and Persistence
State includes PCI BAR mapping, MDIO bus registration, `mdio_priv->mdio_base = ENETC_EMDIO_BASE`, and the global static branch controlling erratum locking in `enetc_hw.h`. Hardware state is reset by FLR and later configured by MDIO transactions.

## Dependencies and Integration Points
Depends on `enetc_mdio.c` callbacks, `enetc_hw_alloc`, PCI core, OF MDIO registration, and the global register accessor erratum path. It can coexist with port-local MDIO buses used by PF drivers.

## Risks
Probe order and static-key reference counting matter: enabling the erratum changes locking behavior globally for all ENETC accessors. Error unwinding must disable the key only after it has been incremented. `pci_iomap` occurs before `pci_enable_device_mem`, so platform quirks around BAR mapping can surface.

## Test Signals
Register central MDIO with DT PHY children, unload/reload the module while other ENETC devices run, confirm static-key enable/disable messages and reference counts across multiple devices, test Clause 22/45 transactions, and validate all error unwind paths under forced allocation/registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pci_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf.c

## Purpose
Implements the original ENETC rev1 PF driver. It initializes PF hardware, partitions resources for VFs, manages MAC/VLAN filters, handles SR-IOV mailbox commands, configures port MAC/phylink behavior, initializes RSS/RFS command memory, and registers the PF netdev.

## Important APIs, Types, and Functions
Important functions include `enetc_pf_probe`, `enetc_pf_remove`, `enetc_psi_create`, `enetc_psi_destroy`, `enetc_configure_port`, `enetc_pf_set_rx_mode`, `enetc_msg_handle_rxmsg`, `enetc_sriov_configure`, `enetc_pf_setup_tc`, `enetc_pl_mac_link_up`, `enetc_pl_mac_link_down`, `enetc_init_port_rfs_memory`, and `enetc_init_port_rss_memory`. It defines `enetc_ndev_ops`, `enetc_mac_phylink_ops`, `enetc_psi_ops`, and `enetc_pf_ops`.

## Control Flow
Probe first attempts IERB registration, creates the PF SI through generic PCI setup and CBDR initialization, clears RFS/RSS tables, initializes PF private state/VF state, sets MAC addresses, configures port/SI registers, allocates netdev resources/MSI-X, reads `phy-mode`, creates MDIO/PCS/phylink, and registers the netdev. Link-up sets Qbv speed, optional forced RGMII speed/duplex, pause behavior, RX BDR congestion mode, MAC pause registers, enables MAC, and notifies MAC Merge. Removal disables SR-IOV, unregisters netdev, destroys phylink/MDIO, frees MSI-X/resources/netdev/VF state, tears down CBDR, and removes PCI state.

## State and Persistence
Hardware state includes primary MAC registers for PF/VFs, SI configuration, RFS/RSS tables, VLAN promisc/isolation/filter registers, exact/hash MAC filters, port MAC mode, flow control, pause thresholds, and port enable. Software state includes VF flags, filter caches, VLAN bitmaps, phylink/PCS/MDIO pointers, capability flags, active offloads, and `num_vfs`.

## Dependencies and Integration Points
Uses common PF helpers, IERB, CBDR, `pcs-lynx`, phylink, MDIO, SR-IOV PCI core, mailbox support in `enetc_msg.c`, QoS offload functions, ethtool ops, XDP and hwtstamp paths from the shared driver. A PCI fixup runs `enetc_psi_create`/destroy for disabled functions to clear RSS/RFS.

## Risks
Risks include resource partitioning for VFs, mailbox MAC override policy, exact-to-hash filter fallback, VLAN isolation errata, phylink PCS creation failures, cleanup ordering across many probe labels, and link-mode assumptions for RGMII/SGMII/USXGMII. CBDR commands are synchronous and can fail mid-probe.

## Test Signals
Exercise PF probe/remove, disabled-device PCI fixup, SR-IOV enable/disable, VF MAC/VLAN/spoofchk controls, unicast/multicast/promisc modes, VLAN filter toggling, link-up/down across supported PHY modes, Qbv/Qbu/CBS/ETF/PSFP setup, RSS/RFS initialization, and IERB absent/deferred cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf.h

## Purpose
Defines PF-private data structures, constants, operation hooks, and mailbox prototypes shared by rev1 and rev4 PF implementation files.

## Important APIs, Types, and Functions
Key types are `enum enetc_vf_flags`, `struct enetc_vf_state`, `struct enetc_port_caps`, `struct enetc_pf_ops`, and `struct enetc_pf`. It declares `enetc_msg_psi_init`, `enetc_msg_psi_free`, and `enetc_msg_handle_rxmsg`. The `phylink_to_enetc_pf` helper maps a phylink config back to its PF container.

## Control Flow
The header has no runtime control flow except macro expansion. It supplies function-pointer dispatch for generation-specific MAC address access, PCS creation/destruction, and optional PSFP enablement.

## State and Persistence
`struct enetc_pf` stores the PF's SI pointer, VF counts and flags, software MAC filter entries, VF mailbox buffers/work item, VLAN promiscuity/hash/active VLAN bitmaps, external/internal MDIO buses, PCS, PHY interface mode, phylink config, hardware capabilities, PF ops table, and ENETC4 MAFT entry count.

## Dependencies and Integration Points
Includes `enetc.h` and phylink. Consumed by `enetc_pf.c`, `enetc4_pf.c`, `enetc_msg.c`, MDIO helpers, and PF common helpers. Its fields bridge netdev, PCI SR-IOV, phylink, mailbox, VLAN, and hardware-filter code.

## Risks
As shared private ABI, field semantics must remain consistent across rev1 and rev4. Some fields are generation-specific (`num_mfe`, capabilities, `enable_psfp`) and callers must guard them. Bitmap sizes and `ENETC_MAX_NUM_VFS` bound mailbox/filter arrays.

## Test Signals
Compile both rev1 and rev4 PFs, SR-IOV-enabled and disabled builds, PSFP-capable and non-PSFP configs, and verify probe/remove paths initialize only the fields each generation later uses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf_common.c

## Purpose
Provides generation-neutral PF helper code for MAC address setup, netdev feature initialization, MDIO bus creation/destruction, phylink creation/destruction, default RSS key setup, and VLAN hash filter maintenance.

## Important APIs, Types, and Functions
Exports `enetc_pf_set_mac_addr`, `enetc_setup_mac_addresses`, `enetc_pf_netdev_setup`, `enetc_mdiobus_create`, `enetc_mdiobus_destroy`, `enetc_phylink_create`, `enetc_phylink_destroy`, `enetc_set_default_rss_key`, `enetc_vlan_rx_add_vid`, and `enetc_vlan_rx_del_vid`. Important internals are `enetc_setup_mac_address`, `enetc_mdio_probe`, `enetc_imdio_create`, `enetc_port_has_pcs`, `enetc_vid_hash_idx`, and `enetc_set_si_vlan_ht_filter`.

## Control Flow
MAC setup tries device-tree MAC, then hardware-programmed MAC, then random MAC, and writes it back through PF ops. Netdev setup initializes standard offload features, ethtool ops, MTU, XDP features for rev1, active offload flags, and optional PSFP hardware TC feature. MDIO creation registers an external child MDIO bus if present and creates an internal MDIO/PCS bus when the PHY interface requires PCS. VLAN add/delete updates active VLAN bitmap, recomputes the 64-bit VLAN hash, and writes rev1 or rev4 SI hash registers.

## State and Persistence
Persistent hardware state includes primary MAC addresses, RSS hash key, MDIO controller registration, internal PCS device, phylink instance, and VLAN hash filters. Software state includes `priv` netdev fields, feature flags, `pf->mdio`, `pf->imdio`, `pf->pcs`, `pf->active_vlans`, and `pf->vlan_ht_filter`.

## Dependencies and Integration Points
Depends on PF operation hooks from `enetc_pf.h`, MDIO callbacks from `enetc_mdio.c`, Lynx PCS creation through PF ops, Open Firmware helpers, phylink, netdev features, ethtool ops, and revision helpers. Used by both rev1 PF and ENETC4 PF.

## Risks
Risk areas include inconsistent MAC address source priority, failure unwinding when internal PCS creation fails after external MDIO registration, unsupported PCS on interfaces that require it, VLAN hash collisions inherent in the 64-entry filter, and enabling advanced features only on supported revisions.

## Test Signals
Probe with DT MAC, bootloader MAC, and missing MAC; external MDIO child present/absent; PCS-required and non-PCS PHY modes; VLAN add/delete/filter toggling; rev1/rev4 VLAN hash register selection; and netdev feature advertisement for RSS, loopback, XDP, PSFP, and checksum/TSO offloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf_common.h

## Purpose
Declares the PF common helper interface shared by rev1 and rev4 PF drivers.

## Important APIs, Types, and Functions
It declares MAC, netdev, MDIO, phylink, RSS, and VLAN helper functions implemented in `enetc_pf_common.c`, and defines inline `enetc_get_ip_revision` to read `ENETC_G_EIPBRR0`.

## Control Flow
No runtime control flow beyond the inline revision read. The declarations allow generation-specific PF files to avoid duplicating common setup logic.

## State and Persistence
The header owns no state, but its APIs operate on persistent PF/SI/netdev state such as MAC registers, MDIO buses, phylink, RSS key, VLAN filter registers, and netdev feature flags.

## Dependencies and Integration Points
Includes `enetc_pf.h`, so consumers get PF state, ENETC hardware accessors, and phylink types. Used by `enetc_pf.c` and `enetc4_pf.c`.

## Risks
Prototype drift breaks both PF generations. The inline revision helper assumes PF global register mapping is valid before use.

## Test Signals
Build rev1 and rev4 PF drivers, verify revision reads during probe after generic PCI mapping, and confirm all declared helpers are exported for module linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ptp.c

## Purpose
Registers the ENETC PTP hardware clock PCI function using the shared QorIQ PTP implementation.

## Important APIs, Types, and Functions
Important elements are `enetc_ptp_caps`, `enetc_ptp_probe`, `enetc_ptp_remove`, the PCI ID table for `ENETC_DEV_ID_PTP`, and module PCI driver registration. PTP operations are delegated to `ptp_qoriq_adjfine`, `ptp_qoriq_adjtime`, `ptp_qoriq_gettime`, `ptp_qoriq_settime`, and `ptp_qoriq_enable`.

## Control Flow
Probe skips disabled OF nodes, enables PCI memory space, sets a 64-bit DMA mask, requests BARs, enables bus mastering, allocates `struct ptp_qoriq`, maps BAR0, allocates one MSI-X vector, requests the QorIQ PTP ISR, initializes the PTP clock with `ptp_qoriq_init`, and stores drvdata. Remove frees the PTP clock, IRQ vectors, driver state, memory regions, and PCI device.

## State and Persistence
Persistent hardware state is the mapped timer/PTP PCI BAR and MSI-X interrupt. Software state is `struct ptp_qoriq`, including IRQ number, device pointer, registered PTP clock, and QorIQ timer state.

## Dependencies and Integration Points
Depends on PCI core, `linux/fsl/ptp_qoriq.h`, kernel PTP clock APIs, and OF availability checks. PF/VF ethtool timestamp reporting locates this PHC by OF `ptp-timer` phandle or PCI devfn assumptions.

## Risks
Risks include PHC lookup mismatch if PCI devfn layout changes, interrupt allocation failure, missing cleanup of mapped BAR on init failure, and relying on QorIQ PTP behavior for all ENETC timer revisions. Remove calls `ptp_qoriq_free` but not an explicit `iounmap`, assuming the QorIQ free path owns mapped resources after init.

## Test Signals
Probe the PTP function, run `phc2sys`/`ptp4l`, query `ethtool -T` from PF/VF, test disabled DT nodes, force MSI-X or PTP init failures, and verify module unload/reload leaves no IRQ or PHC leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_qos.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_qos.c

## Purpose
Implements ENETC traffic-control offloads for TSN/QoS: Qbv taprio gate control, CBS credit shaping, ETF/txtime time-specific departure, and PSFP/Qci stream identification, stream filtering, stream gates, policing, and delayed stats.

## Important APIs, Types, and Functions
Exports `enetc_sched_speed_set`, `enetc_setup_tc_taprio`, `enetc_setup_tc_cbs`, `enetc_setup_tc_txtime`, `enetc_setup_tc_psfp`, `enetc_qos_query_caps`, `enetc_setup_tc_block_cb`, `enetc_set_psfp`, `enetc_psfp_init`, and `enetc_psfp_clean`. Key internal structures are `enetc_streamid`, `enetc_psfp_filter`, `enetc_psfp_gate`, `enetc_psfp_meter`, `enetc_stream_filter`, and global `epsfp`.

## Control Flow
Taprio validates GCL length/time ranges and TSD mutual exclusion, allocates a long-format CBDR data buffer, writes gate list data, enables time gating, sends a port GCL command, and updates max SDU/active offloads. CBS validates priority ordering and slope math, computes bandwidth and hiCredit from port speed/sysclk, and writes per-TC registers. ETF toggles TSD per TX ring when Qbv is inactive. PSFP parses cls_flower gate/police actions and Ethernet/VLAN keys, allocates or reuses stream filter/gate/meter objects, programs stream ID/filter/gate/meter CBDR commands with rollback on failure, stores refcounted global software state, and retrieves hardware counters for delayed stats.

## State and Persistence
Hardware state includes PTGCR, port GCL, PTCMSDUR, CBS registers, TSD registers, stream identification entries, stream filter instances, stream gate control lists, and flow meter instances. Software state includes `active_offloads`, TX ring `tsd_enable` and window-drop counters, global PSFP hlist databases, SFI allocation bitmap, device bitmap, refcounts, and per-filter stats deltas.

## Dependencies and Integration Points
Called from PF netdev `ndo_setup_tc` and ethtool/MM paths. Depends on CBDR command sending, ENETC PTP cycle registers, traffic-control APIs, flow dissector/action APIs, mqprio helpers, port mapping, and PSFP capability fields initialized elsewhere.

## Risks
Risks include global PSFP state shared across devices, spinlock coverage around lists versus hardware commands, refcount/list replacement errors, partial rollback after command failures, Qbv/TSD mutual exclusion, cycle time and base-time arithmetic, limited action/key support, and CBS bandwidth/order constraints that may surprise users.

## Test Signals
Use `tc qdisc taprio`, `cbs`, and `etf` with valid/invalid combinations; verify Qbv and TSD reject each other; bind/unbind clsact flower PSFP rules with gate and police actions; read delayed stats; test resource exhaustion; remove devices while rules exist; and run line-rate traffic to validate shaping, drops, and gate schedules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_vf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_vf.c

## Purpose
Implements the ENETC virtual-function PCI netdev driver. It initializes a VF SI, configures shared SI resources, exposes basic netdev/ethtool operations, and sends mailbox requests to the PF for primary MAC address changes.

## Important APIs, Types, and Functions
Important functions are `enetc_vf_probe`, `enetc_vf_remove`, `enetc_vf_netdev_setup`, `enetc_vf_set_mac_addr`, `enetc_msg_vsi_send`, `enetc_msg_vsi_set_primary_mac_addr`, and `enetc_vf_setup_tc`. It defines VF `net_device_ops` and `enetc_vsi_ops` for legacy RSS table access.

## Control Flow
Probe performs generic PCI SI setup, fixes revision to ENETC rev1, reads driver data/capabilities, allocates the netdev, initializes features, ring parameters, CBDR, SI resources, hardware SI configuration, MSI-X vectors, registers netdev, and starts with carrier off. MAC changes allocate a coherent mailbox message, populate command header/action and sockaddr, wait for mailbox availability, install the DMA message pointer, trigger send, poll completion, and apply the netdev MAC on success. Remove unregisters, frees MSI-X/resources/CBDR/netdev, removes PCI state, and frees the last saved mailbox DMA buffer.

## State and Persistence
Hardware state includes SI registers, BDR/CBDR configuration, mailbox send registers, RSS/RFS tables, and VF primary MAC programmed by the PF. Software state includes `si->msg` for the last DMA message, netdev features, ring resources, interrupt vectors, and classifier/RSS state inherited from common code.

## Dependencies and Integration Points
Depends on the PF mailbox implementation, generic ENETC PCI/SI/resource code, CBDR legacy commands, ethtool VF ops, hwtstamp helpers, mqprio offload, and PF-assigned SI capabilities. It does not manage phylink because link ownership belongs to the PF.

## Risks
Mailbox polling can time out, PF may reject commands, and freeing the previous message before sending the next assumes hardware is no longer using it after mailbox status clears. VF revision is hard-coded to rev1. Failure unwinding must free CBDR and netdev state in the right order.

## Test Signals
Create VFs through PF SR-IOV, probe/remove VF driver, set VF MAC from the guest/host, test busy and timeout mailbox behavior, run traffic with VLAN/checksum/TSO/RSS, configure mqprio, inspect ethtool VF stats/RSS, and unload VF while a previous mailbox buffer exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/netc_blk_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/netc_blk_ctrl.c

## Purpose
Implements the NXP NETC block-control platform driver for i.MX94/i.MX95. It performs SoC-level pre-initialization of NETCMIX, PRB, and IERB blocks before ENETC/NETC PCI child devices probe, and recreates child platform devices after setup.

## Important APIs, Types, and Functions
Important types are `struct netc_devinfo` and `struct netc_blk_ctrl`. Important functions include `netc_blk_ctrl_probe`, `netc_blk_ctrl_remove`, `imx95_netcmix_init`, `imx94_netcmix_init`, `netc_ierb_init`, `imx95_ierb_init`, `imx94_ierb_init`, `imx95_enetc_mdio_phyaddr_config`, `imx94_enetc_update_tid`, debugfs `netc_prb_show`, and helper parsers for PCI BDF, link mode, PHY address, and EMDIO masks.

## Control Flow
Probe enables the optional IPG clock, matches platform data, maps named `ierb`, `prb`, and optional `netcmix` resources, runs NETCMIX link protocol configuration from child PCI nodes and `phy-mode`, unlocks IERB with warm reset if needed, applies SoC-specific IERB LDID/timer/MDIO PHY address programming, locks IERB, warns on PRB error, creates debugfs, and calls `of_platform_populate` for child devices. Remove depopulates children and removes debugfs.

## State and Persistence
Persistent state is SoC register programming: link MII/PCS protocol, I/O variant, external pin mux, IERB LDIDs for PF/VF/timer/EMDIO, timer binding per ENETC, port MDIO PHY addresses, and PRB lock state. Software state stores mapped base pointers, devinfo, platform device pointer, and debugfs root.

## Dependencies and Integration Points
Depends on OF child PCI descriptions, `phy-mode`, `ptp-timer` phandles, `linux/fsl/netc_global.h` accessors, clocks, debugfs, and platform population. It gates later ENETC4 PF/MDIO/PTP child probing by completing shared NETC initialization first.

## Risks
Risks include DT parsing assumptions, duplicate PHY addresses between central EMDIO and port MDIO, incorrect BDF-to-link/ID mappings, IERB unlock/lock timeout, invalid PRB configuration warnings that do not fail probe, and suspend/resume requirements not fully represented in this file.

## Test Signals
Probe i.MX94 and i.MX95 device trees with enabled/disabled ENETCs, all supported `phy-mode` values, central EMDIO plus port MDIO, custom `ptp-timer` phandles, debugfs PRB state, duplicate PHY address rejection, IERB lock timeout injection, and child-device probe ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/netc_blk_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/ntmp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/ntmp.c

## Purpose
Provides the NETC Table Management Protocol 2.0 library used by ENETC4 to manage hardware tables through a NETC control BD ring, currently MAC Address Filter Table and RSS Table operations.

## Important APIs, Types, and Functions
Exports `ntmp_init_cbdr`, `ntmp_free_cbdr`, `ntmp_maft_add_entry`, `ntmp_maft_query_entry`, `ntmp_maft_delete_entry`, `ntmp_rsst_update_entry`, and `ntmp_rsst_query_entry`. Internal helpers include `netc_xmit_ntmp_cmd`, `ntmp_clean_cbdr`, `ntmp_alloc_data_mem`, `ntmp_fill_request_hdr`, `ntmp_fill_crd_eid`, `ntmp_delete_entry_by_id`, and `ntmp_query_entry_by_id`.

## Control Flow
CBDR init allocates coherent descriptors with extra space for 128-byte alignment, allocates software CBD tracking entries, records register pointers, initializes indices from hardware, writes base/length, and enables the ring. Command transmit cleans the ring when enough BDs are used, copies request CBD and software buffer metadata into the next slot, updates PIR, polls CIR for completion, checks system bus and NTMP response errors, copies writeback CBD, and leaves buffer cleanup to later ring cleaning/free. Table helpers allocate 32-byte-aligned coherent data buffers, fill NTMP v2 headers and request data, serialize access through the selected ring mutex, transmit, decode query data, and log table-specific failures.

## State and Persistence
State includes CBDR hardware registers, aligned descriptor memory, coherent per-command data buffers, software CBD metadata, producer/consumer indices, ring mutex, table versions in `ntmp_user->tbl`, MAFT entries, and the 64-entry RSS table.

## Dependencies and Integration Points
Used by `enetc4_pf.c` for MAFT exact unicast filters and by `enetc_cbdr.c`/ethtool for ENETC4 RSS get/set. Depends on `ntmp_private.h`, `linux/fsl/netc_global.h` register access, DMA APIs, vmalloc, and iopoll.

## Risks
Risks include delayed cleanup of successful command buffers until later CBDR cleaning, fixed one-ring selection, strict RSS count of 64 entries, response layout assumptions, alignment math for DMA and virtual buffers, and table-version assumptions initialized to zero for ENETC 4.1.

## Test Signals
Initialize/free CBDR repeatedly, set/query/delete MAFT entries from receive-mode changes, set/query RSS table through ethtool, force command timeout/SBE/response error paths, test ring wrap and cleanup under many commands, and inspect ENETC4 debugfs MAFT output against expected filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/ntmp.c -->
