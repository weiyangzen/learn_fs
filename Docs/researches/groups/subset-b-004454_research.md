# subset-b-004454 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pf.c

## Purpose
Implements the PF-specific hardware operations for the Intel fm10k Ethernet driver. It resets and initializes the PF datapath, programs GLORT/DGLORT forwarding maps, owns PF MAC/VLAN/multicast/xcast mailbox requests to the switch manager, partitions queues and MSI-X vectors for SR-IOV VFs, handles PF-side VF mailbox state, and collects PF/VF hardware statistics and fault records.

## Important APIs, Types, and Functions
The exported/externally consumed entry points are `fm10k_glort_valid_pf`, `fm10k_queues_per_pool`, `fm10k_vf_queue_index`, `fm10k_iov_msg_msix_pf`, `fm10k_iov_select_vid`, `fm10k_iov_msg_lport_state_pf`, `fm10k_msg_lport_map_pf`, `fm10k_msg_err_pf`, and the exported `fm10k_pf_info`. The `mac_ops_pf` table wires PF behavior into generic driver code: reset/init/start/stop, VLAN and MAC updates, xcast and logical-port state, stats, DGLORT configuration, DMA mask, faults, host-state checks, and LPORT-map requests. The `iov_ops_pf` table supplies SR-IOV resource assignment, traffic-class shaping, interrupt moderator updates, default MAC/VLAN delivery, VF reset, VF logical-port setup/reset, and VF stats collection. Important helper flows include `fm10k_reset_hw_pf`, `fm10k_init_hw_pf`, `fm10k_configure_dglort_map_pf`, `fm10k_iov_assign_resources_pf`, `fm10k_iov_assign_default_mac_vlan_pf`, `fm10k_iov_reset_resources_pf`, `fm10k_update_hw_stats_pf`, and `fm10k_get_fault_pf`.

## Control Flow
PF reset disables interrupts and moderation, maps all VF queue-table entries back to queue 0, disables all queues, verifies DMA quiescence, asserts datapath reset, then verifies the switch IP reports not-in-reset. PF init installs the default DGLORT entry, invalidates the rest, configures ITR link-list defaults, programs all queues for PF ownership, TPH hints, TSO flags, DMA control, max queue count, and total VF count based on ARI hierarchy support. Runtime MAC/VLAN/xcast updates validate GLORT/VLAN/MAC inputs, build TLV messages, and enqueue them to the switch-manager mailbox. DGLORT configuration writes queue SGLORTs, per-priority class TX controls, and DGLORTDEC/DGLORTMAP register entries from a supplied `fm10k_dglort_cfg`.

SR-IOV setup records the VF/pool counts, computes queues/vectors per pool, initializes VF traffic classes to blocked, clears VF mailbox memory and FLR events, assigns unused rings back to the PF, links interrupt moderation registers, maps VF queues through TQMAP/RQMAP, and repeats each VF's first queue for unused map slots. VF reset handling disconnects the VF mailbox, hides queues, reinitializes queue ownership, traffic shaping, interrupt links, mailbox/VLAN/RSS state, base-address MAC handoff registers, and queue maps. VF mailbox LPORT requests are capability-clamped and converted into switch-manager LPORT create/delete and xcast updates, with a ready response sent when a VF is allowed to enable.

## State and Persistence Behavior
PF state is stored in `hw->mac` (`default_vid`, `itr_scale`, `max_queues`, `dglort_map`, reset counters), `hw->iov` (`total_vfs`, `num_vfs`, `num_pools`, ops), `hw->swapi` table usage/status, and per-VF `struct fm10k_vf_info` fields including mailbox state, rate limit, GLORT, PF/SW VLANs, MAC, VSI, VF index, and xcast capability/enabled flags. Hardware persistence is register-based: DGLORT maps, queue ownership, queue-to-VF maps, MSI-X moderation chains, traffic-class rate/credit registers, VLAN/RETA/RSS registers, mailbox memory, fault registers, and MAC handoff values encoded into queue base registers for VFs that are not mailbox-connected.

## Dependencies and Integration Points
Includes `fm10k_pf.h` and `fm10k_vf.h`, and relies on common fm10k register access, mailbox, TLV, generic queue, and stats helpers. It integrates with Linux SR-IOV through VF resource ownership and FLR event registers, with the switch manager through PF TLV messages, and with generic fm10k code via `struct fm10k_info` operation tables. It also uses Linux bitfield helpers, Ethernet address validation, sleeping/polling helpers, and endian conversion for mailbox ABI structs.

## Risks
The highest-risk paths are reset and SR-IOV resource transitions because queue maps, queue ownership, traffic shaping, interrupt moderator links, and mailbox disconnects must be ordered so a VF cannot DMA through stale state. The temporary use of VF queue base and TDLEN registers to pass MAC and ITR scale to uninitialized VFs is subtle and must stay synchronized with VF init logic. TLV messages assume mailbox availability and sorted handler tables. GLORT mask validation and DGLORT bit lengths are easy to break with off-by-one changes. Stats use a queue-control ID canary to avoid aggregating across resets; changing that can corrupt counters. Fault handling clears valid bits after reading, so readers must preserve all needed fields.

## Test Signals
Useful validation includes PF probe/reset/init, reset while TX/RX requests are pending, DMA-pending reset failure, ARI and non-ARI VF-count detection, LPORT map and PVID mailbox replies, GLORT rejection cases, VLAN multi-bit set/clear, unicast/multicast/xcast mailbox commands, DGLORT map programming for PF and VF layouts, SR-IOV enable with 7 and 64 VF limits, VF FLR reset, VF mailbox absent/present default MAC/VLAN delivery, VF rate limiting boundaries, MSI-X vector mask rescans, PF/VF stats across resets, fault injection for PCA/THI/FUM, and switch-ready host-state polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pf.h

## Purpose
Declares the PF-side fm10k mailbox ABI and public PF helpers used by the PF implementation, VF-facing handlers, and generic fm10k integration. It is the header contract for PF TLV message IDs, PF TLV attribute IDs, packed switch-manager ABI structs, and handler registration macros.

## Important APIs, Types, and Functions
Public helpers are `fm10k_glort_valid_pf`, `fm10k_queues_per_pool`, `fm10k_vf_queue_index`, `fm10k_iov_select_vid`, `fm10k_iov_msg_msix_pf`, `fm10k_iov_msg_lport_state_pf`, `fm10k_msg_lport_map_pf`, and `fm10k_msg_err_pf`. Message IDs in `enum fm10k_pf_tlv_msg_id_v1` cover xcast mode changes, MAC forwarding updates, LPORT map/create/delete, config, PVID updates, and flow-table operations. Attribute IDs in `enum fm10k_pf_tlv_attr_id_v1` define error, LPORT map, xcast, MAC/VLAN/config/flow payload, port, and PVID attributes. ABI structs are `fm10k_mac_update`, `fm10k_global_table_data`, and `fm10k_swapi_error`, all packed and 4-byte aligned for TLV serialization. Handler macros bind message IDs to `fm10k_tlv_attr` tables.

## Control Flow
The header has no runtime execution. It shapes PF mailbox dispatch by providing sorted message-handler macro entries consumed by `fm10k_msg_data_pf` in `fm10k_pf.c`, and it provides the attribute schemas that `fm10k_tlv_msg_parse` uses before calling PF handlers.

## State and Persistence Behavior
The packed structs are persistent firmware/switch-manager ABI payloads embedded in TLV messages. `fm10k_mac_update` carries MAC, VLAN, GLORT, flags, and add/remove action. `fm10k_swapi_error` persists switch API status and global table usage counters for MAC, nexthop, and FFU tables. The header itself stores no runtime state.

## Dependencies and Integration Points
Includes `fm10k_type.h` and `fm10k_common.h`, and depends on the TLV parser types declared through those headers. It integrates with `fm10k_pf.c` for implementation, with `fm10k_tlv.c` for parse/build behavior, and with PF/VF mailbox initialization code that installs `fm10k_info`.

## Risks
Message and attribute numeric values are ABI-sensitive. Reordering handler tables without preserving sorted ID order can break parser lookup because dispatch walks until `data->id >= msg_id`. Changing packed struct layout, endian fields, or alignment can break switch-manager communication while still compiling. The header contains future flow-table IDs not implemented in the C file, so callers must tolerate not-implemented replies.

## Test Signals
Compile coverage for all includers, TLV parsing of LPORT map/PVID/error replies, MAC update message generation, switch-manager error table decoding, unknown PF message fallback, and ABI size/alignment checks for packed structs are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_tlv.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_tlv.c

## Purpose
Implements the fm10k mailbox TLV encoder, decoder, validator, dispatcher, default error handler, and a built-in test-message generator/validator. This is the shared protocol layer for PF-to-switch-manager and PF-to-VF mailbox messages.

## Important APIs, Types, and Functions
Message construction starts with `fm10k_tlv_msg_init`, then attributes are appended with `fm10k_tlv_attr_put_mac_vlan`, `fm10k_tlv_attr_put_bool`, `fm10k_tlv_attr_put_value` and typed wrappers, or `fm10k_tlv_attr_put_le_struct`. Attribute extraction uses `fm10k_tlv_attr_get_mac_vlan`, `fm10k_tlv_attr_get_value` and typed wrappers, and `fm10k_tlv_attr_get_le_struct`. Parser internals are `fm10k_tlv_attr_validate`, `fm10k_tlv_attr_parse`, and `fm10k_tlv_msg_parse`. `fm10k_tlv_msg_error` is the default not-implemented handler. Test support is provided by `fm10k_tlv_msg_test_attr`, `fm10k_tlv_msg_test_create`, and `fm10k_tlv_msg_test`.

## Control Flow
Writers initialize a message header with the message flag and ID, append attributes at `FM10K_TLV_DWORD_LEN(*msg)`, encode data in CPU-order dwords, set each attribute length, then grow the message length with 4-byte alignment. The parser first verifies the message flag, extracts the message ID, finds a handler entry by sorted ID, falls back to the error handler entry if no exact match exists, parses attributes into a fixed `results[32]` array according to the handler's attribute schema, then invokes the handler. Attribute parsing validates each header and type/length contract, silently ignores schema-unknown attributes, rejects out-of-range result IDs, and verifies the final parsed byte offset equals the message length. The test handler validates each present attribute against known constants, recursively parses nested attributes, and returns a TLV result message through the mailbox.

## State and Persistence Behavior
There is no global mutable protocol state except static test constants. State is encoded in caller-provided `u32` message buffers and in `results` pointer arrays. Message and attribute headers persist lengths in bytes above bit 20, flags in bits 16-19, and IDs in bits 0-15. Little-endian structs are converted to/from CPU-order dwords when placed in TLVs, which makes the mailbox dword stream host-order while preserving ABI struct endian fields.

## Dependencies and Integration Points
Includes `fm10k_tlv.h`, which includes `fm10k_type.h`; relies on Ethernet address helpers, endian helpers, bit helpers, and mailbox `enqueue_tx` operations through handler callbacks. It is used by PF and VF code to build mailbox requests, parse replies, and register message handlers in `struct fm10k_msg_data` tables.

## Risks
The implementation does not track caller buffer capacity when appending attributes, so callers must size stack buffers correctly. Handler and attribute schema arrays are expected to be sorted by ID and terminated with `FM10K_TLV_ATTR_LAST` or `FM10K_TLV_ERROR`; malformed ordering can produce wrong lookup or out-of-bounds walking. `fm10k_tlv_attr_get_mac_vlan` does not check a non-null VLAN pointer even though callers pass one. Nested attribute support is private and relies on the nested header length being updated through the nest pointer. Length math is packed into header-shifted units, so mistakes in byte-versus-shifted length handling can corrupt parsing.

## Test Signals
Test with every TLV attribute type, minimum and maximum integer sizes, null strings including missing terminator, MAC/VLAN encoding, little-endian struct round trips, nested attributes, unknown attributes, unknown message IDs, malformed message/attribute flags, invalid lengths, result IDs above 31, unaligned struct lengths, buffer-size stress in callers, and mailbox test-message request/reply through PF/VF paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_tlv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_tlv.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_tlv.h

## Purpose
Defines the fm10k mailbox TLV header format, type system, parser result limits, attribute schema structures, handler table structures, typed put/get wrappers, parser entry points, and test-message IDs. It is the shared declaration layer for the TLV implementation and PF/VF mailbox users.

## Important APIs, Types, and Functions
Key macros define ID, flags, and length bit positions, `FM10K_TLV_HDR_LEN`, aligned-length calculation, dword count calculation, `FM10K_TLV_RESULTS_MAX`, and the sentinel `FM10K_TLV_ERROR`. `enum fm10k_tlv_type` covers null strings, MAC addresses, booleans, unsigned/signed integers, little-endian structs, and nested attributes. `struct fm10k_tlv_attr` describes legal attributes, and `struct fm10k_msg_data` maps message IDs to attribute schemas and handler callbacks. Declaration macros such as `FM10K_TLV_ATTR_U32`, `FM10K_TLV_ATTR_LE_STRUCT`, `FM10K_MSG_HANDLER`, `FM10K_TLV_MSG_TEST_HANDLER`, and `FM10K_TLV_MSG_ERROR_HANDLER` reduce table boilerplate.

## Control Flow
The header has no runtime control flow, but it controls TLV dispatch contracts. Message handlers receive an array of attribute pointers indexed by attribute ID, and callers use the typed wrappers to encode/decode values using fixed lengths. The message and attribute arrays must be sentinel-terminated for the parser's linear search behavior.

## State and Persistence Behavior
The header defines the persistent TLV wire format. A TLV header stores byte length excluding the header, a message flag when the item is a top-level message, and a 16-bit type/ID. It also defines the maximum parser result array size of 32, meaning mailbox protocols with attribute IDs above 31 are rejected by this parser unless handled outside the normal result array.

## Dependencies and Integration Points
Includes `fm10k_type.h` after a forward declaration for `struct fm10k_msg_data`. It is included by `fm10k_tlv.c`, `fm10k_pf.h`, `fm10k_vf.h`, and mailbox-related code that registers handlers or emits TLVs.

## Risks
The macros encode ABI assumptions in bit shifts and alignment; any change affects every mailbox protocol user. Attribute IDs must stay within `FM10K_TLV_RESULTS_MAX` for parsed results. The include chain depends on `fm10k_type.h` for `struct fm10k_hw` and `struct fm10k_mbx_info`, so circular header changes can break compilation. Signed integer wrappers reuse the same raw value function as unsigned wrappers, so consumers must pass correctly typed storage.

## Test Signals
Compile all PF/VF mailbox users, static checks of TLV header length/dword macros, parser tests for all declared `enum fm10k_tlv_type` values, attribute IDs at 0 and 31, ID 32 rejection, sorted and unsorted handler schema behavior, unknown-message fallback, and the built-in test handler are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_tlv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_type.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_type.h

## Purpose
Defines the central fm10k hardware contract: PCI IDs, queue/vector limits, error codes, register offsets and bitfields, descriptor formats, bus/stat/fault structures, DGLORT configuration, PF/VF operation tables, VF state, IOV state, hardware identity, and the top-level `struct fm10k_hw`.

## Important APIs, Types, and Functions
Important constants include device IDs, queue and vector maxima, PCIe capability offsets, fm10k error codes, PF/VF register offsets, DMA control bits, DGLORT and VLAN constants, TQMAP/RQMAP table sizes, stats registers, interrupt moderation registers, VF control registers, reset/queue-disable timeouts, and descriptor multiple requirements. Core types include `fm10k_bus_info`, `fm10k_hw_stat`, `fm10k_hw_stats_q`, `fm10k_hw_stats`, `fm10k_dglort_cfg`, `fm10k_fault`, `fm10k_mac_ops`, `fm10k_mac_info`, `fm10k_swapi_info`, `fm10k_vf_info`, `fm10k_iov_ops`, `fm10k_iov_info`, `fm10k_info`, `fm10k_hw`, `fm10k_tx_desc`, `fm10k_tx_desc_cache`, `fm10k_rx_desc`, and `fm10k_ftag`.

## Control Flow
The header has no direct execution. It controls runtime dispatch through function-pointer tables in `fm10k_mac_ops` and `fm10k_iov_ops`, and it drives register access/control-flow decisions in PF, VF, common, mailbox, and TX/RX code through named offsets and masks.

## State and Persistence Behavior
`struct fm10k_hw` is the persistent in-memory device state for the driver instance, carrying MMIO base, OS backpointer, MAC state, bus state, IOV state, PF/VF mailbox state, switch API status, and PCI identity. `struct fm10k_vf_info` is PF-owned persistent state for each VF, including mailbox, stats, rate, GLORT, VLANs, MAC, VSI, and capability/enabled flags. Hardware-persistent state is represented by register definitions and descriptor layouts. TX/RX descriptors, FTAG, queue stats, fault records, and TLV-related structs are ABI-sensitive because hardware or firmware consumes them directly.

## Dependencies and Integration Points
Includes Linux integer, byteorder, and Ethernet helpers plus `fm10k_mbx.h`. It is included across the fm10k driver and underpins `fm10k_common`, PF/VF ops, TLV handling, mailbox setup, queue programming, interrupt moderation, stats, and netdev TX/RX paths.

## Risks
This is a high-blast-radius hardware ABI header. Changing register offsets, bit masks, descriptor layout, struct alignment, queue/vector maxima, or operation table signatures can break PF, VF, and data path behavior. The TDLEN ITR-scale software handoff between PF and VF is documented here and must remain consistent with both implementations. `struct fm10k_vf_info` requires `mbx` as the first field because PF VF handlers cast mailbox pointers back to VF info. `fm10k_hw_stats` only sizes queue stats for `FM10K_MAX_QUEUES_PF`, which matches PF max rather than absolute hardware max.

## Test Signals
Build coverage across PF and VF drivers, register programming smoke tests, descriptor size/layout checks, endian/bitfield validation, PF and VF probe, SR-IOV VF allocation, queue reset/start/stop, TX/RX descriptor handling, VLAN/RSS/RETA programming, interrupt moderation, stats aggregation and reset rebind, fault capture, TDLEN ITR-scale handoff, and mailbox handler casts are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_vf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_vf.c

## Purpose
Implements VF-specific fm10k hardware operations and mailbox handlers. It discovers VF queue resources assigned by the PF, resets/stops VF queues, retrieves PF-provided MAC/VLAN/ITR information, requests VLAN/MAC/multicast/xcast/logical-port changes through the PF mailbox, and exposes a VF `fm10k_info` operation table.

## Important APIs, Types, and Functions
Externally used handlers and data are `fm10k_mac_vlan_msg_attr`, `fm10k_msg_mac_vlan_vf`, `fm10k_lport_state_msg_attr`, `fm10k_msg_lport_state_vf`, and `fm10k_vf_info`. Core internal functions are `fm10k_stop_hw_vf`, `fm10k_reset_hw_vf`, `fm10k_init_hw_vf`, `fm10k_update_vlan_vf`, `fm10k_read_mac_addr_vf`, `fm10k_update_uc_addr_vf`, `fm10k_update_mc_addr_vf`, `fm10k_update_int_moderator_vf`, `fm10k_update_lport_state_vf`, `fm10k_update_xcast_mode_vf`, `fm10k_update_hw_stats_vf`, and `fm10k_rebind_hw_stats_vf`. `mac_ops_vf` wires these into generic fm10k code.

## Control Flow
VF init first verifies queue 0 is assigned, probes additional queues by checking descriptor cache offsets and queue ownership, disables the owned queues, records `max_queues`, reads the default VLAN from `TXQCTL(0)`, and reads the PF-provided ITR scale from the software-defined TDLEN bits. Stop disables queues through generic code, restores the permanent MAC and ITR scale into queue base/TDLEN registers for a future VF init, and returns pending-request status if relevant. Reset stops hardware, sets `VFCTRL_RST`, waits, clears the bit, and verifies reset completion. MAC/VLAN operations build `FM10K_VF_MSG_ID_MAC_VLAN` TLVs and enqueue them to the PF mailbox. Logical-port enable resets local DGLORT state, sends an LPORT_STATE request, and waits for a ready indication; disable includes the DISABLE bool. Xcast and MSI-X updates are mailbox requests to the PF.

## State and Persistence Behavior
VF state is held in `hw->mac.perm_addr`, `hw->mac.addr`, `hw->mac.default_vid`, `hw->mac.vlan_override`, `hw->mac.max_queues`, `hw->mac.itr_scale`, and `hw->mac.dglort_map`. The PF persists some VF bootstrap data in queue base registers and TDLEN until the VF reads it. Mailbox replies can update permanent MAC/default VLAN and LPORT readiness. Stats are queue-only and use generic queue-stat helpers over `max_queues`.

## Dependencies and Integration Points
Includes `fm10k_vf.h`, which brings in the common and type contracts. It depends on generic fm10k queue stop/start/stats helpers, TLV helpers, PF/VF mailbox initialization through `fm10k_pfvf_mbx_init`, Linux bitfield helpers, Ethernet address validation, and mailbox `enqueue_tx`. It integrates with the PF implementation through shared VF message IDs and attributes.

## Risks
VF initialization relies on PF-programmed register encodings, including the TDLEN ITR-scale handoff and MAC storage in queue base registers. Queue discovery uses inverted register reads to detect unavailable or PF-owned queues, so hardware semantics must not change. VF unicast changes enforce a locked permanent MAC when one exists; changing that can weaken PF policy. Mailbox sends mostly return enqueue status but do not wait for policy acceptance. `fm10k_configure_dglort_map_vf` is a stub, so callers must not expect local DGLORT programming on VFs.

## Test Signals
VF probe/init with one and multiple queues, no-resource detection, queue disable pending behavior, VF reset bit completion, PF-provided MAC/default VLAN/vlan-override mailbox update, MAC read from base registers, locked-MAC rejection, VLAN set/clear with reserved-bit rejection, multicast validation, MSI-X rescan requests, LPORT enable/disable ready state, xcast mode requests, stats update/rebind, and PF absent or mailbox enqueue failure paths should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_vf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_vf.h

## Purpose
Declares the VF-side fm10k mailbox message IDs, attribute IDs, handler registration macros, VF message attribute tables, VF message handlers, and exported `fm10k_vf_info`. It is the shared protocol contract between `fm10k_vf.c`, PF-side VF handlers, and TLV dispatch setup.

## Important APIs, Types, and Functions
`enum fm10k_vf_tlv_msg_id` defines VF test, MSI-X, MAC/VLAN, and LPORT-state messages. `enum fm10k_tlv_mac_vlan_attr_id` defines VLAN, set, MAC, default-MAC, and multicast attributes. `enum fm10k_tlv_lport_state_attr_id` defines disable, xcast-mode, and ready attributes. Macros `FM10K_VF_MSG_MSIX_HANDLER`, `FM10K_VF_MSG_MAC_VLAN_HANDLER`, and `FM10K_VF_MSG_LPORT_STATE_HANDLER` build `struct fm10k_msg_data` entries. Declared handlers are `fm10k_msg_mac_vlan_vf` and `fm10k_msg_lport_state_vf`.

## Control Flow
The header has no runtime flow, but it defines how VF mailbox dispatch tables are built and how PF/VF code identify TLV attributes inside parsed result arrays.

## State and Persistence Behavior
The header stores no runtime state. Its enums are persistent PF/VF mailbox ABI values, and the declared attribute tables control validation for MAC/VLAN and LPORT-state messages.

## Dependencies and Integration Points
Includes `fm10k_type.h` and `fm10k_common.h`, and depends on the TLV handler/attribute types from the fm10k include chain. It is included by `fm10k_vf.c` and `fm10k_pf.c` because the PF handles VF-originated MSI-X and LPORT-state messages.

## Risks
Message and attribute IDs are ABI-sensitive between PF and VF. Attribute IDs must stay below `FM10K_TLV_RESULTS_MAX`. Handler macros assume the attribute tables are defined and sorted. Adding a VF message without updating both VF and PF dispatch paths can result in not-implemented mailbox replies.

## Test Signals
Compile PF and VF builds, VF mailbox dispatch table initialization, PF-side handling of MSI-X and LPORT-state requests, VF-side handling of MAC/VLAN and ready replies, unknown VF message fallback, and ABI compatibility of enum values are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_vf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/Makefile

## Purpose
Defines the kernel build composition for the Intel i40e driver module. It selects include paths, builds `i40e.o` when `CONFIG_I40E` is enabled, and lists the object files linked into the module, with DCB support added conditionally.

## Important APIs, Types, and Functions
The key build variables are `ccflags-y`, `subdir-ccflags-y`, `obj-$(CONFIG_I40E)`, `i40e-y`, and `i40e-$(CONFIG_I40E_DCB)`. Core objects include main, ethtool, admin queue, common, HMC, LAN HMC, NVM, debugfs, diagnostics, TX/RX, PTP, DDP, client, virtchnl PF, AF_XDP, and devlink support. Conditional DCB objects are `i40e_dcb.o` and `i40e_dcb_nl.o`.

## Control Flow
There is no runtime control flow. Kernel Kbuild uses these assignments to decide which source files are compiled and linked into `i40e.ko`.

## State and Persistence Behavior
The file defines build-time module composition only. It does not define runtime or persistent device state.

## Dependencies and Integration Points
Integrates with Linux Kbuild and `CONFIG_I40E`/`CONFIG_I40E_DCB`. The include path flags allow local driver headers to be found by objects in this directory and subdirectories.

## Risks
Removing or misordering objects can produce unresolved symbols or omit feature initialization at link time. Conditional DCB object selection must stay consistent with preprocessor guards in `i40e.h` and other source files. Adding a new source file without listing it here means it will not be part of the module.

## Test Signals
Build with `CONFIG_I40E=m`, `CONFIG_I40E=y`, and disabled; build with `CONFIG_I40E_DCB` on and off; run modpost for unresolved symbols; and verify the resulting module contains adminq, netdev, virtchnl, devlink, PTP, AF_XDP, and optional DCB entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e.h

## Purpose
Provides the main internal header for the Intel i40e driver. It defines driver limits, feature flags, PF/VSI/VEB/channel/filter/PTP state, helper macros, inline helpers, and cross-module prototypes used by the i40e implementation.

## Important APIs, Types, and Functions
Important constants cover descriptor limits, CSR size, AdminQ sizing, queue/VF/VMDq defaults, Flow Director limits, interrupt name length, NVM/OEM version masks, bandwidth credits, UDP tunnel indices, flex parser programming, and queue interrupt-control value construction. State enums include `i40e_state`, `i40e_vsi_state`, `i40e_pf_flags`, `i40e_interrupt_policy`, and `i40e_filter_state`. Major structs are `i40e_lump_tracking`, `i40e_fdir_filter`, `i40e_cloud_filter`, `i40e_tc_configuration`, `i40e_udp_port_config`, `i40e_flex_pit`, `i40e_fwd_adapter`, `i40e_channel`, `i40e_pf`, `i40e_mac_filter`, `i40e_new_mac_filter`, `i40e_veb`, `i40e_vsi`, `i40e_netdev_priv`, `i40e_q_vector`, and `i40e_device`.

Inline helpers format NVM strings, iterate PF VSIs/VEBs, convert MAC addresses to hash keys, map netdev/hw to PF, access Flow Director input-set registers, find VSIs/VEBs by type or SEID, enable dynamic interrupts, test DCB/mqprio/XDP state, and choose max descriptor count. The prototype tail exposes lifecycle, reset, RSS, switch config, filters, queue control, VEB/VSI management, stats, debugfs, client notifications, netdev open/close/ioctl, VLAN/MAC filters, DCB, PTP, ADQ, bandwidth, cloud filters, devlink-related helpers, and device pointer conversion.

## Control Flow
The header has limited inline control flow for iteration and lookup. `i40e_pf_for_each_vsi` and `i40e_pf_for_each_veb` walk sparse arrays by repeatedly skipping null entries. Lookup helpers scan those arrays for type or SEID matches. Formatting helpers branch on NVM EETrack/OEM markers to build version strings. Most runtime control flow is delegated to C files via the declared prototypes and state flags defined here.

## State and Persistence Behavior
`struct i40e_pf` is the long-lived PF driver state: PCI device, devlink port, hardware struct, state bitmap, MSI-X entries, queue/vector/VF allocation counters, Flow Director and cloud filter lists, UDP tunnel state, service timer/work, PF feature flags, client instance, stats, reset counters, switch/VSI/VEB topology, resource piles, debugfs, SR-IOV state, DCB config, PTP clock/timestamp state, RSS/DDP/NVM fields, and bandwidth limits. `struct i40e_vsi` is per-interface state: netdev, VLAN bitmap, filter hash, stats, rings, XDP, q_vectors, queue counts, HW SEID, traffic class config, bandwidth, parent PF, channels, macvlan state, client private data, IRQ handler, and AF_XDP zero-copy map. `struct i40e_veb` persists switching/bandwidth/stats state. Filter structs persist software pending/active/remove state before firmware synchronization.

## Dependencies and Integration Points
Includes Linux PCI, PTP, virtchnl, devlink, traffic control, UDP tunnel, and i40e internal headers for DCB, debug, devlink, IO, prototypes, registers, and TX/RX. It is included by most i40e source files and coordinates netdev, ethtool, AdminQ, NVM, DCB, PTP, SR-IOV/virtchnl, client drivers, devlink, AF_XDP, and switch/VEB/VSI management.

## Risks
This header has very high coupling. Adding fields to hot structs can affect cache layout and assumptions in many modules. State bit semantics coordinate workqueues, reset paths, interrupt handling, VF release, and removal; incorrect flag use can race resets or teardown. Filter states are protected by locks and staged wrappers because firmware commands can sleep; bypassing that pattern can create races. Prototype drift against C implementations breaks module builds. Conditional DCB declarations must match Kconfig object selection. Helper macros directly program register fields and must stay aligned with hardware definitions.

## Test Signals
Full i40e module build with feature combinations, sparse/lockdep coverage for state and filter locking, probe/remove, reset/rebuild paths, service task scheduling, netdev open/close, queue start/stop, RSS config, VLAN/MAC filter sync, Flow Director and cloud filters, SR-IOV VF enable/reset, DCB on/off, PTP timestamping and GPIO pins, devlink, client driver callbacks, AF_XDP queue enablement, interrupt dynamic enable, NVM version formatting, and descriptor-limit selection by MAC type are important validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq.c

## Purpose
Implements i40e Admin Queue lifecycle and descriptor processing. It allocates and frees ASQ/ARQ rings and buffers, programs hardware AdminQ registers, initializes firmware communication, derives hardware capability flags from firmware/API/MAC type, sends synchronous/asynchronous AdminQ commands, cleans send completions, receives AdminQ events, and resumes queues after register reset.

## Important APIs, Types, and Functions
Public functions are `i40e_init_adminq`, `i40e_shutdown_adminq`, `i40e_asq_send_command_atomic`, `i40e_asq_send_command`, `i40e_asq_send_command_atomic_v2`, `i40e_fill_default_direct_cmd_desc`, and `i40e_clean_arq_element`. Internal allocation/config helpers include `i40e_alloc_adminq_asq_ring`, `i40e_alloc_adminq_arq_ring`, `i40e_alloc_arq_bufs`, `i40e_alloc_asq_bufs`, `i40e_free_arq_bufs`, `i40e_free_asq_bufs`, `i40e_config_asq_regs`, `i40e_config_arq_regs`, `i40e_init_asq`, `i40e_init_arq`, `i40e_shutdown_asq`, `i40e_shutdown_arq`, `i40e_set_hw_caps`, `i40e_clean_asq`, `i40e_asq_done`, `i40e_asq_send_command_atomic_exec`, and `i40e_resume_aq`.

## Control Flow
AdminQ init validates queue sizes, sets the ASQ command timeout, initializes ASQ, initializes ARQ, then repeatedly tries `i40e_aq_get_firmware_version` because firmware may not be immediately ready. On early EIO timeouts it sleeps, reprograms the queue registers with `i40e_resume_aq`, and retries up to ten times. After a successful firmware version query, it sets hardware capability bits based on MAC type and firmware/API versions, reads NVM/OEM version words, rejects a too-new firmware API major version, releases any stale NVM resource lock, and initializes NVM update state. Any failure unwinds ARQ then ASQ.

ASQ send acquires `asq_mutex`, validates queue/head/buffer/detail state, applies caller detail flags/cookie, cleans completed send descriptors, copies the descriptor to the next ring slot, copies indirect buffers into preallocated DMA memory and patches descriptor DMA addresses, advances tail unless postponed, waits for completion for non-async/non-postponed commands, copies descriptor and buffer writeback to caller memory, maps firmware return values to Linux status, stores `asq_last_status`, optionally saves a writeback descriptor, and returns timeout/critical errors when firmware does not advance the head. ARQ clean acquires `arq_mutex`, checks whether hardware head differs from `next_to_clean`, copies the event descriptor and message into caller buffers, restores the descriptor as a posted receive buffer, advances ARQ tail and software indices, computes pending events, and notifies NVM update waiting logic.

## State and Persistence Behavior
Persistent AdminQ state lives in `hw->aq`: ASQ/ARQ ring descriptors, DMA buffer arrays, command-detail array, ring counts, buffer sizes, next-to-use/clean indices, mutexes, firmware/API versions, command timeout, and last status values. Hardware persistence is in PF_ATQ/ARQ head/tail/length/base registers and in DMA rings visible to firmware. ASQ indirect command buffers and ARQ event buffers are preallocated DMA memory reused across command/event cycles. Capability bits in `hw->caps`, NVM version fields, NVM resource lock state, and NVM update state are initialized from AdminQ/NVM responses.

## Dependencies and Integration Points
Includes allocation, register, and prototype headers. Depends on `i40e_allocate_dma_mem`, `i40e_allocate_virt_mem`, `i40e_free_*`, MMIO accessors `rd32`/`wr32`, AdminQ command descriptors from shared libie/i40e headers, firmware commands such as `i40e_aq_get_firmware_version`, NVM reads/resource release, debug tracing, and NVM update wait-event handling. It is called during PF probe/reset and by all i40e modules that issue firmware AdminQ commands.

## Risks
Queue lifecycle ordering is critical: freeing rings while firmware or another thread can access them can corrupt DMA memory. `i40e_init_asq` and `i40e_init_arq` free only descriptor rings on some buffer-allocation failures, so their allocation helper cleanup behavior is part of the safety contract. ASQ send supports async and postponed commands; invalid combinations or missing tail bumps can strand descriptors. The command buffer size must not exceed preallocated ASQ buffer size. The synchronous wait loops depend on hardware head movement rather than DD bits. `asq_last_status` is shared, hence the v2 API exists to return status under lock. ARQ event copying truncates to caller buffer length but restores the full firmware buffer, so callers must size buffers for expected events.

## Test Signals
Probe/init with valid and invalid queue sizes, ASQ/ARQ allocation failure unwind, register write/readback failure, firmware readiness retry, too-new API major rejection, capability-bit setting for XL710 and X722 firmware versions, NVM version reads, shutdown with live queues, ASQ direct and indirect commands, async and postponed command behavior, timeout/critical error handling, queue-full handling, callback invocation during send clean, v2 status race avoidance, ARQ no-event and event paths, ARQ error flag handling, pending count wraparound, NVM update wait events, and resume after PF reset are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq.h

## Purpose
Declares the i40e Admin Queue ring, command-detail, event, and top-level queue state structures, descriptor accessor macros, default alignment/sizing constants, firmware-error to POSIX-error conversion helper, and descriptor initialization prototype.

## Important APIs, Types, and Functions
`I40E_ADMINQ_DESC` indexes a descriptor ring, and `I40E_ADMINQ_DETAILS` indexes the ASQ command-detail array. `I40E_ADMINQ_DESC_ALIGNMENT`, `I40E_AQ_LARGE_BUF`, and `I40E_ASQ_CMD_TIMEOUT` define memory alignment, large-buffer threshold, and synchronous command timeout. `struct i40e_adminq_ring` stores descriptor DMA memory, command/event buffer metadata, per-descriptor DMA buffer arrays, count, receive buffer length, and ring indices. `struct i40e_asq_cmd_details` carries callback, cookie, flag masks, async/postpone controls, and optional writeback descriptor. `struct i40e_arq_event_info` is the caller-facing event container. `struct i40e_adminq_info` owns ASQ/ARQ rings, sizes, firmware/API versions, mutexes, and last statuses. `i40e_aq_rc_to_posix` maps firmware AQ return codes to Linux errors. `i40e_fill_default_direct_cmd_desc` initializes a direct command descriptor.

## Control Flow
The header has only inline control flow in `i40e_aq_rc_to_posix`, which bounds-checks the firmware return code and maps it through a static table. Runtime AdminQ behavior is implemented in `i40e_adminq.c`.

## State and Persistence Behavior
The declared structs define long-lived AdminQ state inside `struct i40e_hw`. Descriptor rings and command/event buffers are DMA-visible to firmware and persist for the lifetime of the initialized AdminQ. Mutexes serialize ASQ sends and ARQ event cleaning. Last-status fields preserve the most recent firmware return values but can race if read outside the locked v2 send path.

## Dependencies and Integration Points
Includes Linux mutex support, i40e allocation helpers, and AdminQ command descriptor definitions. It is consumed by AdminQ C code, firmware command wrappers in common/prototype code, and PF lifecycle code that initializes/shuts down firmware communication.

## Risks
The ring accessor macros assume descriptor and detail buffers are allocated and typed exactly as expected. Alignment must remain compatible with hardware DMA requirements. The POSIX mapping table must stay synchronized with `enum libie_aq_err`; unknown codes map to `-ERANGE`. Async/postpone fields in `i40e_asq_cmd_details` are subtle because callers control whether tail is rung and whether completion is waited for.

## Test Signals
Compile all AdminQ users, verify descriptor alignment, ASQ/ARQ ring index access, firmware error mappings including out-of-range codes, direct descriptor initialization, async/postpone command callers, and lockdep coverage for ASQ/ARQ mutex-protected access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq.h -->
