# subset-b-005270 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/initio.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/initio.c

## Purpose
`initio.c` is the Linux low-level SCSI driver for Initio INI-9X00U/UW family PCI SCSI host adapters, including supported Initio and Domex PCI IDs. It binds a PCI device to the SCSI mid-layer, initializes controller registers from serial EEPROM configuration, allocates software SCSI control blocks, translates `struct scsi_cmnd` requests into controller SCBs, drives the Tulip/Jasmin hardware state machine, handles interrupts and reselection, maps completion status back to SCSI result codes, and releases PCI/SCSI resources on removal.

## Important APIs, Types, And Functions
The module-facing integration points are `initio_pci_tbl`, `initio_pci_driver`, `module_pci_driver(initio_pci_driver)`, `initio_probe_one()`, and `initio_remove_one()`. The SCSI mid-layer integration is through `initio_template`, which supplies `i91u_queuecommand`, `i91u_bus_reset`, `i91u_biosparam`, queue limits, SG limits, and `cmd_size` for `struct initio_cmd_priv`.

The command path starts in `i91u_queuecommand_lck()`, obtains a free `struct scsi_ctrl_blk` with `initio_alloc_scb()`, fills it in `initio_build_scb()`, and submits it through `initio_exec_scb()`. `i91uSCBPost()` is the SCB completion callback that remaps controller host status to mid-layer `DID_*` values, unmaps DMA resources through `i91u_unmap_scb()`, calls `scsi_done()`, and returns the SCB to the free list.

The interrupt path is `i91u_intr()` -> `initio_isr()` -> `tulip_main()` -> `tulip_scsi()` and `initio_next_state()`. The SCSI phase/state handlers are `initio_state_1()` through `initio_state_7()`, plus `initio_xfer_data_in()`, `initio_xfer_data_out()`, `initio_xpad_in()`, `initio_xpad_out()`, and `initio_status_msg()`. Bus events and recovery are handled by `int_initio_busfree()`, `int_initio_scsi_rst()`, `int_initio_resel()`, `int_initio_bad_seq()`, `initio_bad_seq()`, `initio_reset_scsi()`, `initio_post_scsi_rst()`, and `initio_bus_device_reset()`.

The EEPROM path is built around bit-banged NVRAM helpers: `initio_se2_instr()`, `initio_se2_ew_en()`, `initio_se2_ew_ds()`, `initio_se2_rd()`, `initio_se2_wr()`, `initio_se2_rd_all()`, `initio_se2_update_all()`, and `initio_read_eeprom()`. `i91udftNvRam`, `i91unvram`, and `i91unvramp` provide defaults and a shared scratch image. `initio_init()` consumes the EEPROM image to program host ID, parity, termination, target flags, geometry hints, transfer periods, and optional bus reset policy.

## Control Flow
Probe enables the PCI device, derives a BIOS segment from config dword `0x44`, requires a 32-bit DMA mask, allocates a `Scsi_Host` plus private `struct initio_host`, reserves the I/O port window, allocates the largest SCB array it can down to `MAX_TARGETS + 3`, links the SCB free list, initializes locks, reads EEPROM and programs hardware through `initio_init()`, fills SCSI host parameters, requests the shared IRQ, registers the host with `scsi_add_host()`, and starts discovery with `scsi_scan_host()`.

For each queued SCSI command, the driver allocates an SCB, maps the sense buffer, maps the request SG list with `scsi_dma_map()`, optionally maps the controller SG table with `dma_map_single()`, fills CDB, target, LUN, transfer direction, request sense, and tag metadata, then appends the SCB to the pending queue. If the host semaphore is open, interrupts are masked, `tulip_main()` is run synchronously to kick the hardware, and interrupts are unmasked.

`tulip_main()` repeatedly services hardware state and drains the done queue. Queue-full target status reduces `host->max_tags[target]` and requeues the SCB. Check-condition status triggers an automatic six-byte REQUEST SENSE command if `SCF_SENSE` is enabled and the SCB is not already in request-sense mode. Otherwise the SCB is marked done and posted to the mid-layer.

`tulip_scsi()` first consumes pending hardware interrupts: SCSI reset, reselection, selection timeout, disconnect, function-complete, and bus-service events. If there is no active SCB, it picks the first runnable pending SCB, honoring per-target busy state and tag limits. For ordinary commands it selects the target, negotiates WDTR and SDTR when needed, chooses tagged or untagged selection, and in polling mode advances the state machine until the command blocks. Bus-device-reset and abort SCBs use the select-with-ATN-stop path and then state 8.

The numbered state machine mirrors SCSI bus phases. State 1 completes select/ATN/stop and emits identify, tag, WDTR, or SDTR messages. State 2 handles selection with identify and CDB already staged. State 3 sends the CDB and processes message/status phases. State 4 starts data transfer or handles early status/message phases. State 5 handles DMA completion or phase change, computes residual bytes, adjusts the current SG element after disconnect/partial transfer, and resumes state 4 or transitions to state 6. State 6 handles post-data status/message phases or pads overrun data. State 7 flushes unexpected FIFO residue. State 8 sends TARGET RESET and aborts queued commands for the target.

Message processing handles disconnect/save/restore/NOP, command complete, message reject, parity errors, SDTR, WDTR, tagged reselection, and abort messages. Reselection either uses the incoming tag to index directly into the SCB array or finds an untagged busy SCB by target/LUN. Invalid reselection or phase sequences trigger abort messages or bus reset recovery.

## State And Persistence
Persistent device configuration lives in the adapter EEPROM. The driver reads 32 words into the global `i91unvram` image, validates signature and checksum, and if validation fails writes `i91udftNvRam` defaults back to EEPROM before reading again. The EEPROM scratch variables are global and explicitly require single-threaded use; `initio_init()` calls them during probe, before the host is externally active.

Runtime state is held in `struct initio_host` inside `Scsi_Host.hostdata`. It tracks the I/O base, IRQ, host SCSI ID, maximum targets, controller flags, current phase and interrupt register snapshots, active SCB and target, per-target negotiation/configuration, tag limits and active tag counts, and four SCB queues: available, pending, busy, and done. `avail_lock` protects free-list allocation/release, while `semaph_lock` serializes entry into the controller engine. The SCSI core host lock also wraps queue and interrupt entry paths.

Each SCB stores the command identity, target/LUN, CDB, tag message/tag ID, status fields, request-sense state, current data pointer/length, SG table, DMA bus addresses, and callback. On disconnect or phase mismatch, the SCB fields are mutated in place so a later reselection resumes at the right SG element and byte offset. Per-command DMA addresses for sense and SG-list mappings are persisted in `struct initio_cmd_priv`, allocated by the SCSI core via `cmd_size`.

## Dependencies And Integration Points
The driver depends on Linux PCI, interrupt, I/O-port, delay/jiffies, DMA mapping, and SCSI mid-layer APIs. Hardware access is entirely via port I/O helpers such as `inb()`, `outb()`, `inl()`, and `outl()` using register definitions from `initio.h`. It includes `<scsi/scsi.h>`, `<scsi/scsi_cmnd.h>`, `<scsi/scsi_device.h>`, `<scsi/scsi_host.h>`, and `<scsi/scsi_tcq.h>`.

The SCSI core calls `i91u_queuecommand`, `i91u_bus_reset`, and `i91u_biosparam`; the PCI core calls probe/remove; the IRQ core calls `i91u_intr`; block partition logic may use `bios_param`; and DMA/IOMMU state is owned through `scsi_dma_map()`, `scsi_dma_unmap()`, `dma_map_single()`, and `dma_unmap_single()`. The file is tightly coupled to `initio.h` for register offsets, bit definitions, status codes, NVRAM layout, SCB layout, target/host structures, and `initio_priv()`.

## Risks And Edge Cases
Many hardware waits are unbounded busy loops on I/O register bits, including EEPROM writes, DMA abort, SCSI reset, interrupt waits, and disconnect waits. A wedged adapter or missing interrupt condition can spin indefinitely, sometimes under locks or with interrupts masked.

The EEPROM image uses shared globals and casts byte arrays/structures to `u16 *` for checksum and word I/O. This relies on layout, alignment, and endian assumptions, and the invalid-EEPROM path writes defaults back to device nonvolatile storage.

`initio_build_scb()` treats negative `scsi_dma_map()` as impossible via `BUG_ON(nseg < 0)` and does not handle DMA mapping failure for the sense buffer or controller SG table. It also stores DMA addresses in 32-bit SCB fields after enforcing only a 32-bit DMA mask. The SCB CDB field is 12 bytes, but the code copies `cmnd->cmd_len` bytes without an explicit local bound, so compatibility depends on the SCSI host/device command-size expectations. The sense transfer size is fixed at 14 bytes.

Queue accounting is delicate. Untagged commands set and clear `TCF_BUSY`, tagged commands increment and decrement `act_tags[target]`, and queue-full handling lowers `max_tags[target]`. Bugs in unlink paths, target reset, reselection, or abort handling can leave tag counts or busy flags imbalanced, stalling future commands for a target.

Resource cleanup appears asymmetric: probe failure frees `host->scb`, but the normal remove path removes the host, frees the IRQ, releases the I/O region, puts the SCSI host, and disables PCI without explicitly freeing the SCB array allocated by `kzalloc()`. This should be verified against the surrounding kernel version's hostdata ownership because the array is not embedded in `Scsi_Host`.

The driver uses legacy assumptions around I/O port BARs, BIOS geometry memory via `phys_to_virt(bios_seg << 4)`, shared IRQ detection by polling controller interrupt state, and controller register programming. Error recovery often escalates to bus reset and reports broad `DID_ERROR`/`DID_RESET` statuses.

## Test Signals
Useful validation signals include successful PCI probe/remove with each listed PCI ID, correct I/O-region and IRQ cleanup on every probe failure label, SCSI scan with EEPROM defaults and with valid EEPROM data, host ID and target count derived from NVRAM, queueing with no-data, single-segment, and multi-segment requests, SG count capped at `TOTAL_SG_ENTRY`, DMA map/unmap balance for normal completion and auto request sense, tagged and untagged command concurrency, queue-full tag throttling, disconnect/reselection resume across partial SG transfers, SDTR/WDTR negotiation and message-reject fallback, SCSI bus reset and target reset recovery, selection timeout, unexpected bus-free handling, parity error message-out, and module unload leak checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/initio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/initio.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/initio.h -->
