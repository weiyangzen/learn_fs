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
