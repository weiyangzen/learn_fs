# Research Group: subset-b-004431

This grouped report covers the HNS3/HNAE3 common Ethernet driver files assigned to `subset-b-004431`. Each section is source-tree aligned and wrapped with the required reconciliation sentinels.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hnae3.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hnae3.h

## Purpose

`hnae3.h` is the central interface contract for the Hisilicon HNS3 Ethernet acceleration engine framework. It defines PCI device identifiers, firmware/device capability bits, reset and debug command enums, queue and ring abstractions, device specification structures, client registration structures, the large `hnae3_ae_ops` operations vector implemented by PF/VF hardware backends, DCB callbacks, and per-client private state for KNIC and RoCE consumers.

## Important APIs, Types, and Macros

- Capability helpers such as `hnae3_dev_roce_supported()`, `hnae3_dev_fec_supported()`, `hnae3_ae_dev_cq_supported()`, and related `test_bit()` wrappers expose firmware capability state from `struct hnae3_ae_dev::caps`.
- Ring helpers `ring_ptr_move_fw()` and `ring_ptr_move_bw()` wrap ring indices by `desc_num`.
- `struct hnae3_queue` models a TQP queue with MMIO bases, owner handle, queue index, buffer size, and TX/RX descriptor counts.
- `struct hnae3_dev_specs` stores firmware-discovered hardware limits such as RSS table/key sizes, interrupt moderation maxima, MAC table sizes, frame size, TQP/qset counts, tunnel count, and Hilink version.
- `struct hnae3_client`, `struct hnae3_client_ops`, `struct hnae3_ae_dev`, and `struct hnae3_ae_algo` define the client/backend registration layer.
- `struct hnae3_ae_ops` is the primary backend vtable for lifecycle, link, MAC, VLAN, RSS, coalescing, stats, register dumps, vectors, reset, SR-IOV, flow director, PTP, WOL, debugfs, and hardware timestamp operations.
- `struct hnae3_dcb_ops` defines IEEE ETS/PFC/application and DCBX operations consumed by `hns3_dcbnl.c`.
- `struct hnae3_knic_private_info` stores netdev-facing state: RSS sizes, descriptor counts, TC mapping, DSCP priority mapping, TQPs, DCB ops, and MMIO base.
- `struct hnae3_roce_private_info` stores RoCE netdev, MMIO bases, vector assignment, and state bitmaps.
- `hnae3_set_field()`, `hnae3_get_field()`, `hnae3_set_bit()`, and `hnae3_get_bit()` are shared bitfield helpers used by command/RSS code.
- `hnae3_format_mac_addr()` masks middle MAC octets for safer formatted display.
- Public registration functions include `hnae3_register_ae_dev()`, `hnae3_unregister_ae_dev()`, `hnae3_register_ae_algo()`, `hnae3_unregister_ae_algo()`, `hnae3_register_client()`, and `hnae3_unregister_client()`.

## Control Flow and Integration

The header does not execute control flow itself except for inline helpers. Its definitions shape the runtime flow across the driver: PCI PF/VF code registers an `hnae3_ae_algo`, creates an `hnae3_ae_dev`, binds clients through `hnae3_client_ops`, and exposes hardware behavior through `hnae3_ae_ops`. Netdev, ethtool, debugfs, DCBNL, RSS, stats, reset, and RoCE paths all dereference these vtables through `struct hnae3_handle`. Debugfs helpers use `hnae3_seq_file_to_ae_dev()` and `hnae3_seq_file_to_handle()` to recover driver objects from seq files.

## State and Persistence Behavior

All persistent driver state described here is in memory and tied to the PCI device lifetime. Capability bits in `hnae3_ae_dev::caps`, feature flags in `hnae3_ae_dev::flag`, private flags in `hnae3_handle`, TQP arrays, TC/DSCP maps, and debugfs dentries persist until device removal, reset teardown, or client unregistration. No on-disk state is defined. Several structures reflect firmware state cached in the driver, so reset and reinitialization paths must refresh or preserve them deliberately.

## Dependencies

The header depends on Linux networking, PCI, DCBNL, ethtool, ACPI, bitmap, packet scheduler, and traffic control headers. It is consumed by HNS3 PF/VF backend files, common command/RSS/stats modules, NIC frontend code, debugfs, and DCBNL wrappers.

## Risks and Edge Cases

- `struct hnae3_ae_ops` is broad and mostly optional by convention; callers must check function pointers before invoking optional operations.
- Capability helper correctness depends on firmware capability parsing and the bit mapping in command code.
- `hnae3_set_field()` and `hnae3_set_bit()` evaluate the `origin` lvalue multiple times and assume masks/shifts are valid.
- `ring_ptr_move_bw()` assumes `desc_num` is nonzero.
- `hnae3_seq_file_to_handle()` assumes seq file private data carries an `hnae3_ae_dev` with a live handle.
- `struct hnae3_handle` uses a union where `netdev` must remain the first member for netdev-oriented access.

## Test Signals

Useful validation signals include successful PF/VF probe and removal, client registration/unregistration, ethtool operations routed through `hnae3_ae_ops`, DCB setup only when supported, reset notification coverage, debugfs reads resolving the correct handle, RSS/TC configuration bounded by `hnae3_dev_specs`, and capability-dependent features enabling only when the relevant bit is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hnae3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_cmd.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_cmd.c

## Purpose

`hclge_comm_cmd.c` implements the shared PF/VF command queue transport used to communicate with HNS3 firmware. It allocates coherent descriptor rings, programs command queue registers, submits synchronous command descriptors, waits for firmware writeback, converts firmware return codes to Linux errors, queries firmware version/capabilities, enables firmware compatibility features, and tears command queues down.

## Important Functions

- `hclge_comm_cmd_init_regs()` and internal `hclge_comm_cmd_config_regs()` write CSQ/CRQ DMA base, depth, head, and tail registers.
- `hclge_comm_cmd_setup_basic_desc()` zeroes and initializes command descriptors with opcode, `NO_INTR`, `IN`, and optional read/writeback flag.
- `hclge_comm_cmd_reuse_desc()` prepares an existing descriptor for reuse.
- `hclge_comm_firmware_compat_config()` sends `HCLGE_OPC_IMP_COMPAT_CFG` to enable or disable firmware compatibility feature bits.
- `hclge_comm_alloc_cmd_queue()` and internal allocation/free helpers manage coherent descriptor memory.
- `hclge_comm_cmd_query_version_and_capability()` sends `HCLGE_OPC_QUERY_FW_VER`, stores firmware version, derives device version from hardware version plus PCI revision, and populates `ae_dev->caps`.
- `hclge_comm_cmd_send()` is the main synchronized submission path.
- `hclge_comm_cmd_uninit()`, `hclge_comm_cmd_queue_init()`, and `hclge_comm_cmd_init()` implement lifecycle.
- `hclge_comm_cmd_init_ops()` installs optional trace callbacks.

## Control Flow

Initialization first sets ring locks, descriptor counts, timeout, and coherent CSQ/CRQ memory in `hclge_comm_cmd_queue_init()`. `hclge_comm_cmd_init()` resets software indices, programs hardware registers, clears `HCLGE_COMM_STATE_CMD_DISABLE`, checks pending reset state, queries version/capabilities, logs the firmware version, and attempts compatibility enablement when supported by PF/V3+ requirements.

Command submission in `hclge_comm_cmd_send()` traces outgoing descriptors, takes the CSQ lock, rejects disabled command queues, checks ring space, snapshots the descriptor position for writeback, copies descriptors into the CSQ ring, rings the hardware tail register, waits for completion when the descriptor requests sync behavior, copies firmware-updated descriptors back, converts firmware status to `errno`, cleans the software head from the hardware head register, releases the lock, and traces returned descriptors.

Teardown disables firmware compatibility, sets command disable state, waits for in-flight firmware work, clears hardware registers under CSQ/CRQ locks, and frees both rings.

## State and Persistence Behavior

State lives in `struct hclge_comm_hw::cmq` and `comm_state`: DMA descriptor memory, ring head/tail indices, descriptor counts, timeout, last firmware status, trace callbacks, and disable bit. Firmware-derived capabilities persist in `hnae3_ae_dev::caps` until reset or device teardown. Command descriptor rings are coherent DMA memory and are freed during uninit. There is no filesystem persistence.

## Dependencies and Integration Points

This module depends on `hnae3.h` bitfield helpers and capability definitions, command opcodes and ring structures from `hclge_comm_cmd.h`, PCI DMA APIs, MMIO register accessors, spinlocks, and firmware-visible descriptor formats. It is a foundation for common RSS, TQP stats, MAC, DCB, reset, register dump, and PF/VF backend code that sends admin commands.

## Risks and Edge Cases

- `hclge_comm_cmd_csq_clean()` disables future commands if the hardware head is outside the expected software window, expecting firmware watchdog recovery.
- `hclge_comm_cmd_send()` returns `-EBUSY` when disabled or full; higher layers must retry or fail gracefully.
- Completion waits are polling microsecond loops; long reset commands require the special timeout map.
- Multi-descriptor "special opcodes" take return status from descriptor zero, while normal commands use the last descriptor.
- Capability defaults for V2 devices differ from parsed capabilities for newer devices.
- Firmware compatibility enable failures are warnings after init, so callers must tolerate features not being enabled.

## Test Signals

Strong signals include successful command queue allocation/free under probe/remove, firmware version log output, valid capability bits for PF and VF devices, command timeout behavior for reset trigger commands, clean `-errno` conversion for firmware errors, no command submission after disable, trace callbacks seeing both send and completion descriptors, and reset paths reinitializing indices and registers without leaking DMA memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_cmd.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_cmd.h

## Purpose

`hclge_comm_cmd.h` defines the shared command queue ABI between HNS3 driver code and firmware. It contains command descriptor flags, command queue register offsets, reset and timeout constants, the complete firmware opcode enum used by common/PF/VF code, firmware return status enums, firmware capability bit definitions, descriptor/ring/control structures, MMIO helpers, and public command queue APIs implemented in `hclge_comm_cmd.c`.

## Important APIs and Types

- Descriptor flags include `HCLGE_COMM_CMD_FLAG_IN`, `NEXT`, `WR`, and `NO_INTR`; `HCLGE_COMM_SEND_SYNC()` treats `NO_INTR` as synchronous polling mode.
- Register constants cover CSQ/CRQ base, depth, head, tail, vector0 command event registers, interrupt registers, and reset-ready bits.
- `enum hclge_opcode_type` is the firmware command namespace for generic, stats, DFX/register, MAC, PTP, pause/PFC, scheduler, buffer, TQP, TSO/GRO, RSS, promiscuous, VLAN, interrupts, flow director, mailbox, LED, PHY, WOL, RAS, and diagnostics commands.
- `enum hclge_comm_cmd_return_status` maps firmware descriptor return values before conversion to Linux errors.
- `enum HCLGE_COMM_CAP_BITS` and `enum HCLGE_COMM_API_CAP_BITS` define firmware-advertised feature bits.
- `struct hclge_desc` is the firmware command descriptor: opcode, flags, retval, reserved field, and six 32-bit data words.
- `struct hclge_comm_cmq_ring`, `struct hclge_comm_cmq`, and `struct hclge_comm_hw` model command queue DMA rings, queue state, trace hooks, and MMIO bases.
- Public APIs include descriptor setup/reuse, queue allocation/free/init/uninit, command send, firmware compatibility config, version/capability query, register init, and trace op installation.

## Control Flow and Integration

The header has no runtime flow by itself, but every command user constructs one or more `struct hclge_desc` values with an opcode from `enum hclge_opcode_type`, marks it read or write with the descriptor flags, and calls `hclge_comm_cmd_send()`. RSS and TQP stats in this subset use `HCLGE_OPC_RSS_*` and `HCLGE_OPC_QUERY_*_STATS`; other HNS3 modules use the rest of the opcode space.

## State and Persistence Behavior

The structures describe in-memory driver and DMA state. `struct hclge_comm_hw` persists for the lifetime of the PF/VF hardware object and owns command queue state. Descriptor memory is coherent DMA memory allocated during queue init and freed during queue uninit. `last_status` preserves the most recent firmware command status for diagnostics. No state is persisted outside the driver.

## Dependencies

The header includes Linux types and `hnae3.h` for device structures, capability bit definitions, and bitfield helpers. It assumes Linux PCI DMA/MMIO infrastructure in implementation files. Firmware ABI compatibility is critical because opcodes, descriptor layout, return codes, and capability bits must match firmware definitions.

## Risks and Edge Cases

- Opcode enum values are firmware ABI and must not drift.
- `HCLGE_COMM_SEND_SYNC()` is based on the `NO_INTR` bit, so descriptor flag misuse changes completion behavior.
- `HCLGE_DESC_DATA_LEN` fixes command payload to six words; command-specific structs cast over `desc.data` must fit.
- Capability bit mappings use firmware bit positions that are not contiguous and contain version-specific gaps.
- Register offsets and descriptor ring depth are hardware-specific; incorrect values can break probe or hang command submission.

## Test Signals

Validation should include compile coverage for all command users, static layout checks where available, successful admin command traffic on PF and VF devices, firmware error conversion checks, feature-gated behavior matching advertised capabilities, and RSS/TQP command users producing correct descriptors with the expected opcodes and flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_rss.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_rss.c

## Purpose

`hclge_comm_rss.c` implements shared Receive Side Scaling helpers for HNS3 PF/VF code. It initializes default RSS hash keys and tuple selections, manages a shadow indirection table, converts ethtool hash function and tuple requests into firmware command formats, programs RSS hash keys, programs RSS indirection table chunks, configures RSS traffic-class mode, and returns current RSS settings to callers.

## Important Functions

- `hclge_comm_rss_init_cfg()` chooses default hash algorithm by device version, initializes tuple defaults, allocates the shadow indirection table, copies the default 40-byte key, and fills the table.
- `hclge_comm_get_rss_tc_info()` derives per-TC valid, size, and offset arrays from RSS size and hardware TC map.
- `hclge_comm_set_rss_tc_mode()` encodes TC mode bitfields and sends `HCLGE_OPC_RSS_TC_MODE`.
- `hclge_comm_set_rss_hash_key()` parses ethtool hash function input, programs firmware, and updates the shadow key/algo.
- `hclge_comm_set_rss_tuple()` validates requested RXH fields, builds an RSS tuple command, sends it, and updates shadow tuple state.
- `hclge_comm_parse_rss_hfunc()` maps `ETH_RSS_HASH_TOP`, `ETH_RSS_HASH_XOR`, and `ETH_RSS_HASH_NO_CHANGE` to HNS3 algorithms.
- `hclge_comm_set_rss_indir_table()` writes the indirection table in 16-entry firmware chunks, including high queue ID bits.
- `hclge_comm_set_rss_algo_key()` writes the 40-byte key in 16-byte command chunks.
- `hclge_comm_init_rss_tuple_cmd()` converts an `ethtool_rxfh_fields` request into per-flow tuple bytes and enforces old-device SCTP IPv6 limitations.
- `hclge_comm_convert_rss_tuple()` maps HNS3 tuple bits back to ethtool RXH bits.

## Control Flow

RSS setup begins with `hclge_comm_rss_init_cfg()`, which establishes shadow state before hardware programming. Runtime ethtool changes enter through set-key, set-table, or set-tuple wrappers in PF/VF code, then call this module to validate user input, encode firmware descriptors, send commands through `hclge_comm_cmd_send()`, and update shadow state only after successful firmware completion. Query paths copy the shadow key/table/algo/tuple values back without reading firmware.

## State and Persistence Behavior

The module persists RSS state in `struct hclge_comm_rss_cfg`: `rss_hash_key`, `rss_indirection_tbl`, `rss_algo`, `rss_tuple_sets`, and `rss_size`. The indirection table is device-managed memory allocated with `devm_kcalloc()`, so it is tied to the PCI device lifetime. Firmware programming mirrors this shadow state, but query helpers read the shadow copy. No on-disk state exists.

## Dependencies and Integration Points

This module depends on ethtool RSS constants, flow type constants, `hnae3_ae_dev::dev_specs`, `hnae3_handle::kinfo`, device version constants from `hnae3.h`, command opcodes and descriptor helpers from `hclge_comm_cmd.h`, and the common command queue transport. It integrates with ethtool `get_rss`, `set_rss`, `get_rss_tuple`, and `set_rss_tuple` backend operations.

## Risks and Edge Cases

- `rss_cfg->rss_size` must be nonzero before `hclge_comm_rss_indir_init_cfg()` divides by it.
- `hclge_comm_set_rss_indir_table()` assumes RSS indirection table size is divisible by 16.
- `hclge_comm_append_rss_msb_info()` ORs high-bit storage into `req->rss_qid_h`; descriptors must be freshly zeroed each chunk, which `hclge_comm_cmd_setup_basic_desc()` provides.
- Old devices reject IPv6 SCTP requests that include L4 port fields.
- Shadow state updates only happen after successful commands in some paths; direct firmware changes would not be reflected.
- `hclge_comm_get_rss_tc_info()` rounds RSS size up to a power of two and encodes log2 size, so unusual queue counts need hardware validation.

## Test Signals

Useful tests include ethtool RSS key get/set, hash function TOP/XOR/no-change behavior, invalid hash function rejection, tuple programming for TCP/UDP/SCTP/IPv4/IPv6, SCTP IPv6 port rejection on V2-or-older devices, indirection table programming with queue IDs above 255, TC mode encoding for multiple TC maps, and reset restore of the shadow RSS configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_rss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_rss.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_rss.h

## Purpose

`hclge_comm_rss.h` defines the shared RSS configuration ABI for HNS3 common code. It contains hash algorithm identifiers, tuple bit masks, TC mode bitfield layout, firmware command payload structures, the persistent shadow RSS configuration structure, and function prototypes for RSS initialization, query, conversion, and programming.

## Important APIs and Types

- Hash algorithms are `HCLGE_COMM_RSS_HASH_ALGO_TOEPLITZ`, `SIMPLE`, and `SYMMETRIC`; the implementation maps only TOP and XOR ethtool functions directly.
- Tuple bit definitions cover source/destination port, source/destination IP, and verification tag for SCTP.
- `struct hclge_comm_rss_tuple_cfg` stores per-flow tuple masks for IPv4/IPv6 TCP, UDP, SCTP, and fragments.
- `struct hclge_comm_rss_cfg` is the driver shadow state for the 40-byte key, indirection table pointer, selected algorithm, tuple sets, and RSS queue size.
- Firmware payload structs include `hclge_comm_rss_config_cmd`, `hclge_comm_rss_input_tuple_cmd`, `hclge_comm_rss_ind_tbl_cmd`, and `hclge_comm_rss_tc_mode_cmd`.
- Public APIs expose key size, initialization, hash/tuple get and set, indirection table programming, TC mode programming, and ethtool tuple conversion.

## Control Flow and Integration

PF/VF backend code includes this header when implementing `hnae3_ae_ops` RSS callbacks. Callers initialize `struct hclge_comm_rss_cfg`, program firmware through the command queue, and serve ethtool queries from the shadow state. TC setup code can derive `tc_offset`, `tc_valid`, and `tc_size` arrays and pass them to `hclge_comm_set_rss_tc_mode()`.

## State and Persistence Behavior

The header defines the shape of in-memory RSS state but does not allocate it. The shadow config persists for the backend device lifetime and must be restored after reset. Firmware command payload structs are transient overlays on command descriptor data.

## Dependencies

The header depends on Linux types, `hnae3.h` for handle/device structures and bit helpers, and `hclge_comm_cmd.h` for command queue types. It assumes ethtool RSS and flow constants are available to implementation callers.

## Risks and Edge Cases

- The command payload structs must fit within `struct hclge_desc::data`.
- The indirection table command splits low and high queue ID bits; queue ID width assumptions must match firmware.
- `HCLGE_COMM_RSS_INPUT_TUPLE_SCTP_NO_PORT` encodes old-device behavior that callers must preserve.
- `rss_size`, `rss_ind_tbl_size`, and queue mappings are not self-validating in the struct definitions.

## Test Signals

Compile-time coverage across PF and VF users, successful ethtool RSS query/set operations, descriptor payload compatibility with firmware, reset restore tests, and multi-TC queue distribution checks are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_rss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_tqp_stats.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_tqp_stats.c

## Purpose

`hclge_comm_tqp_stats.c` implements shared per-TQP queue statistics helpers. It exposes ethtool stat values and names for TX/RX queue packet counters, updates cached counters by querying firmware for each queue, and resets cached TQP stats.

## Important Functions

- `hclge_comm_tqps_get_stats()` writes all TX queue packet counters followed by all RX queue packet counters into an ethtool data buffer.
- `hclge_comm_tqps_get_sset_count()` reports `num_tqps * 2`.
- `hclge_comm_tqps_get_strings()` emits stat names like `txq%u_pktnum_rcd` and `rxq%u_pktnum_rcd` using each TQP global index.
- `hclge_comm_tqps_update_stats()` loops over each TQP, sends `HCLGE_OPC_QUERY_RX_STATS` and `HCLGE_OPC_QUERY_TX_STATS`, and accumulates returned 32-bit descriptor values into 64-bit cached counters.
- `hclge_comm_reset_tqp_stats()` zeroes each cached TQP stats struct.

## Control Flow

Update flow obtains `handle->kinfo`, converts each `struct hnae3_queue *` back to `struct hclge_comm_tqp` with `container_of()`, sends a read command with the TQP index in descriptor data word zero, and adds firmware data word one to the cached RX/TX counter. Query flow does not contact hardware; it reads the cached values in stable TX-then-RX order.

## State and Persistence Behavior

The persistent state is `struct hclge_comm_tqp::tqp_stats`, held in memory per queue. Hardware appears to return 32-bit packet count deltas or readings; this module accumulates them into 64-bit software counters. Resetting stats clears only the cached software values. No on-disk state exists.

## Dependencies and Integration Points

The module depends on `hnae3_handle::kinfo.num_tqps` and `kinfo.tqp`, the common command queue, TQP stat opcodes from `hclge_comm_cmd.h`, `struct hclge_comm_tqp` from the companion header, and ethtool string formatting. It integrates with backend ethtool stats paths.

## Risks and Edge Cases

- The code assumes every `kinfo.tqp[i]` points to the embedded `q` member of a valid `struct hclge_comm_tqp`.
- A command failure returns immediately, leaving later queues stale and earlier queues already updated.
- Accumulating `desc.data[1]` without wrap handling details relies on firmware semantics.
- No explicit locking protects stats while updates and ethtool reads occur in this file.
- Name/count/order must remain synchronized with any caller-provided stat buffers.

## Test Signals

Validation should cover ethtool stat count and names, TX/RX ordering, successful per-queue firmware command traffic, partial failure behavior, reset-to-zero behavior, counter monotonicity under traffic, and race checks during concurrent stat update/read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_tqp_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_tqp_stats.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_tqp_stats.h

## Purpose

`hclge_comm_tqp_stats.h` defines the shared TQP stats data structures and public helper APIs used by HNS3 PF/VF code to expose per-queue packet counters through ethtool.

## Important APIs and Types

- `HCLGE_COMM_QUEUE_PAIR_SIZE` documents that each TQP contributes two stats: TX and RX.
- `struct hclge_comm_tqp_stats` stores cached 64-bit software counters for TX and RX packet records queried through firmware opcodes `0x0B03` and `0x0B13`.
- `struct hclge_comm_tqp` embeds the generic `struct hnae3_queue`, device pointer, stats, global queue index, and allocation flag.
- Public prototypes cover stats extraction, string-set count, stat name emission, firmware update, and reset.

## Control Flow and Integration

The header establishes the container layout used by `container_of(kinfo->tqp[i], struct hclge_comm_tqp, q)`. Backend code allocates TQPs as `struct hclge_comm_tqp`, exposes their embedded `hnae3_queue` through `hnae3_knic_private_info::tqp`, and calls these helpers from ethtool stats operations.

## State and Persistence Behavior

Per-TQP stats and allocation state are in-memory driver state. The embedded `hnae3_queue` ties the common stats object to generic HNAE3 queue users. Stats persist until reset, explicit reset helper invocation, or queue teardown.

## Dependencies

The header includes Linux types, `etherdevice.h`, and `hnae3.h`. The implementation also requires common command queue types and firmware opcodes.

## Risks and Edge Cases

- The embedded queue layout is contractual; callers that allocate a plain `hnae3_queue` cannot use these helpers safely.
- The global `index` is used in firmware queries and stat names, so it must match hardware queue numbering.
- Counter semantics depend on firmware and are not documented beyond 32-bit opcode comments.

## Test Signals

Tests should confirm layout assumptions, ethtool stat count equals `num_tqps * 2`, stat names use global queue indices, firmware update commands use the correct index, and reset clears cached counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_tqp_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_dcbnl.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_dcbnl.c

## Purpose

`hns3_dcbnl.c` bridges Linux DCBNL netdevice callbacks to HNS3 backend DCB operations. It exposes IEEE ETS, PFC, application priority, and DCBX get/set operations when the handle has backend `dcb_ops` and the device is not a VF.

## Important Functions

- `hns3_dcbnl_ieee_getets()` / `hns3_dcbnl_ieee_setets()` delegate ETS get/set.
- `hns3_dcbnl_ieee_getpfc()` / `hns3_dcbnl_ieee_setpfc()` delegate PFC get/set.
- `hns3_dcbnl_ieee_setapp()` / `hns3_dcbnl_ieee_delapp()` delegate DCB application priority changes.
- `hns3_dcbnl_getdcbx()` / `hns3_dcbnl_setdcbx()` delegate DCBX mode get/set.
- `hns3_dcbnl_setup()` attaches `hns3_dcbnl_ops` to `net_device::dcbnl_ops` only when supported and not a VF.

## Control Flow

Each callback obtains the HNAE3 handle from the netdev with `hns3_get_handle()`. Mutating and query operations that can touch backend DCB state first reject NIC reset with `-EBUSY`. If the corresponding backend function pointer exists, the call is forwarded with the handle and original DCB object. Missing operations return `-EOPNOTSUPP`, except `getdcbx()` returns `0` and `setdcbx()` returns `1` to match DCBNL expectations.

## State and Persistence Behavior

This file owns no persistent hardware state. It installs a static `struct dcbnl_rtnl_ops` pointer into the netdev. Actual DCB state is owned by the backend implementation referenced by `handle->kinfo.dcb_ops` and likely persisted in firmware or driver state outside this file.

## Dependencies and Integration Points

The file depends on `hnae3.h` for `struct hnae3_handle` and DCB ops, `hns3_enet.h` for `hns3_get_handle()` and `hns3_nic_resetting()`, and Linux DCBNL structures. It integrates with netdev registration and HCLGE DCB backend code.

## Risks and Edge Cases

- `hns3_dcbnl_getdcbx()` and `setdcbx()` do not check reset state unlike the IEEE callbacks.
- The callbacks assume `h->kinfo.dcb_ops` is valid after setup; setup skips null ops, but later teardown ordering must preserve it while netdev callbacks are registered.
- VF devices are intentionally excluded, so SR-IOV behavior depends on PF-side management.
- Missing backend operations produce user-visible unsupported errors.

## Test Signals

Useful tests include DCBNL operations during normal operation and reset, PF devices with and without DCB support, VF devices confirming no DCBNL ops are installed, missing callback behavior, ETS/PFC round trips through firmware, and DCBX mode return conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_dcbnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_debugfs.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_debugfs.c

## Purpose

`hns3_debugfs.c` builds the HNS3 debugfs interface. It creates per-device directories and files for traffic management, queue state, descriptor rings, MAC lists, register dumps, flow director state, page pool state, interrupt coalescing, device capabilities/specs, and backend-provided diagnostics. It also registers and unregisters the global HNS3 debugfs root.

## Important Data and Functions

- `hns3_dbgfs_root` stores the global root dentry.
- `hns3_dbg_dentry[]` defines per-device child directories such as `tm`, `tx_bd_info`, `rx_bd_info`, `mac_list`, `reg`, `queue`, `fd`, and `common`.
- `hns3_dbg_cmd[]` maps file names to `enum hnae3_dbg_cmd`, target directory, and init function.
- `hns3_dbg_cap[]` maps user-readable capability names to HNAE3 capability bits.
- `hns3_dbg_coal_info()` reports TX/RX DIM and interrupt moderation state.
- `hns3_dbg_rx_queue_info()` and `hns3_dbg_tx_queue_info()` dump queue MMIO register state.
- `hns3_dbg_queue_map()` reports local queue, global queue, and vector IRQ mapping.
- `hns3_dbg_rx_bd_info()` and `hns3_dbg_tx_bd_info()` dump descriptor contents for a selected queue.
- `hns3_dbg_dev_info()` reports device capabilities and firmware-derived specs.
- `hns3_dbg_page_pool_info()` reports RX page pool counters and configuration.
- `hns3_dbg_bd_file_init()`, `hns3_dbg_common_init_t1()`, and `hns3_dbg_common_init_t2()` create debugfs files for local and backend-provided readers.
- `hns3_dbg_init()` creates the per-device debugfs tree and all supported files.
- `hns3_dbg_uninit()`, `hns3_dbg_register_debugfs()`, and `hns3_dbg_unregister_debugfs()` remove per-device and global debugfs trees.

## Control Flow

Module/global setup calls `hns3_dbg_register_debugfs()` to create the root. Device setup calls `hns3_dbg_init()`, which creates a per-PCI-device directory under the root, creates child directories, then iterates `hns3_dbg_cmd[]`. It skips unsupported TM nodes on old devices and PTP info when PTP capability is absent. Each command invokes its configured initializer: type 1 uses local seq-file readers, type 2 asks backend `dbg_get_read_func()` for a reader, and BD commands create one file per available queue. On any init error, the per-device tree is removed recursively.

Read flow for queue/page-pool/BD files resolves the handle from seq private data or `hns3_dbg_data`, checks ring/page-pool presence and reset/init state where needed, then reads software state and MMIO registers into seq output. Teardown removes debugfs recursively and clears saved dentries.

## State and Persistence Behavior

Debugfs dentries persist for the global module lifetime and per-device handle lifetime. Per-BD-file `hns3_dbg_data` arrays are `devm_kcalloc()` allocations tied to the PCI device. The file stores no durable state; it exposes live driver memory, live MMIO registers, cached capabilities/specs, descriptors, page pool counters, and DIM state. Reads can fail during reset to avoid dereferencing invalid ring memory.

## Dependencies and Integration Points

The module depends on Linux debugfs and seq_file APIs, `string_choices.h`, `hnae3.h`, `hns3_debugfs.h`, and `hns3_enet.h`. It integrates with NIC private structures (`hns3_nic_priv`, rings, vectors, descriptors, page pools), HNAE3 backend debug read functions, capability bits populated by command init, and queue/vector helpers from the NIC frontend.

## Risks and Edge Cases

- `hns3_dbg_dentry[]` is static global state reused per device; concurrent multi-device init could overwrite dentry pointers.
- Several read paths access live ring and descriptor memory; reset checks reduce but do not fully eliminate races without broader synchronization.
- BD dump files are created for max available channels, while reads reject queues beyond current `num_tqps`.
- `sprintf()` into `HNS3_DBG_FILE_NAME_LEN` relies on command names plus queue numbers fitting the 16-byte buffer.
- Backend `dbg_get_read_func()` failures abort all debugfs init for the device.
- Queue register reads assume mapped TQP MMIO remains valid during the seq read.

## Test Signals

Signals include debugfs tree creation/removal on probe/remove, all expected files under each directory, old-device and no-PTP skips, queue info reads during traffic, reset-time reads returning `-EPERM` or `-EBUSY` rather than crashing, BD dump bounds checks, page-pool absent behavior, backend-provided debug readers, and multi-device debugfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_debugfs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_debugfs.h

## Purpose

`hns3_debugfs.h` defines the small set of structures used by `hns3_debugfs.c` to describe debugfs files, per-file private data, directory categories, command mappings, and capability display mappings.

## Important APIs and Types

- `HNS3_DBG_ITEM_NAME_LEN` and `HNS3_DBG_FILE_NAME_LEN` bound display item and generated file names.
- `struct hns3_dbg_item` stores a display name plus spacing interval for table-like debug output.
- `struct hns3_dbg_data` carries the handle, debug command, and queue id for per-queue BD files.
- `enum hns3_dbg_dentry_type` indexes debugfs directory categories.
- `struct hns3_dbg_dentry_info` stores a directory name and dentry pointer.
- `struct hns3_dbg_cmd_info` maps a debugfs file name to an HNAE3 debug command, directory, and initializer.
- `struct hns3_dbg_cap_info` maps display strings to capability bit numbers.

## Control Flow and Integration

The header provides data shapes only. `hns3_debugfs.c` fills arrays of these structures and uses them to create debugfs directories/files and route seq-file reads to local or backend-provided functions. `struct hns3_dbg_data` becomes seq private data for descriptor dump files.

## State and Persistence Behavior

Instances of these structures persist in static arrays or device-managed allocations in the implementation. Dentry pointers are valid only while debugfs entries exist. Per-file `hns3_dbg_data` persists for the PCI device lifetime because allocation is device-managed.

## Dependencies

The header includes `hnae3.h` for `struct hnae3_handle`, debug command enums, and capability bit enum values. It relies on Linux debugfs `struct dentry` declarations available through included kernel headers in consumers.

## Risks and Edge Cases

- Name length constants are small; generated queue file names must fit.
- Directory enum order must match the static dentry array in the implementation.
- Capability bit enum values must stay synchronized with `hnae3.h`.
- Per-file private data contains raw handle pointers, so debugfs teardown must happen before the handle becomes invalid.

## Test Signals

Compile coverage, debugfs file creation with long queue indices, directory mapping correctness, per-queue BD reads using the intended queue id, and teardown without stale private data are the key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_debugfs.h -->
