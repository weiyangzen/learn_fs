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
