# subset-b-005536 Research

Grouped research for USB storage transport/UAS/device quirk tables and USB Type-C alternate-mode build/runtime files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sierra_ms.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/sierra_ms.h

## Purpose

`sierra_ms.h` is the tiny declaration header for the Sierra USB mass-storage initializer used by the generic `usb-storage` probe path when matching Sierra modem/storage devices. It lets `usb.c` include the initializer without depending on the implementation body.

## Important APIs, Types, and Functions

The only API is `int sierra_ms_init(struct us_data *us)`, which receives the per-device `struct us_data` allocated by the usb-storage core. The header relies on `struct us_data` being visible or forward-declared by the including translation unit.

## Control Flow

There is no executable control flow in this header. `usb.c` includes it before expanding `unusual_devs.h`; matched device entries can then name `sierra_ms_init` as an `initFunction`, and `usb_stor_acquire_resources()` calls that initializer before the usb-storage control thread is started.

## State and Persistence Behavior

The header stores no state. Any state changes happen in the initializer implementation through `struct us_data`, device transport hooks, or extra destructor/private data attached by the subdriver. There is no filesystem persistence.

## Dependencies and Integration Points

It integrates with the usb-storage unusual-device table and the standard probe sequence in `usb.c`. It depends on the mass-storage core's `struct us_data` contract and on the implementation being linked when Sierra support is built.

## Risks and Edge Cases

Because this is only a prototype, the risk is interface drift: a signature mismatch between the initializer implementation and this header would break builds, and missing inclusion would break `unusual_devs.h` entries that name the initializer. Runtime risks belong to the initializer body.

## Test Signals

Compile coverage with Sierra mass-storage support enabled is the primary signal. Runtime validation should attach a Sierra device that matches the unusual table and confirm the initializer is invoked before SCSI scanning begins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sierra_ms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/transport.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/transport.c

## Purpose

`transport.c` implements the low-level USB Mass Storage transport engine for classic `usb-storage`. It translates SCSI commands into Control/Bulk/Interrupt or Bulk-Only USB transactions, manages URB and scatter-gather transfer lifetimes, performs automatic REQUEST SENSE, and drives reset recovery when a transport or device phase fails.

## Important APIs, Types, and Functions

Transfer helpers include `usb_stor_control_msg()`, `usb_stor_ctrl_transfer()`, `usb_stor_bulk_transfer_buf()`, `usb_stor_bulk_srb()`, `usb_stor_bulk_transfer_sg()`, `usb_stor_clear_halt()`, and `usb_stor_stop_transport()`. `usb_stor_msg_common()` is the shared URB submission/wait path and is the center of the abort/disconnect race contract. `interpret_urb_result()` maps USB status values into `USB_STOR_XFER_*` results.

Transport entry points are `usb_stor_CB_transport()` for Control/Bulk and Control/Bulk/Interrupt devices, `usb_stor_Bulk_transport()` for Bulk-Only Transport, `usb_stor_Bulk_max_lun()` for discovery, and reset helpers `usb_stor_CB_reset()`, `usb_stor_Bulk_reset()`, and `usb_stor_port_reset()`. `usb_stor_invoke_transport()` is the SCSI-facing orchestration layer that calls the selected transport and then handles autosense, capacity hacks, underflow checks, and reset recovery.

## Control Flow

Queued SCSI commands enter through the protocol layer and call `usb_stor_invoke_transport()`. That clears residual data, invokes the device-specific transport function pointer, and short-circuits if the command timed out or the transport reported a fatal error. Command failures trigger autosense unless the transport supplied sense data itself. Autosense temporarily rewrites the SCSI command with `scsi_eh_prep_cmnd()`, selects 6- or 12-byte REQUEST SENSE based on subclass, retries with a smaller sense buffer if a device rejects large sense, then restores the original command and updates `srb->result`.

Bulk-Only transport sends a CBW over bulk-out, optionally transfers data over bulk-in or bulk-out, then reads a CSW. It handles delayed devices (`US_FL_GO_SLOW`), long reads by returning fake invalid-CDB sense data, skipped data phases where the CSW appears in the data buffer, zero-length CSWs that need a retry, bad tags optionally masked by `US_FL_BULK_IGNORE_TAG`, learned nonstandard CSW signatures, and unreliable residues via `US_FL_IGNORE_RESIDUE`. CBI transport sends the command over control, transfers any data over bulk, then reads a two-byte interrupt status for CBI devices and clears the data pipe after reported failures.

## State and Persistence Behavior

There is no file-backed persistence. State is per-device in `struct us_data`: `current_urb`, `current_sg`, `iobuf`, DMA address, dynamic flags, current SCSI command, learned CSW signature, tag counter, max LUN, and last-sector retry state. Hardware and device state changes include endpoint halt clearing, bulk/class resets, and port resets. The last-sector hack mutates in-memory retry counters and may rewrite a command result/sense buffer to stop repeated end-of-disk retries.

## Dependencies and Integration Points

The file depends on USB core URBs, scatter-gather helpers, endpoint halt/reset APIs, SCSI command and error-handling helpers, block disk capacity data, and usb-storage protocol glue. It exports many functions for usb-storage subdrivers and depends on `usb.h`, `transport.h`, `protocol.h`, `scsiglue.h`, and `debug.h`.

## Risks and Edge Cases

Abort and disconnect races are the dominant risk. The code relies on precise ordering around `US_FLIDX_URB_ACTIVE`, `US_FLIDX_SG_ACTIVE`, `US_FLIDX_ABORTING`, and `US_FLIDX_DISCONNECTING` so an active transfer is cancelled exactly once and never during `usb_submit_urb()`. Autosense rewrites live SCSI command fields and must restore them on every path. Device compatibility handling is deliberately permissive, so incorrect residues, signatures, tags, or skipped phases can mask real device faults. Reset recovery drops `dev_mutex` for port reset and then reacquires it, so call sites must follow the locking contract.

## Test Signals

Useful validation includes BOT and CBI devices, short/long/stalled transfers, SG and non-SG buffers, timeout/abort/disconnect during URB submission and wait, GetMaxLUN failures, bad CSW signature/tag/residue cases, skipped data phases, autosense success/failure/large-sense fallback, last-sector capacity quirks, class reset fallback after port reset failure, and endpoint halt clearing after STALL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/transport.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/transport.h

## Purpose

`transport.h` declares the usb-storage transfer and transport API shared between the core, protocol handlers, and device-specific subdrivers. It also defines the return-code taxonomy that separates USB transfer outcomes from higher-level SCSI transport outcomes.

## Important APIs, Types, and Functions

The header defines `USB_STOR_XFER_GOOD`, `USB_STOR_XFER_SHORT`, `USB_STOR_XFER_STALLED`, `USB_STOR_XFER_LONG`, and `USB_STOR_XFER_ERROR` for low-level transfers, plus `USB_STOR_TRANSPORT_GOOD`, `USB_STOR_TRANSPORT_FAILED`, `USB_STOR_TRANSPORT_NO_SENSE`, and `USB_STOR_TRANSPORT_ERROR` for command transports. It declares CBI and BOT entry points, reset helpers, transfer helpers, `usb_stor_invoke_transport()`, and `usb_stor_stop_transport()`.

## Control Flow

There is no executable logic here, but the constants define how control flows through `transport.c`: transfer helpers return `USB_STOR_XFER_*`, transport implementations convert those into `USB_STOR_TRANSPORT_*`, and `usb_stor_invoke_transport()` decides whether to autosense, complete, or reset. The comment documents that aborts are represented as generic errors and distinguished by checking dynamic flags rather than a separate return code.

## State and Persistence Behavior

The header stores no state. It exposes APIs that operate on per-device `struct us_data` and per-command `struct scsi_cmnd` state owned by the usb-storage core. There is no persistence.

## Dependencies and Integration Points

It includes block-device definitions for SCSI buffer handling and assumes `struct us_data` is declared by `usb.h` in includers. It is included by `usb.c`, `transport.c`, protocol implementations, and subdriver modules that need to submit transfers or reset devices.

## Risks and Edge Cases

The return code ordering is semantically important: transport code tests relative severity in some paths. Adding new codes or changing values could alter error handling. Callers must not confuse `USB_STOR_XFER_*` with `USB_STOR_TRANSPORT_*`; doing so would make failed commands look like dead transports or vice versa.

## Test Signals

Compile all usb-storage transports and subdrivers. Runtime tests should confirm each return class drives the expected autosense, retry, reset, and SCSI result behavior in `usb_stor_invoke_transport()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/transport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/uas-detect.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/uas-detect.h

## Purpose

`uas-detect.h` contains shared UAS detection helpers used by both `uas.c` and `usb.c`. It decides whether an interface can and should bind to the UAS driver instead of falling back to classic `usb-storage`, including endpoint validation and bridge-specific quirks.

## Important APIs, Types, and Functions

`uas_is_interface()` recognizes mass-storage/SCSI/UAS alternate settings. `uas_find_uas_alt_setting()` scans a USB interface for such an alternate setting. `uas_find_endpoints()` parses endpoint extra descriptors with `USB_DT_PIPE_USAGE` and maps command, status, data-in, and data-out endpoints. `uas_use_uas_driver()` combines alternate-setting discovery, endpoint presence, device quirks, module `quirks=` overrides via `usb_stor_adjust_quirks()`, HCD scatter-gather support, and SuperSpeed streams support.

## Control Flow

When `usb-storage` probes a device, it calls `uas_use_uas_driver()` and declines binding if UAS is viable. When `uas.c` probes, the same helper must return true before the driver switches the interface to the UAS alternate setting. The helper first checks descriptors, then applies known ASMedia, Seagate, Realtek/HIKSEMI, and user-supplied quirks, then rejects UAS if `US_FL_IGNORE_UAS` is set, scatter-gather is unsupported, or SuperSpeed streams are required but unavailable.

## State and Persistence Behavior

The helpers do not persist state. They compute a `u64` flags value returned to the caller and may emit warnings. Runtime state such as selected alternate setting, allocated streams, and SCSI host data is created later by `uas.c`.

## Dependencies and Integration Points

The file depends on USB descriptors, HCD capabilities, UAS pipe-usage descriptors, `usb.h`, and `usb_stor_adjust_quirks()`. It is an integration point between the legacy usb-storage driver and the UAS driver, preventing both from binding to the same capable interface.

## Risks and Edge Cases

Endpoint extra descriptor parsing assumes sane descriptor lengths; malformed descriptors with zero length could cause parser trouble in USB descriptor walking. ASMedia detection uses power, speed, product IDs, and stream counts as heuristics because IDs are reused. String-based HIKSEMI detection depends on manufacturer/product strings being present and exact. Overriding flags through the `quirks=` parameter can force fallback or remove safeguards.

## Test Signals

Test UAS-capable devices with and without all four pipe-usage endpoints, USB2 and SuperSpeed ASMedia bridges, Seagate enclosures, RTL9210/HIKSEMI MD202 strings, HCDs without SG, HCDs without streams, and module quirk overrides that add or remove `US_FL_IGNORE_UAS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/uas-detect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/uas.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/uas.c

## Purpose

`uas.c` implements the USB Attached SCSI driver. It binds UAS-capable USB mass-storage interfaces, allocates streams when available, exposes a SCSI host with tagged queueing, submits command/status/data URBs, handles UAS IUs, and coordinates reset, suspend, shutdown, and disconnect.

## Important APIs, Types, and Functions

`struct uas_dev_info` stores the USB interface/device, URB anchors, quirk flags, queue depth, endpoint pipes, stream mode, reset/shutdown state, pending command table, spinlock, and work items. `struct uas_cmd_info` is per-SCSI-command private state with UAS tag, state bits, and URB pointers. Key paths include `uas_queuecommand_lck()`, `uas_submit_urbs()`, `uas_stat_cmplt()`, `uas_data_cmplt()`, `uas_eh_abort_handler()`, `uas_eh_host_reset_handler()`, `uas_configure_endpoints()`, `uas_probe()`, `uas_pre_reset()`, `uas_post_reset()`, `uas_suspend()`, `uas_disconnect()`, and `uas_shutdown()`.

## Control Flow

Probe first reuses `uas_use_uas_driver()` to validate the interface, switches to the UAS alternate setting, allocates a SCSI host, initializes anchors/work, discovers UAS endpoints, allocates USB streams for SuperSpeed devices, registers the host, and schedules asynchronous scanning. SCSI queueing finds a free one-based UAS tag, initializes state bits for status, command, and optional data URBs, pre-submits data URBs when streams are unavailable, and either submits everything immediately or queues work for retry on allocation/submission pressure.

Status URB completions decode IU tags and IDs. STATUS IUs copy sense data and complete commands; READ_READY and WRITE_READY trigger data URB submission; RESPONSE IUs evaluate task-management responses; errors cancel outstanding data URBs. Data URB completions clear inflight bits, set residuals or host errors, and call `uas_try_complete()`. Completion only calls `scsi_done()` after command, data-in, data-out, and abort state are all clear. Reset paths block requests, wait for pending commands, free and reallocate streams, kill anchored URBs on host reset, zap command table entries, and report bus resets.

## State and Persistence Behavior

State is entirely in memory and USB device configuration: command slots in `cmnd[]`, URB anchors, per-command state flags, stream allocation, endpoint pipes, SCSI queue depth, and quirk flags. The driver changes USB alternate settings, allocates/frees streams, and on restart shutdown deliberately switches back to altsetting 0 and resets the device so firmware/BIOS code sees usb-storage mode. There is no filesystem persistence.

## Dependencies and Integration Points

The driver depends on USB core, UAS descriptors and IUs, SuperSpeed streams, scatter-gather support, SCSI host/template APIs, SCSI error handling, workqueues with `WQ_MEM_RECLAIM`, and shared usb-storage quirk definitions. It integrates with `unusual_uas.h`, `uas-detect.h`, `scsiglue.h`, and SCSI block-device configuration flags such as broken FUA, max sectors, no REPORT LUNS, and capacity heuristics.

## Risks and Edge Cases

The command state machine is concurrency-sensitive: status, command, data, abort, reset, and workqueue paths all coordinate under `devinfo->lock`. `uas_eh_abort_handler()` intentionally returns `FAILED` because it does not send a UAS abort task management command; it only drops local references and kills data URBs. SuperSpeed streams reserve two tags, so queue-depth math must avoid off-by-one firmware bugs. Suspend/pre-reset wait loops can time out if a device stops sending status IUs. The shutdown mode switch/reset is scoped to system restart because some firmware hangs with devices left in UAS mode.

## Test Signals

Validate UAS and fallback binding, endpoint pipe mapping, USB2 non-stream mode, SuperSpeed stream allocation/freeing, tagged queue depth, READ_READY/WRITE_READY sequencing, bidirectional command handling, sense copying, RESPONSE IU error mapping, data URB errors/residuals, allocation retry work, SCSI aborts, host reset, pre/post reset, suspend timeout, disconnect with pending commands, and restart shutdown reverting to altsetting 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/uas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_alauda.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_alauda.h

## Purpose

`unusual_alauda.h` is a specialized usb-storage device table for Alauda-based card readers that are handled by the `USB_PR_ALAUDA` transport rather than by the generic mass-storage path.

## Important APIs, Types, and Functions

The file contributes two `UNUSUAL_DEV()` rows for Olympus and related Alauda devices. Each row sets `USB_SC_SCSI`, `USB_PR_ALAUDA`, and `init_alauda` with no extra flags.

## Control Flow

`usual-tables.c` includes this file in its ignore table so the standard usb-storage driver can decline these devices. The specialized Alauda subdriver includes the same macro-style data in its own match table and initializer path. At probe time, matching by VID/PID/bcdDevice chooses the Alauda-specific protocol and initializer.

## State and Persistence Behavior

The header has no state. It influences probe-time matching and initializer selection; any persistent media state belongs to the card-reader device and subdriver.

## Dependencies and Integration Points

It depends on the includer defining `UNUSUAL_DEV`, the `USB_SC_SCSI` and `USB_PR_ALAUDA` constants, and the `init_alauda` initializer symbol. Its integration point is the libusual/usb-storage split between generic and specialized drivers.

## Risks and Edge Cases

VID/PID/bcd ranges are exact compatibility gates. A firmware revision outside the listed range may bind to the wrong driver, while an overly broad range could steal unrelated devices. The standard driver ignore table must remain aligned with the specialized subdriver table.

## Test Signals

Build with Alauda support enabled, verify the entries appear in the intended USB ID table, attach matching readers, and confirm the generic driver ignores them while the Alauda transport initializes and scans media.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_alauda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_cypress.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_cypress.h

## Purpose

`unusual_cypress.h` lists Cypress-based devices that need the Cypress ATACB protocol path rather than fully generic usb-storage handling.

## Important APIs, Types, and Functions

The file contributes three `UNUSUAL_DEV()` entries using Cypress-related subclasses/transports, including entries that route to `USB_PR_CYP_ATACB` behavior in the broader usb-storage stack. The macro arguments provide device ID ranges, short inquiry strings, protocol override, transport override, optional initializer, and flags.

## Control Flow

The file is consumed through macro expansion by usb-storage tables. Generic usb-storage ignore logic uses the rows to avoid claiming devices intended for the Cypress subdriver, while the specialized path uses them to select the nonstandard command wrapper.

## State and Persistence Behavior

There is no runtime state in the header. It only controls probe-time matching. Device state is managed by the Cypress transport implementation and the SCSI/media layers.

## Dependencies and Integration Points

It depends on `UNUSUAL_DEV` being defined by the includer and on Cypress protocol constants and initializer symbols being available where used. It integrates with `usual-tables.c`, usb-storage device ID matching, and any Cypress-specific transport module.

## Risks and Edge Cases

The table is compatibility-sensitive: incorrect bcd ranges can either miss devices that need the Cypress path or force the path on compatible generic devices. Since these entries are small, stale firmware knowledge is the main maintenance risk.

## Test Signals

Compile the Cypress transport configuration, inspect generated USB modalias tables, attach each represented bridge revision, and validate command execution and media enumeration through the specialized protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_cypress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_datafab.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_datafab.h

## Purpose

`unusual_datafab.h` lists Datafab and compatible flash readers that require the `USB_PR_DATAFAB` usb-storage protocol transport. These devices historically use nonstandard command handling and are kept out of the generic mass-storage path.

## Important APIs, Types, and Functions

The file contains ten `UNUSUAL_DEV()` rows, mostly VID `0x07c4` product variants plus one compatible ID. Rows set `USB_SC_SCSI`, `USB_PR_DATAFAB`, no initializer, and in selected cases `US_FL_SINGLE_LUN`.

## Control Flow

Macro expansion inserts these IDs into ignore or specialized subdriver tables. During probe, a matching device is associated with Datafab command handling; if `US_FL_SINGLE_LUN` is present, the SCSI scan is constrained to LUN 0.

## State and Persistence Behavior

The header persists no state. It shapes in-memory probe configuration: protocol, transport, flags, vendor/product strings, and LUN policy.

## Dependencies and Integration Points

It depends on the macro-table pattern used by `usual-tables.c` and the Datafab subdriver. It integrates with usb-storage quirk flags and SCSI LUN scanning decisions.

## Risks and Edge Cases

The first row covers a narrow bcd range while many later rows cover all revisions. That split must reflect real firmware behavior. Wrong `US_FL_SINGLE_LUN` use could hide media slots or cause invalid LUN probing on fragile readers.

## Test Signals

Validate ID-table generation, probe routing to the Datafab transport, LUN behavior on single- and multi-slot readers, and media read/write across represented product IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_datafab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_devs.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_devs.h

## Purpose

`unusual_devs.h` is the main usb-storage unusual-device database. It maps hundreds of vendor/product/revision ranges to protocol overrides, transport overrides, initializer functions, and `US_FL_*` quirk flags, then appends generic `USUAL_DEV()` class matches for standard mass-storage subclasses and transports.

## Important APIs, Types, and Functions

The file is pure macro data and requires `UNUSUAL_DEV`, `COMPLIANT_DEV`, and `USUAL_DEV` to be defined by the includer. It contains roughly 340 device/class entries. Important fields are VID, PID, bcdDevice min/max, short vendor/product names, protocol (`USB_SC_*`), transport (`USB_PR_*`), initializer such as `usb_stor_euscsi_init` or `sierra_ms_init`, and flags such as `US_FL_IGNORE_RESIDUE`, `US_FL_FIX_CAPACITY`, `US_FL_FIX_INQUIRY`, `US_FL_SINGLE_LUN`, `US_FL_IGNORE_UAS`, `US_FL_BROKEN_FUA`, `US_FL_NO_REPORT_OPCODES`, and `US_FL_ALWAYS_SYNC`.

## Control Flow

`usb.c` expands this file into `us_unusual_dev_list[]`, which is parallel to `usb_storage_usb_ids[]` from `usual-tables.c`. `storage_probe()` uses the matched USB ID index to locate the matching unusual metadata, then `get_device_info()`, `get_transport()`, and `get_protocol()` configure `struct us_data`. Initializers run in `usb_stor_acquire_resources()` before the control thread starts. `usual-tables.c` also expands the file into the public USB device ID table used for module matching.

## State and Persistence Behavior

The file has no runtime storage of its own, but it determines per-device in-memory flags and function pointers. Those flags affect SCSI scanning, inquiry data, cache/FUA behavior, residue interpretation, UAS fallback, capacity handling, and reset behavior. There is no filesystem persistence.

## Dependencies and Integration Points

It depends on usb-storage protocol constants, transport constants, initializer declarations from headers such as `sierra_ms.h` and `option_ms.h`, and quirk flag definitions from `linux/usb_usual.h`. It integrates with both the kernel module alias table and usb-storage's runtime metadata table; line-for-line alignment between those expansions is part of the contract.

## Risks and Edge Cases

This table is high-risk because entries are compatibility policy. Overly broad revision ranges can apply quirks to devices that no longer need them; overly narrow ranges can leave broken firmware on the generic path. Vendor/product strings are reused for fake inquiry data and should stay within legacy size expectations when `US_FL_FIX_INQUIRY` is used. The parallel-table invariant between `usb_storage_usb_ids[]` and `us_unusual_dev_list[]` must be preserved.

## Test Signals

Run compile checks for table expansion, verify module aliases, and regression-test representative devices for each major flag: ignored devices, fixed inquiry, capacity fixes, bad residues, single LUN, SCM multi-target, UAS ignore, broken FUA, sync-cache behavior, and initializer-backed devices. Static checks should confirm each non-NULL initializer is declared and linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_devs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_ene_ub6250.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_ene_ub6250.h

## Purpose

`unusual_ene_ub6250.h` contains the device table entry for ENE UB6250 card-reader hardware that has a specialized driver path and should not be claimed as plain usb-storage.

## Important APIs, Types, and Functions

The file contributes one `UNUSUAL_DEV()` row for VID `0x0cf2`, PID `0x6250`, all revisions, using device-reported subclass/protocol and no initializer or flags.

## Control Flow

`usual-tables.c` includes this file in the ignore list. Probe matching by VID/PID/bcdDevice returns `-ENXIO` from `usb_usual_ignore_device()`, allowing the specialized ENE driver to bind instead.

## State and Persistence Behavior

There is no state. The row only affects match-time binding policy.

## Dependencies and Integration Points

It depends on the `UNUSUAL_DEV` macro contract and the specialized ENE UB6250 driver existing elsewhere in the storage tree. It integrates with libusual's generic-driver ignore list.

## Risks and Edge Cases

The all-revision range assumes every UB6250 revision needs the specialized path. If future firmware becomes standards-compliant, this row may unnecessarily prevent generic binding.

## Test Signals

Compile the ignore table, attach UB6250 hardware, and confirm the generic usb-storage driver declines it while the ENE driver handles media enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_ene_ub6250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_freecom.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_freecom.h

## Purpose

`unusual_freecom.h` maps the Freecom USB-ATAPI bridge to its specialized Freecom transport.

## Important APIs, Types, and Functions

The file contains one `UNUSUAL_DEV()` row for VID `0x07ab`, PID `0xfc01`, all revisions. It selects `USB_SC_QIC`, `USB_PR_FREECOM`, and `init_freecom`.

## Control Flow

The row is expanded into ignore or specialized subdriver tables. When matched by the Freecom subdriver, probe uses the QIC subclass, Freecom transport, and initializer before SCSI scanning.

## State and Persistence Behavior

The header has no state. It controls transport selection and initializer invocation at probe time.

## Dependencies and Integration Points

It depends on `init_freecom`, Freecom transport support, and the `UNUSUAL_DEV` macro. It integrates with usb-storage's subdriver split and SCSI command routing for the device.

## Risks and Edge Cases

An all-revision range may capture devices that do not need the Freecom path. The initializer and transport must match the protocol override or commands may be padded/transferred incorrectly.

## Test Signals

Build Freecom support, verify USB ID matching, attach the bridge, and test media inquiry, read/write, reset, and disconnect through the specialized transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_freecom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_isd200.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_isd200.h

## Purpose

`unusual_isd200.h` lists ISD200-based USB-to-ATA bridges that require the ISD200 initialization/protocol path.

## Important APIs, Types, and Functions

The file contributes six `UNUSUAL_DEV()` entries for Sony, In-System/ISD, and related bridges. Rows select `USB_SC_ISD200`, `USB_PR_BULK`, `isd200_Initialization`, and usually no extra flags.

## Control Flow

Macro expansion routes matching devices away from generic usb-storage and into the ISD200 subdriver. The initializer runs before the usb-storage control thread starts, allowing ATA bridge setup before SCSI scanning.

## State and Persistence Behavior

No state is stored in the header. The rows influence in-memory protocol and initializer fields in `struct us_data`; bridge state is programmed by the initializer.

## Dependencies and Integration Points

It depends on ISD200 subclass support and `isd200_Initialization`. It integrates with the usb-storage unusual-device infrastructure, USB ID matching, and SCSI scan setup.

## Risks and Edge Cases

All listed rows use a narrow bcd range (`0x0100` to `0x0110`). Devices outside that range may not bind to the specialized path even if they need it. Conversely, broadening the range without hardware evidence could affect unrelated bridge firmware.

## Test Signals

Compile with ISD200 enabled, attach represented bridges, verify initializer execution, check ATA identify/translation behavior, and exercise reset plus media read/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_isd200.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_jumpshot.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_jumpshot.h

## Purpose

`unusual_jumpshot.h` contains the Lexar JumpShot table entry for the `USB_PR_JUMPSHOT` transport.

## Important APIs, Types, and Functions

The single `UNUSUAL_DEV()` row matches VID `0x05dc`, PID `0x0001`, revisions `0x0000` to `0x0001`, selects `USB_SC_SCSI`, `USB_PR_JUMPSHOT`, no initializer, and `US_FL_NEED_OVERRIDE`.

## Control Flow

The entry is expanded into the usual ignore/specialized-driver tables. `US_FL_NEED_OVERRIDE` suppresses the usb-storage notice that a subclass/protocol override might be unnecessary, indicating this override is intentional.

## State and Persistence Behavior

The header has no state. It sets probe-time matching and flags only.

## Dependencies and Integration Points

It depends on the JumpShot transport implementation and the unusual-device macro contract. It integrates with usb-storage quirk logging through `US_FL_NEED_OVERRIDE`.

## Risks and Edge Cases

The revision range is tight; unlisted firmware may miss the JumpShot path. Removing `US_FL_NEED_OVERRIDE` would not change runtime behavior but would create misleading maintenance warnings.

## Test Signals

Build JumpShot support, verify the device is ignored by generic usb-storage, confirm the JumpShot transport binds, and test card detection and block I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_jumpshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_karma.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_karma.h

## Purpose

`unusual_karma.h` routes the Rio Karma music player/storage device to its specialized transport and initializer.

## Important APIs, Types, and Functions

The file contains one `UNUSUAL_DEV()` row matching VID `0x045a`, PID `0x5210`, revision `0x0101`, with `USB_SC_SCSI`, `USB_PR_KARMA`, and `rio_karma_init`.

## Control Flow

Macro expansion places the row in usb-storage match/ignore tables. Matching devices use the Karma transport and run `rio_karma_init()` before command processing.

## State and Persistence Behavior

No state is stored in this header. The initializer and transport may alter device state; this row only selects them.

## Dependencies and Integration Points

It depends on `rio_karma_init` and `USB_PR_KARMA` support. It integrates with the standard unusual-device table pattern and the SCSI scan path after specialized initialization.

## Risks and Edge Cases

The exact revision range limits compatibility to known firmware. The row assumes the Karma protocol remains necessary for the matched device and should not be replaced by generic BOT.

## Test Signals

Compile Karma transport support, attach a matching device, verify initializer execution, and test mount/read/write/reset behavior through the specialized path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_karma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_onetouch.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_onetouch.h

## Purpose

`unusual_onetouch.h` lists Maxtor OneTouch devices that need an input-button side-channel initializer in addition to normal storage behavior.

## Important APIs, Types, and Functions

The file contains two `UNUSUAL_DEV()` rows for Maxtor OneTouch product IDs `0x7000` and `0x7010`. They keep device-reported subclass/protocol, use `onetouch_connect_input` as the initializer, and set no extra flags.

## Control Flow

When expanded into the usb-storage metadata table, a matching storage device receives `onetouch_connect_input` as its `initFunction`. `usb_stor_acquire_resources()` invokes that function before starting the control thread, allowing the side-button input device to be registered while storage continues through the normal protocol.

## State and Persistence Behavior

The header stores no state. The initializer may allocate input-device state and attach cleanup through `struct us_data` extra fields; storage media state is unaffected by this table alone.

## Dependencies and Integration Points

It depends on the OneTouch initializer symbol, usb-storage's initializer hook, and the unusual-device macro contract. It integrates with both USB storage and Linux input subsystems through the initializer.

## Risks and Edge Cases

Because the rows use all revisions, any product-ID reuse could register an inappropriate input device. If the initializer fails, usb-storage probe can fail before normal SCSI scanning depending on the initializer return.

## Test Signals

Attach both product IDs, verify the storage device scans normally, confirm the OneTouch input device is registered, test button events, and validate cleanup on disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_onetouch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_realtek.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_realtek.h

## Purpose

`unusual_realtek.h` lists Realtek card-reader devices that use the Realtek-specific initialization path.

## Important APIs, Types, and Functions

The file contributes six `UNUSUAL_DEV()` rows for VID `0x0bda` products `0x0138`, `0x0153`, `0x0158`, `0x0159`, `0x0177`, and `0x0184`. Rows use device-reported subclass/protocol and call `init_realtek_cr`.

## Control Flow

Macro expansion lets the generic ignore table decline these devices or lets the Realtek subdriver claim them. For matching devices, `init_realtek_cr` runs before command processing to set up reader-specific behavior.

## State and Persistence Behavior

The header stores no state. Runtime state is created by the Realtek initializer and associated subdriver cleanup.

## Dependencies and Integration Points

It depends on `init_realtek_cr`, Realtek card-reader support, and macro-table inclusion by `usual-tables.c` or the subdriver. It integrates with usb-storage probe and SCSI media scanning.

## Risks and Edge Cases

All entries cover all firmware revisions. This is convenient for reused Realtek reader IDs but may be too broad if a future revision becomes generic-compatible. Missing a new product ID would leave it on the generic path without Realtek setup.

## Test Signals

Compile Realtek reader support, verify ID-table expansion, attach each supported product family, test media insertion/removal, suspend/resume, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_realtek.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_sddr09.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_sddr09.h

## Purpose

`unusual_sddr09.h` describes SanDisk/ImageMate SDDR09 and related readers that need the EUSB SDDR09 or DPCM USB protocol paths.

## Important APIs, Types, and Functions

The file contains six `UNUSUAL_DEV()` rows. Some entries select `USB_PR_EUSB_SDDR09` with `usb_stor_sddr09_init`; others select `USB_PR_DPCM_USB` with either no initializer or `usb_stor_sddr09_dpcm_init`. Rows use `USB_SC_SCSI` and no extra flags.

## Control Flow

The rows are expanded into ignore or specialized subdriver tables. Matching hardware is routed to the SDDR09/DPCM transport and optional initializer before SCSI scanning.

## State and Persistence Behavior

There is no state in the header. Probe-time metadata selects protocol and initializer; runtime state belongs to the SDDR09 transport implementation.

## Dependencies and Integration Points

It depends on SDDR09 and DPCM protocol constants plus `usb_stor_sddr09_init` and `usb_stor_sddr09_dpcm_init`. It integrates with usb-storage's protocol handler selection and specialized media-reader transports.

## Risks and Edge Cases

The table mixes exact and broad revision ranges. Incorrect revision coverage can either miss special handling or force it on unrelated firmware. DPCM devices interact with autosense policy in `transport.c`, so protocol selection must be correct.

## Test Signals

Build SDDR09 support, attach represented readers, verify initializer selection by product/revision, test card enumeration and I/O, and exercise reset/error paths for DPCM and EUSB variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_sddr09.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_sddr55.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_sddr55.h

## Purpose

`unusual_sddr55.h` lists SDDR55-style readers that require the `USB_PR_SDDR55` transport.

## Important APIs, Types, and Functions

The file contributes four `UNUSUAL_DEV()` rows for SanDisk and related product IDs. They select `USB_SC_SCSI`, `USB_PR_SDDR55`, no initializer, and usually no extra flags.

## Control Flow

Macro expansion routes matching readers to the SDDR55 subdriver and prevents generic usb-storage from claiming them through the ignore table.

## State and Persistence Behavior

No state is stored. The table controls matching and transport choice; runtime media state belongs to the reader driver.

## Dependencies and Integration Points

It depends on `USB_PR_SDDR55` support and the usual macro inclusion mechanism. It integrates with usb-storage/libusual matching and SCSI block-device enumeration.

## Risks and Edge Cases

The rows are product/revision-specific. Firmware outside those ranges may be mishandled. Since no initializer is supplied, all special behavior must be in the selected transport.

## Test Signals

Compile SDDR55 support, verify the table expansion, attach matching readers, and test card detection, reads/writes, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_sddr55.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_uas.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_uas.h

## Purpose

`unusual_uas.h` is the UAS-specific quirk table. It lists USB storage devices that advertise UAS but need flags such as disabling UAS, limiting command size, avoiding ATA pass-through, disabling FUA, suppressing REPORT OPCODES/LUNS, or forcing sync-cache behavior.

## Important APIs, Types, and Functions

The file contains 23 `UNUSUAL_DEV()` rows and intentionally requires the includer to define `UNUSUAL_DEV`. Rows mostly use `USB_SC_DEVICE` and `USB_PR_DEVICE` because they augment matching devices rather than selecting a nonstandard usb-storage transport. Important flags include `US_FL_IGNORE_UAS`, `US_FL_NO_REPORT_OPCODES`, `US_FL_NO_SAME`, `US_FL_NO_REPORT_LUNS`, `US_FL_NO_ATA_1X`, `US_FL_IGNORE_RESIDUE`, `US_FL_BROKEN_FUA`, and `US_FL_ALWAYS_SYNC`.

## Control Flow

`uas.c` expands the file into `uas_usb_ids[]`, before the generic mass-storage UAS/BOT interface matches. During probe, `uas_use_uas_driver()` starts with `id->driver_info`, applies dynamic heuristics and user quirks, and may reject UAS if `US_FL_IGNORE_UAS` is set. If UAS binds, `uas_sdev_configure()` translates flags into SCSI device behavior such as queue limits, broken FUA, no report opcodes, no write same, capacity heuristics, and cache page handling.

## State and Persistence Behavior

The file stores no state. It determines per-device quirk flags copied into `struct uas_dev_info`. Those flags persist only for the device lifetime and affect SCSI queue/device configuration.

## Dependencies and Integration Points

It depends on UAS driver ID-table expansion, usb-storage quirk definitions, and shared detection in `uas-detect.h`. It integrates with both bind selection and SCSI device configuration.

## Risks and Edge Cases

UAS quirk policy is especially sensitive because devices often advertise UAS despite broken firmware. A missing `US_FL_IGNORE_UAS` can expose data-corrupting command sequencing; an unnecessary one reduces performance by forcing BOT. Flags that suppress REPORT OPCODES, FUA, SAME, or ATA pass-through can hide features but improve compatibility.

## Test Signals

Validate each listed device or bridge family for binding/fallback, command queueing, large transfer limits, FUA/write-cache behavior, REPORT LUNS/OPCODES handling, ATA passthrough, and BOT fallback when `US_FL_IGNORE_UAS` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_uas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_usbat.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_usbat.h

## Purpose

`unusual_usbat.h` lists USBAT bridge devices that need the `USB_PR_USBAT` transport and either CD or flash initialization.

## Important APIs, Types, and Functions

The file has four `UNUSUAL_DEV()` rows. HP CD devices use `USB_SC_8070`, `USB_PR_USBAT`, and `init_usbat_cd`; SCM/SanDisk flash devices use `USB_SC_SCSI`, `USB_PR_USBAT`, `init_usbat_flash`, and `US_FL_SINGLE_LUN`.

## Control Flow

Macro expansion routes matching bridges to the USBAT subdriver. The selected initializer runs before the control thread starts, and `US_FL_SINGLE_LUN` constrains flash readers to LUN 0 where needed.

## State and Persistence Behavior

No state is kept in the header. Runtime bridge/media state is owned by the USBAT initializer and transport.

## Dependencies and Integration Points

It depends on `init_usbat_cd`, `init_usbat_flash`, and USBAT protocol support. It integrates with usb-storage probe, specialized transport selection, and SCSI LUN scanning policy.

## Risks and Edge Cases

The CD rows are exact revision `0x0001`; flash rows are narrow for SanDisk and broad for SCM. Incorrect ranges can select the wrong initializer type, which is more serious here because CD and flash setup differ.

## Test Signals

Build USBAT support, attach represented CD and flash bridges, confirm initializer selection, test media access, LUN behavior, reset, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_usbat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/usb.c

## Purpose

`usb.c` is the main driver body for classic USB Mass Storage. It owns module parameters, device matching metadata, probe/unbind, SCSI host allocation, the per-device command thread, delayed scanning, suspend/resume/reset hooks, quirk parsing, and integration with UAS fallback.

## Important APIs, Types, and Functions

Module parameters are `delay_use` and `quirks`. Probe helpers include `usb_stor_probe1()`, `usb_stor_probe2()`, `storage_probe()`, `associate_dev()`, `get_device_info()`, `get_transport()`, `get_protocol()`, `get_pipes()`, and `usb_stor_acquire_resources()`. Runtime functions include `usb_stor_control_thread()`, `usb_stor_scan_dwork()`, `fill_inquiry_response()`, `usb_stor_adjust_quirks()`, `usb_stor_disconnect()`, `quiesce_and_remove_host()`, `release_everything()`, and PM/reset hooks `usb_stor_suspend()`, `usb_stor_resume()`, `usb_stor_reset_resume()`, `usb_stor_pre_reset()`, and `usb_stor_post_reset()`.

## Control Flow

`storage_probe()` first lets UAS claim viable devices and lets specialized subdrivers claim devices from the usual ignore table. It then maps the matched USB ID to the parallel unusual-device metadata table, calls `usb_stor_probe1()` to allocate and initialize `struct us_data`, and calls `usb_stor_probe2()` to validate transport/protocol, find endpoints, acquire URB/control-thread resources, add the SCSI host, and schedule delayed scanning after `delay_use`.

The control thread sleeps on `cmnd_ready`, takes `dev_mutex`, validates target/LUN/data direction, fakes INQUIRY for `US_FL_FIX_INQUIRY`, otherwise calls the selected protocol handler, then releases locks and completes the SCSI command. Scanning optionally sends GetMaxLUN for BOT, raises host max_lun for large LUN counts, calls `scsi_scan_host()`, and balances runtime PM. Disconnect cancels scanning, removes the SCSI host, sets disconnect flags, wakes reset waits, stops the control thread, calls subdriver destructors, frees DMA buffers/URB/control request, and drops the SCSI host reference.

## State and Persistence Behavior

Long-lived state is per-device `struct us_data`: USB pointers, unusual metadata, quirk flags, dynamic flags, endpoint pipes, transport/protocol function pointers, SCSI command pointer, control thread, coherent I/O buffer, control request, current URB/SG request, completions, delayed scan work, subdriver private data, and last-sector hack counters. `delay_use` and `quirks` are module parameters exposed through sysfs. There is no file persistence, but probe changes USB interface state, runtime PM references, SCSI hosts, and block devices.

## Dependencies and Integration Points

The file depends on USB core, SCSI midlayer, workqueues, kthreads, runtime PM, unusual device tables, transport/protocol/scsiglue helpers, optional UAS detection, and subdriver initializer headers. It exports common probe/disconnect/PM helpers for usb-storage subdrivers.

## Risks and Edge Cases

The `usb_storage_usb_ids[]` and `us_unusual_dev_list[]` arrays must remain line-for-line aligned. `quirks=` parsing can override important flags and ignore unrecognized characters silently. The control thread uses a single outstanding `us->srb`, guarded by host lock and `dev_mutex`; abort and reset paths rely on dynamic flags being cleared in the right order. Highmem hosts without DMA/local-memory support are rejected because the driver does not bounce or kmap buffers. Delayed scan cancellation must balance autopm references.

## Test Signals

Test normal BOT devices, UAS-capable fallback, ignored specialized devices, dynamic IDs, quirk parameter parsing, fixed inquiry, invalid target/LUN rejection, delayed scan and scan cancellation, GetMaxLUN behavior, suspend/resume/reset hooks, disconnect during scan and active I/O, highmem/non-DMA host rejection, and subdriver initializer/destructor lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/usb.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/usb.h

## Purpose

`usb.h` is the central header for the classic usb-storage core. It defines the unusual-device metadata shape, dynamic state flags, `struct us_data`, common callback typedefs, host conversion helpers, exported probe/PM/disconnect APIs, and the module registration macro used by storage subdrivers.

## Important APIs, Types, and Functions

`struct us_unusual_dev` stores short inquiry names, protocol override, transport override, and initializer callback. `struct us_data` holds all per-device runtime state: USB device/interface, quirk flags, dynamic flags, pipes, protocol/transport names and function pointers, current SCSI command, tag, coherent I/O buffer, current URB/SG request, control thread, completions, waitqueue, delayed scan work, subdriver private data/destructor, PM hook, and capacity-hack counters. Typedefs include `trans_cmnd`, `trans_reset`, `proto_cmnd`, `extra_data_destructor`, and `pm_hook`.

## Control Flow

The header has no executable flow, but its definitions drive the driver lifecycle. Probe allocates `struct us_data` as SCSI host private data, transport/protocol setup fills function pointers, the command thread consumes `us->srb`, transfer code uses `current_urb` and `current_sg`, and disconnect/PM/reset paths use the exported functions. `module_usb_stor_driver()` wraps module init/exit by initializing a SCSI host template and registering/deregistering a USB driver.

## State and Persistence Behavior

All state defined here is in memory and scoped to a USB storage device or module. Dynamic flags record URB active, SG active, aborting, disconnecting, resetting, timed out, scan pending, redo READ(10), and prior READ(10) success. There is no filesystem persistence.

## Dependencies and Integration Points

It depends on Linux USB, usb usual quirks, block layer, completions, mutexes, workqueues, and SCSI host APIs. It is included by the core, transports, protocol handlers, and subdrivers and is the main ABI inside the usb-storage subsystem.

## Risks and Edge Cases

`struct us_data` is shared by many asynchronous paths, so lock/flag contracts documented in C files must be respected by any new subdriver. The small coherent `US_IOBUF_SIZE` is sized for known control/BOT/Freecom needs; new protocols must not overrun it. `scsi_lock` and `scsi_unlock` macros directly use host spinlocks and should not be mixed casually with sleeping operations.

## Test Signals

Compile all usb-storage subdrivers, verify host/private-data conversion, exercise module registration, and use lockdep/runtime tests around abort, reset, scan, PM, and subdriver init/destructor paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/usual-tables.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/usual-tables.c

## Purpose

`usual-tables.c` builds the USB device ID tables for classic usb-storage and libusual. It expands the main unusual-device table into `usb_storage_usb_ids[]` for driver matching and expands specialized subdriver tables into an ignore list used by generic usb-storage.

## Important APIs, Types, and Functions

`usb_storage_usb_ids[]` is generated by defining `UNUSUAL_DEV`, `COMPLIANT_DEV`, and `USUAL_DEV` macros and including `unusual_devs.h`. `ignore_ids[]` is generated from specialized tables such as `unusual_alauda.h`, `unusual_datafab.h`, `unusual_realtek.h`, and others. `usb_usual_ignore_device()` compares the current device VID/PID/bcdDevice against `ignore_ids[]` and returns `-ENXIO` on a match.

## Control Flow

At module load, the generated USB ID table provides modalias matching. During `storage_probe()`, `usb_usual_ignore_device()` runs before generic probe setup; if a device is listed in a specialized table, generic usb-storage declines it so the relevant subdriver can bind.

## State and Persistence Behavior

The file defines static const tables only. Runtime state is limited to stack variables in `usb_usual_ignore_device()`. There is no persistence.

## Dependencies and Integration Points

It depends on USB core ID macros, `linux/usb_usual.h` quirk flags, and all included unusual table headers. It integrates with module device-table generation, the generic usb-storage probe path, and specialized subdriver ownership.

## Risks and Edge Cases

The macro expansion must stay aligned with `usb.c`'s parallel `us_unusual_dev_list[]` construction. The ignore table uses only VID/PID/bcd ranges; interface-level differences are not considered. Missing a specialized-device row can let generic usb-storage bind first, while an overly broad ignore row can prevent usable generic storage.

## Test Signals

Build and inspect USB modalias output, verify generic and specialized devices bind to the intended driver, test `usb_usual_ignore_device()` for boundary bcd values, and ensure all included tables compile under the simplified ignore-entry macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/usual-tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/Kconfig

## Purpose

`drivers/usb/typec/Kconfig` defines the top-level USB Type-C configuration menu and the selectable Type-C port-controller drivers in this tree. It gates Type-C core compilation and sources submenus for TCPM, UCSI, TI PD controllers, muxes, and alternate modes.

## Important APIs, Types, and Functions

The main symbol is `TYPEC`, a tristate menuconfig for USB Type-C support. Driver symbols include `TYPEC_ANX7411`, `TYPEC_RT1719`, `TYPEC_HD3SS3220`, `TYPEC_STUSB160X`, and `TYPEC_WUSB3801`. Dependencies include `I2C`, `USB_ROLE_SWITCH`, `POWER_SUPPLY`, and `REGMAP_I2C` selections for relevant drivers.

## Control Flow

Kconfig evaluation exposes the Type-C menu. If `TYPEC` is disabled, the nested sources are skipped. If enabled, the build system can select core Type-C class support, controller drivers, mux support, and alternate-mode drivers. The help text documents OS-managed versus firmware-managed Type-C/PD state machines.

## State and Persistence Behavior

This file has no runtime state. Configuration selections persist in the kernel `.config` and determine which objects are built in or as modules.

## Dependencies and Integration Points

It integrates with `drivers/usb/typec/Makefile`, nested `tcpm`, `ucsi`, `tipd`, `mux`, and `altmodes` Kconfig files, and subsystem dependencies such as I2C, power-supply, and role-switch frameworks.

## Risks and Edge Cases

Incorrect dependencies can expose drivers that cannot link or hide drivers on valid systems. The `USB_ROLE_SWITCH || !USB_ROLE_SWITCH` pattern allows optional role-switch integration and must match driver code. Help text must not imply that all Type-C systems require OS policy drivers.

## Test Signals

Run Kconfig coverage for built-in, module, and disabled Type-C configurations; check randconfig/allmodconfig builds; and verify selected symbols produce expected object lists in the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/Makefile

## Purpose

`drivers/usb/typec/Makefile` maps Type-C Kconfig symbols to the core Type-C objects, controller-driver objects, and child directories.

## Important APIs, Types, and Functions

`obj-$(CONFIG_TYPEC)` builds `typec.o`, `altmodes/`, and `mux/`. The `typec-y` composite includes `class.o`, `mux.o`, `bus.o`, `pd.o`, `retimer.o`, and `mode_selection.o`, with `port-mapper.o` added for ACPI. Controller objects include `anx7411.o`, `hd3ss3220.o`, `stusb160x.o`, `rt1719.o`, and `wusb3801.o`; subdirectories include `tcpm/`, `ucsi/`, and `tipd/`.

## Control Flow

Kbuild evaluates each `obj-$()` expression from `.config`. Enabling `TYPEC` builds the core and descends into mux and altmode directories. Enabling controller-specific symbols adds the corresponding module or built-in object.

## State and Persistence Behavior

There is no runtime state. Build selections persist through `.config` and the generated build graph.

## Dependencies and Integration Points

The file integrates with Type-C Kconfig symbols, Kbuild composite-object rules, and child Makefiles under Type-C subdirectories. It must stay synchronized with source file names and driver symbols.

## Risks and Edge Cases

Missing an object here makes a visible Kconfig option build nothing; stale object names break builds. Directory descent under `CONFIG_TYPEC` means alternate-mode and mux builds depend on the core symbol being enabled.

## Test Signals

Run `make olddefconfig`, `allmodconfig`, and representative module/built-in combinations to ensure every selected Type-C symbol produces a valid object or directory traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/Kconfig

## Purpose

`drivers/usb/typec/altmodes/Kconfig` defines the selectable USB Type-C alternate-mode drivers for DisplayPort, NVIDIA VirtualLink, and Thunderbolt 3.

## Important APIs, Types, and Functions

Symbols are `TYPEC_DP_ALTMODE`, `TYPEC_NVIDIA_ALTMODE`, and `TYPEC_TBT_ALTMODE`. DisplayPort depends on `DRM`; NVIDIA depends on `TYPEC_DP_ALTMODE`; Thunderbolt has no explicit dependency beyond being in the Type-C alternate-mode menu.

## Control Flow

When sourced from the parent Type-C Kconfig, this file presents a submenu. Selecting a symbol enables the matching object in `altmodes/Makefile`. NVIDIA's dependency forces reuse of the DisplayPort altmode implementation exported by `displayport.c`.

## State and Persistence Behavior

No runtime state is stored here. Choices persist in `.config` and determine module availability.

## Dependencies and Integration Points

It integrates with the Type-C bus, DisplayPort DRM hotplug support, the NVIDIA wrapper driver, Thunderbolt altmode support, and the altmodes Makefile.

## Risks and Edge Cases

Dependency drift is the main risk. If DisplayPort starts depending on additional connector or firmware-node APIs, Kconfig must express them. NVIDIA support must remain tied to DisplayPort because its implementation delegates to `dp_altmode_probe()` and `dp_altmode_remove()`.

## Test Signals

Kconfig and build tests should cover each symbol disabled, built-in, and modular, with special attention to NVIDIA without DisplayPort being impossible and DisplayPort requiring DRM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/Makefile

## Purpose

`drivers/usb/typec/altmodes/Makefile` maps alternate-mode Kconfig symbols to the DisplayPort, NVIDIA, and Thunderbolt driver objects.

## Important APIs, Types, and Functions

`CONFIG_TYPEC_DP_ALTMODE` builds `typec_displayport.o` from `displayport.o`; `CONFIG_TYPEC_NVIDIA_ALTMODE` builds `typec_nvidia.o` from `nvidia.o`; `CONFIG_TYPEC_TBT_ALTMODE` builds `typec_thunderbolt.o` from `thunderbolt.o`.

## Control Flow

Kbuild evaluates `obj-$()` expressions and composite object definitions. Selected drivers are built as modules or built-ins according to their tristate values.

## State and Persistence Behavior

There is no runtime state. The file controls build artifacts only.

## Dependencies and Integration Points

It must match `altmodes/Kconfig` symbols and the module driver names registered in the corresponding C files. NVIDIA relies on the DisplayPort object exporting probe/remove helpers when built together according to Kconfig dependency rules.

## Risks and Edge Cases

Stale composite names break module naming or linking. If a driver gains multiple source files, this Makefile must add them to the right composite object rather than as separate modules.

## Test Signals

Run allmodconfig and per-symbol builds to verify `typec_displayport`, `typec_nvidia`, and `typec_thunderbolt` objects link with expected module names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/displayport.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/displayport.c

## Purpose

`displayport.c` implements the USB Type-C DisplayPort Alternate Mode driver. It negotiates DP mode entry, status update, cable plug configuration, pin assignment, HPD/IRQ_HPD reporting, sysfs controls, DRM out-of-band hotplug notification, and optional active-cable SOP' handling.

## Important APIs, Types, and Functions

`struct dp_altmode` stores port/partner/cable data, current and cable-prime DP status/configuration VDOs, state machine state, HPD flags/counters, mutex/work item, typec altmode pointers, connector fwnode, and optional SOP' plug. Core functions include `dp_altmode_configure()`, `dp_altmode_status_update()`, `dp_altmode_configure_vdm()`, `dp_altmode_configure_vdm_cable()`, `dp_altmode_work()`, `dp_altmode_attention()`, `dp_altmode_vdm()`, `dp_cable_altmode_vdm()`, `dp_altmode_activate()`, `dp_altmode_probe()`, and `dp_altmode_remove()`. Sysfs attributes are `displayport/configuration`, `pin_assignment`, `hpd`, and `irq_hpd`.

## Control Flow

Probe requires the local Type-C data role to be host/DFP_U and verifies compatible pin assignments between port and partner. It gets an optional SOP' plug, installs Type-C altmode/cable ops, resolves the connector firmware node, and auto-enters either SOP' then SOP or SOP directly when mode selection is automatic. The work item serializes entry, status update, configure, and exit states.

VDM ACKs advance the state machine: ENTER_MODE triggers status update, STATUS_UPDATE records the partner status and may choose a configuration, CONFIGURE notifies that configuration is active, and EXIT_MODE clears active state and HPD. ATTENTION updates status and can schedule configure/exit work. Configuration selection intersects port, partner, and cable signaling/pin capabilities, honors multi-function preference, defaults to pin C when available for DP-only assignments, and sends the connector to safe mode before reconfiguring. Sysfs stores allow userspace to request source/sink/USB mode or a specific pin assignment when supported.

## State and Persistence Behavior

State is in-memory per altmode: DP status VDOs, configuration VDOs, state enum, HPD state, pending HPD/IRQ flags, IRQ counter, plug reference, and connector fwnode reference. The driver emits Type-C modal-state notifications, sysfs notifications, and DRM hotplug events; it does not persist settings to disk or firmware.

## Dependencies and Integration Points

The driver depends on Type-C altmode bus APIs, USB PD VDO helpers, DisplayPort altmode definitions, DRM connector hotplug notification, firmware-node properties, mutexes, and workqueues. It exports `dp_altmode_probe()` and `dp_altmode_remove()` for the NVIDIA VirtualLink wrapper.

## Risks and Edge Cases

The state machine returns `-EBUSY` while another VDM transaction is active, so callers must retry rather than overlap operations. Cable SOP' support can be dropped on entry/configuration failure, then the driver retries without the plug. HPD can arrive before configuration and is deferred until configuration completes. Pin assignment logic depends on correctly intersecting DFP/UFP and active-cable capabilities; a bad choice can break display connectivity or USB lane sharing. The sysfs `pin_assignment_store()` has a TODO for manual SOP' cable configure.

## Test Signals

Test automatic and manual mode selection, SOP' active cable entry/configuration failure fallback, source and sink configurations, multi-function preference, all supported pin assignments, status update NAK leading to exit, configure NAK fallback, ATTENTION during non-idle state, HPD and IRQ_HPD sysfs notifications, DRM hotplug fwnode resolution, sysfs invalid values, and remove cleanup/disconnect notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/displayport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/displayport.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/displayport.h

## Purpose

`displayport.h` exposes the DisplayPort altmode probe/remove helpers to wrapper drivers such as NVIDIA VirtualLink while providing no-op stubs when DisplayPort altmode support is disabled.

## Important APIs, Types, and Functions

When `CONFIG_TYPEC_DP_ALTMODE` is enabled, it declares `int dp_altmode_probe(struct typec_altmode *alt)` and `void dp_altmode_remove(struct typec_altmode *alt)`. Otherwise it defines inline stubs returning `-ENOTSUPP` and doing nothing.

## Control Flow

There is no independent control flow. `nvidia.c` includes this header and delegates matching VirtualLink altmodes to these helpers. Compile-time configuration decides whether that delegation reaches the real DisplayPort implementation.

## State and Persistence Behavior

The header stores no state. Real state is owned by `displayport.c` when enabled.

## Dependencies and Integration Points

It depends on Type-C altmode declarations being visible to callers and on `CONFIG_TYPEC_DP_ALTMODE`. It integrates the NVIDIA altmode module with the DisplayPort implementation without duplicating code.

## Risks and Edge Cases

The non-static stub definitions in a header are acceptable only because Kconfig prevents consumers that need the real implementation from building without it in normal configurations. Signature drift between header and implementation would break NVIDIA delegation.

## Test Signals

Build NVIDIA altmode with DisplayPort enabled, verify successful linking to exported helpers, and build configurations where DisplayPort is disabled to confirm stubs compile for any guarded users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/displayport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/nvidia.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/nvidia.c

## Purpose

`nvidia.c` implements the NVIDIA USB Type-C Alternate Mode wrapper for VirtualLink devices. It binds NVIDIA's SVID and delegates behavior to the DisplayPort altmode implementation.

## Important APIs, Types, and Functions

`nvidia_altmode_probe()` checks `alt->svid` for `USB_TYPEC_NVIDIA_VLINK_SID` and calls `dp_altmode_probe()`. `nvidia_altmode_remove()` calls `dp_altmode_remove()` for the same SVID. The file defines a Type-C ID table and registers `typec_nvidia` through `module_typec_altmode_driver()`.

## Control Flow

When the Type-C altmode bus discovers the NVIDIA SVID, probe delegates to DisplayPort because VirtualLink carries DisplayPort semantics. Remove delegates cleanup to the same DisplayPort helper. Unsupported SVIDs return `-ENOTSUPP`, though the ID table should only match the NVIDIA SVID.

## State and Persistence Behavior

This wrapper stores no private state. Any runtime state is the `struct dp_altmode` allocated by `displayport.c` and attached to the altmode device. There is no persistence.

## Dependencies and Integration Points

It depends on `TYPEC_NVIDIA_ALTMODE`, `TYPEC_DP_ALTMODE`, Type-C altmode APIs, NVIDIA VirtualLink SVID constants, and `displayport.h`. It integrates VirtualLink devices with the DisplayPort driver module.

## Risks and Edge Cases

The wrapper assumes VirtualLink can be treated exactly as DisplayPort altmode by the shared implementation. If NVIDIA-specific VDM behavior diverges, this delegation would be insufficient. Kconfig dependency on DisplayPort is required for linking and behavior.

## Test Signals

Build `typec_nvidia`, verify the module ID table matches `USB_TYPEC_NVIDIA_VLINK_SID`, attach or emulate a VirtualLink altmode, and confirm DisplayPort negotiation, sysfs attributes, HPD, and cleanup function through the delegated path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/nvidia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/thunderbolt.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/thunderbolt.c

## Purpose

`thunderbolt.c` implements the USB Type-C Thunderbolt 3 Alternate Mode driver. It handles ordered entry and exit of cable plug altmodes and the port altmode, constructs the Thunderbolt Enter Mode VDO from device/cable capabilities, and notifies the Type-C subsystem when Thunderbolt mode becomes active.

## Important APIs, Types, and Functions

`enum tbt_state` models idle, SOP'/SOP'' enter, port enter, port exit, SOP'' exit, and SOP' exit. `struct tbt_altmode` stores state, cable reference, port altmode, two plug altmode references, computed enter VDO, work item, and mutex. Key functions are `tbt_ready()`, `tbt_enter_mode()`, `tbt_enter_modes_ordered()`, `tbt_altmode_work()`, `tbt_cable_altmode_vdm()`, `tbt_altmode_vdm()`, `tbt_altmode_activate()`, `tbt_altmode_probe()`, and `tbt_altmode_remove()`.

## Control Flow

Probe allocates state, sets ops, describes the altmode as Thunderbolt3, and auto-enters if mode selection is not manual and `tbt_ready()` succeeds. `tbt_ready()` requires an eMarker cable, discovers SOP' and SOP'' plug altmodes when present, installs cable ops, and computes the Enter Mode VDO from port VDO bits, cable speed, active/passive status, rounded/optical/retimer/link-training bits, or passive USB3 fallback.

Activation enters cable altmodes in USB Type-C order: SOP', then SOP'', then the port; exit runs in reverse after the port exits. VDM ACKs from cable plugs and the port advance the state and schedule work. If entering SOP' fails, the driver drops plug references and directly enters the port altmode. A port ENTER_MODE ACK sends `typec_altmode_notify()` with `struct typec_thunderbolt_data` including device mode, enter VDO, and optional cable mode.

## State and Persistence Behavior

State is in-memory per altmode: current state, cable/plug references, computed enter VDO, and work item. Runtime effects are Type-C altmode active/modal notifications and cable/port mode entry/exit commands. There is no persistent storage.

## Dependencies and Integration Points

The driver depends on Type-C altmode and cable APIs, USB PD VDO helpers, Thunderbolt Type-C VDO definitions, mutex/workqueue infrastructure, and the Type-C altmode bus. It registers for `USB_TYPEC_TBT_SID` with module name `typec-thunderbolt`.

## Risks and Edge Cases

Thunderbolt 3 requires an eMarker cable, but the driver accepts systems without visible SOP'/SOP'' plug altmodes and relies on port-level ordering in that case. State transitions reject overlapping VDM handling with `-EBUSY`. Remove releases plug and cable references but does not explicitly cancel the work item, so removal ordering must ensure no scheduled work uses freed devm state. Enter VDO construction depends on correct cable capability VDO parsing.

## Test Signals

Test active and passive cables, missing eMarker rejection, SOP' only, SOP' plus SOP'', no plug altmode fallback, automatic and manual activation, NAKed enter mode, cable entry failure fallback, ordered exit after port exit ACK, Type-C modal notification payload, and disconnect/remove while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/thunderbolt.c -->
