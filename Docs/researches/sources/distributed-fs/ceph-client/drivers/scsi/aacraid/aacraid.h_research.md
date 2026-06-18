# sources/distributed-fs/ceph-client/drivers/scsi/aacraid/aacraid.h

## Purpose

`aacraid.h` is the shared ABI and state-definition header for the AACRAID driver. It defines the firmware command numbers, queue layouts, FIB headers, adapter initialization records, scatter-gather formats, SCSI/SRB/HBA command and response formats, ioctl request numbers, adapter state structures, feature flags, register mappings, helper macros, inline helpers, and cross-file function prototypes used by the driver implementation.

This header is not a passive declaration file. It encodes firmware contracts that must match controller expectations, including packed/native command layout, endianness, queue ordering, init-structure revisions, and status codes. Changes here can affect every transport, SCSI, ioctl, reset, interrupt, and discovery path.

## Important APIs, Types, and Definitions

Major constants and feature definitions:

- Interrupt and mode flags: `AAC_INT_MODE_*`, `AAC_ENABLE_*`, `AAC_DISABLE_*`, PMC interrupt bits, doorbell bits.
- Capacity and topology limits: `MAXIMUM_NUM_CONTAINERS`, `AAC_NUM_MGT_FIB`, `AAC_NUM_IO_FIB`, `AAC_MAX_LUN`, `AAC_MAX_BUSES`, `AAC_MAX_TARGETS`, `AAC_MAX_NATIVE_SIZE`, `AAC_MAX_MSIX`.
- Firmware options and extended options: `AAC_OPT_*`, `AAC_EXTOPT_*`, `AAC_OPTION_*`, `AAC_FEATURE_JBOD`.
- Communication interface types: `AAC_COMM_PRODUCER`, `AAC_COMM_MESSAGE`, and message type 1/2/3.
- FIB commands: `ContainerCommand`, `ContainerCommand64`, `ContainerRawIo`, `ContainerRawIo2`, `ScsiPortCommand`, `ScsiPortCommand64`, `RequestAdapterInfo`, `RequestSupplementAdapterInfo`, `AifRequest`, and others.
- Container manager commands: `CT_GET_CONFIG_STATUS`, `CT_COMMIT_CONFIG`, `CT_GET_CONTAINER_COUNT`, `CT_READ_NAME`, `CT_CID_TO_32BITS_UID`, `CT_FLUSH_CACHE`, `CT_POWER_MANAGEMENT`, `CT_PAUSE_IO`, `CT_RELEASE_IO`.
- User ioctl command numbers: `FSACTL_SENDFIB`, `FSACTL_SEND_RAW_SRB`, `FSACTL_QUERY_DISK`, `FSACTL_DELETE_DISK`, `FSACTL_OPEN_GET_ADAPTER_FIB`, `FSACTL_GET_NEXT_ADAPTER_FIB`, `FSACTL_RESET_IOP`, `FSACTL_GET_HBA_INFO`.

Core data structures:

- `struct aac_dev`: main per-adapter state. It stores negotiated limits, FIB memory, queues, locks, adapter operation callbacks, PCI/register mappings, SCSI host pointer, container table, AIF context list, firmware info blocks, capability flags, sync state, MSI/MSI-X state, HBA target map, SA firmware CISS data, and shutdown/reset flags.
- `struct adapter_ops`: polymorphic adapter hooks for interrupts, sync commands, restart/start, ioremap, FIB delivery, bounds/read/write/SCSI paths, and communication selection.
- `struct fib`, `struct hw_fib`, `struct aac_fibhdr`, `struct aac_fib_xporthdr`: host and firmware FIB representations.
- `struct aac_queue`, `struct aac_queue_block`, `struct aac_entry`, `struct aac_qhdr`: producer/consumer queue infrastructure shared with firmware.
- `union aac_init`: adapter init structures for older r7-style interfaces and newer r8/type3 RRQ interfaces.
- `struct fsa_dev_info`: per-logical-container state consumed by SCSI command handling.
- `struct aac_hba_map_info`, `struct aac_hba_cmd_req`, `struct aac_hba_resp`, `struct aac_native_hba`: native HBA request/response state and physical target mapping.
- `struct aac_srb`, `struct aac_srb_reply`, `struct user_aac_srb`: firmware SCSI passthrough command ABI and user-space representation.
- `struct aac_adapter_info`, `struct aac_supplement_adapter_info`, `struct aac_bus_info_response`, `struct aac_hba_info`: firmware and management metadata.
- `struct aac_fib_context`: user AIF subscription context for adapter-initiated FIB delivery.

Important inline helpers and macros:

- Adapter operation macros such as `aac_adapter_read()`, `aac_adapter_write()`, `aac_adapter_scsi()`, `aac_adapter_sync_cmd()`, and `aac_adapter_check_health()`.
- `fib_data(fibctx)` to access FIB payload data.
- `aac_priv(struct scsi_cmnd *cmd)` to get AAC per-command private state.
- `aac_is_src()` and `aac_supports_2T()` feature helpers.
- Worker scheduling helpers for SA firmware scans and SRC AIF reinitialization.

## Control Flow and Design Role

The header defines the driver layering. Adapter-specific files fill `struct adapter_ops`; initialization code negotiates communication settings and fills `struct aac_dev`; SCSI code uses operation macros to call the selected transport; ioctl code uses the same FIB ABI to pass control commands between user space and firmware.

FIB flow is described by the `struct aac_fibhdr` fields and `enum fib_xfer_state`. Host-owned/adapter-owned state, response expectation, priority, async state, fast response, and API-FIB markers are all encoded in the header. Transport code builds queue entries from `struct aac_entry`, while higher-level code fills payload structs such as `struct aac_read`, `struct aac_write`, `struct aac_raw_io2`, or `struct aac_srb`.

Initialization flow is driven by `union aac_init`. Older communication modes use r7 fields for adapter FIBs, communication queue headers, printf buffer, host memory pages, max I/O commands, max FIB size, and host RRQ addresses. Type3/SA firmware uses r8 fields with multiple host RRQs and MSI-X vector metadata. `comminit.c` fills these layouts according to the negotiated interface.

## State and Persistence Behavior

No data is persisted to disk by this header, but it defines all important in-memory state and firmware-visible DMA layout. The state lifetime is typically per-adapter:

- DMA coherent regions are tracked through `comm_addr`, `comm_phys`, `init`, `host_rrq`, `hw_fib_va`, `hw_fib_pa`, and related fields.
- Logical containers persist in memory through `fsa_dev` until rescan/reset/free.
- Physical target exposure persists through `hba_map`.
- User-space AIF consumers persist through `fib_list` entries of `struct aac_fib_context`.
- Reset/shutdown state is tracked in `adapter_shutdown`, `in_reset`, `in_soft_reset`, `handle_pci_error`, and `init_reset`.
- Module-global policy variables are declared here and defined elsewhere, allowing runtime parameters to influence all files.

Because these structures are firmware ABI, state layout itself is a persistence boundary across firmware/driver versions. Endianness annotations (`__le32`, `__le16`, `__le64`) mark values that cross that boundary.

## Dependencies and Integration Points

`aacraid.h` depends on Linux interrupt, completion, PCI, and SCSI host/command headers. It is included by the major driver source files. It exposes prototypes for FIB allocation/delivery, adapter initialization, SCSI command handling, ioctl handling, reset, IRQ setup, scanning, AIF handling, and adapter-specific init routines.

Integration with the Linux SCSI mid-layer occurs through `struct Scsi_Host`, `struct scsi_cmnd`, command-private data, host wait queues, and delayed-work scan helpers. Integration with PCI and DMA occurs through register mapping structs and DMA address fields. Integration with user space occurs through ioctl constants and user-visible structures.

## Risks and Edge Cases

- Firmware ABI structures must retain exact field order, size, alignment, and endianness. Even small layout changes can break controller communication.
- Several flexible arrays and variable-size structures (`sg[]`, `rrq[]`, CISS LUN list) require careful size calculations in callers.
- `struct aac_dev` is broad shared mutable state. Locking rules are distributed across source files, increasing the risk of reset, ioctl, AIF, and SCSI races.
- The header includes both firmware-endian and CPU-endian user structures. Confusing `struct aac_srb` with `struct user_aac_srb` can introduce endian or pointer bugs.
- FIB state flags are bitfields shared by transport and high-level code. Incorrect flags can cause double completion, missing response waits, or leaked FIBs.
- Feature flags such as native HBA, new communication modes, SA firmware, 64-bit SG, and variable block size alter control flow in multiple files. Test coverage must combine these flags, not validate them in isolation.
- Register definitions for SA, RX, RKT, and SRC devices are hardware-specific and accessed through macros, so wrong adapter identification can produce invalid MMIO.

## Test Signals

Useful signals include successful build-time size/alignment assumptions for firmware ABI structs, probe logs showing negotiated communication interface and init revision, correct queue and RRQ setup for producer/message/type1/type2/type3 modes, SCSI scan behavior across container and native channels, ioctl compatibility for 32-bit and 64-bit user space, reset behavior with `adapter_shutdown` and `handle_pci_error`, MSI/MSI-X interrupt routing, AIF delivery to user contexts, and DMA/FIB leak checks under I/O, passthrough, reset, and shutdown stress.
