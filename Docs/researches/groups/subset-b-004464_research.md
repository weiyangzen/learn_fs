# subset-b-004464 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ptp.c

## Purpose
Implements Precision Time Protocol support for the Intel IAVF virtual function driver when `CONFIG_PTP_1588_CLOCK` is enabled. Because the VF does not directly own the physical hardware clock, the file exposes a PTP clock to userspace by sending virtchnl requests to the PF, caches PHC time for timestamp extension, and controls Rx hardware timestamp reporting on Rx rings.

## Important APIs, Types, and Functions
The exported entry points are `iavf_ptp_init`, `iavf_ptp_release`, `iavf_ptp_process_caps`, `iavf_ptp_cap_supported`, `iavf_ptp_set_ts_config`, and `iavf_ptp_extend_32b_timestamp`. Internal helpers include `iavf_ptp_set_timestamp_mode`, `iavf_send_phc_read`, `iavf_read_phc_indirect`, `iavf_ptp_gettimex64`, `iavf_ptp_register_clock`, `iavf_ptp_cache_phc_time`, and `iavf_ptp_do_aux_work`. `iavf_clock_to_adapter` maps `ptp_clock_info` back to `struct iavf_adapter`.

## Control Flow
Capability-gated initialization checks `VIRTCHNL_1588_PTP_CAP_READ_PHC`, registers a `ptp_clock_info`, points every active Rx ring at `adapter->ptp`, and schedules auxiliary PTP work. Userspace PHC reads call `gettimex64`, which queues `VIRTCHNL_OP_1588_PTP_GET_TIME`, waits up to one second on `phc_time_waitqueue`, and returns `cached_phc_time` after the virtchnl completion path fills it. Timestamp configuration accepts Rx timestamp filters, normalizes any supported Rx filter to `HWTSTAMP_FILTER_ALL`, rejects Tx timestamping, and flips `IAVF_TXRX_FLAGS_HW_TSTAMP` on all active Rx rings. Auxiliary work refreshes PHC time roughly twice per second, while `iavf_ptp_extend_32b_timestamp` combines cached 64-bit PHC time with 32-bit descriptor timestamps.

## State and Persistence
Persistent driver state lives in `adapter->ptp`: registered PTP clock pointer, `ptp_clock_info`, PF-reported capabilities, cached PHC nanoseconds, cache update jiffies, current `kernel_hwtstamp_config`, command queue, waitqueue, and `phc_time_ready`. Per-ring timestamp state is represented by `rx_ring->ptp` and `IAVF_TXRX_FLAGS_HW_TSTAMP`. No state is written to disk; hardware-visible changes are mediated by virtchnl messages and queue configuration.

## Dependencies and Integration Points
Depends on `iavf_ptp.h`, `iavf_types.h`, the kernel PTP clock API, virtchnl 1588 opcodes, watchdog/AQ scheduling through `adapter->aq_required`, and the completion logic in `iavf_virtchnl.c`. Rx timestamp delivery integrates with `iavf_txrx.c` flexible descriptor parsing, which calls `iavf_ptp_extend_32b_timestamp`. Netdev hardware timestamp ioctls enter through `iavf_main.c` and call `iavf_ptp_set_ts_config`.

## Risks
The indirect PHC read path can return `-EBUSY` if the PF response does not arrive within one second, so PHC reads are latency-sensitive to AdminQ health. Timestamp extension is only correct when cached PHC time is close to the descriptor event; stale auxiliary work or PF communication stalls can produce wrong 64-bit timestamps. Capability changes during reset must release or recreate the PTP clock without leaving queued commands, and Rx timestamp enabling touches ring flags without per-ring locking, relying on driver serialization around configuration. Tx hardware timestamping is explicitly unsupported.

## Test Signals
Useful signals include `ptp4l` or `phc2sys` PHC reads against a VF with PTP capability, `ethtool -T`, `hwtstamp_config` set/get for Rx filters, reset while PTP is enabled, PF capability loss and regain, AdminQ timeout injection for `GET_TIME`, Rx timestamp validation on flexible descriptors, and checking that timestamping is disabled after `iavf_ptp_release`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ptp.h

## Purpose
Declares the IAVF PTP interface used by the main driver, virtchnl control plane, and Tx/Rx data path. It also provides no-op or error stubs when PTP clock support is not compiled into the kernel.

## Important APIs, Types, and Functions
The header declares `iavf_ptp_init`, `iavf_ptp_release`, `iavf_ptp_process_caps`, `iavf_ptp_cap_supported`, `iavf_virtchnl_send_ptp_cmd`, `iavf_ptp_set_ts_config`, and `iavf_ptp_extend_32b_timestamp`. `IAVF_PTP_40B_TSTAMP_VALID` defines the valid bit used when extracting flexible Rx descriptor timestamp data.

## Control Flow
There is no runtime control flow beyond conditional compilation. With `CONFIG_PTP_1588_CLOCK`, callers bind to real implementations in `iavf_ptp.c` and `iavf_virtchnl.c`. Without it, initialization/release/capability processing are no-ops, capability checks return false, timestamp configuration returns failure, and timestamp extension returns zero.

## State and Persistence
The header owns no mutable state. It defines the compile-time contract that controls whether `adapter->ptp` state is active and whether virtchnl PTP commands can be sent.

## Dependencies and Integration Points
Includes `iavf_types.h` for `struct iavf_adapter` and PTP-related adapter state. It is included by PTP implementation, virtchnl code, main netdev setup, and Tx/Rx code that needs Rx timestamp extension.

## Risks
The stub `iavf_ptp_set_ts_config` returns `-1` instead of a symbolic errno, so callers should not depend on a specific disabled-PTP errno. Build coverage must ensure all call sites compile in both PTP-enabled and PTP-disabled configurations. The timestamp valid bit must match the hardware descriptor ABI used by `iavf_txrx.c`.

## Test Signals
Compile with and without `CONFIG_PTP_1588_CLOCK`, verify `ethtool -T` and hwtstamp operations report unavailable behavior without PTP, and check that Rx timestamp code is either inactive or correctly linked depending on the config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_register.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_register.h

## Purpose
Defines the VF-visible MMIO register offsets and bit masks used by the IAVF driver. These are the low-level hardware ABI for AdminQ rings, reset status, interrupt control, queue tails, RSS tables, and interrupt throttling registers.

## Important APIs, Types, and Functions
This file is macro-only. Key register families are `IAVF_VF_ARQ*` and `IAVF_VF_ATQ*` for Admin Receive/Transmit Queue base, head, tail, and length registers; `IAVF_VFGEN_RSTAT` for VF reset state; `IAVF_VFINT_DYN_CTL*`, `IAVF_VFINT_ICR*`, and `IAVF_VFINT_ITRN1` for interrupt control and ITR programming; `IAVF_QRX_TAIL1` and `IAVF_QTX_TAIL1` for Rx/Tx queue tails; and `IAVF_VFQF_HENA/HKEY/HLUT` for RSS hash enable, key, and lookup table registers.

## Control Flow
The header has no executable control flow. Other driver files compose these offsets with `rd32`, `wr32`, or `writel` operations. For example, `iavf_txrx.c` writes `IAVF_VFINT_DYN_CTLN1` to re-enable interrupts and force writebacks, and uses queue tail pointers derived from these register definitions.

## State and Persistence
State is hardware-resident: AdminQ indices and enable bits, interrupt enable/mask/ITR settings, queue tail producer indices, RSS key/LUT/hash enable registers, and reset status. The software persistence is only the set of constants compiled into the module.

## Dependencies and Integration Points
Uses `IAVF_MASK` from `iavf_type.h`. It is included by `iavf_type.h` and consequently reaches the AdminQ, interrupt, queue setup, RSS, and Tx/Rx paths. It must stay in sync with Intel VF hardware documentation and with PF/virtchnl expectations.

## Risks
Any incorrect offset or mask can break DMA queue operation, AdminQ communication, interrupt moderation, or RSS programming. Some indexed macros document limited hardware ranges, so callers must validate queue/vector indices elsewhere. Register reset-domain comments are informative but not enforced.

## Test Signals
Signals include successful VF probe and AdminQ initialization, queue enable/disable traffic tests, MSI-X interrupt delivery, adaptive ITR changes visible in interrupt rate behavior, RSS hash/LUT programming via ethtool, reset recovery, and register dumps matching expected VF offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_register.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_status.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_status.h

## Purpose
Defines the internal `enum iavf_status` error namespace used by IAVF hardware/AdminQ helpers before conversion to Linux errno values or diagnostic strings.

## Important APIs, Types, and Functions
The central type is `enum iavf_status`, with `IAVF_SUCCESS` as zero and negative driver-specific failures such as NVM, PHY, configuration, queue, AdminQ, timeout, unsupported, firmware API, and critical AdminQ errors. There are no functions in this header.

## Control Flow
No executable control flow is present. Callers return or switch on these values in lower-level AdminQ and hardware helper paths. `iavf_virtchnl.c` converts send failures with `iavf_status_to_errno` and logs names with `iavf_stat_str`.

## State and Persistence
The file owns no runtime state. The enum values are persistent ABI within the driver source and must remain coherent with status-to-string and status-to-errno translation tables elsewhere in the driver.

## Dependencies and Integration Points
Included by `iavf_type.h`, making it available to hardware structures, AdminQ code, and virtchnl send/receive handling. It also aligns conceptually with AdminQ status reporting from the shared Intel Ethernet code.

## Risks
Adding, renumbering, or deleting entries without updating conversion helpers can cause misleading logs or incorrect errno propagation. Because all failures are negative and not Linux errno values, callers must avoid returning them directly to kernel subsystems unless translated.

## Test Signals
Compile-time coverage for all status users, AdminQ failure injection, virtchnl send failure logging, timeout paths, and checks that user-visible netdev/ethtool operations receive Linux errno values rather than raw IAVF status codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_trace.h

## Purpose
Defines the IAVF tracepoint subsystem and trace events for Tx cleaning, Rx cleaning, and transmit submission/drop paths. It gives the driver low-overhead observability for queue and descriptor activity.

## Important APIs, Types, and Functions
The main macros are `iavf_trace(trace_name, args...)`, `iavf_trace_enabled(trace_name)`, and the tracepoint name builders. Event classes are `iavf_tx_template`, `iavf_rx_template`, and `iavf_xmit_template`. Concrete events include `iavf_clean_tx_irq`, `iavf_clean_tx_irq_unmap`, `iavf_clean_rx_irq`, `iavf_clean_rx_irq_rx`, `iavf_xmit_frame_ring`, and `iavf_xmit_frame_ring_drop`.

## Control Flow
The header follows Linux tracepoint conventions: it defines `TRACE_SYSTEM iavf`, uses the special `TRACE_HEADER_MULTI_READ` include guard pattern, declares event classes and `DEFINE_EVENT` instances, then sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` before including `trace/define_trace.h`. Runtime call sites in `iavf_txrx.c` invoke `iavf_trace(...)` around descriptor processing and packet submission/drop.

## State and Persistence
Tracepoints do not persist driver state. When enabled, each event captures pointers to the ring, descriptor, skb or Tx buffer, plus the netdev name string. Trace enablement is controlled by the kernel tracing subsystem.

## Dependencies and Integration Points
Depends on `<linux/tracepoint.h>` and on IAVF data structures being visible to call sites. It integrates with ftrace/perf/BPF tooling and is included by `iavf_txrx.c`. The file name/path setup is necessary because the trace header lives in the driver directory rather than the kernel trace include directory.

## Risks
Tracepoint ABI changes can disrupt scripts or BPF tools that consume these events. Captured pointers are diagnostic only and must not be dereferenced outside safe tracing contexts. The event field order intentionally matches prototypes for tooling compatibility, so reordering fields has observability risk.

## Test Signals
Build with tracing enabled, verify trace events appear under the `iavf` subsystem, enable each event during Tx/Rx traffic, confirm drop events fire for offload setup failures, and check that module unload/reload works without trace definition conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_txrx.c

## Purpose
Implements the IAVF data path: Tx/Rx descriptor allocation and cleanup, NAPI polling, adaptive interrupt moderation, Rx buffer recycling, Rx metadata extraction, checksum/hash/VLAN/timestamp reporting, Tx offload setup, DMA mapping, and netdev transmit entry points.

## Important APIs, Types, and Functions
Public functions are `iavf_setup_tx_descriptors`, `iavf_free_tx_resources`, `iavf_setup_rx_descriptors`, `iavf_free_rx_resources`, `iavf_alloc_rx_buffers`, `iavf_napi_poll`, `iavf_detect_recover_hung`, `__iavf_chk_linearize`, `__iavf_maybe_stop_tx`, and `iavf_xmit_frame`. Important internal paths are `iavf_clean_tx_irq`, `iavf_clean_rx_irq`, `iavf_update_itr`, `iavf_update_enable_itr`, `iavf_process_skb_fields`, `iavf_flex_rx_tstamp`, `iavf_tso`, `iavf_tx_enable_csum`, `iavf_create_tx_ctx`, `iavf_tx_map`, and `iavf_xmit_frame_ring`.

## Control Flow
Setup allocates coherent descriptor rings and software side arrays; Rx setup uses `libeth_rx_fq_create` and page-pool backed buffers. NAPI first cleans Tx completions, then divides Rx budget across ring pairs, cleans completed Rx descriptors until budget or DD exhaustion, replenishes buffers in batches, and re-enables interrupts with updated ITR when polling completes. Rx processing validates descriptor done bits, extracts legacy or flexible descriptor fields, builds or extends an skb from page-pool buffers, drops MAC-error frames, records checksum/hash/VLAN/protocol metadata, optionally extends flexible Rx timestamps through PTP cached time, and submits packets through GRO. Tx processing pads too-short frames, counts descriptors, linearizes unsupported fragment layouts, stops queues when space is low, prepares VLAN/TSO/checksum/tunnel context descriptors, maps skb head and frags to DMA descriptors, marks the EOP descriptor as `next_to_watch`, and rings the hardware tail when needed.

## State and Persistence
Per-ring state includes descriptor DMA memory, software Tx buffers or Rx frame queue entries, `next_to_use`, `next_to_clean`, queue stats, `prev_pkt_ctr`, ITR settings, queue shaper state, Rx descriptor format, VLAN tag location flags, timestamp flag, page-pool state, and optional partial skb for multi-descriptor Rx packets. Per-vector state accumulates Tx/Rx packets and bytes for adaptive ITR and stores current/target interrupt throttling values. Netdev queues persist stop/wake state and byte queue accounting. Hardware-visible state is descriptor content and queue tail writes; no disk persistence exists.

## Dependencies and Integration Points
Depends on `iavf.h`, `iavf_trace.h`, `iavf_prototype.h`, `iavf_ptp.h`, Intel `libeth`/`libie` Rx helpers, Linux DMA mapping, NAPI/GRO, skb checksum and GSO APIs, VLAN offload APIs, MSI-X interrupt control registers from `iavf_register.h`, and descriptor layout from `iavf_type.h`. Virtchnl queue configuration in `iavf_virtchnl.c` supplies ring DMA addresses, descriptor format, Rx flags, and queue enablement. PTP Rx timestamp support depends on negotiated capabilities and flexible descriptors.

## Risks
The highest-risk areas are DMA mapping unwind on partial Tx failure, descriptor index wraparound, memory barriers around descriptor ownership, queue stop/wake races, adaptive ITR tuning under CPU affinity changes, Rx partial-packet state across NAPI exits, descriptor-format mismatches, stale PHC cache causing bad timestamps, and VLAN tag-location flag mismatches with PF configuration. Tx offload code must handle encapsulation, GSO partial, unsupported L4 protocols, and hardware limits of eight DMA buffers per packet.

## Test Signals
Core signals are sustained TCP/UDP traffic across MTUs and queue counts, GSO/TSO/USO and tunneled checksum tests, VLAN insertion/stripping for C-TAG and S-TAG, RSS hash reporting, Rx checksum error accounting, NAPI budget and netpoll behavior, interrupt rate behavior under small-packet and bulk traffic, Tx hang recovery, DMA mapping failure injection, page-pool allocation failure paths, flexible versus legacy Rx descriptor modes, and Rx hardware timestamp validation with PTP enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_txrx.h

## Purpose
Defines the IAVF Tx/Rx data-path ABI used across the driver: interrupt moderation constants, RSS defaults, descriptor accounting helpers, Tx flags, per-ring/per-vector state structures, queue stats, and data-path function prototypes.

## Important APIs, Types, and Functions
Important types include `struct iavf_tx_buffer`, `struct iavf_queue_stats`, `struct iavf_tx_queue_stats`, `struct iavf_rx_queue_stats`, `struct iavf_ring`, and `struct iavf_ring_container`. Key macros and helpers include `IAVF_DESC_UNUSED` from `iavf_type.h`, `IAVF_RX_INCREMENT`, `IAVF_RX_NEXT_DESC`, `iavf_txd_use_count`, `iavf_xmit_descriptor_count`, `iavf_maybe_stop_tx`, `iavf_chk_linearize`, `txring_txq`, ITR conversion macros, Tx flag bit definitions, and default RSS hash masks. Function prototypes expose descriptor setup/free, Rx buffer allocation, NAPI poll, hung detection, linearization checks, and transmit entry points.

## Control Flow
Most code is declarative or inline. Descriptor-count helpers walk skb head/frags to estimate Tx descriptors. Stop helpers perform a fast unused-descriptor check before calling the slower queue-stop path. Linearization helpers enforce hardware scatter-gather limits, calling into the implementation only for complex TSO cases.

## State and Persistence
`struct iavf_ring` is the central persistent in-memory state for one Tx or Rx queue, including descriptor memory, DMA base, software buffer arrays, tail register pointer, counters, flags, queue index, count, current indices, descriptor format, stats, q_vector/VSI backreferences, RCU header, partial Rx skb, PTP pointer, Rx buffer sizing, and queue shaper data. `struct iavf_ring_container` persists per-interrupt aggregate traffic and ITR state.

## Dependencies and Integration Points
Depends on Linux netdevice/skbuff/page-pool concepts, Intel `libie` packet type definitions, descriptor definitions from `iavf_type.h`, and netdev queue APIs. Included by Tx/Rx implementation, main queue allocation/configuration, interrupt setup, ethtool stats, and virtchnl queue programming paths.

## Risks
This header encodes hardware limits and shared state layout. Incorrect descriptor accounting can cause ring overruns or unnecessary queue stops. Flag bit drift between queue configuration, Tx offload code, and Rx metadata extraction can break VLAN or timestamp behavior. `struct iavf_ring` is cacheline-aligned and hot in the data path, so layout changes can have performance side effects.

## Test Signals
Compile coverage for all users, Tx descriptor accounting unit-style checks with fragmented skbs, queue stop/wake stress, RSS hash defaults via ethtool, ITR setting changes, VLAN tag-location behavior, timestamp flag behavior, and performance regression tests on multi-queue traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_type.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_type.h

## Purpose
Defines common IAVF hardware-facing types, descriptor formats, descriptor bit masks, hardware capability structures, bus/MAC metadata, debug masks, and Ethernet statistics. It is the main local hardware ABI header for the VF driver.

## Important APIs, Types, and Functions
Important definitions include `IAVF_MASK`, `IAVF_DESC_UNUSED`, queue/VSI constants, `enum iavf_debug_mask`, `enum iavf_vsi_type`, `enum iavf_queue_type`, `struct iavf_hw_capabilities`, `struct iavf_mac_info`, bus enums and `struct iavf_bus_info`, `struct iavf_hw`, `struct iavf_rx_desc`, `struct iavf_tx_desc`, `struct iavf_tx_context_desc`, and `struct iavf_eth_stats`. The header defines legacy and flexible Rx descriptor fields, Tx data descriptor command/type/offset/length fields, Tx context descriptor tunnel/TSO/VLAN fields, and status/error enums used by Rx parsing.

## Control Flow
The file is almost entirely declarative. Runtime behavior appears indirectly when callers use field masks with `FIELD_GET` or construct descriptor command words. `IAVF_DESC_UNUSED` computes ring free space from `next_to_clean`, `next_to_use`, and ring count.

## State and Persistence
The structures mirror persistent hardware and driver state: PCI identity, MMIO base, AdminQ data, MAC addresses, capabilities, descriptor memory formats, and statistics returned by the PF. Descriptor definitions govern the exact DMA writeback and transmit command layout shared with hardware.

## Dependencies and Integration Points
Includes `iavf_status.h`, OS dependency wrappers, register definitions, AdminQ declarations, and device IDs. It is included transitively by most IAVF files, including queue setup, Tx/Rx, AdminQ, virtchnl, and stats code. It also uses Linux endian and bitmask types through included headers.

## Risks
This is hardware ABI. Wrong masks, shifts, endian annotations, struct sizes, or descriptor alignment can corrupt packet IO or metadata parsing. Flexible descriptor timestamp fields must match PTP handling, and RSS/checksum/VLAN masks must match `iavf_txrx.c`. `IAVF_DESC_UNUSED` assumes a one-descriptor gap ring discipline.

## Test Signals
Build-time static assertions, traffic with legacy and flexible Rx descriptors, checksum/hash/VLAN metadata validation, TSO/tunnel Tx offloads, stats updates from virtchnl, reset/probe on supported PCI IDs, and comparing descriptor/register definitions against hardware documentation are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_types.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_types.h

## Purpose
Defines PTP-specific IAVF state containers that are shared between PTP implementation, virtchnl command dispatch, and Rx timestamp processing.

## Important APIs, Types, and Functions
`struct iavf_ptp_aq_cmd` is a flexible-array command wrapper containing a list node, virtchnl opcode, message length, and message payload. `struct iavf_ptp` stores the PTP waitqueue, PF-advertised `virtchnl_ptp_caps`, `ptp_clock_info`, registered `ptp_clock`, queued PTP AQ commands, cached PHC time, cache update timestamp, AQ command mutex, current hardware timestamp configuration, and `phc_time_ready` flag.

## Control Flow
The header has no executable control flow. `iavf_ptp.c` allocates and queues `iavf_ptp_aq_cmd` objects, while `iavf_virtchnl.c` dequeues and sends them, then updates `struct iavf_ptp` when PF responses arrive.

## State and Persistence
All state is in-memory adapter state. `aq_cmds` persists queued virtchnl PTP work until sent or released. `cached_phc_time` and `cached_phc_updated` persist the latest PF-reported PHC reading for Rx timestamp extension. `hwtstamp_config` persists the last accepted userspace timestamp mode.

## Dependencies and Integration Points
Includes the base `iavf_types.h` header, virtchnl definitions, and `<linux/ptp_clock_kernel.h>`. This unusual self-include is protected by the include guard, allowing the file to layer PTP-specific definitions while sharing the historical header name. Integrated by `iavf_ptp.h`, PTP code, virtchnl code, and adapter initialization in `iavf_main.c`.

## Risks
The command flexible array depends on correct `msglen` allocation and lifetime management. `cached_phc_time` is read in the Rx path while updated in virtchnl completion, so correctness depends on simple atomic-width access and freshness rather than complex locking. Initialization of list head, waitqueue, and mutex must happen before any PTP command can be queued.

## Test Signals
Compile with PTP enabled, run probe/remove with PTP capability, validate queued command cleanup during `iavf_ptp_release`, check PHC read wait/wakeup behavior, and test reset paths that reinitialize or clear PTP capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_virtchnl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_virtchnl.c

## Purpose
Implements the IAVF virtchnl control plane used by the VF to negotiate capabilities and request PF-owned operations. It sends AdminQ messages to the PF, polls or handles asynchronous replies, configures queues, IRQ maps, MAC/VLAN filters, promiscuous mode, RSS, VLAN offloads, PTP, QoS, ADq channels, cloud filters, Flow Director, advanced RSS rules, reset, and link events.

## Important APIs, Types, and Functions
Key send/get functions include `iavf_send_api_ver`, `iavf_verify_api_ver`, `iavf_send_vf_config_msg`, `iavf_get_vf_config`, `iavf_send_vf_offload_vlan_v2_msg`, `iavf_get_vf_vlan_v2_caps`, `iavf_send_vf_supported_rxdids_msg`, `iavf_get_vf_supported_rxdids`, `iavf_send_vf_ptp_caps_msg`, and `iavf_get_vf_ptp_caps`. Queue and interrupt control uses `iavf_configure_queues`, `iavf_enable_queues`, `iavf_disable_queues`, and `iavf_map_queues`. Feature operations include MAC/VLAN add/delete, promiscuous mode, stats, RSS key/LUT/hash/hfunc, VLAN stripping/insertion v1/v2, PTP command send, QoS quanta/bandwidth, channel enable/disable, cloud filters, FDIR filters, advanced RSS, and `iavf_request_reset`. `iavf_virtchnl_completion` is the central response dispatcher.

## Control Flow
Most request functions first check `adapter->current_op == VIRTCHNL_OP_UNKNOWN`, build a virtchnl message, clear the relevant `aq_required` bit, set `current_op`, and send with `iavf_send_pf_msg`. Initialization can also poll specific replies synchronously through `iavf_poll_virtchnl_msg`, which detects reset-impending events. Asynchronous completions handle PF events first, then log and repair request-specific failures, then update success state by opcode. Queue setup sends ring lengths, DMA addresses, descriptor IDs, CRC settings, PTP Rx timestamp flags, and max frame sizes. Filter operations batch within AQ buffer limits and maintain local pending/active states. PTP commands are dequeued under `ptp.aq_cmd_lock` and sent one at a time.

## State and Persistence
Persistent adapter state includes `current_op`, `aq_required`, negotiated PF/API version, `vf_res`, `vsi_res`, VLAN v2 caps, supported Rx descriptor IDs, PTP caps and cached PHC time, queue counts, link state/speed, netdev features, MAC/VLAN filter lists, RSS key/LUT/hashcfg/hfunc, QoS caps, queue shaper update flags, channel config state, cloud filter list, FDIR list, advanced RSS list, and current stats. Hardware/PF state persists after successful virtchnl requests until reset or later reconfiguration.

## Dependencies and Integration Points
Depends on AdminQ helpers, `iavf.h`, `iavf_ptp.h`, `iavf_prototype.h`, Intel `libie` Rx helpers, virtchnl structures and opcodes, netdev queue/carrier APIs, VLAN capability helpers, ethtool/TC-derived filter state, and reset/workqueue orchestration in `iavf_main.c`. It directly coordinates with `iavf_txrx.c` by configuring ring descriptors and with `iavf_ptp.c` by delivering PTP capability and time responses.

## Risks
The single `current_op` gate serializes most control operations; missed completion or send failure can stall later requests unless explicitly reset. Batched filter updates must correctly preserve `aq_required` when more messages are needed. Error paths mutate local MAC/VLAN/FDIR/RSS/cloud state and can diverge from PF state if not carefully matched to PF return status. Message length validation is uneven across opcodes. PTP time reads depend on timely completion wakeups. Reset events can arrive while synchronous polling expects another opcode.

## Test Signals
Signals include VF probe negotiation across PF API versions, queue configure/enable/disable/map, reset during configuration, link change events, MAC address changes and rejection, VLAN v1/v2 add/delete and stripping/insertion toggles, RSS get/set/hfunc rollback on failure, stats polling, PTP caps/time reads, QoS quanta and bandwidth programming, ADq channel setup/teardown, cloud/FDIR/advanced RSS add/delete success and failure paths, oversized filter batches, and PF communication failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_virtchnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/Makefile

## Purpose
Defines the kbuild object composition for the Intel ICE E800 series Ethernet driver. It selects the core `ice.o` module and conditionally adds source objects based on kernel configuration options.

## Important APIs, Types, and Functions
The important kbuild variables are `subdir-ccflags-y`, `obj-$(CONFIG_ICE)`, `ice-y`, and conditional `ice-$(CONFIG_...)` additions. The core object list includes main PCI/device control, control queue, common/NVM/switch/scheduler/base/lib code, Tx/Rx, filters, IRQ, VLAN mode and ops, Flow Director, parser, IDC, devlink, subfunction support, firmware update, LAG, ethtool, representors, TC, debugfs, and adapter code. Conditional blocks add SR-IOV/virtchnl support, PTP/DPLL/TSPLL support, DCB, accelerated RFS, AF_XDP, switchdev, GNSS, and HWMON.

## Control Flow
There is no runtime control flow. Kbuild evaluates config symbols and constructs the set of objects linked into `ice.o`. `subdir-ccflags-y += -I$(src)` ensures local headers are discoverable for files in subdirectories such as `devlink/` and `virt/`.

## State and Persistence
The Makefile persists build-time module composition. Runtime driver state is in the compiled sources it selects. Configuration-dependent object inclusion controls which features exist in the resulting module.

## Dependencies and Integration Points
Integrates with the Linux kernel kbuild system and the ICE source tree. Feature dependencies come from Kconfig symbols including `CONFIG_ICE`, `CONFIG_PCI_IOV`, `CONFIG_PTP_1588_CLOCK`, `CONFIG_DCB`, `CONFIG_RFS_ACCEL`, `CONFIG_XDP_SOCKETS`, `CONFIG_ICE_SWITCHDEV`, `CONFIG_GNSS`, and `CONFIG_ICE_HWMON`.

## Risks
Missing an object causes link failures or silently removes feature hooks if declarations are also conditional. Adding a feature object under the wrong config can create unresolved symbols or compile code without its subsystem dependencies. Subdirectory object paths must remain aligned with source layout.

## Test Signals
Build `CONFIG_ICE=m/y` with major feature combinations: base only, SR-IOV, PTP, DCB, RFS, AF_XDP, switchdev, GNSS, and HWMON. Watch for unresolved symbols, missing module sections, and feature-specific probe or ethtool/devlink behavior in the resulting ICE driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/Makefile -->
