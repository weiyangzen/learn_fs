# subset-b-004502 Research

This grouped report covers the requested Intel Ethernet VF and common-library source files. Each source file section is bounded by the exact reconciliation markers required for splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ixgbevf_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ixgbevf_main.c

## Purpose
`ixgbevf_main.c` is the Linux PCI/netdev driver body for Intel 10GbE virtual functions. It binds PCI VF IDs to hardware operation tables, manages net_device lifecycle, configures MSI-X vectors, allocates Tx/Rx/XDP rings, handles NAPI polling, implements transmit and receive datapaths, and coordinates PF/VF mailbox-driven reset, link, VLAN, multicast, MTU, RSS, and feature negotiation.

## Important APIs, Types, and Functions
- Module and PCI integration: `ixgbevf_pci_tbl`, `ixgbevf_driver`, `ixgbevf_init_module()`, `ixgbevf_exit_module()`, `ixgbevf_probe()`, `ixgbevf_remove()`, PM callbacks, and PCI error recovery callbacks.
- Netdev operations: `ixgbevf_open()`, `ixgbevf_close()`, `ixgbevf_xmit_frame()`, `ixgbevf_set_rx_mode()`, `ixgbevf_get_stats()`, `ixgbevf_set_mac()`, `ixgbevf_change_mtu()`, VLAN add/remove, feature checks, and `ndo_bpf` XDP setup.
- Datapath: `ixgbevf_clean_tx_irq()`, `ixgbevf_clean_rx_irq()`, `ixgbevf_poll()`, `ixgbevf_tx_map()`, `ixgbevf_tso()`, `ixgbevf_tx_csum()`, `ixgbevf_xmit_xdp_ring()`, and page-backed Rx buffer helpers.
- Resource management: `ixgbevf_setup_*_resources()`, `ixgbevf_free_*_resources()`, q-vector allocation/free, MSI-X request/free, interrupt enable/disable, and ring configure functions.
- Service path: `ixgbevf_service_timer()`, `ixgbevf_service_task()`, reset, queue-reset, watchdog link update, stats update, and Tx hang detection.

## Control Flow
Probe enables PCI, sets 64-bit DMA, requests BARs, allocates a multi-queue Ethernet device, maps BAR0, installs netdev and ethtool ops, copies MAC and mailbox ops from the board info table, performs software init and VF reset/API negotiation, configures features/MTU bounds, initializes a service timer/work item, allocates MSI-X/q-vector topology, registers the netdev, and initializes optional IPsec offload.

Open allocates Tx and Rx descriptor rings, configures PF-mediated Rx mode/VLAN/IPsec state, configures hardware rings, requests MSI-X IRQs, publishes real queue counts, then calls `ixgbevf_up_complete()` to program IVAR/EITR, set RAR, enable NAPI and interrupts, start Tx queues, snapshot counters, and arm the service timer. Close and suspend reverse this: down the queues, disable interrupts, stop NAPI/timer, reset, clean rings, free IRQs, and release descriptors.

NAPI polling first cleans all Tx rings on a q-vector, then distributes Rx budget over Rx rings. Rx processing refills descriptors in batches, prepares an `xdp_buff`, runs an attached XDP program before SKB construction, handles XDP_TX by posting to a paired XDP Tx ring, builds or constructs SKBs for stack delivery, filters VEPA-reflected multicast/broadcast, applies checksum/hash/VLAN/IPsec metadata, and submits via GRO. Tx maps SKB header and fragments into advanced descriptors, emits context descriptors for TSO/checksum/IPsec/VLAN, handles DMA unwind on map failure, and stops/wakes subqueues based on descriptor pressure.

## State and Persistence Behavior
Persistent driver state is held in `struct ixgbevf_adapter`, `struct ixgbe_hw`, ring arrays, q-vectors, `active_vlans`, RSS key/indirection table, hardware counter baselines, `pf_features`, link state, XDP program pointer, and state bit flags such as `__IXGBEVF_DOWN`, `__IXGBEVF_RESETTING`, `__IXGBEVF_REMOVING`, `__IXGBEVF_SERVICE_SCHED`, and reset request bits. Hardware state persists in VF registers, PF mailbox configuration, descriptor DMA memory, and PF-owned VF policy. Statistics are accumulated across reset by saving base and saved-reset counters. The module has one global workqueue.

## Dependencies and Integration Points
The file depends on Linux PCI, netdev, NAPI, BPF/XDP, DMA mapping, page allocation, VLAN, GRO, xfrm/IPsec conditionals, ethtool hooks, and the `ixgbevf` hardware/mailbox abstractions from local headers. Its core integration boundary is the PF over mailbox operations in `vf.c`/`mbx.c`; most privileged settings are requests to the PF rather than direct VF hardware writes. XDP setup changes queue topology because the hardware requires separate Tx resources for XDP_TX.

## Risks and Edge Cases
- Mailbox failures or PF reset state can leave `adapter_stopped` true and prevent open.
- Queue topology is rebuilt for XDP transitions and DCB changes; failures must not leave stale q-vectors or published queue counts.
- Rx page reuse relies on page reference bias, DMA sync discipline, and page-size-dependent offsets.
- Tx hang detection intentionally requires two checks, but false positives still schedule disruptive resets.
- `ixgbevf_clean_rx_ring()` assumes populated `rx_buffer_info` entries between `next_to_clean` and `next_to_alloc` are valid DMA mappings.
- XDP disallows MTU changes and validates frame size against current ring buffers; missing this would overrun Rx buffers.
- PCI removal is detected via failed MMIO reads and schedules service cleanup; any path touching MMIO after removal must honor `IXGBE_REMOVED`.

## Test Signals
Useful signals include probe/open/close under PF reset and normal PF states, MSI-X allocation failure, mailbox API downgrade, link up/down watchdog, Tx hang reset, MTU and XDP attach/detach transitions, VLAN add/remove restoration, multicast/promisc mode changes, RSS queue count and RETA setup, suspend/resume, PCI error recovery, RX checksum/hash/VLAN metadata, XDP_DROP/PASS/TX behavior, DMA mapping failure injection, and stats continuity across reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ixgbevf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/mbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/mbx.c

## Purpose
`mbx.c` implements the VF side of the ixgbe PF/VF mailbox transport. It provides polling, status-bit handling, mailbox lock ownership, message read/write, legacy and newer mailbox semantics, stats accounting, and public wrappers used by VF hardware operations.

## Important APIs, Types, and Functions
- Public wrappers: `ixgbevf_poll_mbx()` waits for a PF message then reads it; `ixgbevf_write_mbx()` writes a VF message and waits for PF ACK.
- Operation tables: `ixgbevf_mbx_ops` and `ixgbevf_mbx_ops_legacy` fill `struct ixgbe_mbx_operations`.
- Internal helpers: `ixgbevf_poll_for_msg()`, `ixgbevf_poll_for_ack()`, `ixgbevf_read_mailbox_vf()`, clear/check helpers, `ixgbevf_obtain_mbx_lock_vf()`, release helpers, and legacy/current read/write implementations.

## Control Flow
Current write obtains VF ownership (`VFU`), clears stale PF status/ACK bits, writes up to 16 dwords to `VFMBMEM`, increments Tx stats, sets `REQ`, and polls for ACK before releasing ownership. Current read checks PF status, clears it, copies dwords from `VFMBMEM`, writes `ACK`, and increments Rx stats. Legacy write/read use older ownership and ACK behavior, including no-op release for legacy.

## State and Persistence Behavior
State is stored in `hw->mbx`: timeout, delay, mailbox size, cached `vf_mailbox` read-to-clear bits, operation table, and stats (`msgs_tx`, `msgs_rx`, `reqs`, `acks`, `rsts`). The cached mailbox preserves read-to-clear status bits so separate check/clear operations do not lose PF notifications.

## Dependencies and Integration Points
The code depends on mailbox register definitions from `mbx.h`, MMIO helpers from `vf.h`/`ixgbevf_main.c`, and delay functions. `vf.c` uses these wrappers for API negotiation, reset, link state, queue discovery, VLAN, MAC, multicast, and feature requests. `ixgbevf_main.c` serializes most calls with `adapter->mbx_lock`.

## Risks and Edge Cases
- Calls fail with `IXGBE_ERR_CONFIG` when timeout or required ops are unset.
- Message sizes larger than mailbox size are rejected by `ixgbevf_write_mbx()` and clipped by `ixgbevf_poll_mbx()`.
- Lock acquisition can time out if PF/VF ownership bits do not settle.
- Stats can double count some read-to-clear flows if check and clear are both used in close succession.
- Correct operation depends on matching PF firmware/driver expectations for legacy versus ESX/new mailbox ops.

## Test Signals
Exercise successful write/ACK/read, timeout without PF response, stale ACK/status clearing, reset indication handling, lock contention, oversized message rejection, legacy mailbox path, and transition from legacy to current ops after feature negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/mbx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/mbx.h

## Purpose
`mbx.h` defines the ixgbe PF/VF mailbox register offsets, ownership/status bits, mailbox message result bits, API revision enum, command IDs, response indices, and default polling timing constants.

## Important APIs, Types, and Constants
- Mailbox size and register offsets: `IXGBE_VFMAILBOX_SIZE`, `IXGBE_VFMAILBOX`, `IXGBE_VFMBMEM`, PF mailbox equivalents.
- VF/PF ownership and status bits: `REQ`, `ACK`, `VFU`, `PFU`, `PFSTS`, `PFACK`, `RSTI`, `RSTD`, and read-to-clear mask.
- Message result bits: `IXGBE_VT_MSGTYPE_SUCCESS`, `FAILURE`, `CTS`, and `IXGBE_VT_MSGINFO_*`.
- `enum ixgbe_pfvf_api_rev` captures API versions 1.0 through 1.7 and unknown.
- Command IDs include reset, set MAC/multicast/VLAN/LPE/MACVLAN, API negotiate, queue query, RETA/RSS key, xcast mode, IPsec add/delete, link-state queries, and feature negotiation.

## Control Flow
This header is declarative. Runtime code composes `msgbuf[0]` from command IDs plus result/info bits, then interprets PF replies by masking `CTS` and checking success/failure. API version checks in `vf.c` gate availability of later commands.

## State and Persistence Behavior
No state is stored here, but values define the ABI between VF and PF. The enum notes that existing API numbers must not change and new versions must append at the end, making it a persistent compatibility contract.

## Dependencies and Integration Points
Included by `vf.h` and `mbx.c`; used by `vf.c` and `ixgbevf_main.c` for all PF-mediated operations. The constants must match PF driver and firmware behavior.

## Risks and Edge Cases
- Typo in comment (`exra`) is harmless but confirms this is a low-level ABI header where comments are not enforcement.
- Reordering API enum values would break compatibility.
- Command payload lengths are implicit and must be kept synchronized with users in `vf.c` and PF-side handlers.

## Test Signals
Build coverage should catch missing constants. Behavioral coverage should include API negotiation across all supported revisions, each mailbox command’s success/failure handling, and backward compatibility with older PF drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/mbx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/regs.h

## Purpose
`regs.h` centralizes VF-visible ixgbe register offsets and RSS control bit definitions used by the VF driver.

## Important APIs, Types, and Constants
It defines offsets/macros for VF control/status/link, interrupt cause/mask/throttle/IVAR, Rx and Tx descriptor ring base/length/head/tail/control registers, DCA controls, packet-split type, hardware counters, mailbox-flush read, and RSS registers (`VFMRQC`, `VFRSSRK`, `VFRETA`) plus RSS field bits.

## Control Flow
This file has no executable flow. It enables driver code to use `IXGBE_READ_REG()`/`IXGBE_WRITE_REG()` against symbolic offsets. Array-like macros compute queue register addresses from queue index.

## State and Persistence Behavior
No software state is stored here. The constants describe MMIO-backed device state that persists in hardware until reset or explicit writes.

## Dependencies and Integration Points
Included by `vf.h` and consumed heavily by `ixgbevf_main.c`, `vf.c`, and `mbx.c`. It is the common address contract for VF hardware access.

## Risks and Edge Cases
Incorrect offsets or queue-stride math would cause silent MMIO corruption. `IXGBE_WRITE_FLUSH()` reads `VFSTATUS`, which also participates in removal detection via failed reads in `ixgbevf_main.c`.

## Test Signals
Compile coverage, hardware smoke tests for queue enable/disable, interrupt masking, RSS programming, stats reads, and register-access behavior after PCI removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/vf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/vf.c

## Purpose
`vf.c` implements the hardware abstraction operations for ixgbe virtual functions. It translates driver requests into VF register operations and PF mailbox commands, with separate Hyper-V variants for environments where PF/VF communication is exposed differently.

## Important APIs, Types, and Functions
- Operation tables: `ixgbevf_mac_ops`, `ixgbevf_hv_mac_ops`, and exported `ixgbevf_info` instances per VF device family.
- Reset/init/stop/link: `ixgbevf_reset_hw_vf()`, `ixgbevf_hv_reset_hw_vf()`, `ixgbevf_init_hw_vf()`, `ixgbevf_stop_hw_vf()`, `ixgbevf_check_mac_link_vf()`, Hyper-V link checks, and `ixgbe_read_vflinks()`.
- PF-mediated configuration: set RAR/UC/multicast/VLAN/LPE/xcast mode, API negotiation, feature negotiation, PF link query, queue query, RETA query, and RSS key query.
- Public locked helpers: `ixgbevf_get_queues()`, `ixgbevf_get_reta_locked()`, and `ixgbevf_get_rss_key_locked()`.

## Control Flow
Reset stops adapter queues, resets API version and mailbox ops to legacy, writes `VFCTRL.RST`, waits for reset indication to clear, sends `IXGBE_VF_RESET`, polls for permanent MAC/multicast filter type, and updates `perm_addr`. API negotiation tries versions in the caller and stores the accepted version. Later mailbox functions construct command buffers, call write-then-read helper, clear `CTS`, and validate success/failure bits before updating outputs.

Link checking either asks E610/API 1.6+ PF for link state or reads `VFLINKS`, then verifies PF clear-to-send by reading the mailbox. Hyper-V variants avoid mailbox operations and mostly return `-EOPNOTSUPP`, except reset reads permanent MAC from PCI config space and RLPML writes Rx control directly.

## State and Persistence Behavior
This file mutates `hw->adapter_stopped`, `hw->api_version`, `hw->mac.addr`, `perm_addr`, `mc_filter_type`, queue maxima, `get_link_status`, and `hw->mbx` ops/timeouts. PF-accepted settings such as MAC, VLAN, multicast, xcast, link, and feature support persist in PF/VF device state.

## Dependencies and Integration Points
It depends on the mailbox transport, VF register macros, netdev multicast iteration, PCI config access for Hyper-V, and local driver structures. `ixgbevf_main.c` calls these ops under `mbx_lock` when changing netdev state or reconfiguring queues. API version gates must align with `mbx.h` command definitions and PF support.

## Risks and Edge Cases
- Reset may accept PF failure for unassigned MAC but leaves caller to assign random MAC.
- API-specific helpers return `-EOPNOTSUPP` for unsupported device/API combinations; callers must degrade cleanly.
- RETA/RSS key mailbox layout assumes 82599/X540 compression and a max of two queues in current driver use.
- Multicast programming truncates to 30 non-link-local entries.
- `ixgbevf_check_mac_link_vf()` sets `*link_up = !get_link_status`, so mailbox error paths can intentionally defer link-down reporting.

## Test Signals
Test PF reset in progress, successful and failed VF reset replies, API negotiation fallback, Hyper-V board IDs, VLAN/MAC/multicast/xcast permission failures, E610 PF link query, VFLINKS speed decode, queue query validation, RETA/RSS key permission and unsupported paths, and PF feature negotiation for IPsec/ESX mailbox.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/vf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/vf.h

## Purpose
`vf.h` defines the shared hardware model for ixgbevf: operation tables, MAC/mailbox state, hardware identity, VF stats, board info, MMIO access helpers, and exported helper prototypes.

## Important APIs, Types, and Functions
- `struct ixgbe_mac_operations` is the main hardware abstraction table used by the driver.
- `struct ixgbe_mac_info`, `struct ixgbe_mbx_operations`, `struct ixgbe_mbx_info`, and `struct ixgbe_hw` hold hardware and mailbox runtime state.
- `struct ixgbevf_hw_stats` stores base, last, current, and saved reset counters.
- `struct ixgbevf_info` maps PCI board IDs to MAC type and ops table.
- Inline MMIO helpers write/read registers and arrays, using `ixgbevf_read_reg()` for removal-aware reads.

## Control Flow
This header is structural. The driver copies operation tables into `hw->mac.ops` and `hw->mbx.ops`, then calls through those function pointers. Inline register writes skip removed devices by checking `hw_addr`.

## State and Persistence Behavior
The structs declared here are the central in-memory state for VF hardware, mailbox, stats, and board capabilities. `hw->back` points to `ixgbevf_adapter`, bridging generic hardware ops back to the Linux netdev driver.

## Dependencies and Integration Points
It includes Linux PCI, delay, interrupt, Ethernet and netdevice headers, plus local `defines.h`, `regs.h`, and `mbx.h`. It is included by low-level hardware, mailbox, and main driver files.

## Risks and Edge Cases
- Operation pointers must be initialized before use; mailbox wrappers explicitly reject missing ops.
- Register write helper does not report failure if device is removed.
- `IXGBE_REMOVED()` only checks null MMIO pointer, while failed read detection is implemented in `ixgbevf_read_reg()`.

## Test Signals
Build and sparse checks for function pointer signatures, register array address math, stats width handling, and removal-aware read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/vf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/Kconfig

## Purpose
`libeth/Kconfig` defines configuration symbols for the common Ethernet library and its XDP/XSk companion module.

## Important APIs, Types, and Symbols
`CONFIG_LIBETH` is a tristate common library, visible under `COMPILE_TEST`, and selects `PAGE_POOL`. `CONFIG_LIBETH_XDP` is a tristate XDP/XSk helper library, also visible under `COMPILE_TEST`, and selects `LIBETH`.

## Control Flow
There is no runtime flow. Kconfig selection determines which objects in the Makefile build and which namespaces/exported helpers are available to drivers.

## State and Persistence Behavior
No runtime state. Build configuration persists as kernel config and module availability.

## Dependencies and Integration Points
`LIBETH` underpins Intel Ethernet drivers that share hotpath helpers. `LIBETH_XDP` depends on `LIBETH` so XDP helpers can patch static calls into the base Tx completion path.

## Risks and Edge Cases
Because symbols are only prompt-visible for `COMPILE_TEST`, production drivers likely select them indirectly. Missing selects in a consumer driver would surface as unresolved symbols or missing helper availability.

## Test Signals
Kconfig dependency checks, allyesconfig/allmodconfig builds, and builds with `LIBETH_XDP=m` while `LIBETH=m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/Makefile

## Purpose
The `libeth` Makefile maps Kconfig symbols to kernel modules and object files.

## Important APIs, Types, and Symbols
`libeth.o` is built from `rx.o` and `tx.o` when `CONFIG_LIBETH` is enabled. `libeth_xdp.o` is built from `xdp.o` and `xsk.o` when `CONFIG_LIBETH_XDP` is enabled.

## Control Flow
No runtime flow. Build flow separates base Rx/Tx helpers from optional XDP/XSk infrastructure.

## State and Persistence Behavior
No runtime state; it controls module composition and exported symbol grouping.

## Dependencies and Integration Points
The separation matches code-level static-call attachment: base `tx.o` can exist without XDP code, while `xdp.o` module init attaches XDP completion operations.

## Risks and Edge Cases
Object split must stay synchronized with symbol namespaces. Moving helpers between base and XDP modules without updating exports/imports can break modular builds.

## Test Signals
Build `LIBETH=y/m`, `LIBETH_XDP=y/m`, and consumer drivers using only base helpers versus XDP helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/priv.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/priv.h

## Purpose
`priv.h` is the private bridge between base `libeth` and `libeth_xdp`. It declares XDP/XSk slowpath helpers and a small operation table used to attach/detach optional XDP support to base Tx completion.

## Important APIs, Types, and Functions
It declares `libeth_xsktmo_slow`, XSk return/exception helpers, `struct libeth_xdp_ops`, `libeth_attach_xdp()`, and inline `libeth_detach_xdp()`.

## Control Flow
At `libeth_xdp` module init, `xdp.c` calls `libeth_attach_xdp(&xdp_ops)` to update base static calls. At exit it calls `libeth_detach_xdp()`, passing null ops.

## State and Persistence Behavior
No direct state in the header. It exposes the attach API that mutates static-call targets in `tx.c`.

## Dependencies and Integration Points
Used by `tx.c`, `xdp.c`, and `xsk.c`. It intentionally avoids exposing these internals as public kernel API while allowing separate module composition.

## Risks and Edge Cases
The operations must remain valid for the lifetime of `libeth_xdp`; detach must happen before code unload. Signature drift between private declarations and XDP implementations would break builds.

## Test Signals
Module load/unload of `libeth_xdp`, base Tx completion with XDP module absent, and consumer cleanup of XDP SQEs while XDP support is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/rx.c

## Purpose
`libeth/rx.c` provides common receive buffer queue allocation/destruction and packet-type hash metadata helpers for Intel Ethernet drivers.

## Important APIs, Types, and Functions
- Exported queue helpers: `libeth_rx_fq_create()`, `libeth_rx_fq_destroy()`, and `libeth_rx_recycle_slow()`.
- Buffer sizing internals: MTU-based, truesize-based, and zero-copy/header-split page-pool parameter calculations.
- Packet-type helper: `libeth_rx_pt_gen_hash_type()` fills XDP RSS hash type bits from a parsed packet-type structure.

## Control Flow
`libeth_rx_fq_create()` builds `page_pool_params` from queue metadata, chooses normal or zero-copy/header-split sizing, creates a page pool, allocates FQEs, registers the pool with XDP, and publishes the pool/array. Error paths unwind in reverse. Destroy unregisters the XDP page pool, frees FQEs, and destroys the page pool.

## State and Persistence Behavior
The caller-owned `struct libeth_fq` receives `buf_len`, `truesize`, FQE array pointer, and page-pool pointer. Page-pool memory and XDP registration persist until destroy. Packet-type LUT entries can have `hash_type` generated at runtime.

## Dependencies and Integration Points
The file depends on Linux page_pool, XDP page-pool registration, netmem, NAPI, netdevice MTU, and public `net/libeth/rx.h`. Consumer drivers use it to standardize Rx queue memory sizing.

## Risks and Edge Cases
- Invalid FQE type or header-split combination returns `-EINVAL`.
- `roundup_pow_of_two()` and clamp behavior are sensitive to tiny or huge MTU/truesize values.
- Zero-copy path assumes separate header buffers account for stack overhead.
- Missing destroy would leak registered page pools and FQE arrays.

## Test Signals
Create/destroy for MTU, short, header, XDP and non-XDP queues; invalid queue types; low-memory allocation failures; MTU boundary values; XDP page-pool registration failure; hash type generation for representative packet types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/tx.c

## Purpose
`libeth/tx.c` provides base Tx completion for normal and XDP SQEs, with optional XDP/XSk completion targets patched in by the XDP module.

## Important APIs, Types, and Functions
`libeth_tx_complete_any()` completes either normal SQEs or XDP SQEs. `libeth_attach_xdp()` updates static-call targets for XDP bulk returns and XSk buffer frees. Two `DEFINE_STATIC_CALL_NULL` entries hold optional callbacks.

## Control Flow
Completion checks `sqe->type`: XDP types go through `__libeth_xdp_complete_tx()` with current static-call targets; normal entries call `libeth_tx_complete()`. Attach updates both static calls to XDP ops or null.

## State and Persistence Behavior
Static-call target state persists module-wide and changes when `libeth_xdp` loads/unloads. SQE state is consumed by completion helpers owned by public libeth headers.

## Dependencies and Integration Points
Depends on `net/libeth/xdp.h` and private attach declarations. It is the base module side of the optional XDP module split.

## Risks and Edge Cases
If `libeth_xdp` is absent, XDP SQEs cannot be fully handled; the comment explicitly notes this. Attach/detach ordering must avoid stale function targets during module unload.

## Test Signals
Tx completion with normal SQEs, XDP SQEs before/after XDP module load, module unload cleanup, and static-call target updates under modular builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/xdp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/xdp.c

## Purpose
`libeth/xdp.c` implements common XDP infrastructure: shared XDPSQ locking, cleanup timer setup, XDP_TX exception handling, `ndo_xdp_xmit` unwind helpers, XDP buffer stash/return, fragment attachment, program exception handling, bulk frame returns, XDP queue thresholds, and netdev XDP feature advertising.

## Important APIs, Types, and Functions
Key exports include `libeth_xdpsq_share`, `__libeth_xdpsq_get/put/lock/unlock()`, `libeth_xdpsq_init_timer()`, `libeth_xdp_tx_exception()`, `libeth_xdp_xmit_return_bulk()`, `libeth_xdp_load_stash()`, `libeth_xdp_save_stash()`, `__libeth_xdp_return_stash()`, `libeth_xdp_return_buff_slow()`, `libeth_xdp_buff_add_frag()`, `libeth_xdp_prog_exception()`, `libeth_xdp_return_buff_bulk()`, `libeth_xdp_queue_threshold()`, `__libeth_xdp_set_features()`, and `libeth_xdp_set_redirect()`.

## Control Flow
XDPSQ share get/put toggles a static key and initializes a lock when sharing is needed. XDP_TX exception handling either preserves unsent frames for retry or drops/returns remaining frames via XSk, native XDP, or ndo_xmit-specific return helpers. Rx helpers convert between an on-stack `libeth_xdp_buff` and a persistent stash, attach page frags, and route invalid actions or redirect failures through trace/free logic. Module init attaches XDP ops to base `libeth`; exit detaches them.

## State and Persistence Behavior
State includes the global static key for XDPSQ sharing, per-queue lock/timer/stash objects owned by consumers, netdev XDP feature fields, and static-call attachment into `libeth_tx_complete_any()`.

## Dependencies and Integration Points
The file integrates Linux XDP, BPF tracepoints, XSk helpers from `xsk.c`, netmem, skb shared-info fragments, netdev feature APIs, and base `libeth` static calls. Consumer drivers use these helpers to share common XDP hotpath mechanics while retaining hardware-specific descriptor programming.

## Risks and Edge Cases
- `libeth_xdp_queue_threshold(0)` would produce nonsensical threshold behavior; callers should pass real descriptor counts.
- Exception helpers must not double-free multi-buffer frames; `FIRST` and `MULTI` flags drive ownership.
- XSk redirect `-ENOBUFS` with need-wakeup changes verdict to aborted to stop polling.
- Feature advertisement must match actual driver support for zerocopy and scatter-gather.

## Test Signals
XDP_TX partial send/drop/retry paths, multi-frag return, invalid XDP action trace, redirect failure with and without XSk need-wakeup, stash save/load/return, queue threshold for power-of-two and non-power-of-two counts, netdev feature flags for XSK zerocopy, and module load/unload attach behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/xsk.c

## Purpose
`libeth/xsk.c` implements common AF_XDP/XSk support for libeth XDP users: XSk buffer free/fragment helpers, XSk program slowpath verdict handling, fill queue setup, NAPI wakeup via call-single-data, and XSk pool DMA mapping.

## Important APIs, Types, and Functions
Exports include `libeth_xsk_buff_free_slow()`, `libeth_xsk_buff_add_frag()`, `libeth_xsk_buff_stats_frags()`, `__libeth_xsk_run_prog_slow()`, `libeth_xskfq_create()`, `libeth_xskfq_destroy()`, `libeth_xsk_init_wakeup()`, `libeth_xsk_wakeup()`, and `libeth_xsk_setup_pool()`. It also defines `libeth_xsktmo_slow` for checksum metadata requests.

## Control Flow
XSk program slowpath handles DROP by freeing, TX/PASS by returning corresponding libeth verdicts, and all other cases by delegating to `libeth_xdp_prog_exception()`. Fill queue creation allocates FQEs, initializes pending count, threshold, frame length, and truesize from the XSk pool. Wakeup first marks scheduled NAPI as missed, then schedules on queue-selected CPU via IPI or local NAPI scheduling. Pool setup maps or unmaps DMA for the queue's XSk pool.

## State and Persistence Behavior
`struct libeth_xskfq` stores FQE array, pending count, threshold, buffer length, truesize, pool, NUMA node, and descriptor count. Wakeup state is stored in caller-owned `call_single_data_t`. DMA mapping persists until pool disable.

## Dependencies and Integration Points
Depends on `net/libeth/xsk.h`, AF_XDP core APIs, NAPI scheduling, SMP call-single-data, and XDP helpers from `xdp.c`. Consumer drivers call this from `ndo_xsk_wakeup`, queue setup, and XSk Rx processing.

## Risks and Edge Cases
- `libeth_xsk_wakeup()` maps queue IDs modulo CPU count when out of range; this is robust but may not match queue affinity.
- Pool setup returns `-EINVAL` if no pool exists for a queue.
- Fragment attach frees both head and frag on failure, so callers must treat null as full ownership loss.
- DMA map/unmap must pair exactly with XSk pool enable/disable.

## Test Signals
XSk pool enable/disable, missing pool path, wakeup from same and remote CPU, queue ID beyond CPU count, fill queue allocation failure, fragmented XSk packets, XDP_DROP/TX/PASS/REDIRECT-failure verdicts, and metadata checksum request behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/Kconfig

## Purpose
`libie/Kconfig` defines Intel Ethernet common-library symbols layered above `libeth`, plus optional admin queue and firmware logging support.

## Important APIs, Types, and Symbols
`CONFIG_LIBIE` is a tristate that selects `LIBETH`. `CONFIG_LIBIE_ADMINQ` provides admin queue helper functions. `CONFIG_LIBIE_FWLOG` selects `LIBIE_ADMINQ` and enables firmware logging support with debugfs configuration and admin queue communication.

## Control Flow
There is no runtime flow. Kconfig symbol selection controls which modules and exported namespaces are built.

## State and Persistence Behavior
No runtime state. Build configuration determines module presence.

## Dependencies and Integration Points
`LIBIE` builds on `LIBETH`; `LIBIE_FWLOG` depends on admin queue helper availability. Intel Ethernet drivers can select these symbols for packet type tables, admin queue error strings, and firmware log debugfs support.

## Risks and Edge Cases
Because these are non-prompt tristates, consumer drivers must select the correct symbols. Missing `LIBIE_ADMINQ` for fwlog would break admin queue string/helper dependencies, so `LIBIE_FWLOG` selects it explicitly.

## Test Signals
Kconfig dependency validation and modular builds for `LIBIE`, `LIBIE_ADMINQ`, and `LIBIE_FWLOG` independently and as selected by consumer drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/Makefile

## Purpose
The `libie` Makefile maps Intel Ethernet common-library Kconfig symbols to module objects.

## Important APIs, Types, and Symbols
`libie.o` contains `rx.o`; `libie_adminq.o` contains `adminq.o`; `libie_fwlog.o` contains `fwlog.o`.

## Control Flow
No runtime flow. The build split mirrors functional namespaces: base Intel Rx packet type table, admin queue helper, and firmware logging debugfs/adminq component.

## State and Persistence Behavior
No runtime state; affects module boundaries and symbol export namespaces.

## Dependencies and Integration Points
Matches Kconfig dependencies and module import namespaces used by source files.

## Risks and Edge Cases
Module object naming must stay consistent with exported symbol namespaces and consumer `MODULE_IMPORT_NS()` declarations.

## Test Signals
Allmodconfig/module builds and consumer driver link tests for each optional component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/adminq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/adminq.c

## Purpose
`adminq.c` provides a small admin queue error-code-to-string helper for Intel Ethernet drivers.

## Important APIs, Types, and Functions
`libie_aq_str(enum libie_aq_err err)` returns a symbolic string for known `LIBIE_AQ_RC_*` codes and falls back to `LIBIE_AQ_RC_UNKNOWN`. It is exported in the `LIBIE_ADMINQ` namespace.

## Control Flow
The function bounds-checks the enum and verifies that a string exists at that index; invalid or sparse values map to the final unknown entry.

## State and Persistence Behavior
The only state is a static const string table. No mutable runtime state.

## Dependencies and Integration Points
Depends on `<linux/net/intel/libie/adminq.h>` for the enum. Used by drivers or libraries that need stable admin queue diagnostics.

## Risks and Edge Cases
The array must remain synchronized with enum values. Sparse enum values are handled by null-entry fallback if the table has holes.

## Test Signals
Unit-style checks for each known admin queue code, out-of-range values, and sparse/unassigned values returning unknown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/adminq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/fwlog.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/fwlog.c

## Purpose
`fwlog.c` implements Intel firmware logging support over admin queue commands with a debugfs user interface. It detects firmware support, reads and writes logging configuration, registers/unregisters for ARQ log events, stores log event payloads in a ring of 4K buffers, and exposes controls for module levels, message count, enable state, log buffer size, and data dumping.

## Important APIs, Types, and Functions
- Public exports: `libie_fwlog_init()`, `libie_fwlog_deinit()`, `libie_get_fwlog_data()`, and `libie_fwlog_reregister()`.
- Admin queue commands: `libie_aq_fwlog_set()`, `libie_aq_fwlog_register()`, and `libie_aq_fwlog_get()`.
- Config/register helpers: `libie_fwlog_set()`, `libie_fwlog_register()`, `libie_fwlog_unregister()`, `libie_fwlog_set_supported()`.
- Ring helpers: empty/full tests, increment, allocate/free buffers, and `libie_fwlog_realloc_rings()`.
- Debugfs file operations for per-module log level, `nr_messages`, `enable`, `log_size`, and `data`.

## Control Flow
Init copies an API callback bundle, probes support by querying firmware, reads current config, allocates default ring metadata and backing buffers, and creates debugfs files. Enabling via debugfs updates ARQ option bits, sends config to firmware, then registers for ARQ events; disabling reverses registration. Incoming ARQ data is copied by `libie_get_fwlog_data()` to the tail buffer and advances head on overwrite. Deinit disables ARQ logging, removes tracked module dentries, unregisters, and frees ring buffers.

## State and Persistence Behavior
Mutable state lives in caller-owned `struct libie_fwlog`: firmware support flag, copied API callbacks/private pointer, PCI device, current `cfg`, debugfs root/module dentries, and ring metadata (`rings`, `size`, `index`, `head`, `tail`). Firmware logging configuration persists in device firmware until changed or disabled during deinit. Debugfs writes mutate cached config and sometimes firmware state.

## Dependencies and Integration Points
The file depends on debugfs, seq_file/simple file ops, PCI device logging, admin queue descriptor layouts from fwlog headers, vmalloc/kzalloc helpers, and a driver-supplied `send_cmd` callback. It exports namespace `LIBIE_FWLOG` and uses admin queue opcodes for firmware communication.

## Risks and Edge Cases
- No explicit locking protects debugfs readers/writers versus ARQ `libie_get_fwlog_data()` ring updates, so concurrency relies on higher-level serialization or tolerance of races.
- `libie_debugfs_data_read()` does not copy a buffer when `cur_buf_len >= count`; small user buffers may see zero progress.
- Log size cannot change while registered; the write path enforces this.
- Ring size is assumed power-of-two because increment masks with `size - 1`.
- `libie_get_fwlog_data()` clears `PAGE_SIZE` bytes even though ring buffers are sized by `LIBIE_AQ_MAX_BUF_LEN`; this must match expected max buffer size.
- Init support probing allocates temporary config and treats any query error as unsupported.

## Test Signals
Firmware unsupported query, init allocation failures, config get/set/register failures, debugfs module level writes including `all`, invalid log level/size/message count inputs, enable/disable transitions, deinit while registered, ring overwrite behavior, data reads with varying user buffer sizes, log size reallocation, ARQ event ingestion, and reset reregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/fwlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/rx.c

## Purpose
`libie/rx.c` provides Intel Ethernet packet-type lookup data, mapping i40e/ice/iavf-style hardware packet type IDs into `struct libeth_rx_pt` fields and XDP RSS hash type bits.

## Important APIs, Types, and Functions
The key export is `libie_rx_pt_lut[LIBIE_RX_PT_NUM]`. Macro families such as `LIBIE_RX_PT`, `LIBIE_RX_PT_IP`, `LIBIE_RX_PT_IP_TUN`, and `LIBIE_RX_PT_IP_GRE` generate table entries for L2, timesync, IPv4/IPv6, fragmented, tunneled, GRE/NAT, and inner protocol cases.

## Control Flow
There is no runtime control flow beyond table lookup by consumers. The preprocessor expands packet-type patterns into a static table ordered according to hardware packet type numbering.

## State and Persistence Behavior
Static const lookup table only. Consumers treat it as immutable runtime metadata.

## Dependencies and Integration Points
Depends on `linux/net/intel/libie/rx.h` and `libeth_rx_pt` definitions. Imports `LIBETH` namespace. Used by Intel Ethernet drivers to convert hardware ptype numbers into parsed metadata in O(1), including XDP hash reporting.

## Risks and Edge Cases
- Table order must exactly match hardware ptype numbering; macro expansion mistakes cause wrong checksum/hash/protocol behavior.
- `LIBIE_RX_PT_UNUSED` entries intentionally represent unsupported or reserved ptypes.
- Supplemental XDP RSS macros fill gaps where token concatenation would not match XDP constants.

## Test Signals
Compile-time table size checks, known ptype-to-metadata fixtures for L2/IPv4/IPv6/tunnel/GRE/fragment/TCP/UDP/SCTP/ICMP/timesync, and consumer receive tests verifying RSS hash type classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/rx.c -->
