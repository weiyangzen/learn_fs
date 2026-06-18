# Research: subset-b-004496

Grouped research for ixgbe FCoE, firmware update, IPsec offload, and queue/interrupt setup sources.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fcoe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fcoe.h

## Purpose

`ixgbe_fcoe.h` defines the driver-private data model and constants for ixgbe Fibre Channel over Ethernet support. It is included through `ixgbe.h` when `IXGBE_FCOE` is enabled and supplies the shared types consumed by `ixgbe_fcoe.c`, `ixgbe_lib.c`, `ixgbe_main.c`, DCB netlink handlers, ethtool stats, and queue layout code. The header does not implement logic; its importance is that it fixes DDP table sizing, DMA alignment, default traffic class, and the per-adapter FCoE state shape.

## Important APIs, Types, and Constants

The file imports FC/FCoE protocol definitions from `<scsi/fc/fc_fs.h>` and `<scsi/fc/fc_fcoe.h>`. Key constants include `IXGBE_RXDADV_FCSTAT_SHIFT` for extracting FC status from advanced Rx descriptors, `IXGBE_BUFFCNT_MAX`, `IXGBE_FCPTR_ALIGN`, and `IXGBE_FCPTR_MAX` for DDP user descriptor list layout, and `IXGBE_FCBUFF_*` values for encoded buffer sizes from 4 KiB through 64 KiB. `IXGBE_FCOE_DDP_MAX` is the legacy 512-XID limit, while `IXGBE_FCOE_DDP_MAX_X550` expands storage to 2048 XIDs for newer hardware. `IXGBE_FCOE_DEFTC` defaults FCoE to traffic class 3, and `IXGBE_FCERR_BADCRC` records the descriptor error bit for bad FC CRC.

`struct ixgbe_fcoe_ddp` records one direct data placement context: completed length and error, scatter-gather list count/pointer, DMA address of the user descriptor pointer table, virtual user descriptor list, and the DMA pool used for allocation. `struct ixgbe_fcoe_ddp_pool` is per-CPU storage for a DMA pool plus `noddp` and `noddp_ext_buff` counters used later in statistics. `struct ixgbe_fcoe` is embedded in `struct ixgbe_adapter` and owns the percpu DDP pools, a reference count, a spinlock, the fixed DDP array, an optional extra DDP bounce buffer and DMA address, mode bits such as `__IXGBE_FCOE_TARGET`, and the selected user priority.

## Control Flow and Integration Points

The control flow is external. During probe/init, `ixgbe_main.c` initializes `adapter->fcoe.lock`, sets `adapter->fcoe.up` to `IXGBE_FCOE_DEFTC`, configures feature limits, and calls `ixgbe_setup_fcoe_ddp_resources()`. The `net_device_ops` table wires FCoE callbacks to `ixgbe_fcoe_ddp_get()`, `ixgbe_fcoe_ddp_target()`, `ixgbe_fcoe_ddp_put()`, enable/disable hooks, WWN lookup, and HBA info. Receive handling checks FCoE packet type and calls `ixgbe_fcoe_ddp()` to consume the DDP context, while transmit offload paths call `ixgbe_tx_ctxtdesc()` with FCoE SOF/EOF state. `ixgbe_lib.c` consults `RING_F_FCOE` feature data to reserve or share queue indices with RSS, DCB, and SR-IOV.

## State and Persistence Behavior

All state is in memory and tied to the adapter lifetime. DDP entries track outstanding XIDs and DMA mappings; `ixgbe_fcoe_ddp_put()` and resource teardown clear them. The percpu pool counters are runtime statistics aggregated into hardware stats, not persisted across module unload or device reset. The `mode` bitmap records target-mode use for the active adapter instance. The default priority may be overridden by DCB application settings and is restored from driver initialization on fresh probe.

## Dependencies

This header depends on Linux SCSI FC/FCoE headers, scatterlists, DMA pools, atomics, spinlocks, percpu allocation, and ixgbe adapter definitions that include it. Queue consumers also depend on DCB and FCoE compile-time feature gates.

## Risks and Test Signals

The fixed `ddp[2048]` array makes table bounds critical; every XID user must honor `netdev->fcoe_ddp_xid` and hardware-specific limits. DMA address list alignment and buffer-size encodings must match hardware expectations or DDP can corrupt data or silently fall back. Locking around shared DDP entries is required because completion, setup, and teardown can race. Useful tests include FCoE enable/disable cycles, DDP setup/done with boundary XIDs, target-mode setup, reset while DDP is active, DCB priority changes, queue count changes with FCoE enabled, and ethtool stat checks for `fcoe_noddp` and CRC/drop counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fcoe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fw_update.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fw_update.c

## Purpose

`ixgbe_fw_update.c` implements devlink firmware flashing for E610 ixgbe devices using PLDM firmware packages. It parses a PLDM image through the kernel `pldmfw` helper, passes package metadata and component tables to device firmware, erases inactive NVM banks, writes new component payloads, and requests bank activation. It also exposes a pending-update query used by devlink reload/status code.

## Important APIs, Types, and Functions

The central private state is `struct ixgbe_fwu_priv`, which embeds `struct pldmfw`, carries the `ixgbe_adapter`, netlink `extack`, component activation flags, and whether EMP reset activation is available. Public exports are `ixgbe_flash_pldm_image()` and `ixgbe_get_pending_updates()`.

The PLDM callback table `ixgbe_fwu_ops_e610` wires `pldmfw_op_pci_match_record`, `ixgbe_send_package_data()`, `ixgbe_send_component_table()`, `ixgbe_flash_component()`, and `ixgbe_finalize_update()`. `ixgbe_send_package_data()` copies PLDM package data and sends it with `ixgbe_nvm_set_pkg_data()`. `ixgbe_send_component_table()` accepts only OROM, NVM, and NETLIST component IDs, builds an `ixgbe_aci_cmd_nvm_comp_tbl`, sends it via `ixgbe_nvm_pass_component_tbl()`, and uses `ixgbe_check_component_response()` to translate firmware accept/reject codes into `extack` messages. `ixgbe_write_nvm_module()` writes component bytes in `IXGBE_ACI_MAX_BUFFER_SIZE` blocks using `ixgbe_aci_update_nvm()` and sends devlink progress notifications. `ixgbe_erase_nvm_module()` wraps `ixgbe_aci_erase_nvm()` with a 300-second devlink timeout notice. `ixgbe_switch_flash_banks()` calls `ixgbe_nvm_write_activate()` and decodes EMP reset availability. `ixgbe_cancel_pending_update()` discovers and reverts existing pending inactive-bank updates before a new flash.

## Control Flow

`ixgbe_flash_pldm_image()` starts by rejecting non-E610 hardware. It maps devlink overwrite flags to NVM preservation policy: preserve all, preserve selected settings/identifiers, or preserve nothing. It rejects unsupported overwrite masks and devices without unified-update support unless firmware recovery mode prevents capability discovery. It initializes `ixgbe_fwu_priv`, notifies devlink that flashing is preparing, cancels any pending previous update, acquires the NVM write resource, and calls `pldmfw_flash_image()`. The PLDM helper then calls back into this file for package data, component tables, per-component flash, and finalization. The NVM lock is released after the PLDM helper returns.

For each component, `ixgbe_flash_component()` maps PLDM identifiers to inactive-bank module pointers and devlink component names: OROM to `fw.undi`, NVM to `fw.mgmt`, and NETLIST to `fw.netlist`. It ORs the matching activation flag into `priv->activate_flags`, erases the module, then writes the payload. Finalization activates all selected components in one bank-switch command and updates `adapter->fw_emp_reset_disabled` according to firmware capability.

## State and Persistence Behavior

The file writes persistent device flash on inactive banks and requests a persistent bank activation. `activate_flags` accumulate across components in a single flash session and start with the requested preservation policy. Existing pending updates are persistent device state; this driver can revert them by issuing `IXGBE_ACI_NVM_REVERT_LAST_ACTIV`. `ixgbe_get_pending_updates()` reads device capabilities and returns a volatile bitmap reflecting persistent pending NVM/OROM/NETLIST activation. Runtime state includes devlink progress, `extack` diagnostics, and `adapter->fw_emp_reset_disabled`, which guides later devlink reload behavior but is not itself flash state.

## Dependencies and Integration Points

The implementation depends on Linux `pldmfw`, devlink flash update APIs, netlink extended ACK, E610 Admin Command Interface wrappers (`ixgbe_nvm_set_pkg_data`, `ixgbe_nvm_pass_component_tbl`, `ixgbe_aci_update_nvm`, `ixgbe_aci_erase_nvm`, `ixgbe_nvm_write_activate`), NVM resource locking, and hardware capability discovery. `devlink/devlink.c` registers `ixgbe_flash_pldm_image()` as `.flash_update` and calls `ixgbe_get_pending_updates()` for reload/update status.

## Risks and Test Signals

Firmware update is high risk because failures can leave pending inactive-bank data, require power cycle, or reject later updates. Important risk points are exact component ID filtering, block write offsets and `last_cmd`, NVM lock coverage, preservation flag mapping, canceling pending updates without erasing desired state, and recovery-mode behavior. `ixgbe_send_package_data()` duplicates PLDM bytes because the AdminQ call may mutate or require a writable buffer; allocation failure must abort cleanly. Test signals include devlink flash of matching and non-matching PLDM images, unsupported overwrite masks, downgrade/reject component responses, forced `ixgbe_acquire_nvm()` failure, erase/write failures mid-component, previous pending update cancellation for all and individual components, recovery mode flashing, pending bitmap reporting, and reload guidance when EMP reset is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fw_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fw_update.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fw_update.h

## Purpose

`ixgbe_fw_update.h` is the small public interface for the ixgbe E610 firmware update implementation. It lets the devlink layer and other driver code call into `ixgbe_fw_update.c` without exposing the PLDM callback internals or the private flash-session state.

## Important APIs

`ixgbe_flash_pldm_image(struct devlink *devlink, struct devlink_flash_update_params *params, struct netlink_ext_ack *extack)` is the devlink flash entry point. It validates hardware and overwrite policy, cancels previous pending updates, locks NVM, delegates image parsing to `pldmfw_flash_image()`, and flashes supported components.

`ixgbe_get_pending_updates(struct ixgbe_adapter *adapter, u8 *pending, struct netlink_ext_ack *extack)` discovers device capabilities and returns a bitmap of pending NVM, OROM, and NETLIST updates using `IXGBE_ACI_NVM_ACTIV_SEL_*` bits.

## Control Flow and Integration Points

`devlink/devlink.c` includes this header to register `.flash_update = ixgbe_flash_pldm_image` and to query pending updates around reload/update actions. The header assumes prior declarations for `struct devlink`, `struct devlink_flash_update_params`, `struct netlink_ext_ack`, and `struct ixgbe_adapter` from the surrounding ixgbe/devlink include graph.

## State and Persistence Behavior

The header itself stores no state. Its two functions operate on persistent NVM state in firmware and transient adapter/devlink state. Callers should treat `ixgbe_flash_pldm_image()` as a persistent flash mutation and `ixgbe_get_pending_updates()` as a hardware state query.

## Dependencies, Risks, and Test Signals

The key dependency is keeping this interface synchronized with `ixgbe_fw_update.c` and devlink registration code. Because the header exposes only two functions, ABI risk inside the driver is low. Compile test signals are missing forward declarations or changed devlink signatures. Functional tests should verify devlink flash registration and pending-update status paths still build and link when firmware update support is compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fw_update.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ipsec.c

## Purpose

`ixgbe_ipsec.c` implements ixgbe hardware IPsec crypto offload for the Linux XFRM stack and a restricted SR-IOV mailbox path. It programs device security association tables, starts/stops the security engines, rebuilds tables after reset, translates Tx/Rx data-path metadata, and exposes `xfrmdev_ops` for SA add/delete. The supported algorithm is AES-GCM RFC4106 with 128-bit ICV and a 128-bit key plus optional 32-bit salt.

## Important APIs and Functions

Low-level register writers are `ixgbe_ipsec_set_tx_sa()`, `ixgbe_ipsec_set_rx_item()`, `ixgbe_ipsec_set_rx_sa()`, and `ixgbe_ipsec_set_rx_ip()`. They load key/salt/SPI/IP/mode registers and trigger writes through `IXGBE_IPSTXIDX` or `IXGBE_IPSRXIDX`. Engine lifecycle helpers are `ixgbe_ipsec_clear_hw_tables()`, `ixgbe_ipsec_stop_data()`, `ixgbe_ipsec_stop_engine()`, and `ixgbe_ipsec_start_engine()`.

Public driver hooks are `ixgbe_ipsec_restore()`, `ixgbe_ipsec_vf_clear()`, `ixgbe_ipsec_vf_add_sa()`, `ixgbe_ipsec_vf_del_sa()`, `ixgbe_ipsec_tx()`, `ixgbe_ipsec_rx()`, `ixgbe_init_ipsec_offload()`, and `ixgbe_stop_ipsec_offload()`. XFRM integration is through static `ixgbe_xfrmdev_ops`, where `.xdo_dev_state_add` is `ixgbe_ipsec_add_sa()` and `.xdo_dev_state_delete` is `ixgbe_ipsec_del_sa()`.

## Control Flow

Initialization rejects 82598 and devices whose security engines report offload disabled. It allocates `struct ixgbe_ipsec`, Rx/Tx SA arrays of 1024 entries each, an Rx IP table of 128 entries, initializes the Rx SA hash, stops/clears hardware tables, and assigns `netdev->xfrmdev_ops`.

SA add validates ESP/AH transport-mode crypto offload, checks management/BMC IP filter conflicts, parses AES-GCM key material, allocates a free SA index, and programs software and hardware tables. Rx SAs also allocate or share an Rx IP table entry with reference counting, set mode bits for valid/ESP/decrypt/IPv6, and insert into an RCU hash by SPI for receive lookup. Tx SAs are blocked when VFs exist outside VEPA bridge mode, then programmed into the Tx table. The first SA starts the security engine and sets `IXGBE_FLAG2_IPSEC_ENABLED`.

SA delete derives the hardware index from `xs->xso.offload_handle`, zeros the matching hardware entry, removes Rx entries from the RCU hash, decrements Rx IP references, clears software state, and stops the engine when both SA counts reach zero. Restore after reset stops and clears the engine, restarts it, reloads PF-owned SAs and IP entries, and deletes VF-owned SAs because VF reset or VF-count changes require the VF to request them again.

Tx path `ixgbe_ipsec_tx()` obtains the XFRM state from the skb secpath, validates the offload handle, marks `IXGBE_TX_FLAGS_IPSEC | IXGBE_TX_FLAGS_CC`, fills context descriptor flags for ESP/IP version/encryption, and computes ESP trailer length for non-GSO packets. Rx path `ixgbe_ipsec_rx()` decodes descriptor packet type, locates IPv4/IPv6 and AH/ESP headers, finds the matching Rx state with RCU lookup, attaches a secpath, marks crypto done/success, and increments `adapter->rx_ipsec`.

VF add/delete translate mailbox messages. Add requires a trusted VF and `IXGBE_FLAG2_VF_IPSEC_ENABLED`, currently permits only inbound offload, creates a synthetic `xfrm_state`, calls the regular add path, marks the resulting SA as VF-owned, and returns the PF offload handle. Delete validates ownership before calling the common delete path and frees the synthetic state.

## State and Persistence Behavior

All IPsec offload state is volatile. Hardware SA/IP tables are register-backed and must be reloaded after reset from `adapter->ipsec` software tables. The software state stores XFRM state pointers, keys, salt, mode bits, VF ownership, counts, and Rx IP table references. VF-created `xfrm_state` objects are allocated by the PF and freed on VF delete; PF-owned XFRM states are held by the networking stack. There is no persistence across driver unload. Sensitive key buffers are freed with `kfree_sensitive()` on VF setup failures, but normal table teardown uses plain `kfree()` for allocated arrays whose entries may contain keys.

## Dependencies and Integration Points

This file depends on `net/xfrm.h`, AEAD algorithm descriptors, bridge mode, ixgbe register definitions, descriptor packet-type bits, mailbox opcodes, ethtool private flag `IXGBE_FLAG2_VF_IPSEC_ENABLED`, and Tx descriptor construction in `ixgbe_main.c`/`ixgbe_lib.c`. `ixgbe_main.c` calls Rx and Tx hooks in packet paths, calls restore during reset, and initializes/stops offload during probe/remove. `ixgbe_sriov.c` invokes VF add/delete/clear handlers.

## Risks and Test Signals

Important risks are SA index bounds from untrusted mailbox handles, RCU lifetime around Rx hash deletion, key endianness, management IP filter conflict logic, ESP trailer parsing near skb tail, engine stop waits when link is down, and hardware/software table divergence across resets. VF paths are especially sensitive because synthetic XFRM states and ownership checks must prevent one VF deleting another VF's SA. Tests should cover PF inbound/outbound ESP offload, unsupported algorithms/modes/types, Rx IP table sharing and exhaustion, SA add/delete races with traffic, reset restore, VF trust and private-flag gating, malformed mailbox indices, GSO and non-GSO Tx trailer behavior, Rx AH/ESP descriptor decode, and module unload after active SAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ipsec.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ipsec.h

## Purpose

`ixgbe_ipsec.h` defines the table sizes, register command bit encodings, and software state structures used by ixgbe IPsec offload. It is the shared contract between `ixgbe_ipsec.c`, `ixgbe.h`, and packet/virtualization paths that need `struct ixgbe_ipsec_tx_data` or mailbox SA message layouts.

## Important Types and Constants

`IXGBE_IPSEC_MAX_SA_COUNT` sets 1024 entries for each Rx and Tx SA table. `IXGBE_IPSEC_MAX_RX_IP_COUNT` sets the separate 128-entry destination IP table used by Rx lookup. `IXGBE_IPSEC_BASE_RX_INDEX` and `IXGBE_IPSEC_BASE_TX_INDEX` partition XFRM offload handles so Rx handles start at 0 and Tx handles start at 1024. `IXGBE_IPSEC_AUTH_BITS` fixes 128-bit authentication.

`IXGBE_RXTXIDX_*`, `enum ixgbe_ipsec_tbl_sel`, and `IXGBE_RXMOD_*` encode table selection, read/write commands, valid/decrypt/protocol/IP-version bits, and VF ownership mode bits used when programming security registers. `struct rx_sa` stores an inbound SA, including hash node, XFRM state, destination IP, key, salt, hardware mode, Rx IP table index, decrypt flag, and VF owner. `struct rx_ip_sa` stores one shared destination IP entry and reference count. `struct tx_sa` stores outbound XFRM state, key/salt/mode/encrypt/owner fields. `struct ixgbe_ipsec_tx_data` is the per-packet data passed from `ixgbe_ipsec_tx()` into context descriptor setup. `struct ixgbe_ipsec` owns all software tables and the Rx SA hash. `struct sa_mbx_msg` is the PF/VF mailbox payload for SA add/delete translation.

## Control Flow and Integration Points

The header has no executable control flow. Its structures drive `ixgbe_init_ipsec_offload()` allocation, XFRM SA add/delete, VF mailbox operations in `ixgbe_sriov.c`, and Tx context descriptor construction in `ixgbe_main.c`. The offload handle base constants are part of the implicit ABI between XFRM state setup, Tx/Rx data paths, and mailbox responses.

## State and Persistence Behavior

The declared tables are runtime-only mirrors of device hardware tables. `used` flags and counters are the authoritative software allocation state, while hardware programming happens separately. Keys and salts are stored in memory inside allocated table arrays. `rx_ip_sa.ref_cnt` allows multiple Rx SAs to share one destination IP table entry.

## Dependencies, Risks, and Test Signals

The header depends on XFRM types, hlist/hash support, endian address types, and ixgbe register definitions included through the parent include graph. Risks are mostly contract risks: changing table sizes or handle bases breaks handle decoding; changing `sa_mbx_msg` breaks PF/VF mailbox compatibility; changing mode bits can program the wrong hardware table behavior. Tests should include compile coverage with and without `CONFIG_IXGBE_IPSEC`, SA handle boundary tests around 1023/1024, Rx IP reference-count tests, and VF mailbox compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ipsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_lib.c

## Purpose

`ixgbe_lib.c` provides core ixgbe queue topology, ring-to-register mapping, interrupt-vector allocation, q_vector lifetime, and advanced Tx context descriptor emission. It is the central setup/teardown helper used by probe, reset, DCB reconfiguration, FCoE enable/disable, SR-IOV changes, and transmit offload paths.

## Important APIs and Functions

The public functions are `ixgbe_init_interrupt_scheme()`, `ixgbe_clear_interrupt_scheme()`, and `ixgbe_tx_ctxtdesc()`. Queue topology helpers include `ixgbe_set_num_queues()` with feature-specific branches for DCB+SR-IOV, DCB, SR-IOV, and RSS. Ring register mapping mirrors that order via `ixgbe_cache_ring_register()`, `ixgbe_cache_ring_dcb_sriov()`, `ixgbe_cache_ring_dcb()`, `ixgbe_cache_ring_sriov()`, and `ixgbe_cache_ring_rss()`. Interrupt helpers include `ixgbe_acquire_msix_vectors()`, `ixgbe_set_interrupt_capability()`, and `ixgbe_reset_interrupt_capability()`. q_vector helpers include `ixgbe_alloc_q_vector()`, `ixgbe_alloc_q_vectors()`, `ixgbe_free_q_vector()`, and `ixgbe_free_q_vectors()`.

## Control Flow

`ixgbe_init_interrupt_scheme()` first computes queue counts from enabled features, then chooses interrupt mode, allocates q_vectors/rings, caches ring register indices, logs queue counts, and marks the adapter down. Queue selection starts from a single queue and tries the most complex enabled combinations first. DCB+SR-IOV and DCB paths size pools/traffic classes, disable RSS or ATR where incompatible, and map netdev traffic classes. SR-IOV sizes VMDq pools and per-pool RSS queues, adjusts FCoE queue sharing/reservation, disables ATR, and constrains netdev traffic classes for macvlan offload. RSS is the base multiqueue path, optionally enabling Flow Director hash capability when ATR sampling is active and reserving FCoE queues near the end of the ring array.

Interrupt setup tries MSI-X first. Requested vectors are based on max Rx/Tx/XDP queues, capped by online CPUs and hardware maximum, plus non-queue vectors. If MSI-X allocation fails, the driver disables or reduces features that require multiple vectors: DCB, SR-IOV, RSS, and related DCB state. It recalculates queues, sets one q_vector, and attempts MSI before falling back to legacy interrupts.

`ixgbe_alloc_q_vectors()` distributes Rx, Tx, and XDP rings across q_vectors. When enough vectors exist, Rx-only vectors are allocated first; remaining vectors get balanced ring counts via `DIV_ROUND_UP`. `ixgbe_alloc_q_vector()` allocates NUMA-local q_vector memory, initializes NAPI, adaptive interrupt moderation values, ring containers, ring indices, XDP locks, FCoE ring state, and the 82599 UDP zero checksum workaround. Freeing deletes NAPI and uses `kfree_rcu()` so stats readers cannot use freed rings immediately after NAPI deletion.

`ixgbe_tx_ctxtdesc()` writes an advanced context descriptor at `next_to_use`, wraps the ring index, sets descriptor extension/context type bits, and stores VLAN/MAC/IP lengths, FCoE EOF or IPsec SA index field, type/TU command flags, and MSS/L4 length fields.

## State and Persistence Behavior

All state is runtime adapter state. The file mutates queue counts, pool counts, `ring_feature[]` indices/masks/offsets, feature flags such as MSI-X/MSI/FDIR/SR-IOV/DCB, q_vector pointers, ring arrays, NAPI instances, and netdev traffic-class mappings. No state persists across driver unload, but these decisions affect hardware register programming after reset and the visible number of netdev queues.

## Dependencies and Integration Points

The file depends on `ixgbe.h`, `ixgbe_sriov.h`, PCI MSI/MSI-X APIs, NAPI, NUMA allocation, CPU masks, DCB config, XDP rings, FCoE feature hooks, Flow Director/ATR flags, and ixgbe descriptor definitions. It is called from `ixgbe_main.c` probe/open/reset paths, DCB netlink reconfiguration, and FCoE enable/disable paths. Tx context descriptors are consumed by TSO/checksum, IPsec, and FCoE transmit paths.

## Risks and Test Signals

Queue topology is high-risk because off-by-one masks or offsets can map rings to the wrong hardware queue, especially with DCB, SR-IOV, and FCoE combined. MSI-X fallback deliberately disables features; tests must verify state is fully consistent after partial vector allocation failure. q_vector allocation must handle NUMA fallback and unwind without stale ring pointers. `kfree_rcu()` is important for stats/NAPI lifetime safety. XDP queues are stacked with Tx queues and need distinct indexing. Test signals include probe under varying CPU counts, forced MSI-X allocation failure, DCB TC changes, SR-IOV enable/disable, FCoE queue reservation, XDP attach/detach, reset/reinit loops, Tx descriptor validation for TSO/IPsec/FCoE, and static checks for ring array bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_lib.c -->
