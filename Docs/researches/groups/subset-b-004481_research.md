# subset-b-004481 Research

Grouped research for Intel `ice` VF, VLAN, virtchnl queue, FDIR, allowlist, and AF_XDP support files. Each section preserves the source path for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib.c

## Purpose
Implements the main SR-IOV VF lifecycle library for the Intel `ice` driver. It owns VF lookup/reference handling, reset orchestration, host-side VF configuration rebuild, VF VSI/control-VSI management, promiscuous mode handling, spoof-check configuration, mailbox counter reset, LLDP bookkeeping, and utility helpers shared by virtchnl handlers.

## Important APIs and Functions
- `ice_get_vf_by_id()` and `ice_put_vf()` provide RCU-safe VF table lookup with `kref` lifetime protection. `ice_release_vf()` drops the PCI VF device reference and calls the hardware-specific `vf_ops->free()`.
- `ice_has_vfs()`, `ice_get_num_vfs()`, and `ice_get_vf_vsi()` expose VF inventory and LAN VSI lookup.
- `ice_check_vf_ready_for_cfg()` waits for reset initialization, rejects disabled VFs, and calls `ice_check_vf_init()`.
- `ice_reset_all_vfs()` resets every allocated VF during PF-level reset flows while holding `pf->vfs.table_lock`.
- `ice_reset_vf()` resets a single VF, optionally notifying it, optionally taking `vf->cfg_lock`, coordinating with LAG, stopping queues, rebuilding the VSI, clearing VF-owned state, and reapplying host-owned configuration.
- `ice_vf_init_host_cfg()` applies initial host defaults: VLAN 0, Rx VLAN filtering, broadcast MAC filter, and spoof checking.
- `ice_vf_set_vsi_promisc()` and `ice_vf_clear_vsi_promisc()` select VLAN-aware or non-VLAN promiscuous filter programming.
- Private virtualization helpers include `ice_initialize_vf_entry()`, `ice_deinitialize_vf_entry()`, `ice_dis_vf_qs()`, `ice_err_to_virt_err()`, `ice_vsi_apply_spoofchk()`, control-VSI helpers, and VF VSI release/invalidation helpers.

## Control Flow
VF reset has a layered flow. `ice_trigger_vf_reset()` clears ACTIVE/INIT, clears mailbox registers outside PF reset, and hits the VF reset register. Reset-all first resets mailbox counters, gates all VF access with `ICE_VF_DIS`, triggers all VF resets, polls reset status, then rebuilds each VF under its `cfg_lock`. Single reset uses `ICE_VF_STATE_DIS`, disables VF queues, issues the required Tx queue AQ disable, polls completion, clears driver caps and allowlist, disables promisc modes, resets FDIR/control VSI, rebuilds/reconfigures the LAN VSI, updates switchdev representation, and resets mailbox abuse counters.

Host-owned state is rebuilt after VSI reconfiguration in `ice_vf_rebuild_host_cfg()`: trust capability, default/broadcast MAC filters, VLAN or port-VLAN config, Tx rate limits, spoof checking, and scheduler aggregator assignment. Driver-owned VF state such as negotiated caps, FDIR rules, queue enable bitmaps, VF VLAN v2 caps, and control VSI is cleared across resets.

## State and Persistence
Persistent host-admin state lives in `struct ice_vf`: `trusted`, `spoofchk`, `port_vlan_info`, `min_tx_rate`, `max_tx_rate`, `hw_lan_addr`, aggregator linkage through VSI, and LLDP counters. VF runtime state is in `vf_states`, `txq_ena`, `rxq_ena`, counters, `driver_caps`, allowlist bits, and FDIR/control-VSI members. The code intentionally preserves host settings across reset while invalidating VF-negotiated state.

## Dependencies and Integration Points
Depends on `ice_vf_lib_private.h`, `ice.h`, `ice_lib.h`, `ice_fltr.h`, `virt/allowlist.h`, VLAN ops, mailbox helpers, FDIR helpers, LAG, eswitch, switchdev representation, AQ VSI update routines, and hardware-specific `ice_vf_ops`. External callers include SR-IOV setup/teardown, virtchnl opcode handlers, devlink/NDO VF controls, reset service tasks, and FDIR control VSI paths.

## Risks
- VF reference users must pair `ice_get_vf_by_id()` with `ice_put_vf()` or leak VF entries.
- Reset sequencing is concurrency-sensitive: `cfg_lock`, PF VF table lock, RCU, PF state bits, and LAG mutex all protect different surfaces.
- Rebuild failures can leave a VF disabled or partially restored; host config rebuild logs errors but continues through later operations.
- Promiscuous mode handling differs for true-promisc, default VSI, port VLAN, and non-zero VLAN cases.
- `ice_vf_update_mac_lldp_num()` decrements an unsigned counter and assumes callers are balanced.

## Test Signals
Exercise PF reset with active VFs, VFLR, VF-requested reset, queue-enable and queue-disable transitions, host-config persistence across reset, port VLAN rebuild, spoofchk toggles, Tx rate limiting restore, switchdev/eswitch VF attach/detach, default VSI promisc handling, and mailbox malicious counter reset on both E830 and non-E830 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib.h

## Purpose
Defines the public VF data model and SR-IOV helper API for the `ice` driver. It centralizes VF resource limits, capability/state bits, VF hash-table iteration contracts, `struct ice_vf`, `struct ice_vfs`, `struct ice_vf_ops`, and public helper prototypes or stubs depending on `CONFIG_PCI_IOV`.

## Important APIs and Types
- `ICE_MAX_SRIOV_VFS` caps supported VFs at 256; `ICE_MAX_RSS_QS_PER_VF` caps VF RSS queues at 16.
- `enum ice_virtchnl_cap` currently defines the trusted/privileged VF capability bit.
- `enum ice_vf_states` defines INIT, ACTIVE, QS_ENA, DIS, MC_PROMISC, and UC_PROMISC runtime bits.
- `struct ice_vf` stores identity, PF/VSI links, FDIR state, RSS/hash contexts, virtchnl version/caps, MACs, VLAN state, mailbox state, queue bitmaps, queue bandwidth config, devlink port, LLDP rule IDs, and callback tables.
- `struct ice_vf_ops` abstracts generation-specific reset, mailbox, IRQ-close, and post-rebuild behavior.
- `ice_for_each_vf()` and `ice_for_each_vf_rcu()` document locking expectations for sleeping versus short RCU iterations.
- Inline helpers expose port VLAN ID/priority/TPID, port VLAN enabled check, and LLDP enabled check.

## Control Flow and Conditional Compilation
When `CONFIG_PCI_IOV` is enabled the header exports real VF operations. When disabled, it provides inert stubs returning false, NULL, zero, or `-EOPNOTSUPP` as appropriate. This lets non-SR-IOV driver code compile while avoiding runtime SR-IOV operations.

## State and Persistence
The state layout in `struct ice_vf` defines which data survives reset and which is transient. Host-admin properties such as `trusted`, `spoofchk`, `port_vlan_info`, requested rates, and default MAC live beside transient negotiated properties such as `driver_caps`, allowlisted opcodes, active FDIR rules, and queue-enable bitmaps.

## Dependencies and Integration Points
Includes Linux hash table, bitmap, mutex, PCI, devlink, virtchnl, `ice_type.h`, `ice_flow.h`, `virt/fdir.h`, and `ice_vsi_vlan_ops.h`. This header is consumed broadly by SR-IOV, virtchnl, reset, devlink, VSI, and representor code.

## Risks
- The VF hash table is keyed by `vf_id`, but iteration bucket index is not the VF ID; callers must use `vf->vf_id`.
- `ice_vf_is_port_vlan_ena()` treats either VID or priority as enabling a port VLAN, which is important for priority-tagged port VLAN behavior.
- Stub behavior under `!CONFIG_PCI_IOV` must remain conservative so callers do not accidentally assume VF availability.

## Test Signals
Build with and without `CONFIG_PCI_IOV`; validate VF table lookup/refcount behavior, non-contiguous VF IDs, port VLAN helper semantics for VID 0/prio non-zero, and that all public users tolerate stubs in non-SR-IOV builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib_private.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib_private.h

## Purpose
Declares private VF library helpers intended only for virtualization translation units that are compiled under `CONFIG_PCI_IOV`. It separates internal SR-IOV implementation functions from the broader public VF API in `ice_vf_lib.h`.

## Important APIs
Exports initialization/teardown (`ice_initialize_vf_entry()`, `ice_deinitialize_vf_entry()`), queue disable, VF init checks, errno-to-virtchnl translation, port-info lookup, spoofchk apply, trust and link helpers, control-VSI setup/release/invalidation, host configuration initialization, and LAN VSI invalidation/release.

## Control Flow and State
The header contains a compile-time warning if included without `CONFIG_PCI_IOV`, reinforcing that these helpers do not have fallback stubs. Callers are expected to be in SR-IOV-only object lists and to use these functions while holding the relevant VF locks documented by the implementation.

## Dependencies and Integration Points
Includes `ice_vf_lib.h`; used by virtchnl queue, FDIR, VF management, and other SR-IOV-only code paths that need internal lifecycle helpers.

## Risks
Including this header from always-built code breaks the intended build contract. Exposing too much through the private header also increases coupling to VF reset and VSI internals.

## Test Signals
Build matrix should cover `CONFIG_PCI_IOV=y` and `n`, ensuring no always-built `.c` file includes this private header. Runtime tests should validate that private helpers are only called under expected VF locks and state gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_mbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_mbx.c

## Purpose
Implements PF-to-VF mailbox send support, hardware-link-speed conversion for virtchnl, and malicious/asynchronous VF mailbox message detection. It supports both software snapshot accounting and newer E830 hardware mailbox counters.

## Important APIs and Functions
- `ice_aq_send_msg_to_vf()` builds the `ice_mbx_opc_send_msg_to_vf` admin queue descriptor, writes opcode/status into cookies, and sends optional payload through `hw->mailboxq`.
- `ice_conv_link_speed_to_virtchnl()` returns Mbps for advanced link support or legacy `VIRTCHNL_LINK_SPEED_*` enums otherwise.
- `ice_mbx_vf_state_handler()` is the entry point for software malicious VF detection over a static mailbox snapshot.
- `ice_mbx_vf_dec_trig_e830()` and `ice_mbx_vf_clear_cnt_e830()` manipulate E830 mailbox in-flight counters.
- `ice_mbx_clear_malvf()`, `ice_mbx_init_vf_info()`, and `ice_mbx_init_snapshot()` initialize or clear per-VF and global snapshot state.

## Control Flow
The software detector operates as a state machine over `ICE_MAL_VF_DETECT_STATE_NEW_SNAPSHOT`, `TRAVERSE`, and `DETECT`. A new snapshot clears per-VF message counts, captures mailbox head/tail from the control queue, and chooses detect mode if pending ARQ entries exceed the async watermark. Detect mode increments `vf_info->msg_count`; reaching `ICE_ASYNC_VF_MSG_THRESHOLD` marks the VF malicious once. Traversal advances through the circular queue until the static snapshot or maximum processed-message budget ends.

## State and Persistence
`hw->mbx_snapshot` stores snapshot traversal counters and the list of `ice_mbx_vf_info` records. Each VF record stores `msg_count` and a one-shot `malicious` flag until cleared on VF reset. On E830, hardware counters are cleared/decremented via registers instead of relying solely on software tracking.

## Dependencies and Integration Points
Depends on `ice_common.h`, `ice_vf_mbx.h`, admin/control queue structures, mailbox registers, virtchnl link speed constants, and VF reset paths that clear mailbox state. Virtchnl message handlers use `ice_aq_send_msg_to_vf()` to return responses and events.

## Risks
- `ice_conv_link_speed_to_virtchnl()` uses `fls(link_speed) - 1`; callers should not pass zero unless they accept an unknown/edge result.
- Watermark and max-message parameters are validated; wrong caller values return `-EINVAL` and disable detection for that pass.
- The software detector reports a malicious VF only once until reset, so monitoring must understand the latch.
- Snapshot queue traversal relies on circular queue masks and current `next_to_clean` consistency.

## Test Signals
Test PF-to-VF response delivery with and without payload, legacy and advanced link speed reporting, mailbox floods below and above the 63-message threshold, invalid watermark/max values, reset clearing malicious state, and E830 counter clear/decrement paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_mbx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_mbx.h

## Purpose
Declares VF mailbox helper APIs and the asynchronous mailbox threshold constant. It also provides no-op stubs for most mailbox operations when SR-IOV support is disabled.

## Important APIs
`ICE_ASYNC_VF_MSG_THRESHOLD` is 63 pending async messages. Under `CONFIG_PCI_IOV`, the header exports PF-to-VF AQ send, link speed conversion, E830 counter helpers, malicious VF state handler, per-VF clear/init, and global snapshot init.

## Control Flow and Conditional Compilation
SR-IOV builds call real mailbox functions. Non-SR-IOV builds return success/zero for send and speed conversion and no-op snapshot/counter functions, preventing mailbox code from being linked into non-IOV configurations.

## State and Persistence
The header does not define the state structures directly but connects callers to `ice_mbx_vf_info`, `ice_mbx_data`, and `ice_mbx_snapshot` state stored under `ice_type.h` hardware/VF structures.

## Dependencies and Integration Points
Includes `ice_type.h` and `ice_controlq.h`; integrated by VF reset, virtchnl response sending, mailbox interrupt processing, and hardware initialization.

## Risks
Only some functions have non-IOV stubs; always-built users must call only the stubbed surface. The threshold constant is a policy decision and should match assumptions in the mailbox detector and operational monitoring.

## Test Signals
Compile with `CONFIG_PCI_IOV` on/off, verify no unresolved mailbox symbols in non-IOV builds, and test threshold behavior with the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_mbx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_vsi_vlan_ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_vsi_vlan_ops.c

## Purpose
Configures the VLAN operation tables for VF VSIs. It maps generic inner/outer VSI VLAN operations to behavior appropriate for port VLANs, single VLAN mode, double VLAN mode, and legacy VFs that negotiated only the older VLAN offload.

## Important APIs and Functions
- `ice_vf_vsi_init_vlan_ops()` initializes a VF VSI's VLAN op tables based on DVM/SVM and whether the VF has a port VLAN.
- `ice_vf_vsi_enable_port_vlan()` and `ice_vf_vsi_disable_port_vlan()` switch operation tables when host port VLAN configuration changes.
- `ice_vf_vsi_cfg_dvm_legacy_vlan_mode()` configures DVM behavior for older VFs without VLAN v2 support.
- `ice_vf_vsi_cfg_svm_legacy_vlan_mode()` disables Rx VLAN filtering for old SVM VFs using legacy VLAN offload.
- Local no-op functions allow successful no-op behavior where the PF must not expose an operation to a VF.

## Control Flow
`ice_port_vlan_on()` disables VF add/delete VLAN on inner VLANs in DVM, assigns outer port VLAN set/clear operations, prevents disabling Rx filtering, and allows Rx filtering enable. In SVM it binds port VLAN operations to inner VLAN helpers. `ice_port_vlan_off()` enables normal add/delete and stripping/insertion operations, selecting outer ops under DVM and inner ops under SVM; Rx filtering enable may become a no-op unless `ICE_FLAG_VF_VLAN_PRUNING` is set.

Legacy DVM mode disables both Rx and Tx VLAN filtering and outer/inner offloads so old VFs can use software VLAN handling when no port VLAN is present. Legacy SVM mode only disables Rx VLAN filtering.

## State and Persistence
The file mutates function pointers in `vsi->inner_vlan_ops` and `vsi->outer_vlan_ops`; it does not directly store hardware state except by invoking the selected operations. Port VLAN state is read from `vsi->vf->port_vlan_info`; global mode is read from cached `hw->dvm_ena`.

## Dependencies and Integration Points
Depends on `ice_vsi_vlan_ops.h`, `ice_vsi_vlan_lib.h`, `ice_vlan_mode.h`, `ice_sriov.h`, VF state from `ice_vf_lib.h`, and PF flags. Used during VSI initialization, VF reset/rebuild, and host port VLAN changes.

## Risks
- Operation-table mutation must remain synchronized with actual hardware port VLAN state.
- Legacy DVM path assigns inner `dis_stripping`/`dis_insertion` to outer disabling helpers, which is unusual and should be regression-tested.
- No-op success functions intentionally hide unsupported operations from some call paths; misuse can mask missing hardware programming.

## Test Signals
Test SVM and DVM with VF port VLAN on/off, legacy VLAN-only VFs, VLAN v2 VFs, `ICE_FLAG_VF_VLAN_PRUNING` enabled/disabled, priority-only port VLANs, and reset rebuild preserving operation tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_vsi_vlan_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_vsi_vlan_ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_vsi_vlan_ops.h

## Purpose
Declares VF-specific VSI VLAN operation setup and mode-adjustment APIs. It separates always-declared legacy mode helpers from SR-IOV-gated init/port-VLAN operation functions.

## Important APIs
Exports `ice_vf_vsi_cfg_dvm_legacy_vlan_mode()` and `ice_vf_vsi_cfg_svm_legacy_vlan_mode()` unconditionally. Under `CONFIG_PCI_IOV`, exports `ice_vf_vsi_init_vlan_ops()`, `ice_vf_vsi_enable_port_vlan()`, and `ice_vf_vsi_disable_port_vlan()`; otherwise provides empty stubs.

## Control Flow and State
The header itself contains no state. It allows generic VSI initialization code to call VF VLAN setup only when relevant and lets non-SR-IOV builds avoid linking VF-specific operation setup.

## Dependencies and Integration Points
Includes `ice_vsi_vlan_ops.h` for the operation-table type and is included by generic VSI VLAN ops code and VF VLAN implementation.

## Risks
The closing include guard comment names `_ICE_PF_VSI_VLAN_OPS_H_`, which is cosmetic but misleading. Unconditional declarations for legacy helpers require their implementation to be available in build configurations that include the object.

## Test Signals
Compile SR-IOV and non-SR-IOV builds, verifying that generic VSI VLAN setup links correctly and that empty stubs do not alter non-IOV behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_vsi_vlan_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan.h

## Purpose
Defines the driver-local VLAN value object used by VSI and VF VLAN code.

## Important APIs and Types
`struct ice_vlan` stores TPID, VID, and priority. `ICE_VLAN(tpid, vid, prio)` provides a compound-literal initializer for concise call-site construction.

## Control Flow and State
This header contains no control flow. The struct is passed to filter and VSI context programming functions; callers decide whether it represents a filter, port VLAN, or VLAN zero/untagged behavior.

## Dependencies and Integration Points
Includes Linux types and `ice_type.h`; consumed by `ice_vsi_vlan_lib.h`, VF state, VLAN filter code, and host VF configuration rebuild.

## Risks
No validation is embedded in the type. TPID, VID, and priority constraints are enforced by callers such as `validate_vlan()` and port VLAN setters.

## Test Signals
Validate all call paths reject invalid TPIDs or priorities and correctly handle VID 0 with priority, VLAN 0 filters, 802.1Q, 802.1ad, and QinQ TPIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan_mode.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan_mode.c

## Purpose
Determines, sets, and caches the device VLAN mode. It negotiates double VLAN mode support with DDP package metadata and firmware, programs DVM/SVM through admin queue commands, updates default switch recipes for DVM, and performs post-DDP-download mode-specific configuration.

## Important APIs and Functions
- `ice_set_vlan_mode()` attempts DVM when both package and firmware support it, falling back to SVM if DVM setup fails.
- `ice_is_dvm_ena()` returns cached `hw->dvm_ena`.
- `ice_post_pkg_dwnld_vlan_mode_cfg()` caches mode after package download and switches parser proto IDs to DVM or logs why QinQ is unavailable.
- `ice_pkg_get_supported_vlan_mode()` reads package metadata section `ICE_SID_RXPARSER_METADATA_INIT`.
- `ice_aq_get_vlan_mode()` and `ice_aq_set_vlan_mode()` wrap AQ opcodes 0x020D/0x020C.
- `ice_set_dvm()` programs DVM AQ parameters, updates default recipes, sets port params, and installs DVM boost entries.
- `ice_set_svm()` programs SVM port and VLAN mode parameters.

## Control Flow
DVM support requires both package support and firmware AQ support. If unsupported, `ice_set_vlan_mode()` leaves the device in SVM-compatible behavior. DVM setup has multiple hardware-programming stages; any failure falls back to `ice_set_svm()`. After DDP download, all PFs call post configuration because only one PF performed package download under the global config lock.

## State and Persistence
The device VLAN mode is hardware/firmware configuration and is not dynamically changed during runtime. `hw->dvm_ena` caches the result for fast operation-table and VLAN behavior decisions. DVM modifies switch recipes and parser/protocol behavior globally.

## Dependencies and Integration Points
Depends on `ice_common.h`, package buffer/AQ helpers, metadata section constants, recipe update APIs, port parameter AQ, boost TCAM setup, and parser protocol mutation. VSI/VF VLAN ops consult `ice_is_dvm_ena()`.

## Risks
- DVM setup changes default recipe lookup indices and packet flag masks; errors can affect VLAN filtering and promiscuous matching globally.
- AQ validation rejects invalid priority tagging, RDMA packet flag, or management protocol ID fields.
- The fallback to SVM hides DVM failure from callers except debug logs; feature-level tests must confirm actual cached mode.
- `ice_post_pkg_dwnld_vlan_mode_cfg()` prints user guidance by probing support again, which repeats AQ/package reads.

## Test Signals
Test package-only support missing, firmware-only support missing, successful DVM, DVM AQ/recipe/port/boost failure falling back to SVM, cached `hw->dvm_ena`, QinQ availability messaging, and VLAN filtering/promisc behavior after recipe updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan_mode.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan_mode.h

## Purpose
Declares the VLAN mode control surface for hardware-level SVM/DVM behavior.

## Important APIs
`ice_is_dvm_ena()` returns cached DVM status, `ice_set_vlan_mode()` programs the hardware mode during initialization, and `ice_post_pkg_dwnld_vlan_mode_cfg()` applies post-DDP-download VLAN-mode configuration.

## Control Flow and State
The header exposes mode state only through `struct ice_hw *`; actual state lives in `hw->dvm_ena` and hardware/firmware configuration.

## Dependencies and Integration Points
Forward-declares `struct ice_hw`; consumed by VLAN ops, VSI setup, and initialization paths after package download.

## Risks
Callers must not assume `ice_set_vlan_mode()` guarantees DVM; it can legitimately return success while SVM remains active if DVM is unsupported.

## Test Signals
Build users with only the forward declaration and validate mode-dependent call sites under both cached SVM and DVM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_lib.c

## Purpose
Implements low-level VLAN operations for VSIs: adding/removing VLAN filters, configuring inner and outer stripping/insertion, setting and clearing inner/outer port VLANs, enabling/disabling Rx VLAN pruning, enabling/disabling Tx VLAN antispoof filtering, and clearing all port VLAN state.

## Important APIs and Functions
- `ice_vsi_add_vlan()` and `ice_vsi_del_vlan()` validate TPID/VID and update `vsi->num_vlan` around filter add/remove.
- Inner operations: `ice_vsi_ena_inner_stripping()`, `ice_vsi_dis_inner_stripping()`, `ice_vsi_ena_inner_insertion()`, `ice_vsi_dis_inner_insertion()`, `ice_vsi_set_inner_port_vlan()`, and `ice_vsi_clear_inner_port_vlan()`.
- Filtering: `ice_vsi_ena_rx_vlan_filtering()`, `ice_vsi_dis_rx_vlan_filtering()`, `ice_vsi_ena_tx_vlan_filtering()`, and `ice_vsi_dis_tx_vlan_filtering()`.
- Outer DVM operations: `ice_vsi_ena_outer_stripping()`, `ice_vsi_dis_outer_stripping()`, `ice_vsi_ena_outer_insertion()`, `ice_vsi_dis_outer_insertion()`, `ice_vsi_set_outer_port_vlan()`, and `ice_vsi_clear_outer_port_vlan()`.
- `ice_vsi_clear_port_vlan()` resets both inner and outer port VLAN context and restores default VLAN flags.

## Control Flow
Filter operations validate TPID and normalize duplicate/missing filter errors (`-EEXIST`, `-ENOENT`, `-EBUSY`) to success where appropriate. Stripping/insertion operations allocate a temporary VSI context, set valid sections, preserve unrelated fields, call `ice_update_vsi()`, and copy updated flags back into `vsi->info` only on success. Port VLAN setters save existing VLAN info into `vsi->vlan_info`, program port-based VLAN fields and pruning, and clearers restore saved VLAN info.

## State and Persistence
Persistent per-VSI VLAN hardware state lives in `vsi->info` fields: `inner_vlan_flags`, `outer_vlan_flags`, `sw_flags2`, `port_based_inner_vlan`, and `port_based_outer_vlan`. `vsi->vlan_info` snapshots previous flags for port VLAN restoration. `vsi->num_vlan` tracks programmed VLAN filter count.

## Dependencies and Integration Points
Depends on `ice_vsi_vlan_lib.h`, `ice_lib.h`, `ice_fltr.h`, `ice.h`, `ice_vlan_mode.h`, AQ `ice_update_vsi()`, filter programming, netdev flags, and hardware VLAN constants. Called through `struct ice_vsi_vlan_ops` by PF, VF, and SF VSI code.

## Risks
- Port VLAN state prevents modifying stripping/insertion and returns success, so callers must account for no-op behavior.
- `ice_cfg_vlan_pruning()` skips enabling pruning while netdev is promiscuous; filtering state may be deferred.
- Only specific TPIDs are valid; wrong TPID produces `-EINVAL`.
- Context update failure leaves cached `vsi->info` unchanged, but partially programmed hardware failure modes depend on AQ behavior.
- `vsi->num_vlan` can become inaccurate if filter programming paths outside this API modify VLAN filters.

## Test Signals
Test valid and invalid TPIDs, duplicate add/delete missing VLAN filters, SVM inner operations, DVM outer operations for 0x8100/0x88a8/0x9100 TPIDs, port VLAN set/clear with priority limits, promisc pruning deferral, Tx VLAN antispoof toggles, `ice_vsi_clear_port_vlan()` in SVM and DVM, and AQ error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_lib.h

## Purpose
Declares low-level VSI VLAN manipulation functions and the saved VLAN-info structure used to restore state after port VLAN removal.

## Important APIs and Types
`struct ice_vsi_vlan_info` stores `sw_flags2`, `inner_vlan_flags`, and `outer_vlan_flags`. The prototypes cover add/delete VLAN, inner stripping/insertion, inner port VLAN, Rx/Tx filtering, outer stripping/insertion, outer port VLAN, and generic port VLAN clearing.

## Control Flow and State
The header has no control flow. It defines the common low-level surface that mode/type-specific operation tables bind to.

## Dependencies and Integration Points
Includes Linux types and `ice_vlan.h`; forward-declares `struct ice_vsi`. Consumed by PF/VF/SF VLAN op setup and host VF reset rebuild.

## Risks
Because functions are low-level, callers should normally use `ice_vsi_vlan_ops` rather than direct calls so SVM/DVM and VSI type semantics are respected.

## Test Signals
Compile all operation-table users and validate direct callers intentionally bypass mode dispatch only where documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_ops.c

## Purpose
Initializes generic VSI VLAN operation tables and provides compatibility selection between inner and outer VLAN ops based on cached hardware VLAN mode.

## Important APIs and Functions
- `ice_vsi_init_vlan_ops()` initializes all ops to unsupported, then dispatches to PF, VF, or SF VSI-specific setup based on `vsi->type`.
- `ice_get_compat_vsi_vlan_ops()` returns outer ops in DVM and inner ops in SVM, preserving older code paths that do not explicitly distinguish inner versus outer VLANs.
- Local unsupported op implementations return `-EOPNOTSUPP` for each signature.

## Control Flow
Every VSI starts with safe unsupported callbacks to avoid NULL function pointer crashes. Type-specific setup overlays supported callbacks for PF/VF/SF. Unknown VSI types keep unsupported ops and log debug output.

## State and Persistence
Mutates `vsi->outer_vlan_ops` and `vsi->inner_vlan_ops` function-pointer tables. No hardware state is changed in this file directly.

## Dependencies and Integration Points
Depends on PF, VF, and SF VLAN op headers, generic library, `ice_lib.h`, and `ice.h`. Called during VSI creation/rebuild and used by callers that need mode-compatible VLAN behavior.

## Risks
- Adding a new op to `struct ice_vsi_vlan_ops` requires updating `ops_unsupported`; otherwise uninitialized pointers may appear.
- Compatibility selection hides inner/outer semantics; new code should prefer explicit ops when behavior differs.
- New VSI types need explicit handling or all VLAN operations will fail with `-EOPNOTSUPP`.

## Test Signals
Test PF, VF, SF, and unknown VSI types; SVM versus DVM compatibility selection; and all ops returning `-EOPNOTSUPP` before type-specific initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_ops.h

## Purpose
Defines the VLAN operation-table interface used by VSI type-specific code to abstract add/delete filters, stripping/insertion, filtering, and port VLAN operations.

## Important APIs and Types
`struct ice_vsi_vlan_ops` contains function pointers for `add_vlan`, `del_vlan`, `ena/dis_stripping`, `ena/dis_insertion`, `ena/dis_rx_filtering`, `ena/dis_tx_filtering`, `set_port_vlan`, and `clear_port_vlan`. The header declares `ice_vsi_init_vlan_ops()` and `ice_get_compat_vsi_vlan_ops()`.

## Control Flow and State
No direct control flow; operation tables are stored in `struct ice_vsi` and initialized by `ice_vsi_vlan_ops.c` plus PF/VF/SF specializers.

## Dependencies and Integration Points
Includes `ice_type.h` and `ice_vsi_vlan_lib.h`; consumed throughout VLAN, VF reset, and netdev VLAN feature handling.

## Risks
All table fields must be initialized before use. API additions require coordinated updates to unsupported defaults and every type-specific initializer.

## Test Signals
Build-time checks for all initializer users and runtime tests that all operations are non-NULL and return expected mode/type-specific results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_xsk.c

## Purpose
Implements AF_XDP zero-copy support for the `ice` driver. It handles XSK pool setup/teardown, queue-pair disable/enable around pool changes, zero-copy Rx buffer allocation, zero-copy Rx processing with XDP actions, AF_XDP Tx descriptor production, wakeup handling, IRQ/NAPI helpers, and ring cleanup.

## Important APIs and Functions
- `ice_xsk_pool_setup()` attaches or detaches an XSK pool to a queue ID, optionally disabling and re-enabling the live queue pair.
- `ice_realloc_rx_xdp_bufs()` allocates/frees the per-descriptor `xdp_buff` pointer array depending on pool presence.
- `ice_alloc_rx_bufs_zc()` and `__ice_alloc_rx_bufs_zc()` populate Rx descriptors from XSK fill/recycle buffers and bump tails.
- `ice_clean_rx_irq_zc()` is the zero-copy NAPI Rx loop; it consumes descriptors, builds multi-buffer XDP state, runs XDP, handles PASS/TX/REDIRECT/DROP/ABORT, refills buffers, updates wakeup state and stats.
- `ice_xmit_zc()` pulls AF_XDP Tx descriptors into the hardware XDP Tx ring.
- `ice_xsk_wakeup()` implements `ndo_xsk_wakeup`.
- IRQ/NAPI helpers include `ice_qvec_toggle_napi()`, `ice_qvec_dis_irq()`, `ice_qvec_cfg_msix()`, and `ice_qvec_ena_irq()`.
- Cleanup helpers free outstanding XSK Rx/XDP Tx buffers and complete AF_XDP Tx frames.

## Control Flow
Pool setup validates VSI type and queue bounds, maps or unmaps DMA, and if XDP is active temporarily disables the queue pair, reallocates the Rx XDP buffer array, then re-enables the queue pair and schedules NAPI for newly attached pools. Rx zero-copy loops until budget or descriptor exhaustion, syncs buffers for CPU, coalesces fragments, runs XDP, converts PASS packets to SKBs, and updates need-wakeup. Tx zero-copy first cleans completions, checks carrier/running state, peeks a bounded batch from the AF_XDP Tx ring, handles hardware ring wrap, marks RS, updates tail, and stats.

## State and Persistence
State is ring-local: `rx_ring->xdp_buf`, `rx_ring->xsk` partial multi-buffer head, ring indices, `xdp_ring->xdp_tx_active`, `tx_buf` types, XSK pool DMA mapping, need-wakeup flags, and q_vector interrupt/NAPI state. No persistent configuration survives queue teardown except pool association through the XSK subsystem.

## Dependencies and Integration Points
Depends on Linux XDP/AF_XDP APIs, `libeth_xdp`, BPF trace helpers, `ice_txrx`, `ice_txrx_lib`, queue-pair enable/disable, MSI-X/interrupt programming, NAPI, DMA mapping, netdev carrier/running state, and the driver XDP program path.

## Risks
- Pool changes while interface is up require precise queue disable/re-enable; failures can leave queues stopped or pool DMA state mismatched.
- Multi-buffer handling must preserve/free partial `first` buffers correctly.
- Need-wakeup behavior depends on correctly identifying allocation failure or empty rings.
- Tx completion distinguishes XSK_TX buffers from AF_XDP user descriptors; wrong `tx_buf->type` accounting can leak or double-complete.
- Queue ID bounds must cover both Rx and Tx real/driver queue counts.

## Test Signals
Test pool attach/detach while interface up/down, invalid queue IDs, PF and SF allowed versus VF rejected, XDP PASS/TX/REDIRECT/DROP/ABORT, multi-buffer packets, need-wakeup mode, Tx ring wrap, carrier down wakeup, cleanup with outstanding Rx and Tx buffers, and interrupt/NAPI disable/enable during XSK transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_xsk.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_xsk.h

## Purpose
Declares AF_XDP zero-copy APIs and provides stubs when `CONFIG_XDP_SOCKETS` is disabled.

## Important APIs
Defines `PKTS_PER_BATCH` as 8 for batched AF_XDP Tx descriptor handling. Real builds export pool setup, zero-copy Rx clean, wakeup, Rx buffer allocation, XSK-enabled query, ring cleanup, zero-copy Tx, Rx XDP buffer reallocation, and queue-vector IRQ/NAPI helpers. Non-XDP-sockets builds return conservative false/zero/`-EOPNOTSUPP` results and no-op cleanup/IRQ helpers.

## Control Flow and State
The header gates all AF_XDP behavior at compile time. Callers can invoke helpers without conditional code and receive disabled behavior when sockets support is absent.

## Dependencies and Integration Points
Includes `ice_txrx.h` for ring and q_vector types; used by netdev XSK hooks, XDP setup, queue pair management, and Tx/Rx datapath code.

## Risks
Stub return values must match caller expectations. In particular, `ice_clean_rx_irq_zc()` returns 0 when disabled, and `ice_xmit_zc()` returns false, so callers must only choose the zero-copy path when feature/pool state is active.

## Test Signals
Compile with `CONFIG_XDP_SOCKETS=y/n`, verify no unresolved XSK symbols, and run datapath tests that ensure disabled builds fall back to normal Rx/Tx paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_xsk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/allowlist.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/allowlist.c

## Purpose
Maintains per-VF virtchnl opcode allowlists. It starts VFs with only minimal default opcodes, enables working opcodes after resources are allocated, and enables feature-specific opcodes based on negotiated VF driver capabilities.

## Important APIs and Functions
- `ice_vc_is_opcode_allowed()` checks an opcode bit in `vf->opcodes_allowlist`.
- `ice_vc_set_default_allowlist()` clears all bits and allows GET_VF_RESOURCES, VERSION, and RESET_VF.
- `ice_vc_set_working_allowlist()` adds operational queue/stats/event opcodes.
- `ice_vc_set_caps_allowlist()` iterates negotiated capability bits and adds corresponding opcode groups.
- Static opcode arrays map L2, requested queues, legacy VLAN, VLAN v2, RSS, flex descriptors, advanced RSS, FDIR, PTP, and QoS capabilities to virtchnl opcodes.

## Control Flow
Capability-to-opcode mapping uses `BIT_INDEX(caps) (HWEIGHT((caps) - 1))`, relying on capability constants being single-bit masks. Setting caps allowlist walks set bits in `vf->driver_caps` up to the mapping table size and applies each opcode list.

## State and Persistence
The mutable state is `vf->opcodes_allowlist`, a bitmap of `VIRTCHNL_OP_MAX` bits. It is reset to default on VF initialization and reset; working and caps allowlists are added during virtchnl negotiation.

## Dependencies and Integration Points
Depends on `allowlist.h`, `ice.h`, virtchnl constants, and VF `driver_caps`. Used by virtchnl message dispatch to reject opcodes outside the VF's current state/capability set.

## Risks
- The `BIT_INDEX` mapping assumes capability values are powers of two; non-bitmask capability definitions would index incorrectly.
- New virtchnl capabilities or opcodes require updating these arrays or VFs may be denied valid messages.
- Default and reset behavior must clear old negotiated opcodes to prevent privilege carryover after reset.

## Test Signals
Test opcode rejection before resource negotiation, working opcode enable after GET_VF_RESOURCES, feature-specific enable for every listed capability, reset returning to default-only, invalid opcode >= `VIRTCHNL_OP_MAX`, and additions for new virtchnl capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/allowlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/allowlist.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/allowlist.h

## Purpose
Declares the VF virtchnl opcode allowlist API.

## Important APIs
Exports `ice_vc_is_opcode_allowed()`, `ice_vc_set_default_allowlist()`, `ice_vc_set_working_allowlist()`, and `ice_vc_set_caps_allowlist()`.

## Control Flow and State
The header has no control flow; functions operate on `struct ice_vf` and its `opcodes_allowlist` bitmap.

## Dependencies and Integration Points
Includes `ice.h` to expose `struct ice_vf`; used by VF lifecycle/reset and virtchnl dispatch code.

## Risks
Including `ice.h` from this small header increases dependency breadth, but keeps callers simple. API users must call the setters in the correct negotiation/reset order.

## Test Signals
Compile all virtchnl users and verify dispatch calls `ice_vc_is_opcode_allowed()` before handling capability-scoped operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/allowlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/fdir.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/fdir.c

## Purpose
Implements VF-controlled Flow Director filters over virtchnl. It validates VF requests, starts a VF control VSI for programming completions, parses protocol-header or raw parser-based filter patterns, configures hardware flow profiles, writes add/delete filter descriptors, tracks rule IDs and profile usage, handles asynchronous completion through control VSI Rx descriptors or timeout, and sends virtchnl status responses.

## Important APIs and Functions
- Public entry points: `ice_vc_add_fdir_fltr()`, `ice_vc_del_fdir_fltr()`, `ice_vc_fdir_irq_handler()`, `ice_flush_fdir_ctx()`, `ice_vf_fdir_init()`, and `ice_vf_fdir_exit()`.
- `ice_vc_fdir_param_check()` gates FDIR enablement, VF ACTIVE state, negotiated `VIRTCHNL_VF_OFFLOAD_FDIR_PF`, valid VSI ID, and VF VSI presence.
- Parsing functions include `ice_vc_fdir_parse_pattern()`, `ice_vc_fdir_parse_raw()`, `ice_vc_fdir_parse_action()`, and `ice_vc_validate_fdir_fltr()`.
- Profile functions include `ice_vc_fdir_alloc_prof()`, `ice_vc_fdir_config_input_set()`, `ice_vc_fdir_write_flow_prof()`, `ice_vc_fdir_rem_prof()`, and raw parser profile management in `ice_vc_add_fdir_raw()`/`ice_vc_del_fdir_raw()`.
- Rule bookkeeping uses `idr` plus `fdir_rule_list` through insert/remove/lookup/flush helpers.
- Async completion uses `ice_vc_fdir_set_irq_ctx()`, `ice_vf_fdir_timer()`, `ice_vc_fdir_irq_handler()`, `ice_vf_verify_rx_desc()`, and add/delete post-processing helpers.

## Control Flow
Add flow: check capacity and VF parameters, create/open control VSI if needed, allocate response and config, validate pattern/action, optionally return success for validate-only, configure input set/profile for structured rules or parser profile for raw rules, reject duplicate/conflicting rules, allocate an ID, set a single in-flight IRQ context, write the FDIR programming descriptor through the control VSI, and return only after async completion later sends final status.

Delete flow: validate parameters, look up flow ID, ensure control VSI exists, set in-flight IRQ context, write a delete descriptor, remove unused profile if this was the last structured rule of that flow/tunnel type, and wait for async completion to send final status and remove/free the rule.

Completion flow: control VSI Rx interrupt copies descriptor into `ctx_done`, clears `ctx_irq`, deletes timer, sets `ICE_FD_VF_FLUSH_CTX`, and schedules service. Timer performs the same handoff with timeout status. `ice_flush_fdir_ctx()` iterates VFs under the VF table lock, verifies descriptors, then calls add/delete post handlers to update counters, remove/free failed rules, and send virtchnl responses.

## State and Persistence
Per-VF FDIR state lives in `vf->fdir`: per-flow/tunnel counters, total filter count, dynamic profile array, IDR, rule list, spinlock-protected in-flight/done contexts, and parser/raw profile info in `vf->fdir_prof_info`. The max per-VF filter limit is 128. FDIR state is initialized on VF creation/reset and fully destroyed on VF reset/exit.

## Dependencies and Integration Points
Depends on `ice.h`, `ice_base.h`, `ice_lib.h`, `ice_flow.h`, `ice_vf_lib_private.h`, virtchnl FDIR structs, parser library, flow director hardware APIs, control VSI creation/open, service task scheduling, timers, IDR, spinlocks, and PF/VF reset cleanup. It integrates with allowlisted virtchnl FDIR opcodes and VF lifecycle code that resets FDIR on VF reset.

## Risks
- Only one FDIR operation per VF can be in flight; concurrent add/delete returns `-EBUSY`/no-resource status.
- Several paths allocate with devm and kfree; ownership must remain consistent on validation, async success/failure, and reset.
- Raw parser profile reference counting relies on PTG and field-vector equality; mismatches can leak or prematurely remove profiles.
- Add/delete responses are asynchronous; callers must not assume the immediate function return is the final VF-visible result.
- The structured add post path currently uses `is_tun = 0` for counter updates, while profile setup uses `ice_fdir_is_tunnel(conf->ttype)`; tunnel counter accounting deserves regression coverage.
- Timeout handling depends on service task scheduling to flush `ctx_done`.

## Test Signals
Test invalid VSI/caps/FD disabled cases, validate-only add, duplicate rule detection, profile conflicts between `OTHER` and TCP/UDP/SCTP flows, raw parser filters, max 128 filters, no hardware FDIR space, single in-flight request rejection, add success/failure descriptor verification, delete nonexistent ID, delete last rule removing profile, timeout path, VF reset while FDIR in flight, control VSI creation failure, and cleanup on `ice_vf_fdir_exit()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/fdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/fdir.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/fdir.h

## Purpose
Defines VF FDIR context/state structures and declares the VF Flow Director virtchnl API.

## Important APIs and Types
- `enum ice_fdir_ctx_stat` records READY, IRQ completion, or TIMEOUT.
- `struct ice_vf_fdir_ctx` stores the timer, virtchnl opcode, status, completion descriptor, valid flag, and associated rule configuration pointer.
- `struct ice_vf_fdir` stores per-flow/tunnel filter counts, profile entry counts, total count, hardware profile pointer table, IDR/list rule registry, spinlock, and IRQ/done contexts.
- Under `CONFIG_PCI_IOV`, exports add/delete, init/exit, IRQ handler, and context flush. Without SR-IOV, exports no-op IRQ and flush stubs.

## Control Flow and State
The structures support one in-flight FDIR request and one completed context per VF. `ctx_lock` protects context flags and handoff between IRQ/timer and service task.

## Dependencies and Integration Points
Forward-declares `ice_vf`, `ice_pf`, and `ice_vsi`; relies on Flow Director constants/types from included driver headers at call sites. Used in `struct ice_vf` and VF reset paths.

## Risks
The `conf` pointer is untyped `void *`, so implementation must maintain correct ownership and casting. Stubs under non-IOV cover only IRQ/flush, so add/delete/init/exit users must be SR-IOV-gated.

## Test Signals
Compile with SR-IOV on/off, validate spinlock/timer lifecycle, ensure context flags are cleared after IRQ, timeout, reset, and exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/fdir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/queues.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/queues.c

## Purpose
Implements virtchnl queue-related VF operations: queue configuration, queue enable/disable, IRQ map programming, queue bandwidth limits, queue quanta profiles, queue-count requests, and max frame size reporting adjusted for host port VLANs.

## Important APIs and Functions
- `ice_vc_get_max_frame_size()` returns port max frame size minus VLAN header when the VF has a hidden port VLAN.
- `ice_vc_cfg_qs_msg()` configures VF Tx/Rx queues from virtchnl queue-pair info.
- `ice_vc_ena_qs_msg()` and `ice_vc_dis_qs_msg()` enable/disable selected queue bitmaps and update VF queue state.
- `ice_vc_cfg_irq_map_msg()` maps VF MSI-X vectors to Rx/Tx queues.
- `ice_vc_cfg_q_bw()` stores and applies per-queue min/max bandwidth.
- `ice_vc_cfg_q_quanta()` selects/programs queue quanta profiles and assigns them to Tx rings.
- `ice_vc_request_qs_msg()` grants or rejects VF queue-count changes, resetting the VF on success.
- `ice_vf_vsi_dis_single_txq()`, `ice_vf_ena_txq_interrupt()`, and `ice_vf_ena_rxq_interrupt()` provide queue-level helpers.

## Control Flow
All virtchnl handlers validate VF ACTIVE state, VSI ID, queue IDs/bitmaps, ring lengths, and allocated queue bounds before programming hardware. Queue config coordinates with LAG reset preparation, supports optional CRC stripping disable only when VF negotiated CRC offload and VLAN stripping is not enabled, writes Tx/Rx ring DMA/count/frame settings, configures Rx descriptor format and PTP timestamp context, and unwinds configured queues on error. Queue enable only explicitly starts Rx rings; Tx queues are already enabled when queue context is configured. Disable can batch-stop all Rx rings when the requested bitmap equals the enabled bitmap.

## State and Persistence
Queue enable state lives in `vf->rxq_ena`, `vf->txq_ena`, and `ICE_VF_STATE_QS_ENA`. Queue bandwidth requests are cached in `vf->qs_bw[]`; quanta profile allocation increments `pf->num_quanta_prof_used`. Ring DMA addresses, lengths, buffer sizes, descriptor formats, max frame size, q_vectors, ITR indices, and quanta profile IDs are stored in VSI ring structures.

## Dependencies and Integration Points
Depends on virtchnl structs, `ice_vf_lib_private.h`, base/lib queue configuration helpers, LAG, scheduler bandwidth APIs, hardware register programming, PTP/flex descriptor capability bits, and PF queue availability accounting. Integrated with virtchnl dispatch and VF reset code.

## Risks
- Queue bitmap validation rejects zero/all-out-of-range but uses `BIT(ICE_MAX_RSS_QS_PER_VF)` boundary assumptions; queue counts must stay within word size.
- Error unwind in `ice_vc_cfg_qs_msg()` uses loop index rather than actual queue IDs configured, so sparse queue config failures should be tested carefully.
- Quanta profile allocation increments a PF counter without visible reclamation in this file.
- Per-queue bandwidth is compared against VF-level min/max limits and can reject configurations that would not take effect.
- Hidden port VLAN frame-size adjustment must stay consistent with netdev MTU and VF expectations.

## Test Signals
Test invalid VSI IDs, inactive VFs, zero/overflow queue bitmaps, invalid ring lengths, queue IDs beyond allocation, sparse queue configs, CRC strip disable with/without capability and VLAN stripping, flex descriptor RXDID validation, PTP timestamp flag, queue enable/disable idempotency, all-Rx batch disable, IRQ vector 0 rejection for queue maps, queue bandwidth min/max constraints, quanta size range/multiple-of-64/profile exhaustion, and queue request success/reset versus shortage response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/queues.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/queues.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/queues.h

## Purpose
Declares virtchnl queue-management handlers for VFs.

## Important APIs
Exports max frame size calculation, enable/disable queues, IRQ map config, per-queue bandwidth config, queue quanta config, queue pair config, and queue request handling.

## Control Flow and State
The header has no control flow. The implementation operates on `struct ice_vf` and virtchnl message buffers.

## Dependencies and Integration Points
Includes Linux types and forward-declares `struct ice_vf`. Included by the virtchnl dispatch layer that routes queue opcodes.

## Risks
All handlers accept raw `u8 *msg` buffers and rely on dispatch-side message size validation. Any new caller must ensure correct virtchnl payload length before invoking these functions.

## Test Signals
Compile dispatch users and test each exported opcode path with valid and malformed payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/queues.h -->
