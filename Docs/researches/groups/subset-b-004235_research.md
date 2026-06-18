# Research: subset-b-004235

Grouped research for Fusion MPT driver files under `sources/distributed-fs/ceph-client/drivers/message/fusion`. Each section is delimited for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptbase.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptbase.h

## Purpose
`mptbase.h` is the shared contract for the legacy LSI Fusion MPT driver family. It defines versioning, adapter limits, message-frame layouts, scatter-gather flag helpers, target/device bookkeeping, IOC management status bits, event structures, protocol-driver callback types, and the large `MPT_ADAPTER` object consumed by the SCSI, Fibre Channel, SAS, LAN, and ioctl drivers.

## Important APIs, Types, and Functions
Core public types include `MPT_ADAPTER`, `MPT_FRAME_HDR`, `MPT_FRAME_TRACKER`, `MPT_MGMT`, `CONFIGPARMS`, `MPT_SCSI_HOST`, `VirtTarget`, `VirtDevice`, `MPT_IOCTL_EVENTS`, `mptfc_rport_info`, and bus/config structs for SPI, SAS, RAID, and FC. Public callback contracts are `MPT_CALLBACK`, `MPT_EVHANDLER`, and `MPT_RESETHANDLER`; reset phases are `MPT_IOC_SETUP_RESET`, `MPT_IOC_PRE_RESET`, and `MPT_IOC_POST_RESET`. Important exported base entry points include `mpt_attach()`, `mpt_detach()`, `mpt_register()`, `mpt_deregister()`, event/reset registration, message-frame get/put/free helpers, `mpt_send_handshake_request()`, `mpt_verify_adapter()`, `mpt_config()`, firmware-memory helpers, RAID page helpers, task-management flag helpers, and reset handlers.

## Control Flow
Protocol modules register callbacks with the base driver and receive a callback index that is embedded into message contexts. They allocate frames with `mpt_get_msg_frame()`, fill MPI request structures, post via `mpt_put_msg_frame()` or `mpt_put_msg_frame_hi_pri()`, and receive completions through the registered callback. The base header also standardizes config-page access through `CONFIGPARMS`, reset fan-out through reset handlers, and adapter discovery through `ioc_list` plus `mpt_verify_adapter()`.

## State and Persistence
Almost all persistent runtime state is anchored in `MPT_ADAPTER`: PCI resources, MMIO register mappings, request/reply frame DMA pools, chain buffers, sense buffers, IOC facts, port facts, cached firmware, per-protocol callback indices, event logs, SCSI host pointers, FC rport lists and workqueues, SAS topology/discovery state, management command completions, reset/task-management flags, and counters for resets/timeouts. State is in-memory and tied to PCI device lifetime; there is no disk persistence.

## Dependencies and Integration Points
The header depends on kernel PCI, mutex, procfs, SCSI, netdev-visible declarations through consumers, and the LSI MPI headers under `lsi/`. It is included by `mptbase.c`, `mptctl.c`, `mptfc.c`, `mptlan.c`, and other Fusion protocol drivers. Its callback and frame-context conventions are the integration point between Linux subsystems and firmware message passing.

## Risks and Edge Cases
`MPT_ADAPTER` is very broad and shared across many protocol drivers, so layout or semantic changes have high blast radius. Message context encodes callback and frame index, making corruption or stale contexts dangerous. Several pointer casts and `CAST_U32_TO_PTR` helpers expose compat-width risks. DMA frame, chain, and sense-buffer sizing depends on IOC facts and compile-time SGE limits. Bitfield-like status macros and shared management command state require careful reset-path synchronization.

## Test Signals
Useful signals include building all Fusion protocol modules, PCI probe/remove smoke tests, request/reply stress with callback index validation, fault injection for frame allocation and config-page reads, reset fan-out tests covering all three reset phases, DMA mapping tests for 32-bit and 64-bit SGE paths, and SCSI/FC/LAN functional traffic after IOC reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptbase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptctl.c -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptctl.c

## Purpose
`mptctl.c` implements `/dev/mptctl`, the misc-device ioctl interface for Fusion MPT controllers. It exposes adapter information, target inventory, event reporting, diagnostic reset, firmware download/replacement, HP compatibility queries, and controlled raw MPI command pass-through to user space.

## Important APIs, Types, and Functions
The file registers `mptctl_fops` and `mptctl_miscdev`, with `mptctl_ioctl()` and optional `compat_mpctl_ioctl()` as user entry points. Command dispatch is in `__mptctl_ioctl()`. Completion paths are `mptctl_reply()` and `mptctl_taskmgmt_reply()`. Major handlers include `mptctl_fw_download()`, `mptctl_do_fw_download()`, `mptctl_mpt_command()`, `mptctl_do_mpt_command()`, `mptctl_do_reset()`, `mptctl_getiocinfo()`, `mptctl_gettargetinfo()`, `mptctl_readtest()`, `mptctl_eventquery()`, `mptctl_eventenable()`, `mptctl_eventreport()`, `mptctl_replace_fw()`, `mptctl_hp_hostinfo()`, and `mptctl_hp_targetinfo()`. DMA helper routines are `kbuf_alloc_2_sgl()` and `kfree_sgl()`.

## Control Flow
Module init registers a base-driver device callback, the misc device, the main and task-management completion callbacks, plus reset and event handlers. An ioctl copies the common header from user space, verifies the target adapter, handles read-only/status commands immediately, and serializes interrupt-dependent commands through `ioc->ioctl_cmds.mutex`. Raw MPI pass-through obtains a request frame, preserves the driver message context, copies the user message, validates allowed MPI functions, appends up to one outbound and one inbound SGE, posts the frame, waits for completion, then copies reply, sense, and inbound data back to user space. Timeouts invoke task management for SCSI-like requests and may escalate to a soft/hard reset.

## State and Persistence
The driver uses global registration IDs (`mptctl_id`, `mptctl_taskmgmt_id`), a global ioctl mutex, a wait queue, and an async SIGIO queue. Per-adapter state lives in `MPT_ADAPTER`: `ioctl_cmds`, `taskmgmt_cmds`, event log buffers, cached firmware, reset counters, and SCSI host/target data. Firmware replacement updates the in-memory cached firmware image and IOC facts; event enable allocates an in-memory circular-style event array. No user data persists across driver unload except firmware state resident in the controller.

## Dependencies and Integration Points
The file integrates with the miscdevice subsystem, Linux compat ioctl handling, user-copy APIs, PCI DMA allocation/mapping, SCSI mid-layer device lists, fasync/SIGIO, and Fusion base callbacks. It relies on MPI request/reply structures from the LSI headers and on `mptbase` functions for adapter lookup, config access, frame posting, firmware memory, reset, and task management.

## Risks and Edge Cases
This is a privileged raw hardware control surface. The command path must reject unsafe MPI functions, frame-size overflows, negative sizes, out-of-range bus/target IDs, and IOC_INIT mismatches. It still trusts many user-provided request fields after validation. Firmware download allocates DMA buffers in chunks and refuses chain SGE requirements; large images can fail with `-EMLINK` or memory pressure. Timeout recovery races with IOC reset and completion state. Compat paths must preserve pointer-width semantics. Event signaling uses a single global async queue and per-IOC `aen_event_read_flag`, so multi-consumer semantics are weak.

## Test Signals
Test coverage should include ioctl ABI size checks for all `MPTIOCINFO` revisions and compat structs, invalid adapter and inactive-controller paths, raw command rejection for illegal MPI functions, SCSI pass-through with sense data, timeout injection, firmware download with boundary-sized images, event enable/report plus SIGIO, HP host/target info queries, and reset during an outstanding ioctl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptctl.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptctl.h

## Purpose
`mptctl.h` defines the user-facing ioctl ABI for `/dev/mptctl`. It contains ioctl numbers, common headers, adapter/target/event query structures, firmware transfer structures, raw MPI pass-through structures, 32-bit compat variants, and HP/Compaq compatibility commands.

## Important APIs, Types, and Functions
Important ioctl constants include `MPTFWDOWNLOAD`, `MPTCOMMAND`, `MPTIOCINFO`, `MPTTARGETINFO`, `MPTTEST`, `MPTEVENTQUERY`, `MPTEVENTENABLE`, `MPTEVENTREPORT`, `MPTHARDRESET`, `MPTFWREPLACE`, `HP_GETHOSTINFO`, and `HP_GETTARGETINFO`. Main ABI structures are `mpt_ioctl_header`, `mpt_fw_xfer`, `mpt_ioctl_iocinfo` plus rev0/rev1 variants, `mpt_ioctl_targetinfo`, event query/enable/report structs, `mpt_ioctl_test`, `mpt_ioctl_replace_fw`, `mpt_ioctl_command`, and HP host/target info records.

## Control Flow
User space populates `mpt_ioctl_header` with IOC number, port, and maximum data size, then passes one of the `_IOWR` or `_IOR` commands to `mptctl.c`. Variable-length commands place flexible trailing arrays at the end of the structure, such as target IDs, event entries, replacement firmware bytes, or raw MPI frames.

## State and Persistence
This header defines ABI shapes rather than storage. Its fields describe data copied across the user/kernel boundary and therefore persist as a compatibility contract for existing tools. Firmware replacement and raw command buffers are caller-owned until copied by the driver.

## Dependencies and Integration Points
The header integrates kernel ioctl encoding, `__user` pointers, compat support under `CONFIG_COMPAT`, and HP legacy tooling. The adapter type constants map driver bus types to SCSI, FC, FC-IP, and SAS interface identifiers consumed by management applications.

## Risks and Edge Cases
Several structures contain user pointers and flexible one-element trailing arrays, so size calculations in the implementation must remain exact. ABI revisions exist because of alignment and PCI-info layout changes; changing fields would break older tools. Compat structures are only available in kernel builds with `CONFIG_COMPAT`. Raw command fields expose multiple independent sizes and pointers that require strict validation by `mptctl.c`.

## Test Signals
Tests should verify ioctl numbers remain stable, structure sizes match expected 32-bit and 64-bit ABIs, all `MPTIOCINFO` revisions are accepted, compat pointer translation works, and variable-length commands reject undersized `maxDataSize` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptdebug.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptdebug.h

## Purpose
`mptdebug.h` centralizes Fusion MPT debug category bits, conditional print macros, and optional verbose frame dump helpers. It lets each protocol driver compile debug logging behind `CONFIG_FUSION_LOGGING` and gate runtime output through `ioc->debug_level`.

## Important APIs, Types, and Functions
Debug bits include `MPT_DEBUG`, `MPT_DEBUG_MSG_FRAME`, `MPT_DEBUG_SG`, `MPT_DEBUG_EVENTS`, `MPT_DEBUG_VERBOSE_EVENTS`, `MPT_DEBUG_INIT`, `MPT_DEBUG_EXIT`, `MPT_DEBUG_FAIL`, `MPT_DEBUG_TM`, `MPT_DEBUG_DV`, `MPT_DEBUG_REPLY`, `MPT_DEBUG_HANDSHAKE`, `MPT_DEBUG_CONFIG`, `MPT_DEBUG_DL`, `MPT_DEBUG_RESET`, `MPT_DEBUG_SCSI`, `MPT_DEBUG_IOCTL`, `MPT_DEBUG_FC`, `MPT_DEBUG_SAS`, `MPT_DEBUG_SAS_WIDE`, and `MPT_DEBUG_36GB_MEM`. Category macros include `dprintk`, `dsgprintk`, `devtprintk`, `dtmprintk`, `dctlprintk`, `dfcprintk`, and similar wrappers. Verbose helpers dump firmware download, request, reply, and task-management frames when `MPT_DEBUG_VERBOSE` and logging are enabled.

## Control Flow
Callers wrap `printk()` calls in a category macro. With logging enabled, `MPT_CHECK_LOGGING()` checks `IOC->debug_level & BITS` before executing the command. Without logging, the macro compiles to a no-op. Verbose dump functions additionally check message-frame or task-management bits before iterating over little-endian frame words.

## State and Persistence
The file stores no state. Runtime behavior depends on per-adapter `debug_level`, which can be set via module parameter or sysfs according to the header comments. Log output persists only through the kernel logging facility.

## Dependencies and Integration Points
It depends on `MPT_ADAPTER` being visible from `mptbase.h`, endian conversion helpers, and kernel `printk`. The macros are used throughout the Fusion base, SCSI, FC, SAS, LAN, and ioctl modules to avoid each file carrying its own logging gates.

## Risks and Edge Cases
Macros evaluate caller-provided command blocks, so arguments must be side-effect safe when logging is disabled. Verbose dump helpers assume valid frame pointers and sizes such as `ioc->req_sz`; using them on malformed frames can read unexpected words. Logging can be extremely noisy and may expose raw command or firmware data in kernel logs.

## Test Signals
Build tests should cover `CONFIG_FUSION_LOGGING` on and off, plus `MPT_DEBUG_VERBOSE` on and off. Runtime tests can set `debug_level` bits and confirm only matching categories emit logs while no-op builds produce no references to verbose helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptfc.c -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptfc.c

## Purpose
`mptfc.c` is the Fibre Channel SCSI host driver for LSI Fusion MPT FC adapters. It binds supported FC PCI IDs, attaches the common MPT base, registers a SCSI host and FC transport, discovers remote FC ports through firmware config pages, maps them to SCSI targets/LUNs, and routes I/O and error recovery through the common `mptscsih` layer.

## Important APIs, Types, and Functions
The main kernel contracts are `mptfc_driver_template`, `mptfc_pci_table`, `mptfc_transport_functions`, and `mptfc_driver`. Module parameters are `mptfc_dev_loss_tmo` and `max_lun`. Key functions include `mptfc_probe()`, `mptfc_remove()`, `mptfc_init()`, `mptfc_exit()`, `mptfc_qcmd()`, `mptfc_target_alloc()`, `mptfc_target_destroy()`, `mptfc_sdev_init()`, `mptfc_abort()`, `mptfc_dev_reset()`, `mptfc_bus_reset()`, `mptfc_event_process()`, `mptfc_ioc_reset()`, `mptfc_GetFcPortPage0()`, `mptfc_GetFcDevPage0()`, `mptfc_register_dev()`, `mptfc_rescan_devices()`, and `mptfc_setup_reset()`.

## Control Flow
Module init attaches FC transport, registers three base callbacks for I/O completion, task management, and internal scan/DV commands, installs event and reset handlers, and registers the PCI driver. Probe calls `mpt_attach()`, verifies the IOC is operational and initiator-capable, allocates a `Scsi_Host`, sets queue and SGE limits, creates `ScsiLookup`, adds the host, builds a workqueue, fetches FC port pages, applies Page1 defaults, and performs an initial rport rescan. SCSI commands validate rport readiness and then delegate to `mptscsih_qcmd()`. Firmware rescan events queue work that refreshes port attributes, walks FC Device Page0 entries, registers or updates remote ports, and deletes ports still marked missing.

## State and Persistence
Persistent state is per IOC: `ioc->sh`, `ScsiLookup`, `fc_rports`, `fc_port_page0`, cached/dma-backed FC Port Page1 data, link-speed cache, FC work structs, and the ordered rescan workqueue. Per SCSI target state is `VirtTarget`; per LUN state is `VirtDevice`. Remote-port information is mirrored in `struct mptfc_rport_info`. State is rebuilt from firmware config pages after probe and reset, and is not stored outside memory.

## Dependencies and Integration Points
The driver integrates with PCI, SCSI mid-layer, FC transport class, workqueues, sorting, DMA config-page reads, and the common `mptscsih` SCSI implementation. It consumes MPI FC Port and FC Device config pages through `mpt_config()`, uses base reset/event callbacks, and exposes host/rport attributes through `scsi_transport_fc`.

## Risks and Edge Cases
Discovery relies on repeated config-page polling and can wait up to roughly 40 seconds for firmware discovery to settle. The code assumes only port 0 populates the single allocated SCSI host attributes. Reset and rescan work manipulate rport registration state asynchronously, so stale `starget`/`vtarget` mappings must be guarded. Error handlers first block on FC rport readiness; if the IOC remains inactive, recovery fails. Queue-depth and SGE calculations must match IOC chain-depth facts or DMA request construction can overrun hardware limits.

## Test Signals
Useful validation includes FC PCI probe/remove, SCSI host registration, initial rport discovery from synthetic FC Device Page0 data, rport deletion/re-addition on rescan events, link status change handling, IOC reset setup/post paths, queuecommand rejection for missing rports, and SCSI error-handler flows for abort, device reset, and bus reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptlan.c -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptlan.c

## Purpose
`mptlan.c` implements IP-over-Fibre-Channel networking for Fusion MPT adapters whose firmware exposes the LAN protocol. It registers a Fibre Channel network device, posts receive bucket buffers to firmware, maps outbound skbs into LAN send requests, processes turbo and normal LAN replies, and converts FC encapsulated frames into Linux network packets.

## Important APIs, Types, and Functions
Important private types are `BufferControl`, `mpt_lan_priv`, and `mpt_lan_ohdr`. The netdev operations are `mpt_lan_open()`, `mpt_lan_close()`, `mpt_lan_sdu_send()`, and `mpt_lan_tx_timeout()`. Firmware callbacks and handlers include `lan_reply()`, `mpt_lan_send_turbo()`, `mpt_lan_send_reply()`, `mpt_lan_receive_post_turbo()`, `mpt_lan_receive_post_reply()`, `mpt_lan_receive_post_free()`, `mpt_lan_post_receive_buckets()`, `mpt_lan_reset()`, `mpt_lan_ioc_reset()`, and `mpt_lan_event_process()`. Device lifecycle is `mpt_lan_init()`, `mpt_lan_exit()`, `mptlan_probe()`, `mptlan_remove()`, and `mpt_register_lan_device()`.

## Control Flow
Module init registers a base callback context, reset handler, and MPT protocol driver. Probe scans IOC ports for `MPI_PORTFACTS_PROTOCOL_LAN`, allocates an FC netdev, initializes MTU and MAC address from LAN config Page1, and registers the device. Open sends a LAN reset, allocates TX/RX context stacks and buffer-control arrays, posts receive buckets, registers event handling, and starts the queue. Transmit pops a TX context, obtains an MPT frame, maps skb payload for DMA, builds a LAN send request with a transaction context and 64-bit SGE, posts the frame, and frees the skb when firmware returns a turbo or normal send reply. Receive replies identify bucket contexts, optionally copy small or multi-bucket packets into new skbs, recycle contexts, decrement posted-bucket counts, deliver the skb to `netif_rx()`, and schedule bucket refill when low.

## State and Persistence
Per-netdev state in `mpt_lan_priv` tracks the adapter pointer, port number, posted-bucket count, bucket threshold, free TX/RX context stacks, TX/RX `BufferControl` arrays, firmware queue limits, posted/received counters, delayed refill work, and active flag. Per-buffer state holds skb, DMA address, and length. Adapter state stores `ioc->netdev`. All state is volatile and rebuilt on open/probe; close/reset returns or frees outstanding DMA buffers.

## Dependencies and Integration Points
The driver depends on the Linux netdevice and FC device helpers (`alloc_fcdev`, FC address length, FC LLC/SNAP parsing), DMA mapping APIs, delayed work, the Fusion base message-frame/callback system, and MPI LAN request/reply definitions. It consumes port facts and LAN config pages populated by the base driver.

## Risks and Edge Cases
The code has fragile context-stack accounting for TX and RX buckets; underflow stops queues or fails posting. DMA mapping return values are not checked. Receive path comments and warnings document firmware bucket-count mismatch and a broadcast-byte-swap firmware bug. Some debug text is old and noisy. Reset and close paths must avoid double-freeing posted skbs while firmware still owns buckets. Multi-bucket and small-packet copy paths must recycle contexts correctly or leak buckets.

## Test Signals
Validation should include netdev registration for LAN-capable ports, open/close leak checks, TX completion for turbo and normal replies, RX for single, small-copy, and multi-bucket packets, bucket refill threshold behavior, IOC reset pre/post behavior, MTU boundary traffic from 96 to 65280 bytes, DMA mapping fault injection, and packet type/protocol parsing for broadcast, multicast, IP, ARP, and 802.2 frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptlan.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptlan.h

## Purpose
`mptlan.h` is the local header for the Fusion MPT IP-over-FC network driver. It includes the kernel networking and MPT base dependencies, defines module metadata, LAN queue/MTU constants, reset resource flags, debug print wrappers, and helper macros for converting netdevs to private adapter state.

## Important APIs, Types, and Functions
Key constants are `MPT_LAN_MAX_BUCKETS_OUT`, `MPT_LAN_BUCKET_THRESH`, `MPT_LAN_BUCKETS_REMAIN_MISMATCH_THRESH`, `MPT_LAN_RX_COPYBREAK`, `MPT_LAN_TX_TIMEOUT`, `MPT_TX_MAX_OUT_LIM`, `MPT_LAN_MIN_MTU`, `MPT_LAN_MAX_MTU`, `MPT_LAN_MTU`, `MPT_LAN_NAA_RFC2625`, `MPT_LAN_NAA_QLOGIC`, and reset resource flags for returning posted buckets and pending transmits. Helper macros include `dioprintk`, `dlprintk`, `NETDEV_TO_LANPRIV_PTR`, `NETDEV_PTR_TO_IOC_NAME_s`, and `IOC_AND_NETDEV_NAMES_s_s`.

## Control Flow
`mptlan.c` includes this header first to pull in Linux networking primitives and `mptbase.h`. Compile-time debug symbols choose whether IO and LAN debug macros emit `printk()` calls or compile to `no_printk()`. Runtime code uses the netdev helper macros in log statements and adapter lookups.

## State and Persistence
The header defines constants and macros only. Persistent state is allocated in `struct mpt_lan_priv` inside `mptlan.c`; this header constrains that state through queue limits, MTU bounds, and timeout settings.

## Dependencies and Integration Points
It integrates the LAN driver with Linux module, netdevice, FC device, skbuff, ARP hardware type, workqueue, delay, uaccess, IO, and the Fusion base header. The MTU defaults follow RFC2625 IP-over-FC sizing.

## Risks and Edge Cases
Changing queue constants can break firmware assumptions about maximum buckets and transaction contexts. The debug macros are compile-time only and do not honor `mptdebug.h` runtime categories. Helper macros assume `netdev_priv()` is a valid `mpt_lan_priv`, so they are unsafe for unrelated netdevs.

## Test Signals
Compile coverage should verify the header works with `mptlan.c` and that debug symbols on/off build cleanly. Runtime tests should verify default MTU, min/max MTU enforcement, watchdog timeout, and log helper paths through normal open, TX/RX, reset, and close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptlan.h -->
