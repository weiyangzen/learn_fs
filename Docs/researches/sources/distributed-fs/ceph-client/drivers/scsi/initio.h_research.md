# sources/distributed-fs/ceph-client/drivers/scsi/initio.h

## Purpose
`initio.h` is the private hardware and state contract for the Initio INI-9X00U/UW SCSI driver implemented in `initio.c`. It defines controller register offsets, command and status bits, SCSI phase encodings, DMA command bits, EEPROM/NVRAM layout, SCB and host-private data structures, per-target negotiation flags, driver-local status codes, and the per-command private DMA bookkeeping accessor used by the SCSI mid-layer integration.

## Important APIs, Types, And Macros
Top-level sizing macros include `TOTAL_SG_ENTRY` at 32 controller SG entries, `MAX_SUPPORTED_ADAPTERS`, `MAX_OFFSET`, and `MAX_TARGETS` at 16. `i91u_config` is a small base/IRQ pair type retained for adapter configuration.

The `TUL_*` macros define the PCI configuration, Jasmin, SCSI core, DMA, interrupt, and NVRAM register offsets used with port I/O in `initio.c`. Key groups are `TUL_P*` PCI config offsets, `TUL_HACFG*` and `TUL_SDCFG*`, global registers such as `TUL_GCTRL`, `TUL_GCTRL1`, and `TUL_NVRAM`, SCSI sequencer registers such as `TUL_SInt`, `TUL_SCtrl0`, `TUL_SStatus0`, `TUL_SCmd`, `TUL_SFifo`, and DMA registers such as `TUL_XAddH`, `TUL_XCntH`, `TUL_XCmd`, `TUL_Int`, `TUL_XStatus`, and `TUL_Mask`.

The `TSC_*`, `TSS_*`, `TAX_*`, `XCMP`/`XABT`/`IPEND`, `XPEND`, `SE2*`, and phase macros encode controller commands, control bits, hardware status bits, SCSI interrupt causes, DMA commands, DMA/interrupt status, EEPROM bit-banging pins, and SCSI bus phases. These are the constants that drive `initio_next_state()`, `wait_tulip()`, DMA start/abort, and serial EEPROM read/write code.

`struct sg_entry` is the hardware scatter/gather descriptor with 32-bit data pointer and length. `struct scsi_ctrl_blk` is the software and firmware command block, containing queue linkage, state-machine status, SG cursor, total/current transfer lengths, target/LUN, CDB, tag fields, sense pointer, callback, original `struct scsi_cmnd *`, and an embedded 32-entry controller SG table. SCB status, opcode, mode, flag, host-status, and target-status macros define how the C file transitions and reports commands.

`struct target_control` tracks per-target negotiation and BIOS geometry state: flags, transfer-period register image, SCSI config image, driver flags, heads, and sectors. `struct initio_host` is the adapter-private state block embedded in `Scsi_Host.hostdata`; it includes hardware identity, current phase/interrupt snapshots, message scratch buffer, SCB queue heads/tails, active SCB/target pointers, tag accounting, target table, locks, and the owning `struct pci_dev *`.

The EEPROM schema is represented by `NVRAM_SCSI` and `NVRAM`, with macros for BIOS configuration, host adapter configuration, target options, the expected `INI_SIGNATURE`, and default byte values. `struct initio_cmd_priv` holds DMA bus addresses for the per-command sense buffer and mapped controller SG list. `initio_priv()` wraps `scsi_cmd_priv()` to retrieve that private data.

## Control Flow
This header has no executable control flow except the inline `initio_priv()`. Its definitions shape the driver flow in `initio.c`: probe allocates `struct initio_host` and SCB arrays sized by these constants; EEPROM helpers read and validate `NVRAM`; `initio_init()` copies NVRAM target bytes into `struct target_control`; `initio_build_scb()` fills `struct scsi_ctrl_blk` and embedded `struct sg_entry` values; queue helpers move SCBs among list heads in `struct initio_host`; interrupt and polling loops interpret `TSS_*` bits and SCSI phase macros; transfer helpers program `TUL_SCnt*`, `TUL_XAddH`, `TUL_XCntH`, and `TUL_XCmd`; completion maps SCB status macros into SCSI mid-layer results.

The register and bit definitions also determine recovery flow. `TSC_RST_BUS`, `TSC_RST_CHIP`, `TSC_FLUSH_FIFO`, `TAX_X_ABT`, `TSS_SCSIRST_INT`, `TSS_DISC_INT`, and related bits are used to reset the bus, abort DMA, flush FIFOs, distinguish selection timeout from disconnect, and clear negotiation state after errors.

## State And Persistence
`NVRAM` and `NVRAM_SCSI` describe persistent adapter configuration stored in serial EEPROM: signature, structure size/revision, model bytes, BIOS settings, host adapter settings, two SCSI channel descriptors, target configuration bytes, reserved bytes, and checksum. The default-value macros and `INI_SIGNATURE` are used by `initio.c` to repair invalid EEPROM contents.

`struct initio_host` defines all volatile adapter state. It persists for the lifetime of the registered SCSI host and owns SCB queues, active command state, negotiated transfer parameters, per-target tag and busy accounting, and synchronization locks. `struct scsi_ctrl_blk` persists for the lifetime of the adapter SCB pool and is recycled per command. `struct initio_cmd_priv` persists only for the lifetime of one SCSI command and records DMA mappings that must be undone at completion.

The SCB and target flag macros encode internal state transitions rather than external ABI. `SCB_RENT`, `SCB_PEND`, `SCB_SELECT`, `SCB_BUSY`, and `SCB_DONE` identify queue/state membership. `TCF_SYNC_DONE`, `TCF_WDTR_DONE`, `TCF_BUSY`, and `TCF_DRV_EN_TAG` record negotiated and scheduling state per target. Host flags such as `HCF_EXPECT_DISC` and `HCF_EXPECT_DONE_DISC` tell wait paths whether a disconnect is expected and whether a completed SCB should be appended to the done queue.

## Dependencies And Integration Points
The header includes `<linux/types.h>` for fixed-width kernel integer types and relies on SCSI declarations available to the including C file for `struct scsi_cmnd`, `dma_addr_t`, and `scsi_cmd_priv()`. It is private to the Initio driver rather than a public UAPI header.

Its hardware constants are consumed almost exclusively by `initio.c` through port I/O. Its SCSI message constants such as `EXTENDED_MESSAGE`, `EXTENDED_SDTR`, `EXTENDED_WDTR`, `SIMPLE_QUEUE_TAG`, `COMMAND_COMPLETE`, and `TARGET_RESET` come from the SCSI headers included before this header in `initio.c`. The `struct initio_cmd_priv` size is passed to the SCSI host template as `cmd_size`, which lets the SCSI core allocate command-private storage addressable via `initio_priv()`.

## Risks And Edge Cases
The hardware descriptor model is 32-bit. `struct sg_entry`, SCB `bufptr`, `paddr`, `sgpaddr`, and `senseptr` are all `u32`, so the C file must enforce a 32-bit DMA mask and must not pass higher DMA addresses. Endianness also matters because SG entries are written with little-endian conversions while many EEPROM fields are cast and checksummed as `u16`.

`struct scsi_ctrl_blk` has a fixed 12-byte CDB array. Any caller path that allows a longer SCSI CDB without host-level filtering would overwrite adjacent SCB fields. `TOTAL_SG_ENTRY` is 32, so the runtime SCSI host SG limit must stay consistent with this embedded array.

Several comments and duplicated/legacy constants reflect older kernel and hardware assumptions. Some reset/abort status macros are local compatibility values rather than current SCSI core enums. Register aliases share offsets for read/write semantics, so mistakes in direction or phase handling can silently access the wrong hardware behavior.

The NVRAM structures are tightly packed by convention but are not annotated with `__packed`. Layout changes, compiler padding differences, or unaligned `u16 *` access would break checksum and EEPROM word mapping. This is mitigated mostly by the simple field ordering and historical target architecture expectations.

## Test Signals
Header-level validation should focus on compile-time and integration signals: `sizeof(NVRAM)` remains 64 bytes for the 32-word EEPROM image, `TOTAL_SG_ENTRY` matches the SCSI host `sg_tablesize`, SCB CDB length assumptions match accepted command lengths, `struct initio_cmd_priv` is large enough for both DMA addresses and is wired through `cmd_size`, 32-bit DMA mask enforcement covers every SCB DMA field, and register/bit macros are exercised by probe, EEPROM read/write, selection, data transfer, reselection, reset, and interrupt tests in `initio.c`.
