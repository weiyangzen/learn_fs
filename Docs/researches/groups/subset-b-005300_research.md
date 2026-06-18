# subset-b-005300 grouped research

Work item: `subset-b-005300`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid.h

## Purpose
This header is the private interface for the older MegaRAID SCSI driver path outside the `megaraid/` subdirectory. It defines firmware mailbox layouts, passthrough packets, scatter-gather elements, adapter soft state, command state flags, I/O port helpers, ioctl structures, and forward declarations for the legacy driver's implementation. The file is not a standalone module, but it is the binding contract between the legacy C file, SCSI mid-layer callbacks, PCI resources, DMA memory, `/proc`, and private management ioctls.

## Important APIs, Types, and Constants
The main firmware-facing layouts are `struct mbox_out`, `struct mbox_in`, `mbox_t`, `mbox64_t`, `mega_passthru`, `mega_ext_passthru`, `mega_sglist`, and `mega_sgl64`. They encode the 32-bit and 64-bit mailbox command protocol, including command id, LBA, transfer address, logical drive, SG count, completion array, poll, and ack fields.

`scb_t` is the legacy driver's command object. It carries a raw mailbox, DMA bookkeeping, SCSI command pointer, SG memory, passthrough memory, state bits such as `SCB_FREE`, `SCB_PENDQ`, `SCB_ISSUED`, `SCB_ABORT`, and `SCB_RESET`, and DMA type/direction fields. `adapter_t` is the large per-controller state container: PCI/MMIO handles, aligned mailbox memory, free/pending/completed command lists, host pointer, inquiry buffers, logical drive metadata, SCSI channel mapping, interrupt mode flags, internal command synchronization, and clustering support.

The ioctl ABI is represented by `struct uioctl_t`, `nitioctl_t`, `megacmd_t`, `megastat_t`, `struct mcontroller`, and adapter query opcodes such as `MEGAIOC_QNADAP`, `MEGAIOC_QDRVRVER`, and `MEGAIOC_QADAPINFO`. The file also declares legacy internal entry points such as `mega_query_adapter`, `issue_scb`, `megaraid_queue`, `mega_build_cmd`, interrupt handlers, abort/reset handlers, passthrough builders, logical-drive deletion helpers, and internal command helpers.

## Control Flow and State
The intended control flow is a classic SCSI host adapter lifecycle. Probe code allocates an `adapter_t`, sets up mailbox memory, initializes SCB pools, asks firmware for inquiry/product capabilities, registers a SCSI host, then queue callbacks translate `struct scsi_cmnd` requests into SCBs. SCBs move from the free list to pending, then firmware-owned issued state, then completed, and finally back to free after DMA unmap and SCSI completion.

The state model is list-heavy and protected with a per-adapter spinlock plus an internal-command mutex/completion pair. `adapter_t.flag` stores controller state such as `IN_ABORT`, `IN_RESET`, `BOARD_MEMMAP`, `BOARD_IOMAP`, `BOARD_40LD`, and `BOARD_64BIT`. Logical drives are represented through channel tables, boot-drive fields, `support_random_del`, and `read_ldidmap`. Internal synchronous commands use `int_scb`, `int_mtx`, `int_status`, and `int_waitq`.

## Dependencies and Integration Points
This header depends on Linux SCSI, PCI, DMA, spinlock, mutex, procfs, and user-copy APIs. Its I/O port macros wrap low-level `inb_p` and `outb_p` operations, while memory-mapped variants are implemented elsewhere. It exposes integration with SCSI queueing, SCSI error handling, private ioctl compatibility, firmware mailbox commands, firmware inquiry/configuration structures, cluster reservations, BIOS private data, and optional `/proc` reporting.

## Risks and Test Signals
The structs are packed firmware ABI, so field size, alignment, and 32-bit versus 64-bit pointer handling are high risk. Several user ABI structures carry raw user pointers and fixed-size buffers, making compat and bounds validation important. The SCB lifecycle is sensitive to list ownership and interrupt/error races. Test signals include building the legacy MegaRAID driver, probing supported PCI IDs, exercising SCSI reads/writes and passthrough commands, checking abort/reset behavior under injected timeout, verifying 64-bit DMA paths, and running ioctl compatibility tests for adapter count, driver version, adapter info, and passthrough data transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/Makefile

## Purpose
This Makefile wires the MegaRAID subdirectory into Kbuild. It selects the common management module, mailbox low-level driver, and SAS driver based on kernel configuration symbols, and defines the object list for the multi-file `megaraid_sas` module.

## Important APIs and Integration Points
`obj-$(CONFIG_MEGARAID_MM) += megaraid_mm.o` builds the common management misc-device module. `obj-$(CONFIG_MEGARAID_MAILBOX) += megaraid_mbox.o` builds the mailbox SCSI driver researched in this work item. `obj-$(CONFIG_MEGARAID_SAS) += megaraid_sas.o` builds the newer SAS module, with `megaraid_sas-objs` composed from base, fusion, fast-path, and debugfs objects.

## Control Flow, State, and Dependencies
There is no runtime control flow or persistent state in this file. Its behavior is entirely build-time: kernel config decides which modules are compiled, and Kbuild links the SAS composite object from the listed components. The key dependency is that `megaraid_mbox.o` expects headers such as `mega_common.h`, `mbox_defs.h`, and `megaraid_ioctl.h`, while `megaraid_mm.o` exports symbols used by the mailbox driver when both are enabled.

## Risks and Test Signals
The main risk is config skew: enabling the mailbox driver without the management module can still build the mailbox path, but management ioctl integration depends on exported symbols from `megaraid_mm` at module load/use time. Build tests should cover `CONFIG_MEGARAID_MM`, `CONFIG_MEGARAID_MAILBOX`, and `CONFIG_MEGARAID_SAS` as built-in and module configurations. A useful signal is `make M=drivers/scsi/megaraid` with each config combination, followed by module dependency inspection for `megaraid_mbox` and `megaraid_mm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/mbox_defs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/mbox_defs.h

## Purpose
`mbox_defs.h` is the firmware ABI definition file for mailbox-based MegaRAID controllers. It centralizes command opcodes, logical and physical drive states, cache policy constants, maximum topology sizes, packed command structures, inquiry/configuration structures, BIOS-private data, and 32-bit/64-bit scatter-gather formats used by `megaraid_mbox.c`, `megaraid_ioctl.h`, and the common management module.

## Important APIs, Types, and Constants
Mailbox commands include logical read/write (`MBOXCMD_LREAD`, `MBOXCMD_LWRITE`, `MBOXCMD_LREAD64`, `MBOXCMD_LWRITE64`), passthrough (`MBOXCMD_PASSTHRU`, `MBOXCMD_PASSTHRU64`, `MBOXCMD_EXTPTHRU`), inquiry (`MBOXCMD_ADAPTERINQ`, `MBOXCMD_ADPEXTINQ`), firmware configuration (`FC_NEW_CONFIG`, `NC_SUBOP_PRODUCT_INFO`, `NC_SUBOP_ENQUIRY3`), flush (`FLUSH_ADAPTER`, `FLUSH_SYSTEM`), random logical drive deletion (`FC_DEL_LOGDRV`, `OP_GET_LDID_MAP`, `OP_DEL_LOGDRV`), BIOS queries, channel class queries, and cluster reservation commands.

The central types are `mbox_t`, `mbox64_t`, `int_mbox_t`, `mraid_passthru_t`, `mega_passthru64_t`, and `mraid_epassthru_t`. Product and topology information is modeled by `mraid_pinfo_t`, `mraid_notify_t`, `mraid_inquiry3_t`, `mraid_adapinfo_t`, `mraid_ldrv_info_t`, `mraid_pdrv_info_t`, `mraid_inquiry_t`, `mraid_extinq_t`, `logdrv_param_t`, `logdrv_40ld_t`, `logdrv_8ld_span8_t`, `logdrv_8ld_span4_t`, `phys_drive_t`, and `disk_array_*` variants. `mbox_sgl64` and `mbox_sgl32` are the DMA SG descriptors consumed by firmware.

## Control Flow and State
This header does not execute control flow, but its layouts define the runtime handshakes. The driver writes an `mbox_t` or `mbox64_t`, marks it busy, rings the inbound doorbell, waits for status/poll/ack fields or interrupt completion, then interprets `status` and `completed[]`. Inquiry structures persist only as driver memory snapshots of firmware configuration and are refreshed by explicit firmware commands.

## Dependencies and Integration Points
The file depends only on `linux/types.h`, but its packed definitions are consumed across the mailbox stack. `megaraid_mbox.c` uses these definitions to initialize the adapter, build logical read/write and passthrough commands, discover product info, collect physical drive states, determine extended CDB and cluster support, flush caches, perform logical-drive deletion, and expose sysfs logical drive mapping. `megaraid_ioctl.h` reuses them for user management packet translation.

## Risks and Test Signals
Because every major structure is `__attribute__((packed))`, any field drift can break firmware communication or user management ABI. Transfer address fields are mostly 32-bit in the base mailbox and require the `0xFFFFFFFF` marker plus `mbox64_t` extension for 64-bit DMA. Topology constants are fixed around old controller limits, so code must guard array indexes when mapping channels, targets, logical drives, and physical drives. Test signals include firmware inquiry responses, successful 64-bit logical read/write commands, passthrough commands with sense data, random delete LD map retrieval, cluster reservation commands, and sysfs/app-handle output matching firmware state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/mbox_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/mega_common.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/mega_common.h

## Purpose
`mega_common.h` defines shared in-kernel data structures and helpers for low-level MegaRAID drivers in the subdirectory. It abstracts common SCSI command block state, adapter state, list locks, SCSI-to-adapter conversions, logical versus physical device mapping, debug logging expectations, assertions, and DMA block descriptors.

## Important APIs and Types
`scb_t` is the common command envelope used by `megaraid_mbox.c`. It stores the driver-specific CCB pointer, list link, serial number, associated `struct scsi_cmnd`, state bits, DMA direction/type, mapped device channel/target, and completion status. SCB states mirror the firmware lifecycle: free, active, pending, issued, abort, and reset. DMA types distinguish no transfer, SG-list transfer, and contiguous-buffer transfer.

`adapter_t` is the generic adapter soft state shared with the mailbox driver. It contains tasklet state, PCI and SCSI host pointers, host lock, quiesce flag, outstanding command count, kernel and user SCB pools, pending/completed lists and locks, SG limit, device ID map, low-level `raid_device` pointer, SCSI geometry limits, unique ID, IRQ, internal command buffer, management-command pools, firmware/BIOS versions, CDB size, HA/clustering fields, max sectors, queue depth, and detach state.

Macros such as `SCSIHOST2ADAP`, `SCP2ADAPTER`, `MRAID_IS_LOGICAL`, `MRAID_IS_LOGICAL_SDEV`, and `MRAID_GET_DEVICE_MAP` connect SCSI mid-layer objects to driver state and translate virtual logical-drive addresses into firmware logical-drive IDs or physical channel/target pairs.

## Control Flow and State
The header encodes the common state machine but leaves execution to low-level C files. Commands are allocated from `kscb_pool` or `uscb_pool`, optionally queued on `pend_list`, posted to firmware, collected into `completed_list`, and returned to pools. `adapter_t.quiescent` is used by the mailbox driver as a stop-issuing counter for operations such as random logical drive deletion. `adapter_t.being_detached` gates management commands during teardown.

## Dependencies and Integration Points
This file depends on kernel PCI, DMA, block, SCSI, interrupt, spinlock, mutex, delay, list, and module parameter headers. It integrates with `mbox_defs.h` through the mailbox driver's CCB layer, with `megaraid_ioctl.h` through common management user command pools, and with the SCSI host template/queue path through `struct scsi_cmnd` and `struct Scsi_Host`.

## Risks and Test Signals
The strongest risk is semantic coupling through macros: `MRAID_GET_DEVICE_MAP` assumes `adapter->device_ids` and `adapter->max_channel` are correctly initialized before SCSI queueing. `SCSIHOST2ADAP` assumes host private storage contains a pointer at index zero. The `quiescent` name is easy to misread because nonzero means stop posting in the low-level driver. Test signals include SCSI scan mapping logical drives onto the virtual channel, physical passthrough channels matching firmware topology, user-management SCBs not colliding with kernel SCBs, and hot-unplug rejecting management requests once `being_detached` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/mega_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_ioctl.h

## Purpose
`megaraid_ioctl.h` defines the user and low-level-driver ABI for the MegaRAID common management module. It provides debug levels/logging, ioctl command numbers and opcodes, legacy and extended management packet layouts, HBA information structures, DMA-pool metadata, and the adapter registration API exported by `megaraid_mm.c`.

## Important APIs, Types, and Constants
The external ioctl entry is `MEGAIOCCMD`, built on `MEGAIOC_MAGIC` and `mimd_t` from `megaraid_mm.h`. The management opcodes include `MBOX_CMD`, `GET_DRIVER_VER`, `GET_N_ADAP`, `GET_ADAP_INFO`, `GET_CAP`, `GET_STATS`, and `GET_IOCTL_VERSION`. `EXT_IOCTL_SIGN`, `MBOX_LEGACY`, `MBOX_HPE`, `APPTYPE_MIMD`, `APPTYPE_UIOC`, `IOCTL_ISSUE`, and `IOCTL_ABORT` describe packet format and command action.

`uioc_t` is the aligned common ioctl packet understood by low-level drivers. Its user-visible fields describe signature, mailbox type, application type, opcode, adapter number, command buffer pointer, transfer length, direction, and status. Its kernel-only fields preserve user buffer pointers, passthrough pointers, allocated passthrough DMA memory, list linkage, completion callback, attached DMA buffer, pool index, free flag, and timeout marker.

`mraid_hba_info_t` is a packed 256-byte controller information response. `mcontroller_t` is the older application-facing adapter-info structure. `mm_dmapool_t` describes one common-management DMA buffer pool. `mraid_mmadp_t` is the registration object passed by low-level drivers and then owned by the common management module. The exported functions are `mraid_mm_register_adp`, `mraid_mm_unregister_adp`, and `mraid_mm_adapter_app_handle`.

## Control Flow and State
The header defines the management flow used at runtime. A userspace packet enters the misc device, is converted into a kernel `uioc_t`, receives DMA-backed buffers from common-management pools, and is issued through `mraid_mmadp_t.issue_uioc`. Completion returns through `uioc_t.done`, after which data and status are copied back to the legacy user packet.

## Dependencies and Integration Points
It depends on Linux type, semaphore, timer, and the firmware definitions in `mbox_defs.h`. It is included by `megaraid_mm.h`, `megaraid_mm.c`, `megaraid_mbox.h`, and `megaraid_mbox.c`. The mailbox driver fills `mraid_mmadp_t` with `DRVRTYPE_MBOX`, a PCI device, timeout, max kioc count, and `megaraid_mbox_mm_handler`, which bridges management commands into mailbox SCBs.

## Risks and Test Signals
The file is ABI-sensitive: `uioc_t` is explicitly 1024-byte aligned, `mraid_hba_info_t` is 256-byte aligned and packed, and legacy structures must work across 32-bit and 64-bit userspace. User pointers are stored inside kernel-side packets and must be validated by conversion code. Timeout ownership is subtle because timed-out `uioc_t` objects can complete later. Test signals include CAP_SYS_ADMIN-gated ioctl access, adapter count/version/info queries, mailbox commands with read/write directions, passthrough commands copying SCSI status, timeout-induced adapter quiesce in the management module, and app-handle values matching sysfs output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mbox.c

## Purpose
`megaraid_mbox.c` is the mailbox-based MegaRAID SCSI low-level driver. It registers a PCI driver for legacy Dell/LSI/Intel/FSC/Acer/NEC controllers, initializes memory-mapped mailbox firmware handshakes, exposes a SCSI host, translates SCSI commands into firmware mailbox and passthrough commands, handles interrupts and deferred completions, implements abort/reset recovery, integrates with the common management module, and provides sysfs attributes for application handles and logical-drive mapping.

## Important APIs and Functions
Module entry and PCI lifecycle are handled by `megaraid_init`, `megaraid_exit`, `megaraid_probe_one`, `megaraid_detach_one`, and `megaraid_mbox_shutdown`. SCSI integration is through `megaraid_template_g`, `megaraid_io_attach`, `megaraid_io_detach`, `megaraid_queue_command`, `megaraid_abort_handler`, and `megaraid_reset_handler`.

Controller initialization is concentrated in `megaraid_init_mbox`, `megaraid_alloc_cmd_packets`, `megaraid_mbox_setup_dma_pools`, `megaraid_mbox_product_info`, `megaraid_mbox_extended_cdb`, `megaraid_mbox_support_ha`, `megaraid_mbox_support_random_del`, `megaraid_mbox_get_max_sg`, `megaraid_mbox_enum_raid_scsi`, and `megaraid_sysfs_alloc_resources`. Command path helpers include `megaraid_alloc_scb`, `megaraid_dealloc_scb`, `megaraid_mbox_mksgl`, `mbox_post_cmd`, `megaraid_mbox_build_cmd`, `megaraid_mbox_runpendq`, `megaraid_mbox_prepare_pthru`, and `megaraid_mbox_prepare_epthru`. Completion and firmware polling are handled by `megaraid_ack_sequence`, `megaraid_isr`, `megaraid_mbox_dpc`, `mbox_post_sync_cmd`, `mbox_post_sync_cmd_fast`, and `megaraid_busywait_mbox`.

Common-management integration uses `megaraid_cmm_register`, `megaraid_cmm_unregister`, `megaraid_mbox_mm_handler`, `megaraid_mbox_mm_command`, `wait_till_fw_empty`, `megaraid_mbox_mm_done`, and `gather_hbainfo`. Sysfs logical-drive support uses `megaraid_sysfs_get_ldmap`, its timeout/done callbacks, `megaraid_mbox_app_hndl_show`, and `megaraid_mbox_ld_show`.

## Control Flow and State
Probe enables PCI, sets bus mastering, allocates `adapter_t`, sets a 32-bit DMA mask, initializes pools/lists/locks, initializes the mailbox controller, registers with `megaraid_mm`, stores PCI driver data, allocates a SCSI host, and scans it. Mailbox initialization maps BAR0, allocates an aligned shared mailbox, internal DMA buffer, kernel SCB array, mailbox/passthrough/SG DMA pools, performs a firmware sync command, requests IRQ, reads product info, detects extended CDB support, detects HA/initiator ID, builds the device map, detects random logical-drive deletion support, gets max SG size, classifies channels, allocates sysfs command resources, optionally upgrades DMA mask to 64-bit, and initializes the completion tasklet.

Queueing starts with `megaraid_mbox_build_cmd`. Logical drive commands on the virtual channel become read/write mailboxes, logical passthrough inquiry/capacity commands, or cluster reservation commands. `MODE_SENSE` and some unsupported/invalid requests are completed without firmware. Physical device commands become standard or extended passthrough packets depending on max CDB size. `megaraid_mbox_mksgl` maps the SCSI buffer and fills 64-bit SG descriptors. `megaraid_mbox_runpendq` places SCBs on the pending list and posts them until the mailbox is busy or the adapter is quiesced. `mbox_post_cmd` copies the per-command mailbox into the adapter mailbox, assigns `cmdid` from the SCB serial number, increments `outstanding_cmds`, marks firmware busy, and rings the inbound doorbell.

The interrupt path acknowledges the outbound doorbell signature, reads `numstatus` and completed command ids, decrements `outstanding_cmds`, attaches firmware status to SCBs, splices them to `completed_list`, and schedules the tasklet. The tasklet handles management completions separately, converts firmware status into SCSI result/sense data, optionally hides configured RAID member disks from physical scan, unmaps DMA, frees the SCB, and calls `scsi_done`.

State is stored in `adapter_t` plus `mraid_device_t`. Persistent in-memory state includes SCB pools, pending/completed lists, outstanding command count, firmware version, BIOS version, max CDB size, HA/init ID, channel/device mapping, physical drive states, random-delete support, current LD map, sysfs command buffer, and hardware error flag. Hardware persistent state is not modified except by firmware commands such as flush, reservation reset, and logical-drive deletion.

## Dependencies and Integration Points
The file depends on kernel PCI, SCSI, DMA, IRQ, tasklet, timer, waitqueue, sysfs, module parameter, and ioremap APIs, plus local headers `megaraid_mbox.h`, `mega_common.h`, `mbox_defs.h`, and `megaraid_ioctl.h`. It integrates with the common management module through exported registration symbols, with userspace through `/dev/megadev0` and sysfs attributes, with firmware through inbound/outbound doorbells and packed mailbox structures, and with the SCSI mid-layer through queue, scan, abort, reset, and completion callbacks.

## Risks and Test Signals
Risk is concentrated in concurrency and firmware ABI handling. SCBs can be owned by the free pool, pending list, firmware, completed list, management pool, or sysfs command path; abort/reset code must not double-complete or leak them. `adapter->quiescent` is a stop-posting counter even though the common management adapter uses a same-named field with the opposite meaning. Timeout paths can leave management commands completing after the caller has returned. DMA handling assumes SG count never exceeds `adapter->sglen`, mailbox alignment is 16-byte correct, and 64-bit commands use the mailbox extension correctly. Reset waits up to `MBOX_RESET_WAIT + MBOX_RESET_EXT_WAIT`, marks `hw_error` on failure, and clears cluster reservations on success.

Strong test signals include building and loading `megaraid_mbox`, successful PCI probe/remove, SCSI scan showing virtual logical-drive channel and physical channels, read/write I/O through logical mailboxes, passthrough inquiry/capacity and extended CDB paths, `unconf_disks` behavior for physical disks, sysfs `megaraid_mbox_app_hndl` and `megaraid_mbox_ld`, management ioctl adapter info and mailbox commands, random logical drive deletion quiescing and resuming pending I/O, shutdown cache flush, abort of pending commands, reset with outstanding commands, and injected firmware nonresponse setting `hw_error`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mbox.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mbox.h

## Purpose
`megaraid_mbox.h` is the mailbox driver's private header. It collects the driver version, supported PCI device/subsystem IDs, command limits, timeout defaults, mailbox CCB layout, mailbox-controller soft state, doorbell register helpers, and bridge macros used by `megaraid_mbox.c`.

## Important APIs, Types, and Constants
The file defines `MEGARAID_VERSION` and `MEGARAID_EXT_VERSION`, many Dell/LSI/Intel controller PCI identifiers, and mailbox operating limits: `MBOX_MAX_SCSI_CMDS`, `MBOX_MAX_USER_CMDS`, default commands per LUN, default/max SG sizes, max sectors, timeout values, busy wait limits, sync wait counts, and internal buffer size.

`mbox_ccb_t` is the driver-specific command payload behind common `scb_t`. It stores raw mailbox pointers, 32-bit and 64-bit mailbox views, mailbox DMA address, 64-bit and 32-bit SG lists, passthrough and extended passthrough objects, and DMA handles. `mraid_device_t` is the low-level mailbox controller state: aligned shared mailbox memory, mailbox lock, BAR address, DMA pools for command mailboxes/passthrough/SG, per-command CCB arrays, user-management CCB arrays, physical drive state cache, scan display flags, hardware error flag, fast-load flag, channel class, sysfs mutex and command resources, random-delete support flag, and current LD map.

Macros `ADAP2RAIDDEV`, `MAILBOX_LOCK`, `IS_RAID_CH`, `RDINDOOR`, `RDOUTDOOR`, `WRINDOOR`, and `WROUTDOOR` hide low-level pointer conversion, locking, channel classification, and MMIO doorbell offsets.

## Control Flow and State
This header does not execute control flow, but `mraid_device_t` defines the state transitions in the C file. During initialization, DMA pools and aligned mailbox pointers are populated. During command issue, SCBs use entries from `ccb_list` or `uccb_list`, copy their mailbox into the shared `mbox64`, and ring doorbells. During sysfs reads, one protected `sysfs_uioc`/`sysfs_mbox64`/`sysfs_buffer` set is reused to fetch LD mapping. `hw_error`, `fast_load`, `channel_class`, `random_del_supported`, and `curr_ldmap` influence later command acceptance and device presentation.

## Dependencies and Integration Points
The header includes `mega_common.h`, `mbox_defs.h`, and `megaraid_ioctl.h`. It bridges generic adapter state from `mega_common.h`, firmware ABI from `mbox_defs.h`, and common-management packets from `megaraid_ioctl.h`. The MMIO macros assume the controller doorbell registers live at offsets `0x20` and `0x2C` from `baseaddr`.

## Risks and Test Signals
The CCB and DMA pool arrays are fixed-size, so command IDs and pool indexing must stay within `MBOX_MAX_SCSI_CMDS` and `MBOX_MAX_USER_CMDS`. Mailbox alignment and DMA handle arithmetic are critical for firmware handshakes. Doorbell offsets are hardware ABI and cannot be changed without breaking the driver. Test signals include successful initialization of all DMA pools, no alignment warnings, correct user command IDs starting after kernel command IDs, sysfs LD map serialization, doorbell interrupt completion, and error paths freeing all mailbox resources on failed probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mm.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mm.c

## Purpose
`megaraid_mm.c` implements the LSI MegaRAID common management module. It registers `/dev/megadev0` as a misc device, gates access to privileged users, translates legacy MIMD ioctl packets into the internal `uioc_t` format, allocates DMA-safe transfer buffers, dispatches commands to registered low-level drivers, waits for completion or timeout, converts results back to the legacy ABI, and exports registration helpers used by `megaraid_mbox.c`.

## Important APIs and Functions
The misc-device surface is `mraid_mm_open`, `mraid_mm_unlocked_ioctl`, and internal `mraid_mm_ioctl`. Driver command handling is in `handle_drvrcmd`, which supports driver version and adapter count locally. Adapter lookup and ioctl translation are done by `mraid_mm_get_adapter`, `mimd_to_kioc`, and `kioc_to_mimd`. Low-level dispatch and completion are handled by `lld_ioctl`, `ioctl_done`, and `lld_timedout`.

Resource management uses `mraid_mm_alloc_kioc`, `mraid_mm_dealloc_kioc`, `mraid_mm_attach_buf`, `mraid_mm_setup_dma_pools`, `mraid_mm_teardown_dma_pools`, and `mraid_mm_free_adp_resources`. Exported low-level-driver integration is implemented by `mraid_mm_register_adp`, `mraid_mm_unregister_adp`, and `mraid_mm_adapter_app_handle`. Module lifecycle is `mraid_mm_init` and `mraid_mm_exit`.

## Control Flow and State
Open requires `CAP_SYS_ADMIN`. Ioctl entry rejects non-MegaRAID commands, reads the first bytes of the user packet to distinguish the extended signature, and currently rejects the newer packet format while supporting legacy MIMD packets. Driver-level commands with opcode `0x82` can be handled locally for version and adapter count; adapter-info commands are converted into `GET_ADAP_INFO` and routed to the low-level driver.

For firmware mailbox commands, `mimd_to_kioc` chooses transfer length and direction from opcodes `0x80` and `0x81`, attaches a DMA buffer, copies user write data, translates the legacy mailbox into an internal `mbox64_t`, points regular commands at `kioc->buf_paddr`, and handles 32-bit passthrough by copying `mraid_passthru_t` into a DMA pool object. Extended passthrough from applications is rejected. `lld_ioctl` calls `adp->issue_uioc`, optionally arms a stack timer, waits on a global wait queue until `kioc->status` changes from `-ENODATA`, and marks the adapter non-accepting on timeout. `kioc_to_mimd` copies adapter info, passthrough SCSI status, data buffers, and mailbox status back to userspace.

The global state is `adapters_list_g`, `adapters_count_g`, `wait_q`, and `drvr_ver`. Each registered `mraid_mmadp_t` owns a kioc array, mailbox array, passthrough DMA pool, five data-buffer DMA pools from 4 KiB through 64 KiB, and one semaphore controlling max concurrent ioctl packets. A global mutex serializes all ioctl entrypoints.

## Dependencies and Integration Points
The module depends on miscdevice, user-copy, DMA pool, timers, wait queues, semaphores, spinlocks, mutexes, PCI device references, and local headers `megaraid_mm.h` and `megaraid_ioctl.h`. Low-level drivers integrate by calling `mraid_mm_register_adp` with a `DRVRTYPE_MBOX` registration and an `issue_uioc` callback. Userspace integrates through the legacy `/dev/megadev0` ABI and receives adapter handles generated with `MKADAP(index)`.

## Risks and Test Signals
The most important risks are legacy ABI handling, pointer compatibility, and timeout ownership. The code defines the newer extended ioctl signature but rejects it, so applications must use the old MIMD layout. Adapter lookup is by current list order, so hotplug ordering matters. `copy_to_user` of `kioc->user_data_len` can copy the full requested transfer length regardless of firmware actual length. Timed-out commands are not deallocated until late completion, so the low-level callback must eventually return or resources remain unavailable. Pool allocation falls back to dynamic DMA-pool buffers when the single preallocated buffer is busy.

Test signals include misc device registration, permission denial for non-admin opens, `MEGAIOC_QDRVRVER`, `MEGAIOC_QNADAP`, and `MEGAIOC_QADAPINFO`, regular `0x80` and alternate-buffer `0x81` mailbox commands, passthrough status copying, large transfers selecting 4/8/16/32/64 KiB DMA pools, concurrent ioctls blocking on `kioc_semaphore`, timeout marking the management adapter offline, late completion freeing timed-out packets, and unregister freeing all pools without pending commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mm.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mm.h

## Purpose
`megaraid_mm.h` is the private header for the common management module. It includes kernel and local ABI headers, defines the common-management module version and debug-level binding, declares the initial DMA buffer size, and defines `mimd_t`, the deprecated legacy ioctl packet consumed by `megaraid_mm.c`.

## Important APIs, Types, and Constants
`LSI_COMMON_MOD_VERSION` and `LSI_COMMON_MOD_EXT_VERSION` describe the module version printed at load. `LSI_DBGLVL` maps shared `con_log` filtering to the module's `dbglevel` variable. `MRAID_MM_INIT_BUFF_SIZE` sets the first common-management DMA pool size to 4096 bytes; subsequent pools double from that base in `megaraid_mm.c`.

`mimd_t` is the old application ioctl layout. It carries `inlen`, `outlen`, a union containing either raw function-control bytes or structured opcode/subopcode/adapter/buffer/length fields, an 18-byte mailbox image, an embedded `mraid_passthru_t`, and a user data pointer. The structure has conditional padding and pointer declarations for 32-bit versus 64-bit kernel word size and is packed to preserve the legacy ABI.

## Control Flow and State
The header itself has no runtime control flow, but every management ioctl begins as this `mimd_t` layout when using the supported legacy path. `megaraid_mm.c` copies it from userspace, uses opcode/subopcode to decide driver-local versus firmware-routed behavior, converts the mailbox and passthrough portions into `uioc_t` plus DMA-backed buffers, then copies status/data back into the same legacy shape.

## Dependencies and Integration Points
This file depends on Linux spinlock, fs, uaccess, module, moduleparam, PCI, list, and miscdevice headers, plus `mbox_defs.h` and `megaraid_ioctl.h`. It is included by `megaraid_mm.c`; low-level drivers do not need `mimd_t` directly, because they receive normalized `uioc_t` commands from the common management module.

## Risks and Test Signals
The packed legacy pointer layout is the central risk. 32-bit userspace on 64-bit kernels relies on compat ioctl behavior and padding matching expectations. Since newer `uioc_t` packets are rejected by the implementation, management tools that send only the extended signature will fail. Test signals include building with 32-bit and 64-bit configs, issuing old MIMD adapter queries and mailbox commands, checking that `inlen`/`outlen` drive data direction correctly, and verifying no structure size drift breaks userspace tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mm.h -->
