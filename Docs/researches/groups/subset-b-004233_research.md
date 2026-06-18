# subset-b-004233 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_ioc.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_ioc.h

## Purpose

`mpi_ioc.h` defines the LSI Fusion MPT MPI controller-management ABI: IOC initialization and facts, port facts and enable, asynchronous event notification and acknowledgement, firmware download/upload, firmware image headers, and the event payload structures shared by the Fusion base, SCSI, SAS, FC, and RAID paths. It is a protocol contract header, not executable code.

## Important APIs, Types, and Definitions

- `MSG_IOC_INIT` and `MSG_IOC_INIT_REPLY` carry driver initialization state, including `WhoInit`, reply frame sizing, high DMA address fields, reply FIFO host signaling, host page buffer SGE, message version, and header version.
- `MSG_IOC_FACTS` and `MSG_IOC_FACTS_REPLY` expose adapter-wide limits and capabilities: queue depths, request/reply frame size, firmware image size/version, number of ports, IOC exceptions, high-priority queue support, diagnostic buffers, bidirectional/EEDP/multicast/SCSIIO32/TLR capability bits, and host-page-buffer state.
- `MSG_PORT_FACTS`, `MSG_PORT_FACTS_REPLY`, `MSG_PORT_ENABLE`, and `MSG_PORT_ENABLE_REPLY` describe per-port type, protocol flags, SCSI IDs, posted command buffer limits, LAN bucket limits, and enable sequencing.
- `MSG_EVENT_NOTIFY`, `MSG_EVENT_NOTIFY_REPLY`, `MSG_EVENT_ACK`, and `MSG_EVENT_ACK_REPLY` define event subscription and acknowledgement. Event IDs cover log data, state change, bus reset, rescan, FC link/loop/logout, integrated RAID, SCSI/SAS device changes, queue full, SAS discovery/PHY/SES/broadcast/SMP/expander events, IR2 events, and log entry additions.
- Event payload types include `EVENT_DATA_SCSI`, `EVENT_DATA_SCSI_DEVICE_STATUS_CHANGE`, `EVENT_DATA_SAS_DEVICE_STATUS_CHANGE`, `EVENT_DATA_QUEUE_FULL`, `EVENT_DATA_RAID`, `MPI_EVENT_DATA_IR_RESYNC_UPDATE`, `MPI_EVENT_DATA_IR2`, FC link/loop/logout payloads, SAS SES/broadcast/PHY/discovery/error/SMP/init/expander payloads, and `EVENT_DATA_LOG_ENTRY_ADDED`.
- Firmware load types include `MSG_FW_DOWNLOAD`, `FW_DOWNLOAD_TCSGE`, `MSG_FW_DOWNLOAD_REPLY`, `MSG_FW_UPLOAD`, `FW_UPLOAD_TCSGE`, and `MSG_FW_UPLOAD_REPLY`; image type constants distinguish firmware, BIOS, NVDATA, bootloader, manufacturing, config, MegaRAID, complete image, and common boot block transfers.
- `MPI_FW_VERSION`, `MPI_FW_HEADER`, and `MPI_EXT_IMAGE_HEADER` define the firmware image metadata, signatures, product ID type/product/family masks, version strings, image chaining, load addresses, and extended image types.

## Control Flow

The normal bring-up sequence issues IOC facts to learn firmware limits, then IOC init with driver-selected reply frame size, address high bits, message/header version, and optional host page buffer/reply FIFO signaling fields. Per-port discovery follows with port facts and port enable. The base driver then enables event notification; each firmware event arrives as `MSG_EVENT_NOTIFY_REPLY` with an event ID, context, and event-specific data words. If `AckRequired` is set, the driver mirrors the event and event context into `MSG_EVENT_ACK`.

Firmware download/upload uses an MPI message with an SGL and a transaction-context SGE that identifies image offset and size. Completion reports IOC status/log info and, for uploads, actual image size. Firmware image parsers validate `MPI_FW_HEADER_SIGNATURE_*`, split product ID fields by type/product/family, and follow `NextImageHeaderOffset` for chained images or `MPI_EXT_IMAGE_HEADER` for secondary images.

## State and Persistence Behavior

The header declares wire-format state surfaces rather than kernel storage. IOC init establishes firmware runtime state such as reply frame sizing, host MFA/sense high addresses, optional host page buffer persistence, and reply signaling address. IOC facts report current firmware state and durable exception signals such as config checksum failure, invalid RAID config, firmware checksum failure, persistent table full, and unsupported metadata. Firmware download can update persistent flash/NVDATA/bootloader/config regions depending on image type, while upload exposes current flash or IOC memory contents. Event subscriptions are runtime state and must be re-established after reset.

## Dependencies and Integration Points

The layouts depend on base MPI scalar types from `mpi_type.h` and SGE unions from sibling MPI headers. `mptbase.h` includes this header for all Fusion protocol drivers. `mptbase.c` uses these definitions for adapter initialization, facts reads, event handling, event logging, event acknowledgement, RAID event text, firmware transfer, and `IOCLogInfo` decode. `mptscsih.c`, `mptsas.c`, and `mptfc.c` consume event IDs and payload structures for transport-specific topology and error handling. SAS log codes in `mpi_log_sas.h`, FC log codes in `mpi_log_fc.h`, and config/log pages in `mpi_cnfg.h` complement the status and event data defined here.

## Risks and Edge Cases

These structures are firmware ABI layouts, so field order, width, implicit padding, and numeric constants must not be changed casually. Many event payloads carry variable-length or data-dependent meanings; consumers must select the correct structure by `Event` and `EventDataLength`. `MSG_EVENT_NOTIFY_REPLY` uses a flexible `Data[]` tail, so callers must bounds-check firmware-provided data length. Several comments contain legacy offsets or obsolete fields that still document compatibility behavior. Firmware update/download image-type mistakes can overwrite persistent adapter regions. Endianness conversion is a caller responsibility when messages cross the host/IOC boundary. Event acknowledgement must use the exact event context supplied by firmware or the event may remain pending.

## Test Signals

Build coverage should include `mptbase`, `mptscsih`, `mptsas`, and `mptfc`. Runtime signals include successful IOC facts/init, correct queue/reply sizing, port facts/enable for SCSI/FC/SAS ports, event notification enable/disable transitions, required event acks, and correct decode/logging of RAID, SCSI, SAS, FC link, SAS discovery, SMP, and log-entry events. Firmware-transfer tests should verify image type, last-segment handling, actual upload size, bad image status, and no persistent writes except through explicit update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_ioc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_lan.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_lan.h

## Purpose

`mpi_lan.h` defines the MPI LAN-over-Fusion message ABI: LAN send, receive-buffer posting, reset, reply context bitfields, LAN device state, and loopback mode constants. It is used by adapters exposing LAN protocol support through MPI, especially the historical LAN-over-FC path noted in `mptbase.h`.

## Important APIs, Types, and Definitions

- `MSG_LAN_SEND_REQUEST` posts a transmit packet through an SGL array and identifies the target port through `PortNumber`.
- `MSG_LAN_SEND_REPLY` returns IOC status/log info and a `BufferContext` used to correlate completion with the host buffer.
- `MSG_LAN_RECEIVE_POST_REQUEST` posts receive buckets using `BucketCount` plus a variable SGL tail.
- `MSG_LAN_RECEIVE_POST_REPLY` returns remaining bucket count, received packet offset and length, and one or more `BucketContext` values.
- `MSG_LAN_RESET_REQUEST` and `MSG_LAN_RESET_REPLY` reset a LAN port context.
- Context macros pack and unpack `LAN_REPLY_PACKET_LENGTH`, `LAN_REPLY_BUCKET_CONTEXT`, `LAN_REPLY_BUFFER_CONTEXT`, and `LAN_REPLY_FORM`. Form values distinguish receive single, receive multiple, send single, and message context replies.
- Device and loopback constants include `MPI_LAN_DEVICE_STATE_RESET`, `MPI_LAN_DEVICE_STATE_OPERATIONAL`, and `MPI_LAN_TX_MODES_ENABLE_LOOPBACK_SUPPRESSION`.

## Control Flow

The host posts receive buffers first with `MSG_LAN_RECEIVE_POST_REQUEST`, supplying one or more DMA SGEs. Firmware later completes receive work with packet offset/length and bucket context in either a normal reply or a compact context reply word. Sends use `MSG_LAN_SEND_REQUEST` with an SGL describing the packet payload, then complete with `MSG_LAN_SEND_REPLY` and a buffer context. Reset is a short request/reply flow that targets a `PortNumber` and returns IOC status/log info.

## State and Persistence Behavior

The header does not define persistent kernel state. Runtime state lives in firmware receive buckets, posted transmit buffers, per-port LAN state, and context words that the driver must preserve until completion. Device state constants are current operational state indicators; persistent LAN configuration is represented in LAN config pages from `mpi_cnfg.h`, not in this header.

## Dependencies and Integration Points

The header depends on MPI base types and `SGE_MPI_UNION`. It is included from `mptbase.h`, making the LAN ABI visible to the Fusion base and control paths. It shares status reporting through the common `IOCStatus` and `IOCLogInfo` fields, with FC LAN log-info subclass values defined in `mpi_log_fc.h`. Port capacity is advertised through `MSG_PORT_FACTS_REPLY.MaxLanBuckets` in `mpi_ioc.h`.

## Risks and Edge Cases

The SGL tails are declared as one-element arrays, so callers must allocate message frames large enough for the requested SGE count. Context macros mutate their first argument and assume callers mask and shift already-sized values; oversized packet lengths or contexts are silently truncated by masks. `MSG_LAN_RESET_REQUEST` comments show `PortNumber` at offset `05h` even though the field follows a two-byte reserved area at byte `06h`, so layout should be verified by structure offsets rather than comments. Receive replies can describe packet data beginning at a nonzero bucket offset, which consumers must honor.

## Test Signals

Useful tests include posting receive buckets, receiving single and multiple packet forms, verifying packet offset/length extraction, sending packets with expected buffer-context completion, exercising reset while buckets are posted, and checking IOC log info for LAN SGL/context errors. Build tests should cover all Fusion code including `mptbase.h` with LAN definitions enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_lan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_fc.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_fc.h

## Purpose

`mpi_log_fc.h` defines Fibre Channel `IOCLogInfo` values returned in MPI reply messages. It is a decode table for FC initiator, FC target, LAN, MPI message-layer, link, context-manager, invalid-field, and state-change log subclasses.

## Important APIs, Types, and Definitions

- `MpiIocLogInfoFc_t` is an enum of 32-bit log values.
- The encoded format is `0xabcccccc`: type nibble `a` is FC log type `2`, subclass nibble `b` identifies firmware area, and the low bits carry subclass-specific detail.
- Initiator codes include out-of-order frame, bad SOF/EOF, overrun, RX other, subprocessor dead, RX SGL overrun, bad receive status, unexpected frame, link failure, and transmit timeout.
- Target codes include missing PDISC/login/class 3/validated login, LIP-disrupted data or response paths, missing data, outbound queue clearing after logout, and waiting-for-data after logout.
- LAN codes cover missing transaction SGL, transaction context ordering, reserved context bits, and invalid SGL flags.
- Link codes cover loop initialization timeout, already initialized loop, link not established, and CRC error.
- Invalid field and state-change ranges reserve the lower 24 bits for byte offsets or state details.

## Control Flow

This header has no runtime control flow. The control path is reply decoding: a Fusion FC command completes with `IOCStatus` and `IOCLogInfo`; driver diagnostic code tests the high nibble/type and subclass bits, then maps the value to the relevant FC failure reason. `mptbase.c` references this file when logging FC IOCLogInfo values.

## State and Persistence Behavior

The values are transient diagnostics attached to a failed or noteworthy reply. They do not create persistent driver state. However, some codes report underlying link, login, loop, or queue states that may influence later recovery, rescan, logout, target reset, or rport handling in the FC transport path.

## Dependencies and Integration Points

The enum integrates with common MPI replies from IOC, SCSI IO, FC direct-access messages, LAN messages, target mode, toolbox, and config operations through the shared `IOCLogInfo` field. It complements `mpi_ioc.h` event IDs and `mpi_fc.h` FC message definitions. `mptbase.c` includes this header for FC log decoding and points diagnostics at it.

## Risks and Edge Cases

The file lacks include guards, so repeated direct inclusion could redefine the enum if not controlled by include topology. Numeric values are ABI diagnostics from firmware; renumbering breaks log interpretation across firmware releases. Some enum entries use lower-case hex suffixes while most use upper-case style, but the numeric values are what matter. Invalid-field and state-change ranges require preserving and decoding lower 24-bit payloads rather than treating only exact enum values as meaningful.

## Test Signals

Tests should inject or capture FC replies with each subclass prefix and verify the driver logs a useful message without corrupting command completion. Error-path tests should include invalid-field offsets, link failures, LIP-disrupted target operations, CT/ELS failures, and LAN-over-FC SGL/context errors. Static checks should ensure no switch assumes the enum is exhaustive for future firmware values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_sas.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_sas.h

## Purpose

`mpi_log_sas.h` defines SAS `IOCLogInfo` bit encodings and log codes for Fusion firmware. It covers IOP-originated errors, SAS port-layer/open/link/data-transfer errors, enclosure-management failures, direct-attached SEP errors, and integrated RAID action/compatibility/device-firmware-update failures.

## Important APIs, Types, and Definitions

- `SAS_LOGINFO_NEXUS_LOSS` and `SAS_LOGINFO_MASK` support high-level nexus-loss recognition.
- Originator constants split SAS log info into IOP, PL, and IR domains, selected by `IOC_LOGINFO_ORIGINATOR_MASK`.
- `IOC_LOGINFO_CODE_MASK` and shift identify the code byte within the 32-bit value.
- IOP codes cover invalid SAS address, invalid config page variants, firmware upload failures, diagnostic message errors, task termination, enclosure management command validation, target-assist/status-send termination, target-mode aborts, and timestamp events.
- PL codes and subcodes cover open failure reasons, invalid SGL, wrong relative offset/frame length, frame transfer errors, SATA NCQ and link failures, discovery failures, config-page errors, resets, aborts, device missing delay retry, persistent reservation ownership failures, and enclosure-management transport failures.
- IR codes cover RAID action errors for volume creation/activation, physical disk creation, compatibility failures, and device firmware update mode errors.
- Convenience prefixes combine `MPI_IOCLOGINFO_TYPE_SAS` and originator bits for IOP, PL, and IR values.

## Control Flow

The header has no executable control flow. It defines the decode path for `IOCLogInfo` values returned by SAS-capable firmware. A driver receives a reply or event with nonzero log info, determines the SAS log type and originator, masks out the code and subcode fields, and maps them to transport, firmware-upload, enclosure, target-mode, or IR management diagnostics. `mptbase.c` explicitly points SAS IOCLogInfo decode users at this header.

## State and Persistence Behavior

The log values are transient observations of firmware and link state. Some codes imply durable or semi-durable conditions, such as invalid config pages, persistent table failures, unsupported metadata, RAID compatibility errors, or firmware upload flash-region failures, but the header itself stores no state. Recovery state is maintained by consumers such as SAS topology management, SCSI error handling, RAID management, and enclosure-management code.

## Dependencies and Integration Points

The prefix macros depend on `MPI_IOCLOGINFO_TYPE_SAS` and `MPI_IOCLOGINFO_TYPE_SHIFT`, defined in the common MPI headers included through `mptbase.h`. `mptscsih.c` includes this header for SCSI/SAS error logging; `mptsas.c` and `mptbase.c` consume the same values alongside SAS events from `mpi_ioc.h`, SAS control messages from `mpi_sas.h`, and SAS config pages from `mpi_cnfg.h`.

## Risks and Edge Cases

Several codes carry subcode payloads in the low bits, so exact equality checks can miss families of errors. Some historical names contain typos such as `ERR0R`; these names are source compatibility surface and should not be renamed without a compatibility plan. `PL_LOGINFO_SUB_CODE_OPEN_FAILURE_ZONE_VIOLATION` and `PL_LOGINFO_SUB_CODE_OPEN_FAILURE_ABANDON0` share the same value, so decoders should allow aliases. The header guard name is generic (`IOPI_IOCLOGINFO_H_INCLUDED`) and could collide if another file uses the same guard. Future firmware may return unknown values with known prefixes; decoders should print raw values.

## Test Signals

Tests should verify originator/code/subcode extraction, prefix matching, nexus-loss matching, unknown-code fallback, and alias handling. Runtime signals include readable diagnostics for SATA link down, open failure, invalid SGL, frame transfer error, discovery timeout, enclosure management errors, target-mode aborts, firmware upload failures, RAID creation/activation failures, and compatibility errors during `mptsas` topology or IR workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_sas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_raid.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_raid.h

## Purpose

`mpi_raid.h` defines the MPI Integrated RAID control ABI: RAID action requests/replies, volume progress indicators, SCSI IO passthrough to physical disks, and mailbox request/reply formats. It is used by Fusion management paths to create, delete, enable, disable, activate, scrub, resync, update, and inspect integrated RAID objects.

## Important APIs, Types, and Definitions

- `MSG_RAID_ACTION_REQUEST` carries an `Action`, volume ID/bus, physical disk number, message context, action data word, and optional action-data SGE.
- RAID action constants include status, indicator structure, create/delete/disable/enable volume, quiesce/enable physical IO, change volume or physical disk settings, offline/online/fail/replace physical disk, create/delete physical disk, activate/inactivate volume, set resync/data scrub rates, device firmware update mode, and set volume name.
- `ActionDataWord` flags control create behavior (`DO_NOT_SYNC`, `LOW_LEVEL_INIT`), delete behavior (keep/delete physical disks, keep/zero LBA0), disable full rebuild, activate all/inactivate all, resync/scrub rate masks, and device firmware update timeout.
- `MSG_RAID_ACTION_REPLY` returns action status, IOC status/log info, volume status, and action data.
- `MPI_RAID_VOL_INDICATOR` reports total blocks and blocks remaining for long-running operations.
- `MSG_SCSI_IO_RAID_PT_REQUEST` and reply provide SCSI passthrough to a physical disk, with CDB, LUN, control, sense address, data length, SGL, SCSI status/state, transfer count, sense count, and response info.
- `MSG_MAILBOX_REQUEST` and `MSG_MAILBOX_REPLY` provide a 10-byte command mailbox with SGL and mailbox status.

## Control Flow

Management code fills `MSG_RAID_ACTION_REQUEST` with a specific action, object identifiers, and optional DMA-backed action data, then waits for `MSG_RAID_ACTION_REPLY`. For actions returning progress, callers interpret `ActionData` or fetch an indicator structure. Physical disk passthrough follows the same shape as initiator SCSI IO: build CDB/control/sense/SGL fields, post to firmware, and translate reply SCSI/IOC status. Mailbox requests are a lower-level command path for firmware-defined RAID management operations.

## State and Persistence Behavior

Unlike many MPI headers, these messages can alter persistent storage state. Creating/deleting volumes and physical disks, zeroing LBA0, changing settings, setting volume names, setting resync/scrub rates, activation/inactivation, and firmware update mode can change metadata on disks or persistent firmware configuration. Replies report current volume and action status, but durable state is also surfaced by RAID config pages and RAID/IR events in `mpi_ioc.h`.

## Dependencies and Integration Points

The header depends on base MPI types and SGE unions. It is included by `mptbase.h`; `mptbase.c` decodes RAID events and status text, while `mptsas.c` consumes integrated RAID and IR2 events, topology state, and physical disk data. `mpi_cnfg.h` provides RAID Volume and RAID PhysDisk config pages that complement these action messages. `mpi_log_sas.h` provides IR log codes for failures returned in `IOCLogInfo`.

## Risks and Edge Cases

RAID actions are high impact and can destroy data, especially delete volume, delete physical disk, fail/offline disk, and zero LBA0 flags. Action data SGE length and format are action-specific and not self-described here. The passthrough path can send arbitrary CDBs to member disks, bypassing normal volume semantics. Status fields must distinguish action-level status from IOC transport status and SCSI status. Persistent action completion can be asynchronous, so a successful reply may not mean resync, scrub, rebuild, or firmware update has finished.

## Test Signals

Validation should cover harmless status/indicator actions first, then controlled create/delete/change operations on disposable media or simulation. Tests should verify action status mapping, rate-mask packing, device firmware update timeout packing, passthrough sense/status handling, and mailbox status handling. Runtime signals include expected RAID events, RAID config page changes, volume status transitions, and clear error logs for failed or invalid actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_raid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_sas.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_sas.h

## Purpose

`mpi_sas.h` defines the SAS-specific MPI control ABI for SMP passthrough, SATA passthrough, SAS IO Unit control, SAS status values, and SAS device-info bitfields. It is the low-level request/reply contract used by Fusion SAS code for topology, link, SATA, SMP, and device-control operations.

## Important APIs, Types, and Definitions

- `MPI_SASSTATUS_*` values describe SAS transport completion status, including invalid frame, open/connect failures, unsupported rate/protocol, STP resources busy, IU length problems, transfer-ready/data offset errors, SDSF failures, connection failure, and initiator response timeout.
- `MPI_SAS_DEVICE_INFO_*` bits classify SAS/SATA devices: product-specific high bits, SEP, ATAPI, LSI, direct attach, SSP/STP/SMP target or initiator, SATA device/host, and device type mask for no device, end device, edge expander, and fanout expander.
- `MSG_SMP_PASSTHROUGH_REQUEST` and reply send SMP frames to a SAS address or physical port with request/response lengths, connection rate, immediate flag, and SGL.
- `MSG_SATA_PASSTHROUGH_REQUEST` and reply send a SATA command FIS to a target/bus with flags for reset, execute diagnostic, DMA queued, packet command, DMA, PIO, vendor unique, write, and read.
- `MSG_SAS_IOUNIT_CONTROL_REQUEST` and reply perform link and topology operations: clear not present, clear all persistent, PHY link/hard reset, clear PHY error log, map current, send primitive, force full discovery, transmit port select, remove device, set IOC parameter, and product-specific operations.
- Primitive flags distinguish single, triple, and redundant primitive transmission.

## Control Flow

SMP passthrough builds a request with a destination SAS address, physical port, requested connection rate, data length, and SGL; firmware returns SAS status, response length, and inline response bytes. SATA passthrough embeds a 20-byte command FIS and data SGL, then returns a status FIS, status/control register snapshot, SAS status, and transfer count. IO Unit control targets either a PHY, target/bus, device handle, SAS address, or IOC parameter depending on operation; firmware completes with IOC status/log info and echoes operation metadata.

## State and Persistence Behavior

Most operations affect runtime topology and link state: resets, primitive sends, discovery, device removal, current mapping, and error-log clearing. `CLEAR_ALL_PERSISTENT` and IOC parameter changes can affect persistent or semi-persistent firmware mapping/behavior. Passthrough requests are transient but can change device state if the embedded SATA or SMP command does so.

## Dependencies and Integration Points

The header depends on MPI base types and `SGE_SIMPLE_UNION`. It is included by `mptbase.h` and used with SAS events from `mpi_ioc.h`, SAS config pages from `mpi_cnfg.h`, and SAS log info from `mpi_log_sas.h`. `mptsas.c` consumes the device-info bit definitions for topology classification and uses SAS IO Unit control for reset/discovery/device management paths.

## Risks and Edge Cases

Passthrough commands are powerful: malformed SMP frames or SATA FISes can disrupt devices or expanders. Direction flags in SATA passthrough must match the command and SGL or DMA behavior can be wrong. Several operations use overlapping identifier fields; callers must fill the fields required by the selected operation and leave irrelevant fields harmless. Link reset, hard reset, force discovery, and remove device can race with topology event handling. Connection-rate constants in this MPI v1.5 header only list negotiated, 1.5, and 3.0 Gbit rates while event structures elsewhere include 6.0 Gbit reporting.

## Test Signals

Tests should include SMP identify/report general passthrough, invalid SMP destination handling, SATA non-data/read/write passthrough on safe commands, PHY link reset and hard reset recovery, PHY error log clearing, force full discovery, remove-device behavior, and IOC parameter setting on supported firmware. Expected signals are correct SAS status, transfer count, status FIS/register data, topology events, and no stale device handles after discovery changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_sas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_targ.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_targ.h

## Purpose

`mpi_targ.h` defines the MPI target-mode ABI for posting command buffers, receiving target command/error replies, representing FCP/SPI/SSP command and task buffers, assisting target data movement, sending target status, aborting target-mode work, and packing target-mode context reply words.

## Important APIs, Types, and Definitions

- `CMD_BUFFER_DESCRIPTOR` and `MSG_TARGET_CMD_BUFFER_POST_REQUEST` post one or more target command buffers by IO index and 32/64-bit physical address.
- `MSG_TARGET_CMD_BUF_POST_BASE_REQUEST` and `MSG_TARGET_CMD_BUF_POST_LIST_REQUEST` support base-address posting and IO-index list posting; `MSG_TARGET_CMD_BUFFER_POST_BASE_LIST_REPLY` completes base/list post operations.
- Error/priority replies include `MSG_PRIORITY_CMD_RECEIVED_REPLY`, `MSG_TARGET_CMD_BUFFER_POST_ERROR_REPLY`, and `MSG_TARGET_ERROR_REPLY`, with priority reason constants for disconnect, task management, parity, CRC, protocol, busy, and unknown causes.
- Command buffer formats include `MPI_TARGET_FCP_CMD_BUFFER`, `MPI_TARGET_SCSI_SPI_CMD_BUFFER`, `MPI_TARGET_SSP_CMD_BUFFER`, and `MPI_TARGET_SSP_TASK_BUFFER`.
- `MSG_TARGET_ASSIST_REQUEST` describes target data movement and optional automatic status. `MSG_TARGET_ASSIST_EXT_REQUEST` adds bidirectional, multicast, SGL offset chain, T10 EEDP, reference/application tag, and bidirectional length fields.
- `MSG_TARGET_STATUS_SEND_REQUEST` sends status data; response buffers include `MPI_TARGET_FCP_RSP_BUFFER`, `MPI_TARGET_SCSI_SPI_STATUS_IU`, and `MPI_TARGET_SSP_RSP_IU`.
- `MSG_TARGET_MODE_ABORT` and reply abort all command buffers, all IO, exact IO, or exact IO request.
- Context macros pack and unpack IO index, initiator index, alias, and port, with separate obsolete MPI v1.0 host/IOC index forms.

## Control Flow

Target-mode setup posts command buffers either as descriptors, a contiguous base region, or a list of IO indexes. Firmware uses posted buffers to deliver incoming FCP/SPI/SSP command or task IUs and returns context information in reply words. The host then issues target assist for data-in/data-out movement, optionally with auto status or EEDP handling. Status send posts the final protocol status IU or FCP response buffer. Error replies and priority reasons report cases where firmware could not use a posted buffer or target operation failed. Abort requests cancel broad or exact target-mode work.

## State and Persistence Behavior

The header defines transient queue and IO state. Posted command buffers remain firmware-owned until consumed, reposted, or aborted. Reply words carry correlation state across command receive, assist, status, and abort flows. No persistent NVRAM state is declared here, but target-mode behavior depends on port capabilities and configuration from IOC/port facts and config pages.

## Dependencies and Integration Points

The header depends on MPI base types plus `SGE_IO_UNION` and `SGE_SIMPLE_UNION`. `mptbase.h` includes it for target-protocol support. It integrates with `mpi_ioc.h` port protocol flags (`TARGET`), FC/SAS/SPI transport semantics, `mpi_sas.h` SSP concepts, and SAS log info target-mode abort/assist/status codes. Normal Linux initiator drivers may not exercise this path heavily, but control/target-capable builds depend on layout correctness.

## Risks and Edge Cases

Command buffer address mode and IO index masks must match firmware expectations; misuse can hand firmware bad DMA addresses. Several structures have one-element SGL or array tails and require correctly sized message frames. FCP, SPI status IU, and SSP response IU comments note big-endian protocol layout; callers on little-endian hosts must avoid accidental byte swapping beyond the intended wire layout. Extended assist EEDP flags can corrupt protection information if operation, block size, tags, or masks are wrong. Abort operations are disruptive and must target the right reply word or message context. Legacy MPI v1.0 context macros remain part of compatibility behavior.

## Test Signals

Tests should cover descriptor/base/list command-buffer posting, 32-bit and 64-bit buffer modes, context word packing/unpacking, FCP/SPI/SSP command decode, data-in and data-out target assist, auto status, explicit status send, confirmed/high-priority/repost flags, extended assist EEDP modes, and exact/all abort behavior. Negative tests should verify priority/error replies for malformed buffers, bad IO indexes, and target busy/protocol error reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_targ.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_tool.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_tool.h

## Purpose

`mpi_tool.h` defines MPI toolbox and diagnostic message layouts: clean persistent regions, memory move, diagnostic data upload, ISTWI read/write, FC management, beacon control, diagnostic buffer post, and diagnostic release. These are management and service operations around the normal IO path.

## Important APIs, Types, and Definitions

- Toolbox selectors identify clean, memory move, diagnostic upload, ISTWI read/write, FC management, and beacon tools.
- `MSG_TOOLBOX_REPLY` is the common toolbox completion with tool, message length, function, context, IOC status, and IOC log info.
- `MSG_TOOLBOX_CLEAN_REQUEST` selects persistent regions such as NVSRAM, SEEPROM, flash, bootloader, firmware backup/current, other persistent pages, manufacturing pages, and boot services.
- `MSG_TOOLBOX_MEM_MOVE_REQUEST` and `MSG_TOOLBOX_DIAG_DATA_UPLOAD_REQUEST` use SGEs for firmware-directed memory movement or diagnostic upload. `DIAG_DATA_UPLOAD_HEADER` describes upload length and format.
- `MSG_TOOLBOX_ISTWI_READ_WRITE_REQUEST` performs I2C-like ISTWI reads/writes with bus number, device address, up to three address bytes, data length, direction flag, and SGE.
- FC management action info unions support discovery by all ports, port identifier, bus/target ID, and max frame size.
- `MSG_TOOLBOX_BEACON_REQUEST` toggles beacon mode for a connector/port.
- `MSG_DIAG_BUFFER_POST_REQUEST` posts trace/snapshot/extended diagnostic buffers by type, length, product-specific fields, extended type, and 64-bit buffer address; release request/reply frees such buffers.

## Control Flow

Toolbox operations are posted as single request/reply management frames. The `Tool` field selects the operation, and operation-specific fields or SGEs describe the payload. Diagnostic buffers use a two-step lifecycle: post a DMA buffer with type and size, then release it when no longer needed. ISTWI operations transfer through an SGE after selecting bus/device/address bytes. FC management encodes the selected action and corresponding union member.

## State and Persistence Behavior

Clean operations can erase persistent adapter regions and are high-impact. Diagnostic buffer posts create firmware-visible runtime buffers until released. Beacon requests alter visible hardware state until toggled back or reset. ISTWI requests may read or write external EEPROM, enclosure, or board-management state depending on bus/device address. FC management can change discovery behavior or max frame size at runtime.

## Dependencies and Integration Points

The header depends on MPI base types, `SGE_SIMPLE_UNION`, and common IOC status/log handling. It is included by `mptbase.h`. IOC facts capability bits in `mpi_ioc.h` advertise diagnostic buffer support. FC management complements FC port/device config pages and FC direct messages. Tool failures report domain-specific details through `IOCLogInfo`, including SAS diagnostic and FC log values.

## Risks and Edge Cases

Clean flags can destroy persistent firmware/configuration data. ISTWI writes can alter board devices outside normal storage paths. Diagnostic buffer addresses are 64-bit physical addresses and must remain DMA-valid until release. `MPI_DIAG_BUF_TYPE_COUNT` is a count, not a valid buffer type. FC management action info is a union; callers must initialize the member matching `Action` and clear stale bytes if firmware validates reserved fields. Beacon state should be restored on failures to avoid misleading service indicators.

## Test Signals

Safe tests include common reply decoding, diagnostic buffer post/release for each supported type, diagnostic upload format parsing, ISTWI read on known-safe devices, FC discovery actions on FC adapters, beacon on/off, and rejection of unsupported tools. Destructive clean flags should only be tested in simulation or disposable hardware. DMA tests should verify buffer lifetime and transfer length reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_tool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_type.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_type.h

## Purpose

`mpi_type.h` defines the base scalar and pointer typedefs used by the LSI Fusion MPT MPI headers. It is the foundation for the firmware ABI structures in the `lsi/mpi_*.h` family.

## Important APIs, Types, and Definitions

- `MPI_POINTER` defaults to `*` but can be overridden before inclusion, preserving the historical ability to express alternate pointer models.
- Signed and unsigned 8/16/32-bit aliases are `S8`, `U8`, `S16`, `U16`, `S32`, and `U32`.
- `S64` and `U64` are structs with `Low` and `High` 32-bit words rather than native C 64-bit integer aliases. `S64.High` is signed; `U64.High` is unsigned.
- Pointer aliases include `PS8`, `PU8`, `PS16`, `PU16`, `PS32`, `PU32`, `PS64`, and `PU64`.

## Control Flow

This file has no runtime control flow. Its compile-time role is to make the rest of the MPI header set agree on field widths and pointer typedef naming. Including `mptbase.h` pulls this file in before SGE, IOC, config, init, FC, LAN, RAID, target, toolbox, and SAS headers.

## State and Persistence Behavior

No state is declared. The key persistence concern is ABI stability: all firmware message structures using these typedefs depend on the aliases continuing to map to the same sizes and signedness.

## Dependencies and Integration Points

`S32` uses `int32_t` and `U32` uses `u_int32_t`, so including code must have the relevant integer typedefs available through kernel or system headers before or during inclusion. Every sibling MPI header depends on these aliases. The split-word `U64`/`S64` layout appears in DMA addresses, SAS addresses, total block counts, and protocol IUs throughout the Fusion headers.

## Risks and Edge Cases

`U64` and `S64` are not native 64-bit scalar types; code must not assume normal integer arithmetic, alignment, format printing, or endian helpers work directly on them. The low/high word order is part of the firmware ABI. `MPI_POINTER` override support is legacy and can make typedef declarations unusual if redefined. `u_int32_t` is less standard than `uint32_t` outside the kernel/BSD style environment, so portability depends on the existing include stack.

## Test Signals

Compile-time tests should assert sizes and offsets for representative MPI structures, especially fields using `U64` and `S64`. Static assertions for `sizeof(U8)==1`, `sizeof(U16)==2`, `sizeof(U32)==4`, and `sizeof(U64)==8` catch accidental include or platform drift. Build coverage should include all Fusion protocol drivers through `mptbase.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_type.h -->
