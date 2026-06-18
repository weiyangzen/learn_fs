# Group Research: group_1156_minix_sources_teaching_minix_minix_drivers_storage_Makefile_sources_9fbb02fa487c

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/teaching/minix`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/Makefile

## Purpose
Top-level MINIX storage driver subtree Makefile. It selects which storage driver subdirectories are built for each architecture and build mode.

## Key Behavior
- Includes `<bsd.own.mk>` and `<bsd.subdir.mk>`.
- When `MKIMAGEONLY == "no"`:
  - On `i386`, builds `ahci`, `fbd`, `filter`, and `virtio_blk`.
  - On `earm`, builds `mmc`.
  - Always builds `vnd`.
- On `i386`, builds legacy `at_wini` and `floppy` regardless of `MKIMAGEONLY`.
- Always builds `ramdisk` and `memory`, with `.WAIT` ordering.
- Explicitly documents that the memory driver must be last for ramdisk image construction.

## Dependencies
- BSD make infrastructure.
- Architecture variables: `MACHINE_ARCH`, `MKIMAGEONLY`.
- Storage subdirectories in the same tree.

## Notes
This file is orchestration only. The ordering of `ramdisk` and `memory` is semantically important for image generation.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/Makefile.inc -->
# File Research: sources/teaching/minix/minix/drivers/storage/Makefile.inc

## Purpose
Shared storage-driver Makefile include.

## Key Behavior
- Includes `../Makefile.inc`.

## Dependencies
- Parent driver-tree build settings.

## Notes
This is a pass-through include used to inherit common driver build configuration.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/ahci/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/ahci/Makefile

## Purpose
Builds the MINIX AHCI storage driver.

## Key Behavior
- Defines program `ahci`.
- Builds from `ahci.c`.
- Links with `libblockdriver`, `libsys`, `libtimers`, and `libmthread`.
- Includes `<minix.service.mk>` for service build integration.

## Dependencies
- AHCI driver uses multithreaded blockdriver support, timers, and system calls.

## Notes
The explicit `LIBMTHREAD` dependency matches `ahci.c` use of `blockdriver_mt_*`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/ahci/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/ahci/ahci.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/ahci/ahci.c

## Purpose
MINIX user-space AHCI driver for SATA ATA/ATAPI devices. It supports hotplug, removable media tracking, custom logical sector sizes, sector-unaligned reads, NCQ, and parallel requests to different devices.

## Architecture
- Maintains global HBA state in `hba_state`.
- Maintains per-port state in `port_state[NR_PORTS]`.
- Exposes a multithreaded `struct blockdriver ahci_dtab`.
- Maps minor devices to AHCI ports through `ahci_map`.
- Uses per-port timers and per-command timers for detection and command timeout.
- Uses contiguous DMA-visible memory for FIS receive buffers, command lists, command tables, temporary identify/capacity buffers, and on-demand padding buffers.

## Port State Machine
The source documents and implements these states:
- `STATE_NO_PORT`: no implemented port.
- `STATE_SPIN_UP`: startup wait for device appearance.
- `STATE_NO_DEV`: no device detected.
- `STATE_WAIT_DEV`: polling for link/device readiness.
- `STATE_WAIT_ID`: identify command pending.
- `STATE_BAD_DEV`: unsupported or unusable device.
- `STATE_GOOD_DEV`: usable device.

Transitions are driven by startup timers, port connection interrupts, PhyRdy changes, identification completion, command failures, and hard resets.

## ATA/ATAPI Support
- ATA path validates nonremovable ATA, LBA, DMA, FLUSH CACHE, and LBA48 support.
- ATAPI path validates removable ATAPI DMA capability and handles CD-ROM read-only status.
- ATAPI helpers implement test unit ready, request sense, load/eject, read capacity, and packet read/write.
- ATA transfer supports DMA EXT and NCQ FPDMA commands.
- Write-through behavior uses FUA when supported and requested through block flags.
- Write cache ioctls support get/set/flush where hardware capability allows.

## I/O Path
- `ahci_transfer` maps a minor to a partition and rejects unavailable/barriered devices.
- `port_transfer` validates vector sizes, limits transfers to `MAX_TRANSFER`, trims EOF, computes sector alignment, and builds PRDs.
- Reads may be sector-unaligned with padding when word-aligned.
- Writes must be sector-aligned; no read-modify-write write path is implemented.
- `setup_prdt` maps client grants with `sys_vumap`, enforces physical contiguity and word alignment, and inserts leading/trailing pad PRDs when required.

## Command Execution
- `port_set_cmd` writes command table and command list entries.
- `port_issue` writes `SACT` for NCQ, barriers compiler reordering, writes `CI`, records pending masks, and arms a timer.
- `port_exec` sleeps the worker thread until interrupt or timeout.
- `port_check_cmds` detects completed commands from `SACT` or `CI`.
- On serious failures, the driver fails outstanding commands and restarts or disconnects the port rather than transparently replaying I/O.

## Hotplug and Failure Handling
- Device changes set `FLAG_BARRIER`, preventing access until close/reopen.
- Hot-unplug and fatal failures call `port_disconnect` and often hard-reset the port.
- The driver intentionally does not implement transparent failure recovery.
- VirtualBox-specific missing interrupt behavior is detected during spin-up timeout by checking the pending PCS bit.

## Initialization and Shutdown
- `ahci_probe` reserves the selected PCI device.
- `ahci_init` maps BAR 6, registers IRQ, resets HBA, enables AHCI and interrupts, reads capabilities, and initializes implemented ports.
- `ahci_set_mapping` builds default device-to-port mappings and supports per-instance `ahciN_map`.
- SEF fresh init announces the block driver.
- SIGTERM defers shutdown until all open ports close, then stops HBA resources and terminates the blockdriver loop.

## Interfaces
- Blockdriver callbacks: open, close, transfer, ioctl, partition lookup, interrupt, alarm, device id.
- Ioctls handled: `DIOCEJECT`, `DIOCOPENCT`, `DIOCFLUSH`, `DIOCSETWC`, `DIOCGETWC`.

## Risks and Edge Cases
- NCQ failure handling cannot identify the exact failed command; remaining pending commands are failed together.
- Assumes lower 32-bit physical addresses in command list/PRD setup by writing upper fields as zero.
- No transparent I/O replay after reset; upper layers see `EIO`.
- Writes reject unaligned ranges rather than synthesizing read-modify-write.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/ahci/ahci.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/ahci/ahci.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/ahci/ahci.h

## Purpose
Private constants, register definitions, command layout definitions, limits, states, flags, and small internal types for the AHCI driver.

## Contents
- AHCI global limits: `NR_PORTS`, `NR_CMDS`.
- Timeout defaults for spin-up, device detection, commands, transfers, and flushes.
- ATA Register Host-to-Device FIS offsets and command constants.
- ATA IDENTIFY word offsets and capability bits.
- ATAPI packet command constants.
- AHCI command list/table offsets and flags.
- HBA and port memory-mapped register offsets and bit masks.
- Memory layout constants for FIS, command list, command table, temporary buffer, and PRDT sizing.
- `cmd_fis_t`, an internal neutral FIS structure later serialized to actual AHCI command table bytes.
- `prd_t` alias to `struct vumap_phys`.
- Legacy-compatible minor sizing: `MAX_DRIVES`, `NR_MINORS`, `NR_SUBDEVS`.
- Port states, command results, port flags, no-port/no-device sentinels, and verbosity levels.

## Dependencies
- Includes `<minix/drivers.h>`.
- Used by `ahci.c` only in this group.

## Notes
The header is hardware-spec dense and is not a public interface. `NR_PRDS` is tied to `NR_IOREQS + 2` to allow lead/trail padding entries around mapped client vectors.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/ahci/ahci.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/at_wini/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/at_wini/Makefile

## Purpose
Builds the MINIX legacy AT Winchester/IDE disk driver.

## Key Behavior
- Defines program `at_wini`.
- Builds from `at_wini.c` and `liveupdate.c`.
- Links with `libblockdriver`, `libsys`, and `libtimers`.
- Includes `<minix.service.mk>`.

## Notes
The extra `liveupdate.c` source provides SEF live update state checks around current ATA command execution.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/at_wini/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/at_wini/at_wini.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/at_wini/at_wini.c

## Purpose
User-space MINIX driver for IBM-AT Winchester/IDE-style disk controllers, with PCI IDE support, SATA-compatible IDE controllers, ATA disks, ATAPI CD-ROM reads, PIO, bus-master DMA, partitioning, geometry, ioctls, and reset/retry handling.

## Architecture
- One driver instance reserves one PCI controller.
- Controller has up to two channels and four actual drives per instance.
- Per-drive state is stored in `struct wini wini[MAX_DRIVES]`.
- Global current-operation variables include `w_command`, `w_drive`, `w_wn`, and `w_dv`.
- Exposes a single-threaded `struct blockdriver w_dtab`.

## Initialization
- `main` sets env args, starts SEF, and enters `blockdriver_task`.
- SEF registers fresh init and live update callbacks.
- `sef_cb_init_fresh` allocates temporary memory, parses boot/env params, probes PCI, initializes controller channels, and announces the service.
- `w_probe` iterates visible PCI devices and reserves the selected instance.
- `w_init` configures native or compatibility channels, IRQ policies, command/control bases, DMA bases, and bus mastering.

## Device Identification
- `w_do_open` prepares the selected minor, skips permanently ignored drives, identifies unprobed or reset-needed drives, runs an ATA test read for non-ATAPI devices, rejects writes to ATAPI, and partitions on first open.
- `w_identify` tries ATA IDENTIFY first, then ATAPI IDENTIFY.
- ATA identify extracts CHS geometry, LBA capability, LBA48 capability, disk size, and DMA support.
- LBA48 sizes above 32-bit sector count are truncated to `ULONG_MAX` sectors in this implementation.
- ATAPI identify marks the drive as ATAPI and leaves size to `atapi_open`.

## Transfer Path
- `w_transfer` handles ATA disk reads/writes.
- Requires sector-aligned positions and sector-multiple request sizes.
- Trims reads/writes to partition EOF.
- Limits transfer size to per-drive `max_count`.
- Uses DMA if available and setup succeeds; otherwise falls back to PIO.
- PIO path loops sector by sector with interrupt waits and `sys_safe_insw/sys_safe_outsw` or local `sys_insw/sys_outsw`.
- DMA path builds PRDT entries for grant-backed or local memory, observes 64K boundary restrictions, starts bus-master DMA, waits for interrupts/status, and disables DMA on detected DMA anomalies.

## ATA Command Handling
- `do_transfer` selects CHS, LBA28, or LBA48 command forms.
- `com_out` writes 28-bit command registers.
- `com_out_ext` writes LBA48 high-order then low-order registers.
- `com_simple` sends one-command operations and waits for completion.
- `w_waitfor`, `w_intr_wait`, and `at_intr_wait` combine polling, synchronous alarms, interrupt messages, and queued unrelated blockdriver messages.

## Recovery and Errors
- Timeouts call `w_timeout`, which reduces `max_count` for data commands, marks the controller deaf, and may ignore devices during testing.
- `w_need_reset` marks all drives on the same command base as `DEAF` and not initialized.
- `w_reset` strobes controller reset, waits for ready, clears `DEAF`, and reenables native IRQs.
- Retries stop at `max_errors`; bad-sector errors are not retried further.

## ATAPI Support
- `atapi_open` assigns a large fixed DVD-size capacity rather than querying real capacity.
- ATAPI writes return `EINVAL`.
- `atapi_transfer` builds SCSI READ10 packets and supports PIO reads, optional DMA for aligned full-CD-sector reads, extra-prefix discard for 2048-byte CD sectors, and retry with optional sense logging.
- `atapi_sendpacket` issues PACKET commands and writes the 12-byte packet.
- `atapi_intr_wait` interprets ATAPI phase from status and interrupt reason registers.

## Ioctls
- `DIOCTIMEOUT`: adjusts or restores timeout/retry behavior.
- `DIOCOPENCT`: returns current open count.
- `DIOCFLUSH`: flushes ATA write cache for initialized non-ATAPI devices.

## Risks and Edge Cases
- Uses global current-drive/current-command state, fitting single-threaded blockdriver operation but fragile for concurrency.
- ATAPI size is approximate, not device-reported.
- Large ATA devices are truncated to 32-bit sector counts.
- DMA setup panics on some mapping failures instead of returning user errors.
- Some legacy K&R function definitions remain, reflecting old MINIX code style.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/at_wini/at_wini.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/at_wini/at_wini.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/at_wini/at_wini.h

## Purpose
Private constants and declarations for the `at_wini` IDE/ATA/ATAPI driver.

## Contents
- Includes MINIX driver, blockdriver, and drvlib headers.
- Debug toggles: `VERBOSE`, `VERBOSE_DMA`, `ATAPI_DEBUG`.
- Legacy command/control I/O port bases.
- PCI BAR offsets for control and secondary DMA.
- ATA register offsets and status/error bits.
- ATA command opcodes, including LBA48 and DMA variants.
- ATA IDENTIFY word offsets and DMA capability bits.
- Bus-master DMA register offsets/status bits.
- LBA threshold constants.
- ATAPI/SCSI packet constants and phase bits.
- Driver-local error codes.
- Timeout/recovery constants and state flags.
- Drive/minor count constants.
- `NO_DMA_VAR` boot variable name.
- Native PCI IDE interface bits.
- Live update callback declarations.

## Notes
This header mixes ATA and ATAPI definitions and defines `REG_STATUS` twice in ATA and ATAPI sections with compatible numeric value but different bit names.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/at_wini/at_wini.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/at_wini/liveupdate.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/at_wini/liveupdate.c

## Purpose
SEF live update readiness policy for `at_wini`.

## Key Behavior
- Imports global `w_command`.
- Defines helpers to classify idle, read-pending, and write-pending ATA commands.
- Defines custom live update states:
  - `AT_STATE_READ_REQUEST_FREE`
  - `AT_STATE_WRITE_REQUEST_FREE`
- `sef_cb_lu_prepare` allows:
  - standard request/protocol-free states only when no command is pending.
  - read-request-free when no read command is pending.
  - write-request-free when no write command is pending.
- `sef_cb_lu_state_isvalid` accepts standard states and the two custom states.
- `sef_cb_lu_state_dump` prints current state and readiness predicates.

## Dependencies
- Includes `at_wini.h` for command constants and SEF declarations.

## Notes
The live update safety model is command-granularity based. It does not serialize or export full controller state, only declares whether the current in-flight command class permits update.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/at_wini/liveupdate.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/fbd/Makefile

## Purpose
Builds the Faulty Block Device service.

## Key Behavior
- Defines program `fbd`.
- Builds from `fbd.c`, `rule.c`, and `action.c`.
- Links with `libblockdriver` and `libsys`.
- Adds `CPPFLAGS+= -DDEBUG=0`.
- Includes `<bsd.own.mk>` and `<minix.service.mk>`.
- Notes that FBD requires NetBSD libc.

## Notes
FBD is a block proxy/fault injector, not a physical driver.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/action.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/fbd/action.c

## Purpose
Implements FBD rule actions and hook dispatch.

## Action Types
- `FBD_ACTION_CORRUPT`: modifies data in the I/O buffer.
- `FBD_ACTION_ERROR`: shortens request before a matched range and returns configured error afterward.
- `FBD_ACTION_MISDIR`: redirects the request to a random aligned position in a configured target range.
- `FBD_ACTION_LOSTTORN`: limits the actual forwarded request but reports full success.

## Key Functions
- `get_rand`: unbiased random value in `[0, max]` using `lrand48`.
- `get_range`: computes the affected overlap of a rule against a request.
- `limit_range`: truncates an iovec/count pair to a byte size.
- `action_io_corrupt`: supports zero, persistent deterministic pattern, and random byte corruption.
- `action_mask`: maps action type to needed pre/io/post hooks.
- `action_pre_hook`, `action_io_hook`, `action_post_hook`: dispatch based on action.

## Risks and Edge Cases
- Persistent corruption only works for dword-aligned positions and sizes; otherwise it silently does nothing for that action.
- Misdir cannot interpret end `0` as disk EOF because this layer does not know disk size.
- Lost/torn action can make upper layers believe a full write completed even when only the lead portion was sent.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/action.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/action.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/fbd/action.h

## Purpose
Declares FBD action hook APIs.

## Exports
- `action_mask`
- `action_pre_hook`
- `action_io_hook`
- `action_post_hook`

## Dependencies
- Expects `struct fbd_rule`, `iovec_t`, `size_t`, and `u64_t` to be available through including context.

## Notes
This is a narrow internal header used by the FBD rule engine.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/action.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/fbd.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/fbd/fbd.c

## Purpose
Faulty Block Device blockdriver. It proxies one underlying block driver while applying configurable fault-injection rules.

## Architecture
- Exposes `BLOCKDRIVER_TYPE_OTHER`.
- Takes options:
  - `label`: DS label of underlying driver.
  - `minor`: underlying driver minor.
- Resolves the underlying endpoint through DS.
- Allocates a contiguous scratch buffer of `BUF_SIZE`.
- Seeds random behavior with `srand48(getticks())`.

## Request Handling
- `fbd_open` and `fbd_close` forward `BDEV_OPEN` and `BDEV_CLOSE`.
- `fbd_ioctl` handles FBD rule ioctls locally and forwards other ioctls through indirect grants.
- `fbd_transfer` computes total request size, finds matching rules, applies pre hooks, forwards the request directly or through copy-buffer interposition, then applies post hooks.

## Direct Transfer
- `fbd_transfer_direct` creates indirect grants for each caller iovec entry, grants the vector to the underlying driver, sends `BDEV_SCATTER` or `BDEV_GATHER`, then revokes all grants.

## Copy Transfer
- `fbd_transfer_copy` copies write data into a local buffer before forwarding, or reads into local buffer before copying back to the caller.
- Used when IO hooks are needed, enabling data corruption/modification.
- Preserves original iovec chunking for forwarding to avoid performance instability with bad hardware.
- Dynamically allocates larger buffers for requests bigger than `BUF_SIZE`.

## Risks and Edge Cases
- Uses `assert` for grant creation and large allocation success in several paths.
- Does not handle underlying driver endpoint changes after startup.
- Rule actions can intentionally violate normal block semantics, including false success and misdirected writes.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/fbd.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/rule.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/fbd/rule.c

## Purpose
Manages FBD fault-injection rule storage, ioctl control, matching, and hook fan-out.

## Data Structures
- `rules[MAX_RULES]`: fixed active rule table.
- `matches[MAX_RULES]`: rules matched by the current request.
- `nr_matches`: count of current matches.

## Ioctl Control
- `FBDCADDRULE`: finds a free slot, copies in a rule, assigns its rule number, and returns that number.
- `FBDCDELRULE`: copies in a rule number and disables the matching active rule.
- `FBDCGETRULE`: copies in a rule number from the struct, then copies out the full active rule.

## Matching Semantics
- Rule range must overlap request range.
- Rule flags must match read/write operation flags.
- `skip` suppresses a number of initial matches.
- `count` limits lifetime and disables the rule when it reaches zero.

## Hook Fan-out
- `rule_find` stores matched rules and ORs their action hook masks.
- `rule_pre_hook`, `rule_io_hook`, and `rule_post_hook` invoke only rules whose action needs that hook.

## Notes
Rule state mutates during matching. This is expected for `skip` and `count`, but means matching is not a pure query.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/rule.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/rule.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/fbd/rule.h

## Purpose
Internal FBD rule API and hook bit definitions.

## Contents
- `MAX_RULES` is 16.
- Declares rule ioctl, matching, and hook functions.
- Defines hook masks:
  - `PRE_HOOK`
  - `IO_HOOK`
  - `POST_HOOK`

## Notes
The fixed rule count bounds memory and matching cost.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/fbd/rule.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/filter/Makefile

## Purpose
Builds the MINIX filter block driver.

## Key Behavior
- Defines program `filter`.
- Builds from `main.c`, `sum.c`, `driver.c`, `util.c`, `crc.c`, and `md5.c`.
- Links with `libblockdriver` and `libsys`.
- Adds debug macros `DEBUG=1` and `DEBUG2=0`.
- Includes `<minix.service.mk>`.

## Notes
Only a subset of the built sources is in this work item. `sum.c` and `util.c` are referenced by this Makefile but are outside the requested file list.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/crc.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/filter/crc.c

## Purpose
CRC32 checksum implementation used by the filter driver checksum layer.

## Key Behavior
- Contains a static CRC table adapted from `cksum.c`.
- `compute_crc` iterates over bytes, computes table index from the high byte of the current state XOR input byte, substitutes intermediate zero indexes with a cycling auxiliary sequence, and updates the checksum with shift/XOR.

## Licensing
Header states copyright 1991 by Vincent Archer and allows redistribution if the copyright notice is preserved.

## Notes
This is not a generic library wrapper; it is a local checksum primitive for filter integrity metadata.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/crc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/crc.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/filter/crc.h

## Purpose
Header for filter CRC support.

## Exports
- `compute_crc(const unsigned char *b, size_t n)`

## Notes
Small guarded internal header.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/crc.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/driver.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/filter/driver.c

## Purpose
Lowest layer of the filter driver. It manages communication with one main disk driver and optionally one backup disk driver, including open/close, async request forwarding, timeouts, restart/refresh through RS, DS event tracking, and mirrored I/O validation.

## Driver State
- Maintains `driver[2]` for main and backup labels, minors, endpoints, restart state, errors, retries, and kill counts.
- Tracks async IPC messages in `amsgtable[2]`.
- Stores raw disk size after opening and validates mirrored disk size equality.
- Counts problem types in `problem_stats`.

## Initialization and Shutdown
- `driver_init` resolves main driver endpoint, opens it, and optionally resolves/opens backup.
- `driver_open` sends `BDEV_OPEN` and retrieves partition size with `DIOCGETP`.
- `driver_shutdown` closes main and optional backup and prints debug statistics.

## Failure Model
- `bad_driver` marks a driver problem and returns `RET_REDO`.
- Problems are typed as `BD_DEAD`, `BD_PROTO`, or `BD_DATA`.
- `check_driver` applies retry thresholds, restart thresholds, endpoint refresh detection, and RS restart/refresh.
- When mirror mode is active and one driver exceeds restart threshold, mirroring is disabled and the surviving driver becomes main if necessary.
- Without mirroring, exceeding restart threshold returns the stored driver error, with `EAGAIN` normalized to `EIO`.

## IPC Flow
- `flt_senda` sends requests asynchronously with `ipc_senda`.
- `flt_receive` receives replies, handles DS notifications, handles CLOCK timeout notifications, ignores stray messages, and classifies missing replies as dead/protocol problems.
- `flt_sendrec` wraps async send/receive with an alarm.
- `do_sendrec_both` sends to both drivers in parallel if labels differ, or sequentially if the same label is used.
- `paired_sendrec` selects one-driver or two-driver behavior.

## Grants and I/O
- `single_grant` splits requests by `CHUNK_SIZE` or full size, creates direct grants for chunks, then grants the iovec vector.
- `paired_grant` creates grants for main and optionally backup.
- `read_write` constructs `BDEV_SCATTER`/`BDEV_GATHER`, sends to one or both drivers, revokes grants, checks reply type/status/short transfers, and updates `*sizep`.

## DS Event Handling
- `ds_event` consumes DS events, filters for `drv.blk.*` with `DS_DRIVER_UP`, and records expected or pending up events for managed endpoints.

## Risks and Edge Cases
- `driver_open` and `driver_close` explicitly note unfinished blocking `ipc_sendrec` behavior.
- Same-driver mirroring is labeled "not tested" in initialization and handled sequentially later.
- Some reply validation treats truncated replies as protocol errors unless they align with disk EOF.
- Request retry/restart policy is stateful and can mutate global mirror configuration.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/driver.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/inc.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/filter/inc.h

## Purpose
Shared include file for the filter driver.

## Contents
- Sets `_SYSTEM`.
- Includes MINIX config, IPC, syslib/sysutil, partition, DS, blockdriver, optset, and C library headers.
- Defines `SECTOR_SIZE`.
- Defines checksum types: nil, XOR, CRC, MD5.
- Defines disk operation modes: write, read from one disk, read from both disks.
- Defines `struct driverinfo` for managed lower drivers.
- Defines driver-up event states and `RET_REDO`.
- Defines driver problem states.
- Defines main/backup indexes, buffer sizes, label size, and `sector_t`.
- Declares globals from `main.c`.
- Declares APIs from `sum.c`, `driver.c`, and `util.c`.

## Notes
This is the central coupling header for the filter service. It exposes many globals rather than encapsulating configuration.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/inc.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/main.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/filter/main.c

## Purpose
Top-level blockdriver interface for the MINIX filter driver. It parses configuration, exposes blockdriver callbacks, copies caller data into local buffers, delegates integrity/mirror work to `transfer`, and handles SEF startup/shutdown.

## Configuration
Global options include:
- Main/backup labels and minors.
- Checksum enable/disable.
- Mirror enable/disable.
- Checksum layout enable/disable.
- Checksum algorithm: nil, XOR, CRC, MD5.
- Bad-checksum error policy.
- Retry/restart/timeout thresholds.
- Request chunk size.

## Startup
- `main` sets env args, performs SEF startup, and enters `blockdriver_task`.
- `sef_cb_init_fresh` parses arguments, allocates the static buffer, initializes checksum layer with `sum_init`, initializes lower driver management with `driver_init`, subscribes to block driver DS events, and announces service.
- Restart init reuses the fresh init callback.

## Block Interface
- Type is `BLOCKDRIVER_TYPE_OTHER`.
- `filter_open` and `filter_close` are no-ops.
- `filter_transfer`:
  - Computes request size.
  - Requires sector-aligned position and sector-multiple size.
  - Allocates local buffer through `flt_malloc`.
  - Copies write data from caller grants into the local buffer.
  - Calls `transfer` with `FLT_WRITE` or `FLT_READ`.
  - On `RET_REDO`, calls `check_driver` for main and backup then retries.
  - Copies read data back to caller.
- `filter_ioctl`:
  - Rejects `DIOCSETP`, `DIOCTIMEOUT`, and `DIOCOPENCT`.
  - Handles `DIOCGETP` by returning size converted through checksum-layout logic.
  - Returns `ENOTTY` for unknown ioctls.
- `filter_other` handles DS notifications.

## Argument Validation
- Requires exactly one option string.
- Requires valid main label/minor.
- Requires valid backup label/minor if mirroring is enabled.
- Enabling checksums implies checksum layout.
- Validates checksum metadata density against sector size.
- Converts timeout seconds to ticks.

## Risks and Edge Cases
- `filter_transfer` ignores return values from `vcarry`; safecopy failures may not stop processing.
- Alignment restrictions are strict and sector-based.
- Open/close do not propagate to lower drivers at caller-open granularity; lower drivers are opened at filter initialization.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/main.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/md5.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/filter/md5.c

## Purpose
MD5 message digest implementation used by the filter checksum layer.

## Origin and Licensing
- Public-domain implementation by Colin Plumb.
- Modified in 1997 by Jim Kingdon to avoid relying on exactly 32-bit integer types.
- The file states no copyright is claimed.

## Key Functions
- `getu32` and `putu32`: little-endian byte conversion independent of host endianness.
- `MD5Init`: initializes digest state.
- `MD5Update`: updates state with arbitrary-length input, processing 64-byte blocks.
- `MD5Final`: pads input, appends bit length, produces 16-byte digest, and clears context.
- `MD5Transform`: core MD5 round function over one 64-byte block.
- Optional `TEST` main can print MD5 for command-line strings when compiled with `TEST`.

## Notes
The implementation uses old-style K&R function definitions. It is a vendored checksum primitive, not specific to MINIX blockdriver APIs.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/md5.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/md5.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/filter/md5.h

## Purpose
Header for the vendored MD5 implementation.

## Contents
- Defines `uint32` as `unsigned long`, requiring at least 32 bits.
- Defines `struct MD5Context` with digest buffer, bit counters, and 64-byte input block.
- Declares `MD5Init`, `MD5Update`, `MD5Final`, and `MD5Transform`.

## Notes
The header documents that speed matters more than exact 32-bit type width for this implementation.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/md5.h -->