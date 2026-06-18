# sources/distributed-fs/ceph-client/drivers/scsi/FlashPoint.c

## Purpose

`FlashPoint.c` is the BusLogic/Mylex FlashPoint SCCB Manager embedded into the Linux BusLogic SCSI host adapter driver. It is included directly by `BusLogic.c`, not compiled as an independent object, and is active only when `CONFIG_SCSI_FLASHPOINT` is enabled. When disabled, the file exposes only external prototypes for the FlashPoint entry points.

The implementation manages FlashPoint Harpoon-family PCI SCSI adapters at the register level. It probes the hardware, reads or repairs EEPROM/NVRAM settings, initializes bus-master DMA and the SCSI automation engine, starts and aborts SCCBs, handles interrupts and SCSI phases, performs synchronous/wide/tag negotiation, manages disconnect/reselect queues, runs SCAM ID assignment, and reports completions back through SCCB callbacks.

## Important APIs, Types, And Data

- `struct sccb_mgr_info` mirrors `struct fpoint_info` from `BusLogic.h` and carries adapter discovery results: I/O base, host ID, firmware revision, per-target negotiation masks, termination flags, model, BIOS translation data, and relative card number.
- `struct sccb` overlays the FlashPoint-specific tail of `struct blogic_ccb`. It stores the SCSI CDB, data pointer/length, sense pointer, callback, target/lun, host and target status, internal transfer counters, SG progress, tag, SCSI message/state, saved CDB for auto request sense, and queue links.
- `struct sccb_card` is the per-adapter runtime object returned as the card handle. It owns `currentSCCB`, `ioPort`, command count, disconnect queue table, scan cursor, global flags, host ID, and optional `struct nvram_info`.
- `struct sccb_mgr_tar_info` is per-card/per-target state: select queue head/tail, contingent allegiance, tag queue count, busy LUN table, disconnect queue indexes, EEPROM negotiation value, current sync register value, and target status flags.
- Global tables `FPT_BL_Card[MAX_CARDS]`, `FPT_sccbMgrTbl[MAX_CARDS][MAX_SCSI_TAR]`, `FPT_scamInfo[MAX_SCSI_TAR]`, and `FPT_nvRamInfo[MAX_MB_CARDS]` hold all manager state for up to eight cards.
- Public entry wrappers map typed BusLogic calls to internal SCCB-manager functions: `FlashPoint_ProbeHostAdapter`, `FlashPoint_HardwareResetHostAdapter`, `FlashPoint_ReleaseHostAdapter`, `FlashPoint_StartCCB`, `FlashPoint_AbortCCB`, `FlashPoint_InterruptPending`, and `FlashPoint_HandleInterrupt`.
- Hardware access is through `RD_HARPOON`, `WR_HARPOON`, `RDW_HARPOON`, `WRW_HARPOON`, and 32-bit Harpoon I/O helpers. The many `hp_*` offsets, phase bits, automation opcodes, EEPROM commands, and SCSI signal definitions describe the chip programming model.

## Control Flow

Probe starts in `FlashPoint_ProbeHostAdapter()`. It validates the Harpoon vendor/device IDs, initializes static manager tables on first use, decides whether existing firmware/BIOS state is usable, reads NVRAM stack data or EEPROM, derives per-target sync/disconnect/wide/fast/ultra masks, programs termination bits, detects narrow versus wide support, reads BIOS translation information from ARAM, installs the phase dispatch table, and marks the card present.

`FlashPoint_HardwareResetHostAdapter()` allocates or reuses a `struct sccb_card` slot, initializes per-card and per-target queues, reinitializes bus-master and SCSI/Xbow hardware, loads the default automation map, sets host ID registers, applies parity and termination policy, optionally resets the SCSI bus and SCAM state, loads target negotiation preferences, and marks the SCCB manager present through the hardware semaphore.

`FlashPoint_StartCCB()` validates target and LUN, calls `FPT_sinits()` to initialize manager fields, marks the manager active, and either queues the SCCB or selects it immediately. Selection is delegated to `FPT_ssel()`, which reserves LUN/tag/disconnect slots, loads automation RAM with ID/tag/CDB/negotiation messages, handles reset and abort messages, and starts Harpoon target selection.

Interrupt handling enters `FlashPoint_HandleInterrupt()`. It disables card interrupts, samples bus-master extended status, then loops over enabled Harpoon interrupts. It handles bad ISR conditions through `FPT_SccbMgr_bad_isr()`, command completion through `FPT_autoCmdCmplt()`, disconnects through `FPT_queueDisconnect()`, reselects through `FPT_sres()` followed by phase decode, data-count interrupts through `FPT_schkdd()`, bus-free events through `FPT_phaseBusFree()`, BIOS tickles, and new-command scheduling through `FPT_queueSearchSelect()`.

SCSI phase work is table-driven. `FPT_phaseDecode()` indexes `FPT_s_PhaseTbl` by the current SCSI phase and calls data-out, data-in, command, status, message-out, message-in, or illegal-phase handlers. Data phases use `FPT_dataXferProcessor()` and either `FPT_busMstrDataXferStart()` or `FPT_busMstrSGDataXferStart()`. Status and message paths update target status, handle `COMMAND_COMPLETE`, `MESSAGE_REJECT`, `RESTORE_POINTERS`, `DISCONNECT`, `SAVE_POINTERS`, `IGNORE_WIDE_RESIDUE`, SDTR, WDTR, aborts, target reset, and auto request sense.

Completion funnels through `FPT_queueCmdComplete()`. It applies underrun filtering, converts host/target status to SCCB status, restores a saved CDB after auto sense, updates residual counts for residual commands, manages low-power clock stop, removes disconnect queue entries, invokes the SCCB callback, clears `currentSCCB`, and schedules another command.

## State And Persistence

Runtime state is mostly in static global arrays, indexed by card and target. It is not dynamically allocated by this file and persists for the lifetime of the included BusLogic driver. Per-command mutable state is stored in the SCCB tail embedded in BusLogic CCBs.

Hardware-persistent state includes FlashPoint EEPROM/NVRAM contents. `FPT_DiagEEPROM()` verifies the firmware signature and checksum, then writes default EEPROM contents when invalid. SCAM device ID strings can be persisted by `FPT_scsavdi()` when `F_UPDATE_EEPROM` is set. `FlashPoint_ReleaseHostAdapter()` writes NVRAM-backed state back to the chip stack/ARAM or clears the stack marker when no NVRAM state exists.

The file also persists negotiated target state in memory: sync/wide/tag support, contingent allegiance, busy LUNs, disconnect tags, and queue depth. These are reset by bus reset, target reset, negotiation rejection, timeout, and table-init helpers.

## Dependencies And Integration Points

The source depends on `BusLogic.h` definitions because it is included from `BusLogic.c`. The internal `struct sccb_mgr_info` and `struct sccb` are intentionally layout-compatible with `struct fpoint_info` and `struct blogic_ccb`; the inline wrappers cast between the BusLogic-facing types and FlashPoint-internal types.

It integrates with the SCSI midlayer indirectly through BusLogic. BusLogic discovers PCI FlashPoint adapters, fills `adapter->fpinfo`, calls the FlashPoint probe/reset functions, passes CCBs into `FlashPoint_StartCCB()`, asks `FlashPoint_InterruptPending()` and `FlashPoint_HandleInterrupt()` from its IRQ path, and calls `FlashPoint_AbortCCB()` and `FlashPoint_ReleaseHostAdapter()` for error handling and teardown.

The code requires PCI I/O port access, SCSI protocol constants and messages, request-sense and status definitions, and BusLogic scatter/gather segment layout. It relies on Harpoon-specific I/O registers, ARAM/SGRAM switching, EEPROM bit-banging, hardware semaphores shared with BIOS, and SCAM bus handshakes.

## Risks And Edge Cases

- The file relies on strict structure layout compatibility with BusLogic CCB and fpoint structures. Any change to `BusLogic.h` fields under `CONFIG_SCSI_FLASHPOINT` must preserve the overlay contract.
- Many polling loops wait on hardware bits with no scheduler interaction and, in several paths, no strong timeout. Broken hardware or lost bus signals can hang the CPU in interrupt or reset paths.
- Queue accounting is delicate: `cmdCounter`, `discQCount`, target queue counts, tag counts, and busy LUN bits are updated from many error, disconnect, abort, and completion branches. A missed decrement can strand commands or corrupt disconnect lookup.
- Scatter/gather arithmetic treats `DataLength` as byte length of the SG table for SG commands and indexes `struct blogic_sg_seg` in a non-obvious way. Residual and restart paths are high risk for off-by-one and partial-segment bugs.
- Bus-master abort and FIFO-drain paths convert hardware faults into `SCCB_BM_ERR`, `SCCB_GROSS_FW_ERR`, parity, underrun, and overrun statuses. Error precedence matters because later code often sets a status only when it is still zero.
- EEPROM repair and SCAM persistence write nonvolatile adapter state. Regressions can change adapter identity, target ID assignments, termination defaults, or checksum contents.
- `FPT_default_intena` is global rather than per-card. In mixed-card or SCAM-level differences, interrupt-enable assumptions can leak across adapters.
- The fallback `#else` branch declares external functions when FlashPoint support is disabled, so callers must still be compiled in a way that does not require missing definitions unless `CONFIG_SCSI_FLASHPOINT` paths are eliminated.

## Test Signals

Build signals include compiling `drivers/scsi/BusLogic.o` with and without `CONFIG_SCSI_FLASHPOINT`, checking that `BusLogic.c` inclusion of `FlashPoint.c` sees the expected `struct blogic_ccb` layout, and verifying no new sparse warnings around I/O casts or pointer truncation.

Runtime signals include PCI FlashPoint probe logs, correct host adapter ID/model/termination reporting, successful hardware reset, successful SCSI scan, command completion under simple read/write, auto request sense on check condition, disconnect/reselect with tagged and untagged I/O, abort and target reset behavior, selection timeout handling, parity/bus-master fault paths, and SCAM ID assignment on legacy and SCAM-capable buses.
