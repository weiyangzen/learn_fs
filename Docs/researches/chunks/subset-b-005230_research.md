# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_core.c lines 9381-10724

## Scope

This chunk covers the tail of the AIC79xx core driver. It begins in the final loop of `ahd_loadseq()`, where the compiled sequencer firmware is patched, address-fixed, parity-adjusted, and downloaded into controller sequencer RAM. It then defines sequencer patch/address helpers, diagnostic register dumping, SEEPROM and flexport accessors, checksum validators, and the end-of-file target-mode command intake path guarded by `AHD_TARGET_MODE`.

The chunk is not a standalone module. It depends on earlier definitions in `aic79xx_core.c`, generated sequencer arrays such as `seqprog`, `patches`, and `critical_sections`, register definitions from the shipped/generated AIC79xx register headers, and public structures/prototypes in `aic79xx.h`. The target-mode code is also partly compile-time-gated: the whole target-mode section requires `AHD_TARGET_MODE`, and the LUN enable/disable and SCSI-ID update bodies are additionally wrapped in `#if NOT_YET`, so those routines are present as scaffolding but not active in normal builds.

## Purpose

The visible code supports three late-stage responsibilities in the driver:

- Finish making the controller firmware image match the probed hardware and driver mode, then place it into sequencer RAM.
- Provide high-value diagnostics for SCSI error handling by dumping controller registers, SCB queues, FIFO state, DMA counters, LQ state, CDB bytes, and the sequencer stack while preserving execution state.
- Read, write, and validate persistent controller configuration data from the serial EEPROM and flexport-attached board logic.
- When target mode is compiled in, translate incoming target command DMA entries into CAM `ccb_accept_tio` completions and maintain the host/sequencer target command FIFO position.

This chunk therefore sits at the boundary between software policy and hardware state. It both mutates persistent adapter settings through SEEPROM/flexport writes and snapshots volatile card state for post-fault debugging.

## Important APIs, Types, and Functions

Sequencer firmware helpers:

- `ahd_check_patch(struct ahd_softc *ahd, const struct patch **start_patch, u_int start_instr, u_int *skip_addr)` walks the sorted `patches[]` table at the current source instruction. It calls each patch predicate, sets `skip_addr` when a patch is rejected, and advances the caller's patch cursor.
- `ahd_resolve_seqaddr(struct ahd_softc *ahd, u_int address)` recomputes a sequencer branch target after rejected patch blocks have been removed. It reruns patch decisions from instruction zero up to the original target and subtracts skipped instruction count.
- `ahd_download_instr(struct ahd_softc *ahd, u_int instrptr, uint8_t *dconsts)` decodes a 32-bit sequencer instruction from `seqprog`, resolves branch/call targets, replaces symbolic download constants when the instruction's parity bit is used as the marker, recalculates odd parity, endian-converts back to little endian, and writes four bytes to `SEQRAM`.
- The visible tail of `ahd_loadseq()` records downloaded critical section ranges in `ahd->critical_sections`, stores `ahd->num_critical_sections`, leaves `SEQCTL0` in normal `PERRORDIS|FAILDIS|FASTMODE` state, and emits verbose firmware feature/bug/flag data.

Diagnostics:

- `ahd_probe_stack_size()` destructively probes the sequencer `STACK` register depth by writing nonzero patterns and reading them back until the hardware no longer returns the expected LIFO sequence.
- `ahd_print_register()` is a generic bitfield printer used by generated register-specific print helpers. It prints the raw register value and decodes non-overlapping masks from an `ahd_reg_parse_entry_t` table.
- `ahd_dump_card_state()` is the central card dump routine. It pauses the card if needed, saves/restores register modes, iterates through mode-independent registers, pending/free SCB lists, sequencer completion lists, both DFF FIFO contexts, LQ state, current SCB/CDB fields, and the sequencer stack.
- `ahd_dump_scbs()` is present only under `#if 0`; it would dump every hardware SCB's control, SCSI ID, next pointers, and SG pointers, but is not compiled.

SEEPROM and flexport:

- `ahd_read_seeprom(struct ahd_softc *ahd, uint16_t *buf, u_int start_addr, u_int count, int bytestream)` reads 16-bit words through the controller SEEPROM state machine using `SEEADR`, `SEECTL`, and `SEEDAT`.
- `ahd_write_seeprom(struct ahd_softc *ahd, uint16_t *buf, u_int start_addr, u_int count)` enables SEEPROM writes, writes each word, then disables writes again.
- `ahd_wait_seeprom()` polls `SEESTAT` until `SEEARBACK|SEEBUSY` clears or a timeout expires.
- `ahd_verify_vpd_cksum(struct vpd_config *vpd)` validates the two 8-bit checksum regions in VPD data. It is static and used by earlier PCI/VPD parsing code in the same file.
- `ahd_verify_cksum(struct seeprom_config *sc)` validates the 16-bit SEEPROM checksum over all words except the checksum word.
- `ahd_acquire_seeprom()` currently always returns success; a flexport-based presence probe is compiled out because not every implementation exposes the logic.
- `ahd_release_seeprom()` is a no-op counterpart.
- `ahd_wait_flexport()`, `ahd_write_flexport()`, and `ahd_read_flexport()` arbitrate the flexport board-control interface through `BRDCTL`/`BRDDAT`, validate the 3-bit address range, and propagate timeout errors.

Target mode, when enabled:

- `ahd_find_tmode_devs()` maps a CAM CCB target/LUN to `struct ahd_tmode_tstate` and `struct ahd_tmode_lstate` pointers, validating target width and `AHD_NUM_LUNS`; wildcard target/LUN maps to the black-hole LUN.
- `ahd_handle_en_lun()` contains a full LUN enable/disable algorithm, but its body is disabled by `#if NOT_YET`. The inactive code allocates LUN state, creates CAM paths, toggles select-in through `SCSISEQ_TEMPLATE`/`SCSISEQ1`, updates target IDs, and reloads sequencer firmware when changing initiator/target roles.
- `ahd_update_scsiid()` is also disabled by `#if NOT_YET`; the inactive code would keep the active `SCSIID` OID consistent with the multi-target ID mask.
- `ahd_run_tqinfifo()` drains the DMA-backed target command FIFO, calls `ahd_handle_target_cmd()`, clears processed `cmd_valid` bytes, resyncs each consumed `struct target_cmd` for device preread, increments `ahd->tqinfifonext`, and lazily mirrors the host position into `HS_MAILBOX`.
- `ahd_handle_target_cmd()` converts a firmware-produced `struct target_cmd` into an ATIO CCB: it decodes initiator/target/LUN, finds or falls back to the black-hole LUN state, consumes an available accept-TIO CCB, copies tag metadata and CDB bytes, handles non-disconnect commands by freezing the CCB and recording `ahd->pending_device`, then completes the CCB via `xpt_done()`.

Key data structures in this chunk and adjacent headers include `struct ahd_softc`, `struct cs`, `struct patch`, `union ins_formats`, `struct scb`, `struct seeprom_config`, `struct vpd_config`, `struct target_cmd`, `struct ahd_tmode_tstate`, and `struct ahd_tmode_lstate`.

## Control Flow

The sequencer download path starts from earlier `ahd_loadseq()` setup that calculates download constants and enters `LOADRAM` mode. In the visible range, each source sequencer instruction is checked against patch predicates. Rejected patch spans are not downloaded. For accepted instructions, critical section source ranges are translated to downloaded instruction addresses, then `ahd_download_instr()` writes the rewritten instruction. After the loop, downloaded critical section ranges are copied into dynamically allocated driver state, the sequencer exits load mode, and verbose diagnostics report the resulting firmware size and active feature/bug/flag set.

Patch application and branch target rewriting are intentionally coupled. `ahd_check_patch()` is stateful for the primary download loop because it advances the caller's `cur_patch` cursor; `ahd_resolve_seqaddr()` uses a fresh cursor and replay of the same predicates to compute the address delta for each branch target. Any predicate with side effects would therefore be dangerous, because branch resolution assumes repeated evaluations produce identical decisions for the same `ahd_softc` state.

`ahd_download_instr()` handles opcodes by class. Branch and call opcodes first resolve their format-3 target, then fall through to format-1 immediate handling. Arithmetic/logical/block-move opcodes treat a nonzero parity bit as a marker that the immediate byte indexes `dconsts[]`; after substitution they clear parity and fall through to parity generation. `AIC_OP_ROL` does only parity generation and output. Unknown opcodes panic because a corrupt or mismatched sequencer image is unrecoverable.

`ahd_dump_card_state()` follows a preserve-and-restore pattern. It pauses only if the card is not already paused, saves current modes, switches through SCSI, DFF0, DFF1, CFG, CCHAN, and saved modes to read the relevant register banks, restores the sequencer stack contents after printing them, restores modes, and unpauses only if it paused the card itself. The dump also bounds pending/free/completion walks with `AHD_SCB_MAX` to avoid infinite output on corrupted lists.

SEEPROM reads and writes are linear register-machine operations. Reads initialize `error` to `EINVAL`, so a zero-length read returns invalid argument. Each iteration writes the word address, starts a read, waits, and copies either the machine-endian word from `ahd_inw(SEEDAT)` or two raw bytes when `bytestream` is set. Writes enable the chip first, initialize `retval` to `EINVAL` for zero-length writes, write each word/address/command tuple, break on per-word timeout, then always attempts write-disable; a write-disable failure overrides the per-word return.

Flexport access is a shorter arbitration flow. Both read and write assert SCSI mode, reject addresses above 7 via panic, request the encoded address through `BRDCTL`, wait for `FLXARBACK`, then either strobe `BRDDAT` for write or sample it for read. Both paths clear `BRDCTL` and flush posted writes to leave the board-control bus idle.

The active target-mode drain path starts when earlier interrupt or event handling calls `ahd_run_tqinfifo()`. It syncs the FIFO DMA area after device writes, processes entries until `cmd_valid` is clear or resources are unavailable, and publishes host progress periodically by updating the `HOST_TQINPOS` bits in `HS_MAILBOX`. Resource unavailability is signaled by `ahd_handle_target_cmd()` returning 1 when no `ccb_accept_tio` is queued for the selected LUN.

## State and Persistence

Persistent controller state affected by this chunk includes:

- SEEPROM contents written by `ahd_write_seeprom()`. These settings are adapter NVRAM and can survive driver unloads and reboots.
- Flexport board-control state written by `ahd_write_flexport()`, especially termination/current-sensing control used by earlier setup paths.
- Loaded sequencer firmware in controller `SEQRAM`, which persists for the lifetime of the controller instance until reset/reload.

Runtime state stored in `struct ahd_softc` includes:

- `ahd->num_critical_sections` and `ahd->critical_sections`, derived from the patched firmware image and later used when coordinating sequencer critical sections.
- `ahd->features`, `ahd->bugs`, and `ahd->flags`, consumed by patch predicates and printed after firmware download.
- Queue and SCB diagnostic state such as `pending_scbs`, free SCB lists, completion-list head registers, current `SCBPTR`, and saved `STACK` entries.
- Target-mode state, when enabled, in `enabled_targets[]`, `black_hole`, `pending_device`, `targetcmds`, `tqinfifonext`, and `AHD_TQINFIFO_BLOCKED`.

Most diagnostic reads are volatile snapshots. `ahd_dump_card_state()` temporarily changes card mode and SCB pointer and reads through FIFO/stack registers that have side effects; it deliberately restores the saved stack and mode but still runs in a fragile error context where concurrent hardware progress must be controlled by pausing.

## Dependencies and Integration Points

This chunk depends heavily on the driver register access layer: `ahd_inb/outb`, `ahd_inw/outw`, `ahd_inl`, `ahd_outsb`, `ahd_inb_scbram`, `ahd_inw_scbram`, `ahd_inl_scbram`, `ahd_set_modes()`, `ahd_save_modes()`, `ahd_restore_modes()`, `ahd_pause()`, `ahd_unpause()`, `ahd_flush_device_writes()`, `ahd_delay()`, and DMA sync wrappers.

It integrates with earlier and adjacent driver code through these call sites:

- `ahd_loadseq()` is invoked during initialization/reinitialization and in the inactive target-mode role-switch path.
- `ahd_dump_card_state()` is called from many error and recovery paths in `aic79xx_core.c`, from PCI setup error handling, and from OS-specific paths in `aic79xx_osm.c`.
- `ahd_read_seeprom()`, `ahd_write_seeprom()`, and `ahd_verify_cksum()` are used by PCI probing/config parsing and by procfs SEEPROM update paths.
- `ahd_read_flexport()` and `ahd_write_flexport()` are used by termination/current-sensing setup in this file and by PCI board setup.
- `ahd_run_tqinfifo()` is called by interrupt/event handling when target-mode incoming commands are pending.

The target-mode code integrates with CAM concepts (`union ccb`, `ccb_accept_tio`, `CAM_*` status values, `xpt_done()`, `xpt_create_path()`, `xpt_free_path()`, `xpt_path_comp()`) and SCSI message/CDB decoding macros. In this Linux-imported tree, much of that target-mode support appears to be compatibility code shared with the original FreeBSD-derived driver and is not necessarily enabled in ordinary Linux builds.

## Risks and Edge Cases

- Patch predicates must be deterministic. `ahd_resolve_seqaddr()` replays patch decisions independently of the main download loop; any predicate that observes mutable hardware state or changes state could produce incorrect branch targets.
- `ahd_download_instr()` casts `&seqprog[instrptr * 4]` to `uint32_t *`. This assumes the sequencer byte array is suitably accessible for unaligned little-endian loads on the target architecture or that compiler/platform constraints make it safe.
- Download constant substitution uses the instruction parity bit as an out-of-band marker. A bad immediate index can read beyond `dconsts[]`, and a malformed firmware image can panic on an unknown opcode.
- `ahd_loadseq()` allocates critical section data with `GFP_ATOMIC` and panics on failure. That matches low-level driver expectations but makes memory pressure during initialization/reload fatal.
- `ahd_print_register()` updates `*cur_column` in the `table == NULL` path without checking `cur_column`; current callers appear to pass a pointer, but the public signature allows `NULL`.
- `ahd_dump_card_state()` is intentionally invasive. It pauses the device, walks potentially corrupt lists, changes mode banks, changes `SCBPTR`, pops and pushes stack entries, and may produce large kernel logs. Its bounded loops reduce but do not eliminate diagnostic-side risk.
- SEEPROM write paths can partially modify persistent NVRAM before returning an error. The function disables writes afterward, but callers must treat nonzero returns as possible partial writes and revalidate checksums.
- Zero-length SEEPROM read/write returns `EINVAL` by design. Callers must not interpret that as successful no-op behavior.
- `ahd_acquire_seeprom()` unconditionally returning success means boards without SEEPROM support are detected later by read/checksum failure rather than acquisition failure.
- Flexport address errors panic rather than returning `EINVAL`, so callers must validate any non-constant addresses before calling.
- `ahd_handle_target_cmd()` assumes a valid `lstate` after falling back to `ahd->black_hole`; if target mode were enabled without a black-hole LUN for disabled targets, dereferencing `lstate->accept_tios` would fault.
- Target command parsing trusts the firmware-provided `bytes[]` layout. It advances over optional tag bytes and one terminator byte, then copies a CDB length based on the opcode group; malformed entries could make the copied CDB semantically invalid even though the fixed 22-byte buffer bounds limit the normal CDB sizes used here.

## Test and Validation Signals

Useful validation for this chunk is mostly hardware, fault-injection, and driver-integration oriented:

- Boot or probe with representative AIC79xx hardware should show successful sequencer download, expected instruction count under `bootverbose`, and no unknown-opcode or critical-section allocation panics.
- Firmware patch matrix testing should cover feature/bug/flag combinations that accept and reject patch blocks, then verify sequencer branch/call targets land on the correct downloaded addresses.
- Fault injection around `kmemdup(..., GFP_ATOMIC)` would confirm the current panic behavior for critical-section allocation failure.
- Error-path tests that trigger `ahd_dump_card_state()` should confirm the card is unpaused only when the dump paused it, modes are restored, stack entries are restored, and SCB/completion list walks terminate on corrupted links.
- SEEPROM tests should cover zero-length operations, normal word reads, bytestream reads, timeout from `ahd_wait_seeprom()`, write-enable failure, per-word write timeout, write-disable timeout, checksum validation success/failure, and partial-write recovery by re-reading and validating the checksum.
- Flexport tests should cover read/write success, arbitration timeout, and all valid addresses 0-7; invalid addresses intentionally panic and should be tested only in controlled fault-injection environments.
- PCI/config integration should verify that VPD and SEEPROM checksum failures cause fallback/default configuration paths rather than accepting corrupt adapter settings.
- If `AHD_TARGET_MODE` is enabled, target-mode tests should queue ATIO CCBs, inject target command FIFO entries with and without tag bytes, verify CDB length decoding for command groups 0/1/2/4/5 and reserved groups, exercise black-hole LUN handling, confirm `AHD_TQINFIFO_BLOCKED` toggles when ATIO resources run out, and check `HS_MAILBOX` host-position updates at the expected FIFO boundaries.
