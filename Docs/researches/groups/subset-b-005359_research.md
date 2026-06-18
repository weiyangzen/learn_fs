# Research: subset-b-005359

Grouped research report for the subset B work item. Each source file section is wrapped for reconciliation into the mapped source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_intr.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_intr.h

### Purpose
Defines the Cisco SNIC vNIC interrupt-control register layout and small inline helpers used by the SNIC interrupt path to mask, unmask, and return interrupt credits to hardware. The file is a hardware ABI header: `struct vnic_intr_ctrl` mirrors the memory-mapped interrupt control table, while `struct vnic_intr` binds a software index and `struct vnic_dev` to that MMIO block.

### Important APIs, Types, and Constants
- `VNIC_INTR_TIMER_MAX`, `VNIC_INTR_TIMER_TYPE_ABS`, and `VNIC_INTR_TIMER_TYPE_QUIET` constrain interrupt coalescing timer programming.
- `struct vnic_intr_ctrl` exposes register offsets for `coalescing_timer`, `coalescing_value`, `coalescing_type`, `mask_on_assertion`, `mask`, `int_credits`, and `int_credit_return`.
- `struct vnic_intr` stores the interrupt index, owning `vnic_dev`, and `ctrl` MMIO pointer.
- Inline APIs `svnic_intr_mask()`, `svnic_intr_unmask()`, `svnic_intr_credits()`, `svnic_intr_return_credits()`, and `svnic_intr_return_all_credits()` are the hot-path helpers.
- Out-of-line lifecycle functions `svnic_intr_alloc()`, `svnic_intr_init()`, `svnic_intr_clean()`, and `svnic_intr_free()` are implemented elsewhere.

### Control Flow and State
The interrupt handler path reads `int_credits`, combines returned credits with optional unmask and timer-reset bits in `svnic_intr_return_credits()`, and writes `int_credit_return`. `svnic_intr_return_all_credits()` is a convenience wrapper that reads the current credit count and returns all credits while unmasking and resetting the timer. Masking state is held in hardware via the MMIO `mask` register rather than in software.

### Dependencies and Integration Points
The header depends on Linux PCI/MMIO helpers and `vnic_dev.h`. SNIC ISR code calls these helpers after completion queue servicing, especially MSI-X handlers that return completion credits. Correctness depends on the register layout matching firmware/hardware expectations.

### Risks and Test Signals
Risk concentrates around MMIO ordering and bit packing: the credit field is 16 bits, with unmask at bit 16 and reset timer at bit 17. Tests should exercise ISR credit return, interrupt coalescing configuration, and sustained completion load to catch lost interrupts, stuck masks, or coalescing timer regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_intr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_resource.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_resource.h

### Purpose
Defines the vNIC PCI resource table ABI used by SNIC and related Cisco virtual NIC drivers to discover hardware regions inside PCI BARs. It provides the magic/version header and resource-type enumeration consumed by `vnic_dev` discovery code.

### Important APIs, Types, and Constants
- `VNIC_RES_MAGIC` is the ASCII `vnic` signature and `VNIC_RES_VERSION` is the resource table version.
- `enum vnic_res_type` names BAR-backed resources such as work queues, receive queues, completion queues, NIC config, interrupt control/table/PBA regions, device command regions, pass-through pages, subvnic resources, multiqueue resources, and `RES_TYPE_DEVCMD2`.
- `struct vnic_resource_header` stores resource table `magic` and `version`.
- `struct vnic_resource` stores `type`, `bar`, `bar_offset`, and `count`, which lets callers map an indexed resource of a given type.

### Control Flow and State
This header has no executable control flow. Runtime state is in the device resource table exposed by firmware. Consumers scan entries until `RES_TYPE_EOL`, validate the header, and use `bar` plus `bar_offset` to derive MMIO addresses.

### Dependencies and Integration Points
The definitions are used by `vnic_dev` helpers such as resource lookup and by SNIC queue/interrupt allocation paths. `vnic_wq.c` asks `svnic_dev_get_res()` for `RES_TYPE_WQ` or `RES_TYPE_DEVCMD2`, and interrupt code asks for `RES_TYPE_INTR_CTRL`.

### Risks and Test Signals
Because this is a hardware contract, enum renumbering or structure packing changes would break probing. Tests should cover device probe on real or emulated SNIC hardware, resource count validation, and failure paths when required WQ, CQ, INTR, or DEVCMD2 resources are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_snic.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_snic.h

### Purpose
Defines the SNIC-specific configuration region delivered through Cisco vNIC device configuration. It captures firmware-provided limits and operational defaults for queue depth, data field size, I/O throttling, link-down behavior, LUN fanout, interrupt timer configuration, transport type, and host ID.

### Important APIs, Types, and Constants
- Min/max macros constrain `wq_enet_desc_count`, `maxdatafieldsize`, `io_throttle_count`, `port_down_timeout`, `port_down_io_retries`, and `luns_per_tgt`.
- `struct vnic_snic_config` stores `flags`, `wq_enet_desc_count`, `io_throttle_count`, `port_down_timeout`, `port_down_io_retries`, `luns_per_tgt`, `maxdatafieldsize`, `intr_timer`, `intr_timer_type`, `xpt_type`, and `hid`.

### Control Flow and State
The header is passive. SNIC probe/configuration code reads this structure from device-specific configuration space and copies it into the adapter state. Its fields become persistent runtime configuration for queue sizing, host discovery, SCSI target limits, interrupt coalescing, and firmware throttling.

### Dependencies and Integration Points
The values feed SNIC main/probe setup, SCSI host limit calculation, interrupt initialization, and work queue allocation. `wq_enet_desc_count` aligns with `vnic_wq` descriptor-ring allocation and `io_throttle_count` aligns with SNIC request accounting.

### Risks and Test Signals
The main risk is trusting firmware-provided values without range validation. Probe tests should cover minimum and maximum values, invalid firmware values, and interactions between `luns_per_tgt`, `io_throttle_count`, and SCSI host queue limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_snic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_stats.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_stats.h

### Purpose
Declares generic Cisco vNIC transmit and receive statistic layouts. SNIC is a SCSI-over-vNIC driver but reuses common vNIC hardware statistics, including Ethernet-like counters for frames, bytes, drops, errors, RSS, CRC, and packet-size buckets.

### Important APIs, Types, and Constants
- `struct vnic_tx_stats` includes successful frame and byte counters split by unicast/multicast/broadcast, plus drops, errors, TSO, and reserved expansion slots.
- `struct vnic_rx_stats` includes successful and total frames, byte counters, drops/no-buffer/error counters, RSS/CRC counters, frame-size buckets, and reserved expansion slots.
- `struct vnic_stats` groups TX and RX stats.

### Control Flow and State
There is no control flow. These are persistent hardware/firmware-facing counters, typically fetched or exposed through driver diagnostics. Reserved fields preserve ABI room for future counters.

### Dependencies and Integration Points
The file depends on fixed-width kernel integer types. It integrates with SNIC/vNIC stats retrieval and debug paths, not with the SCSI command path directly.

### Risks and Test Signals
The ABI risk is layout drift or width mismatch against firmware. Test signals include stable counter reads under traffic, no wrap handling assumptions beyond `u64`, and debugfs/sysfs/ethtool-style consumers reading expected offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_wq.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_wq.c

### Purpose
Implements Cisco vNIC work queue allocation, initialization, enable/disable, and cleanup for SNIC. Work queues are descriptor rings backed by DMA memory with parallel software buffer metadata, used for host-to-firmware requests and device-command queueing.

### Important APIs and Functions
- `vnic_wq_get_ctrl()` obtains the MMIO control block for a resource type and index using `svnic_dev_get_res()`.
- `vnic_wq_alloc_ring()` delegates descriptor-ring DMA allocation to `svnic_dev_alloc_desc_ring()`.
- `vnic_wq_alloc_bufs()` allocates `struct vnic_wq_buf` metadata blocks, links them into a circular list, and maps each software buffer to its descriptor address.
- `svnic_wq_alloc()` initializes normal `RES_TYPE_WQ` queues, disables hardware first, allocates ring memory, then allocates software buffers.
- `vnic_wq_devcmd2_alloc()` initializes the special `RES_TYPE_DEVCMD2` queue without software buffer metadata allocation.
- `vnic_wq_init_start()` writes ring base, ring size, fetch/posted indices, completion queue index, interrupt error settings, and resets software cursors.
- `svnic_wq_enable()`, `svnic_wq_disable()`, `svnic_wq_error_status()`, `svnic_wq_clean()`, and `svnic_wq_free()` manage runtime state and teardown.

### Control Flow and State
Allocation begins by binding a work queue to a device, acquiring MMIO control registers, disabling the queue, allocating the descriptor ring, and building circular software buffer metadata. Initialization programs the hardware ring with `VNIC_PADDR_TARGET` ORed into the physical base address and aligns `to_use`/`to_clean` with the fetch index. Disable writes `enable = 0` and polls `running` up to 100 microseconds. Cleanup requires the queue to be disabled, walks used descriptors through a caller-provided cleanup callback, resets indices and error status, and clears descriptor memory.

### Dependencies and Integration Points
The implementation depends on `vnic_dev` ring/resource helpers, Linux allocation and MMIO APIs, and `vnic_wq.h` register definitions. SNIC I/O code uses the queue to post firmware request descriptors and completion handlers use queue service helpers to release buffers.

### Risks and Test Signals
Risks include allocation failure leaks, incorrect circular buffer linking, off-by-one descriptor availability, and hardware disable timeout. The special devcmd2 path does not allocate `vnic_wq_buf` entries, so callers must not use normal post/service paths on it. Tests should cover queue allocation failure injection, disable timeout handling, descriptor post/complete wraparound, cleanup with outstanding descriptors, and probe/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_wq.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_wq.h

### Purpose
Defines the SNIC vNIC work queue MMIO register layout, software queue metadata, inline descriptor accounting/post/service helpers, and lifecycle function prototypes implemented in `vnic_wq.c`.

### Important APIs, Types, and Constants
- `struct vnic_wq_ctrl` maps hardware registers for ring base/size, posted/fetch indices, CQ index, enable/running bits, DCA value, error interrupt controls, and error status.
- `struct vnic_wq_buf` tracks one descriptor's associated OS buffer, DMA address, length, index, SOP flag, descriptor pointer, and linked-list next pointer.
- Buffer block macros define 32/64-entry block sizing and `VNIC_WQ_BUF_BLKS_MAX` for up to 4096 descriptors.
- `struct vnic_wq` stores queue index, owning `vnic_dev`, MMIO `ctrl`, descriptor ring, buffer-block array, `to_use`, `to_clean`, and outstanding packet count.
- Inline helpers include `svnic_wq_desc_avail()`, `svnic_wq_desc_used()`, `svnic_wq_next_desc()`, `svnic_wq_post()`, and `svnic_wq_service()`.

### Control Flow and State
`svnic_wq_post()` attaches DMA/user metadata to the current buffer, advances `to_use`, and for end-of-packet descriptors issues a write memory barrier before updating the hardware `posted_index`. `svnic_wq_service()` walks from `to_clean` through the completed index, invokes a caller callback for each buffer, increments descriptor availability, and advances the clean cursor. Queue state is split between MMIO indices and software cursors.

### Dependencies and Integration Points
The header includes `vnic_dev.h` and `vnic_cq.h` because queue service callbacks receive completion queue descriptors. SNIC request submission code builds descriptors using `wq_enet_desc.h`, posts through these helpers, and completion handlers clean through `svnic_wq_service()`.

### Risks and Test Signals
The file contains a duplicated `VNIC_WQ_BUF_BLKS_NEEDED` macro definition, currently identical but still a maintainability risk. The most important correctness point is the `wmb()` before publishing `posted_index`; removing or weakening it can let hardware read stale descriptors. Tests should stress descriptor wraparound, multi-descriptor requests with SOP/EOP, completion index handling, and memory-order-sensitive DMA posting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_wq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/wq_enet_desc.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/snic/wq_enet_desc.h

### Purpose
Defines the 16-byte Ethernet-style work queue descriptor used by Cisco vNIC queues and inline encode/decode helpers. SNIC uses this descriptor format to send firmware request buffers over the vNIC work queue even though the payloads are SCSI/FNIC/SNIC control structures.

### Important APIs, Types, and Constants
- `struct wq_enet_desc` contains little-endian `address`, `length`, `mss_loopback`, `header_length_flags`, and `vlan_tag`.
- Bit masks and shifts define fields for length, MSS, loopback, header length, offload mode, EOP, CQ-entry request, FCoE encapsulation, VLAN insertion, and VLAN tag.
- Offload modes include checksum, reserved, L4 checksum, and TSO.
- `wq_enet_desc_enc()` packs host-order arguments into the little-endian descriptor fields.
- `wq_enet_desc_dec()` reverses the operation for diagnostics or validation.

### Control Flow and State
The helpers are pure pack/unpack routines. Runtime state is in descriptor rings allocated by `vnic_wq.c`; descriptor publication happens through `svnic_wq_post()` after callers encode the descriptor.

### Dependencies and Integration Points
The file relies on Linux endian conversion helpers. SNIC queue submission code calls the encoder before posting a WQ entry and requests completion queue notifications with the CQ-entry flag.

### Risks and Test Signals
Risks are bitfield truncation and endian mistakes. Boundary tests should encode/decode maximum length, MSS, and header length values, check VLAN/offload flags independently, and validate descriptor bytes consumed by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/wq_enet_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sr.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/sr.c

### Purpose
Implements the Linux SCSI CD-ROM block driver core. It registers the `sr` SCSI driver and SCSI CD-ROM block major, probes `TYPE_ROM` and `TYPE_WORM` devices, translates block requests into SCSI READ_10/WRITE_10 commands, integrates with the generic CD-ROM layer, handles media-change events, and manages disk capacity/sector-size revalidation.

### Important APIs and Functions
- `sr_template` is the `struct scsi_driver` with probe/remove, request initialization, completion, and runtime PM hooks.
- `sr_dops` is the `struct cdrom_device_ops` exported to the generic CD-ROM layer, delegating tray, lock, audio, packet, speed, status, multisession, MCN, and CDDA reads.
- `sr_probe()` allocates `struct scsi_cd`, `gendisk`, minor numbers, CD-ROM registration, runtime PM setup, capability probing, vendor initialization, and disk publication.
- `sr_init_command()` validates request/device/media state, allocates SCSI SG tables, maps block requests to READ_10 or WRITE_10, enforces hardware block alignment, caps transfer length to 16 bits, and fills command fields.
- `sr_done()` computes good bytes after SCSI completion, including partial-success handling for medium errors, volume overflow, illegal request with valid information, recovered errors, and late capacity trimming.
- `sr_check_events()` reconciles GET_EVENT_STATUS_NOTIFICATION, `sdev->changed`, and TEST_UNIT_READY to report media change/eject events robustly.
- `get_sectorsize()` issues READ_CAPACITY and normalizes 0/2340/2352-byte reports to 2048 while converting 2048-byte capacity to 512-byte sectors.
- `get_capabilities()` reads MMC mode page 0x2a, sets CD-ROM capability masks, speed, READ_CD support, audio support, writer/DVD/RAM flags, eject/changer support, and fallback SCSI-1 behavior.

### Control Flow and State
Probe claims a minor in `sr_index_bits`, guesses 2048-byte sectors, probes capabilities, initializes vendor logic, registers with the CD-ROM layer, revalidates media, and adds the disk. Open gets a SCSI device reference, resumes runtime PM, checks media changes, revalidates on change, then delegates to `cdrom_open()`. Normal block I/O flows through `sr_init_command()` into the SCSI midlayer and returns through `sr_done()`. Media event checks first use GET_EVENT, then TUR when clearing media change; repeated disagreement causes `ignore_get_event` so future checks rely on TUR. Remove deletes the gendisk and relies on disk release to unregister CD-ROM state and free `Scsi_CD`.

### State and Persistence Behavior
Persistent per-device state lives in `struct scsi_cd`: capacity, media presence, READ_CD capability, media-event mismatch counters, CD-ROM info, mutex, and disk pointer. `sdev->sector_size`, disk capacity, CD-ROM capability mask, and `sdev->changed` are updated across opens/revalidations. Runtime PM suspend refuses if media is present.

### Dependencies and Integration Points
The file integrates the block layer, blk-mq SCSI request allocation, SCSI device/error handling, runtime PM, generic CD-ROM core, and vendor/ioctl helpers from `sr.h`, `sr_ioctl.c`, and `sr_vendor.c`. The Makefile links `sr_mod` from `sr.o`, `sr_ioctl.o`, and `sr_vendor.o`.

### Risks and Test Signals
Risk centers on media-change races, GET_EVENT/TUR disagreement, block-size alignment, capacity updates near bad media, and ioctl fallback to raw SCSI. Tests should cover probe/remove, open with changed/no media, READ_CAPACITY sector sizes 512/2048/2340/2352/unsupported, read/write command generation, medium error partial completion, CD-ROM event polling, runtime suspend rejection with media, and generic packet delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sr.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/sr.h

### Purpose
Shared private header for the SCSI CD-ROM driver. It defines the `Scsi_CD` per-device structure, common timeouts/retry counts, logging helper, and cross-file prototypes used by `sr.c`, `sr_ioctl.c`, and `sr_vendor.c`.

### Important APIs, Types, and Constants
- `MAX_RETRIES`, `SR_TIMEOUT`, and `IOCTL_TIMEOUT` define default command retry and timeout policy.
- `typedef struct scsi_cd Scsi_CD` stores capacity, `scsi_device`, vendor code, multisession offset, XA/READ_CD/media flags, GET_EVENT/TUR mismatch state, `cdrom_device_info`, lock, and `gendisk`.
- `sr_printk()` prefixes messages with SCSI device and CD-ROM name.
- Prototypes expose ioctl, CD-ROM operation, audio, XA, vendor initialization, media check, and block-length switching helpers.

### Control Flow and State
This header has no executable flow, but it defines the state that carries across probe, open, media checks, block I/O, ioctl handling, and vendor multisession detection. Bitfields track capability and event behavior compactly.

### Dependencies and Integration Points
It depends on the mutex type and forward-declares `struct scsi_device`. It is the internal contract between the three `sr_mod` compilation units.

### Risks and Test Signals
Because many flags are bitfields, additions need care around type, initialization, and concurrency expectations. Media-event state is documented as protected by block layer exclusion, so tests should stress repeated event clearing/open paths and ensure no stale `changed` or `ignore_get_event` behavior leaks across media changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sr_ioctl.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/sr_ioctl.c

### Purpose
Implements the generic CD-ROM operation callbacks for the SCSI CD-ROM driver. It wraps SCSI packet commands for TOC, audio playback, tray/door control, drive/disc status, multisession metadata, media catalog number, speed selection, generic packet execution, raw sector reads, and optional XA detection.

### Important APIs and Functions
- `sr_do_ioctl()` is the central packet executor. It waits out SCSI error handling, calls `scsi_execute_cmd()`, interprets sense keys, retries UNIT_ATTENTION and becoming-ready states, marks `SDev->changed`, and maps errors to Linux/CD-ROM return codes.
- `sr_read_tochdr()` and `sr_read_tocentry()` issue READ_TOC/PMA/ATIP and decode track/session metadata.
- `sr_play_trkind()` tries PLAY_AUDIO_TI and falls back to `sr_fake_playtrkind()` for ATAPI-like devices by translating track/index ranges to PLAY_AUDIO_MSF.
- `sr_tray_move()`, `sr_lock_door()`, `sr_drive_status()`, `sr_disk_status()`, `sr_get_last_session()`, `sr_get_mcn()`, `sr_reset()`, `sr_select_speed()`, and `sr_audio_ioctl()` implement `cdrom_device_ops`.
- `sr_read_cd()` and `sr_read_sector()` read non-2048-byte sector formats using READ_CD or by temporarily switching block length through `sr_set_blocklength()`.
- `sr_is_xa()` optionally probes XA mode by raw-reading a sector when module parameter `xa_test` is enabled.

### Control Flow and State
Most callbacks build a `struct packet_command`, set command bytes, buffer, length, direction, and timeout, then delegate to `sr_do_ioctl()`. `sr_do_ioctl()` owns retry flow: UNIT_ATTENTION sets media changed and may retry up to 10 times; NOT_READY with ASC/ASCQ 04/01 sleeps two seconds and retries; invalid opcode maps to `-EDRIVE_CANT_DO_THIS`. `sr_read_sector()` remembers READ_CD support in `cd->readcd_known` and falls back to MODE_SELECT plus READ_10 when necessary.

### State and Persistence Behavior
The file updates `SDev->changed`, `cd->readcd_known`, and, through vendor helpers, `cd->device->sector_size`. It consumes `cd->ms_offset`, `cd->xa_flag`, and `cd->readcd_cdda` set elsewhere. `xa_test` is a module parameter and off by default because the probe can trigger firmware bugs.

### Dependencies and Integration Points
The implementation sits between generic `cdrom.c` operations and the SCSI midlayer. It depends on `sr.h`, SCSI sense helpers, SCSI ioctl interfaces, CD-ROM UAPI structs, user access helpers, and `sr_vendor.c` for block-length switching.

### Risks and Test Signals
Risk includes long retry sleeps in ioctl context, fragile sense-key mapping, vendor firmware that hangs on XA/raw reads, and temporary block-size switching failure. Tests should cover TOC decoding in LBA/MSF modes, no-media and becoming-ready behavior, PLAY_AUDIO_TI fallback, tray/door commands, speed clamping, READ_CD unsupported fallback, XA disabled/enabled paths, and permission-gated raw packet handling through `sr.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sr_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sr_vendor.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/sr_vendor.c

### Purpose
Holds vendor-specific SCSI CD-ROM compatibility logic for multisession and XA support. It classifies older drives, avoids commands known to hang limited devices, switches block length when needed, and computes the last-session offset used by the generic CD-ROM layer.

### Important APIs and Functions
- Vendor constants classify default MMC/SCSI-3, NEC, TOSHIBA, pre-SCSI3 writers, and Cygnal/Beurer CD-on-a-chip devices.
- `sr_vendor_init()` inspects `device->vendor`, `model`, type, and READ_CD capability to set `cd->vendor` and mask unsupported/dangerous CD-ROM capabilities.
- `sr_set_blocklength()` sends MODE_SELECT with a block descriptor, including Toshiba density quirks, and updates `device->sector_size` on success.
- `sr_cd_check()` runs after media changes to determine multisession offset, update `cd->ms_offset`, clear or set `cd->xa_flag`, restore 2048-byte block size, and mask multisession support if unsupported.

### Control Flow and State
The default path uses READ_TOC format 0x40 to fetch last-session data. NEC uses vendor command `0xde`, Toshiba uses `0xc7` and BCD MSF conversion, old writers use a two-step READ_TOC flow to locate the last finished session, and unknown vendors disable multisession. After offset discovery, `sr_cd_check()` calls `sr_disk_status()` and `sr_is_xa()` to decide XA state.

### State and Persistence Behavior
Persistent fields updated here are `cd->vendor`, `cd->cdi.mask`, `cd->ms_offset`, `cd->xa_flag`, and `cd->device->sector_size`. These influence later status reporting and raw sector reads.

### Dependencies and Integration Points
The file depends on CD-ROM constants, BCD conversion, SCSI packet command execution through `sr_do_ioctl()`, and `sr_ioctl.c` status/XA helpers. `sr.c` calls `sr_vendor_init()` during probe and `sr_cd_check()` during revalidation.

### Risks and Test Signals
Risks are firmware hangs from issuing unsupported commands, incorrect BCD/MSF-to-LBA conversion, and failure to restore 2048-byte sectors after raw reads. Tests should use representative vendor strings/models, no-multisession media, multisession offsets for each vendor branch, Toshiba block-length transitions, Cygnal command masking, and error handling when vendor commands fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sr_vendor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/st.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/st.c

### Purpose
Implements the Linux SCSI tape character driver. It probes `TYPE_TAPE` devices, creates auto-rewind and non-rewind character devices for several modes, performs tape reads/writes with buffered or direct I/O, handles filemarks/EOM/EOD/ILI sense conditions, exposes MTIO ioctl operations, manages tape positioning/partitioning/compression/default options, and publishes sysfs configuration/statistics.

### Important APIs and Functions
- `st_template` registers the SCSI driver. `init_st()` registers the `scsi_tape` class, SCSI tape char major, and SCSI driver; `exit_st()` unregisters them.
- `st_probe()` rejects incompatible OnStream devices, allocates `struct scsi_tape`, `struct st_buffer`, stats, IDR index, mode definitions, partition state, cdevs, and sysfs devices.
- `st_open()`, `st_flush()`, and `st_release()` serialize exclusive access, runtime PM, readiness checks, buffer flush, write filemarks, optional rewind, door unlock, and reference release.
- `st_read()` and `read_tape()` handle read buffering, direct I/O mapping, READ_6 generation, read-ahead, filemark/EOM/EOD/ILI sense processing, and user copies.
- `st_write()` handles fixed/variable block writes, direct I/O, buffered writes, asynchronous write-behind, EOM retry behavior, and position accounting.
- `st_do_scsi()`, `st_scsi_execute()`, `st_scsi_execute_end()`, `st_chk_result()`, and `st_analyze_sense()` are the internal SCSI request pipeline and sense/status normalization.
- `st_ioctl()`, `st_common_ioctl()`, `st_int_ioctl()`, `get_location()`, `set_location()`, `partition_tape()`, and `st_compression()` implement MTIO operations, generic SCSI ioctl pass-through, positioning, partitioning, load/unload, erase, density/block-size/drive-buffer changes, and compression mode page updates.
- Buffer helpers `new_tape_buffer()`, `enlarge_buffer()`, `normalize_buffer()`, `clear_buffer()`, `append_to_buffer()`, `from_buffer()`, `move_buffer_data()`, `sgl_map_user_pages()`, and `sgl_unmap_user_pages()` manage reserved pages and pinned user pages.

### Control Flow and State
Probe initializes conservative defaults, mode zero, partition state, request timeouts, direct-I/O preference, and character devices for each mode/rewind combination. Open obtains the tape by IDR, enforces single opener with `st_use_lock`, resumes runtime PM, allocates a minimum buffer, and calls `check_tape()`. `check_tape()` issues TEST_UNIT_READY, handles new media and readiness, reads block limits and MODE_SENSE, sets block size/density/write protection, and applies mode defaults. Read/write calls take `STp->lock`, run common checks, optionally switch partitions, set up direct or buffered I/O, and execute READ_6/WRITE_6 through the block request path. Close flushes writes, writes filemarks according to mode, handles SysV/BSD EOF positioning, switches partitions if requested, and rewinds auto-rewind devices.

### State and Persistence Behavior
Persistent state is almost entirely in `struct scsi_tape`: mode definitions, partition status, EOF/EOM/EOD state, current and requested partition, block size, density, buffering flags, write protection, cleaning request, door lock, reset-position state, media counters, and statistics. `struct st_buffer` holds buffered data, read pointer, async write request, direct-I/O mappings, reserved pages, and command status. Some defaults are module or boot parameters (`buffer_kbs`, `max_sg_segs`, `try_direct_io`, `debug_flag`, `try_rdio`, `try_wdio`). Sysfs reports mode defaults/options and atomic counters.

### Dependencies and Integration Points
The file integrates Linux character devices, sysfs classes, IDR, kref, runtime PM, SCSI midlayer, blk-mq request execution, user-page pinning, MTIO UAPI helpers, and generic SCSI ioctl pass-through. It depends on `st.h` for state definitions and `st_options.h` for compile-time defaults.

### Risks and Test Signals
Major risks are state-machine regressions around filemarks and EOM, async write completion lifetime, direct-I/O page pin/unpin correctness, reset handling via `pos_unknown`, partition switching, MODE_SELECT page-format fallback, and single-open/reference races. Tests should cover blocking and nonblocking open with no media, read/write fixed and variable block modes, filemark write/read semantics, auto-rewind and non-rewind close behavior, EOM early warning with partial writes, ILI residual handling, MTIOCPOS/MTIOCGET/MTIOCTOP operations, partition creation/switching, compression toggles, direct-I/O fallback on alignment or mapping failure, sysfs stats, probe/remove while references exist, and error injection for SCSI sense keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/st.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/st.h

### Purpose
Defines the private data model and state constants for the SCSI tape driver. It is the structural contract consumed by `st.c` for command status, request lifetime, buffering, mode definitions, partition status, statistics, per-tape state, EOF/read/write/ready states, door locking, and sense flags.

### Important APIs, Types, and Constants
- `struct st_cmdstatus` stores normalized SCSI result, sense header, residual/remainder, fixed/descriptor format, deferred state, and FMK/EOM/ILI flags.
- `struct st_request` wraps a SCSI command, sense buffer, result, owning tape, completion pointer, and mapped bio.
- `struct st_buffer` tracks reserved buffer pages, pinned user pages, direct-I/O state, buffered byte counts, read pointer, async request, command status, and request mapping data.
- `struct st_modedef` stores per-mode behavior and defaults plus cdev/device pointers for auto-rewind and non-rewind nodes.
- `struct st_partstat` stores per-partition read/write state, EOF state, setmark status, last visited block, and driver-estimated block/file numbers.
- `struct scsi_tape_stats` contains atomic read/write/other counts, bytes, residual count, in-flight count, timing totals, and last request sizes.
- `struct scsi_tape` is the main per-device object with SCSI device pointer, lock/completion, buffer, mode array, partition states, readiness/write protection, block/density/compression/default flags, media/reset counters, debug counters, name, kref, and stats pointer.
- Constants define four modes, four partitions, maximum tape entries, EOF/EOM/EOD transitions, rw states, ready states, door lock states, QFA commands, option trinary values, and sense flag masks.

### Control Flow and State
This header contains no executable control flow, but the constants encode the state machine used by `st.c`. EOF states progress through filemark hit, filemark consumed, EOM/EOD transitions, and error/early-warning states. Ready and door-lock states gate open/read/write/ioctl behavior.

### Dependencies and Integration Points
It depends on completions, mutexes, krefs, and SCSI command definitions. It is private to the tape driver and is paired with `st_options.h` for default values.

### Risks and Test Signals
Because the state structures are broad and shared across many `st.c` paths, changes can silently break close semantics, statistics, or ioctl reporting. Test signals should check MTIOCGET fields after read/write/filemark/EOM paths, kref release after remove, direct-I/O mapping cleanup, and sysfs stats consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/st.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/st_options.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/st_options.h

### Purpose
Provides compile-time default policy for the SCSI tape driver. These macros seed module-level defaults and per-mode settings in `st.c`, while many can later be overridden through module parameters or MTSETDRVBUFFER/MT_ST_OPTIONS ioctl controls.

### Important APIs, Types, and Constants
- `TRY_DIRECT_IO`, `ST_NOWAIT`, `ST_IN_FILE_POS`, `ST_RECOVERED_WRITE_FATAL`, and `ST_DEFAULT_BLOCK` set core behavior for direct I/O, immediate commands, positioning assumptions, recovered write errors, and fallback block size.
- Buffer sizing defaults are `ST_FIXED_BUFFER_BLOCKS`, `ST_MAX_SG`, `ST_FIRST_SG`, and `ST_FIRST_ORDER`.
- Per-drive/mode defaults include `ST_TWO_FM`, `ST_BUFFER_WRITES`, `ST_ASYNC_WRITES`, `ST_READ_AHEAD`, `ST_AUTO_LOCK`, `ST_FAST_MTEOM`, `ST_SCSI2LOGICAL`, `ST_SYSV`, and `ST_SILI`.
- `ST_BLOCK_SECONDS` controls how long blocking open waits for a drive to become ready.

### Control Flow and State
The file has no executable flow. `st.c` reads these macros during module initialization, probe, and mode initialization to seed runtime fields such as `try_direct_io`, `do_async_writes`, `do_buffer_writes`, `do_read_ahead`, `two_fm`, `fast_mteom`, `sili`, and readiness wait behavior.

### Dependencies and Integration Points
This header is included only by `st.c` before `st.h`. Its values interact with module parameters (`buffer_kbs`, `max_sg_segs`, `try_direct_io`) and MTIO option ioctls that can modify per-device/per-mode behavior after probe.

### Risks and Test Signals
Default changes alter user-visible tape semantics. Tests should verify default fixed buffer size, direct-I/O attempts and fallback, async write behavior, read-ahead behavior, auto-rewind/non-rewind close behavior, no automatic door lock by default, and the 120-second blocking-open readiness policy when a drive is becoming ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/st_options.h -->
