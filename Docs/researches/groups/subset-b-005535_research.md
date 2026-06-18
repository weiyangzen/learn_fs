# subset-b-005535 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/isd200.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/isd200.c

## Purpose

`isd200.c` is the usb-storage subdriver for In-System Design ISD200 USB-to-ATA/ATAPI bridge ASICs. It implements a custom protocol handler that translates selected SCSI block commands into the bridge's ATA Command Block format for ATA disks, while detecting ATAPI devices during initialization and switching them back to the normal transparent SCSI path.

## Important APIs, Types, and Functions

The main runtime state is `struct isd200_info`: cached INQUIRY data, ATA IDENTIFY words, bridge configuration, register scratch buffers, ATA register snapshots, selected device/head value, flags, and a private embedded `scsi_cmnd` used for bridge-internal commands. `union ata_cdb` models the 16-byte ATACB layout. Initialization flows through `isd200_Initialization()`, `isd200_init_info()`, `isd200_read_config()`, `isd200_manual_enum()`, `isd200_try_enum()`, and `isd200_get_inquiry_data()`. Command translation is split between `isd200_ata_command()`, `isd200_scsi_to_ata()`, and `isd200_invoke_transport()`.

## Control Flow

Probe installs `isd200_ata_command` as `us->proto_handler` and then lets the generic usb-storage probe complete. Initialization allocates buffers, reads ISD200 configuration bytes, enumerates master/slave and ATA/ATAPI status via ATACB actions, optionally performs SRST or ATAPI soft reset, and issues ATA IDENTIFY for ATA devices. ATA devices get synthesized SCSI INQUIRY and READ CAPACITY answers; READ_10 and WRITE_10 are translated to PIO READ/WRITE register writes with LBA or CHS addressing. INQUIRY, READ_CAPACITY, some MODE_SENSE, and unsupported commands may be completed locally without touching transport. ATAPI devices are handed off by changing `us->proto_handler` to `usb_stor_transparent_scsi_command` and freeing ISD200 ATA-only state.

## State and Persistence Behavior

All state is per-device volatile kernel state in `us->extra`. The driver caches IDENTIFY data and bridge configuration for future SCSI translation. It can write bridge configuration to select master/slave mode and can issue ATA media lock, unlock, eject, media status, reset, and read/write commands that affect device state or media contents, but it stores nothing persistently in the host filesystem.

## Dependencies and Integration Points

The file depends on usb-storage core objects and helpers (`struct us_data`, `usb_stor_probe1/2`, `usb_stor_Bulk_transport`, `usb_stor_set_xfer_buf`), Linux SCSI command structures, ATA constants from `<linux/ata.h>`/`<linux/hdreg.h>`, and unusual-device tables from `unusual_isd200.h`. It registers a standalone `usb_driver` through `module_usb_stor_driver`.

## Risks and Test Signals

Risk centers on old bridge quirks: timeouts during enumeration, bogus ATA IDENTIFY geometry, 28-bit LBA limits, CHS division by zero, and manual manipulation of an embedded `scsi_cmnd`. `isd200_read_regs()` compares an `ISD200_GOOD` return against `ISD200_TRANSPORT_GOOD`, which are both currently zero but semantically fragile. Tests should cover ATA and ATAPI detection, master/slave selection, malformed IDENTIFY data, media-status commands, reset recovery, READ/WRITE translation in LBA and CHS modes, and autosense generation from ATA error bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/isd200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/jumpshot.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/jumpshot.c

## Purpose

`jumpshot.c` supports Lexar Jumpshot CompactFlash readers. These devices are USB-to-ATA readers that do not expose normal SCSI semantics, so the driver implements a private Control/Bulk transport that synthesizes common SCSI responses and translates block reads/writes to ATA-style bridge commands.

## Important APIs, Types, and Functions

`struct jumpshot_info` stores capacity, sector size, and pending sense data. `jumpshot_transport()` is the exported transport hook installed during probe. Low-level helpers include `jumpshot_bulk_read()`, `jumpshot_bulk_write()`, `jumpshot_get_status()`, `jumpshot_id_device()`, `jumpshot_read_data()`, `jumpshot_write_data()`, and `jumpshot_handle_mode_sense()`.

## Control Flow

Probe sets `us->transport_name`, `us->transport`, `us->transport_reset`, and `us->max_lun`. The transport lazily allocates `jumpshot_info`, fakes INQUIRY, identifies the ATA device on READ_CAPACITY, and returns the last LBA plus 512-byte sector size. READ_10, READ_12, WRITE_10, and WRITE_12 extract LBA and transfer count, chunk transfers through a maximum 64 KiB bounce buffer, and use `usb_stor_access_xfer_buf()` to move data to or from the SCSI scatterlist. TEST_UNIT_READY and START_STOP poll or re-identify media; MODE_SENSE returns small static pages; REQUEST_SENSE reports the driver's cached sense triplet.

## State and Persistence Behavior

The only persistent kernel state is `us->extra`, which caches sector size/count and the last sense values. Writes go directly to the CompactFlash media. START_STOP uses the first post-change identify failure as a media-change signal and updates sense state. No filesystem-backed persistence exists.

## Dependencies and Integration Points

The driver uses usb-storage core control and bulk helpers, SCSI opcode constants, `protocol.c` transfer-buffer helpers, `fill_inquiry_response()`, and `unusual_jumpshot.h` for device IDs. It integrates as a separate usb-storage module through `module_usb_stor_driver`.

## Risks and Test Signals

There is an apparent bug in `jumpshot_write_data()`: `waitcount` is initialized but never incremented inside the status polling loop, so failed status polling can spin indefinitely. Other risks include 28-bit LBA rejection, stale sense data, capacity underflow if IDENTIFY returns zero sectors, mode-page incompleteness, and reliance on a fixed 512-byte sector. Tests should exercise media insertion/removal, READ/WRITE chunking across 64 KiB boundaries, status-poll failures, sense after unsupported commands, and READ_CAPACITY after device errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/jumpshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/karma.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/karma.c

## Purpose

`karma.c` is the usb-storage subdriver for the Rio Karma music player. It wraps the normal Bulk-Only transport with proprietary Rio commands that switch the device into or out of storage mode around selected SCSI operations.

## Important APIs, Types, and Functions

`struct karma_data` records whether the device is in storage mode and owns a 512-byte receive buffer. `rio_karma_init()` allocates this state and enters storage mode. `rio_karma_send_command()` implements the Rio packet handshake using `RIOP` command frames, a static sequence number, repeated acknowledgments, and a 6-second timeout. `rio_karma_transport()` traps `READ_10` and `START_STOP`; `rio_karma_destructor()` frees the receive buffer.

## Control Flow

Probe installs `rio_karma_transport` and the Bulk reset path. Initialization sends `RIO_ENTER_STORAGE` and marks `in_storage`. During I/O, a READ_10 observed while out of storage mode sends `RIO_ENTER_STORAGE`, flips the state, then delegates to `usb_stor_Bulk_transport()`. START_STOP sends `RIO_LEAVE_STORAGE`, clears the state, and sends `RIO_RESET` instead of passing the command through. All other commands use normal Bulk transport.

## State and Persistence Behavior

The driver maintains only volatile per-device state in `us->extra`. The static command sequence byte is shared across devices, so it is process-global rather than per-device. Device-side storage-mode transitions are persistent in the attached player until changed or reset, but there is no host-side persistence.

## Dependencies and Integration Points

The file depends on usb-storage bulk transfer helpers, the generic SCSI glue module template, `unusual_karma.h`, jiffies timeout helpers, and SCSI opcode constants. It remains a narrow adapter over `usb_stor_Bulk_transport()`.

## Risks and Test Signals

Risks include the global static sequence counter, leaks on init failure after `recv` allocation if the core does not invoke the destructor for failed init, START_STOP always forcing leave/reset semantics, and timeout sensitivity in the custom handshake. Tests should cover repeated enter/leave cycles, READ_10 after START_STOP, concurrent devices if possible, timeout/error responses from bulk endpoints, and normal passthrough commands before and after storage-mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/karma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/onetouch.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/onetouch.c

## Purpose

`onetouch.c` supports Maxtor OneTouch USB hard drives that expose a storage interface plus a hardware button. It uses the standard usb-storage storage path while registering an input device for the interrupt endpoint that reports the button.

## Important APIs, Types, and Functions

`struct usb_onetouch` stores the input device, USB device, interrupt URB, coherent packet buffer, DMA address, physical/name strings, and open state. `onetouch_connect_input()` creates and registers the input device, `usb_onetouch_irq()` decodes packets, `usb_onetouch_open()` and `usb_onetouch_close()` start/stop the interrupt URB, `usb_onetouch_pm_hook()` handles suspend/resume, and `onetouch_release_input()` frees resources.

## Control Flow

Probe calls `usb_stor_probe1()` and then `usb_stor_probe2()` without replacing the normal storage protocol or transport. The unusual-device table supplies the init hook that calls `onetouch_connect_input()`. Input setup validates that endpoint 2 is interrupt-in, allocates a 2-byte coherent buffer and URB, builds a name and physical path, configures an `EV_KEY`/`KEY_PROG1` input device, and registers it. When open, the URB is submitted continuously; each successful packet reports button state from bit 1 of byte 0 and resubmits.

## State and Persistence Behavior

The only driver-owned state is the live input allocation stored in `us->extra`. The button state is transient and emitted through the Linux input subsystem. Suspend kills the URB if the input device is open; resume resubmits it. There is no persistent storage behavior beyond the underlying usb-storage disk handled by the core.

## Dependencies and Integration Points

The file depends on usb-storage probe/lifecycle hooks, the input subsystem, coherent USB DMA allocation, interrupt URBs, PM hooks in `struct us_data`, and `unusual_onetouch.h`. It integrates one USB interface with both SCSI storage and input event reporting.

## Risks and Test Signals

Risk areas are endpoint assumptions, URB resubmission after transient errors, open-state handling across suspend/resume/disconnect, and resource cleanup after partial allocation or failed input registration. Tests should verify storage still probes normally, button events appear as `KEY_PROG1`, URB shutdown during disconnect is race-free, suspend/resume does not double-submit or lose open state, and malformed endpoint layouts return `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/onetouch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.c

## Purpose

`option_ms.c` handles Option mobile broadband devices that initially enumerate as ZeroCD mass-storage devices. It identifies genuine Option-branded storage presentations and optionally sends a mode-switch command to make the device re-enumerate as a modem.

## Important APIs, Types, and Functions

The module parameter `option_zero_cd` selects force-modem or allow-storage behavior. `option_inquiry()` sends a raw Bulk-Only INQUIRY CBW and checks the returned vendor string for `Option` or `ZCOPTION`. `option_rezero()` sends a raw REZERO-style CBW that triggers mode switching and drains optional response/CSW data. `option_ms_init()` is the init hook declared in `option_ms.h`.

## Control Flow

During unusual-device initialization, `option_ms_init()` first performs the vendor INQUIRY because some IDs are ambiguous. Non-Option or indeterminate devices are left alone. In default force-modem mode, the driver sends the mode-switch CBW, logs failure if the transfer was not good, and returns `-EIO` to stop storage binding so the device can re-enumerate. In allow-storage mode, it leaves the mass-storage interface active and returns success.

## State and Persistence Behavior

No per-device state is kept. The only state is the module parameter. The meaningful persistent side effect is on the USB device: a successful mode switch changes its exposed function until device firmware or re-enumeration changes it again.

## Dependencies and Integration Points

The file depends on usb-storage bulk pipes and raw transfer helpers, module parameters, slab allocation, and unusual-device init wiring. It shares only its public `option_ms_init()` prototype through `option_ms.h`.

## Risks and Test Signals

Risks include handcrafted CBW bytes, ignoring response contents, fixed 1024-byte response buffer assumptions, and returning `-EIO` even after a successful forced switch. Tests should cover true Option and non-Option devices with shared IDs, both module parameter modes, short/stalled response reads, CSW drain failures, and re-enumeration behavior after successful switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.h

## Purpose

`option_ms.h` is the small internal header that exposes the Option ZeroCD initializer to unusual-device tables or usb-storage setup code.

## Important APIs, Types, and Functions

It has one include guard, `_OPTION_MS_H_`, and one declaration: `extern int option_ms_init(struct us_data *us);`. `struct us_data` is supplied by including context, normally `usb.h`.

## Control Flow

The header has no executable control flow. It allows code that selects device-specific init functions to call `option_ms_init()` without including the implementation file.

## State and Persistence Behavior

The header declares no state. Runtime state and device mode-switch behavior are entirely in `option_ms.c`.

## Dependencies and Integration Points

It integrates the Option mode-switch implementation with the usb-storage unusual-device mechanism. Include-order correctness matters because the prototype references `struct us_data`.

## Risks and Test Signals

Risk is limited to prototype drift. Build coverage should catch mismatches between this declaration and `option_ms.c`, missing `struct us_data` declarations, or incorrect include ordering in users of the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.c

## Purpose

`protocol.c` provides generic usb-storage protocol adapters and transfer-buffer utilities. It normalizes SCSI CDBs for devices that require 12-byte commands, delegates protocol handling to the selected transport, and offers scatterlist copy helpers used by many device-specific subdrivers.

## Important APIs, Types, and Functions

The exported protocol entry points are `usb_stor_pad12_command()`, `usb_stor_ufi_command()`, and `usb_stor_transparent_scsi_command()`. The exported buffer helpers are `usb_stor_access_xfer_buf()` and `usb_stor_set_xfer_buf()`. The direction enum comes from `protocol.h`.

## Control Flow

`usb_stor_pad12_command()` extends CDBs shorter than 12 bytes with zeros before calling `usb_stor_invoke_transport()`. `usb_stor_ufi_command()` also forces `cmd_len` to exactly 12 and adjusts INQUIRY, MODE_SENSE_10, and REQUEST_SENSE allocation lengths to values UFI devices tolerate. `usb_stor_transparent_scsi_command()` simply delegates. `usb_stor_access_xfer_buf()` starts a scatterlist mapping iterator, skips to the caller-provided offset, copies bytes to or from mapped segments, and updates the scatterlist pointer and offset for incremental callers. `usb_stor_set_xfer_buf()` copies a local response into the SCSI buffer and sets residual if the copy is short.

## State and Persistence Behavior

There is no persistent state. The functions mutate the active `scsi_cmnd`: CDB padding, command length, selected allocation-length bytes, transfer buffer contents, and residual count.

## Dependencies and Integration Points

The file depends on Linux highmem scatterlist mapping, SCSI command APIs, usb-storage transport invocation, and exported GPL symbols for subdrivers. It is a central integration point for fake INQUIRY, MODE_SENSE, READ_CAPACITY, and media-map drivers that need to copy data between bounce buffers and SCSI scatterlists.

## Risks and Test Signals

Risks include incorrect offset advancement in multi-segment scatterlists, missing `sg_miter_stop()` on early skip failure, assuming `scsi_cmnd.cmnd` has at least 12 bytes, and UFI allocation-length rewrites that may surprise upper layers. Tests should cover single and multi-segment buffers, unaligned offsets, partial copies/residuals, empty scatterlists, UFI command rewriting, and transparent delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.h

## Purpose

`protocol.h` declares usb-storage protocol handlers and scatterlist transfer-buffer utilities implemented by `protocol.c`.

## Important APIs, Types, and Functions

It declares `usb_stor_pad12_command()`, `usb_stor_ufi_command()`, `usb_stor_transparent_scsi_command()`, `enum xfer_buf_dir` with `TO_XFER_BUF` and `FROM_XFER_BUF`, `usb_stor_access_xfer_buf()`, and `usb_stor_set_xfer_buf()`.

## Control Flow

The header has no runtime control flow. Its declarations let usb-storage core and subdrivers select protocol handlers or copy synthetic response data to and from `struct scsi_cmnd` buffers.

## State and Persistence Behavior

It declares no storage. Runtime mutations occur in `protocol.c` through the passed `scsi_cmnd`, scatterlist pointer, and offset.

## Dependencies and Integration Points

Callers need visible definitions for `struct scsi_cmnd`, `struct us_data`, and `struct scatterlist`. The header is used by generic usb-storage code and device-specific transports such as ISD200, Jumpshot, SDDR09, SDDR55, Shuttle USBAT, Realtek, and Sierra mode-switch paths.

## Risks and Test Signals

Risks are prototype drift, enum misuse that reverses copy direction, and include-order errors. Build coverage plus focused tests of `usb_stor_access_xfer_buf()` users are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/realtek_cr.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/realtek_cr.c

## Purpose

`realtek_cr.c` supports Realtek RTS51xx USB card readers. It probes reader status through vendor SCSI commands, configures auto-delink behavior, and optionally wraps the normal protocol handler with selective-suspend-aware behavior.

## Important APIs, Types, and Functions

`struct rts51x_status` stores per-LUN reader status returned by command `F0 09`; `struct rts51x_chip` stores IDs, LUN count, status array, flags, runtime PM state, and the backed-up protocol handler. Low-level helpers include `rts51x_bulk_transport()`, `rts51x_read_mem()`, `rts51x_write_mem()`, `rts51x_read_status()`, `rts51x_check_status()`, `do_config_autodelink()`, and `config_autodelink_after_power_on()`. PM paths use `realtek_cr_suspend()`, `realtek_cr_resume()`, and, under `CONFIG_REALTEK_AUTOPM`, `rts51x_invoke_transport()`.

## Control Flow

Initialization allocates `rts51x_chip`, obtains max LUN, allocates one status record per LUN, reads status for each LUN, detects firmware/product combinations that support auto-delink, optionally installs the autosuspend wrapper, and configures auto-delink registers. The vendor transport hand-builds Bulk-Only CBWs with Realtek CDBs and validates CSWs. Runtime suspend/resume serializes against `us->dev_mutex` and writes Realtek internal registers before power-down or after power-on. The optional protocol wrapper prevents low-value polling commands from waking a selectively suspended device and synthesizes TEST_UNIT_READY or ALLOW_MEDIUM_REMOVAL results from cached LUN readiness.

## State and Persistence Behavior

Per-device state lives in `us->extra`. It caches status, flags, power state, ready LUN bits, and timer state. Register writes to addresses such as `0xFE47`, `0xFE77`, `0xFE79`, and `0x48` alter device firmware behavior for auto-delink and oscillator/power handling. No host file persistence exists.

## Dependencies and Integration Points

The file depends on usb-storage Bulk-Only structures, SCSI command APIs, runtime PM, timers, unusual Realtek IDs, and usb-storage lifecycle callbacks. It integrates with generic protocol handling by backing up and optionally replacing `us->proto_handler`.

## Risks and Test Signals

Risk areas include handwritten CBW/CSW handling, firmware-specific register magic, status-length assumptions, race-prone runtime PM transitions, and compile-time behavior differences with `CONFIG_REALTEK_AUTOPM`. In `config_autodelink_before_power_down()`, one path reads `0xFE47` but writes the modified value to `0xFE77`, which is suspicious. Tests should cover multiple LUNs, suspend/resume with in-flight commands, auto-delink on supported and unsupported firmware, status short reads, CSW signature/tag failures, and behavior with autosuspend disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/realtek_cr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.c

## Purpose

`scsiglue.c` connects usb-storage devices to the Linux SCSI midlayer. It defines the default `scsi_host_template`, command queueing, device configuration quirks, error handlers, reset reporting, proc output, and a per-device `max_sectors` sysfs attribute.

## Important APIs, Types, and Functions

Key callbacks are `host_info()`, `sdev_init()`, `sdev_configure()`, `target_alloc()`, `queuecommand_lck()`, `command_abort()`, `device_reset()`, `bus_reset()`, `show_info()`, and the `max_sectors` show/store pair. Exported helpers are `usb_stor_report_device_reset()`, `usb_stor_report_bus_reset()`, `usb_stor_host_template_init()`, and `usb_stor_sense_invalidCDB`.

## Control Flow

`sdev_init()` forces 36-byte INQUIRY, marks multi-LUN Bulk devices, and skips problematic mode pages. `sdev_configure()` applies transfer-size limits, DMA mapping caps, disk and non-disk SCSI quirk flags, capacity heuristics, MODE_SENSE behavior, VPD/opcode suppression, cache/FUA flags, last-sector hacks, and lockability. `queuecommand_lck()` admits only one active command, rejects commands during disconnect, synthesizes invalid-CDB sense for blocked ATA pass-through, stores `us->srb`, and wakes the usb-storage control thread. Error handlers abort active transport, wait for completion, and invoke device or port reset paths.

## State and Persistence Behavior

The file mutates per-host `struct us_data` fields such as `srb`, `fflags`, `max_lun`, and `use_last_sector_hacks`; per-device SCSI flags; and request queue limits. The sysfs `max_sectors` store changes queue limits at runtime but not persistently across reprobe/reboot.

## Dependencies and Integration Points

It depends on the SCSI midlayer, block queue limits, DMA mapping limits, usb-storage transport and reset helpers, unusual-device flags, proc/scsi, and sysfs. Subdrivers clone the default template via `usb_stor_host_template_init()`.

## Risks and Test Signals

Risks include broad quirk interactions, one-command-at-a-time assumptions, abort/reset lock ordering, queue-limit changes during active I/O, and device-specific flags masking real capabilities. Tests should cover disconnect during queued command, abort vs reset races, disk and non-disk configuration, vendor capacity heuristics, max-sector sysfs updates, blocked ATA_12/ATA_16 sense, and reset reporting on multi-target SCM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.h

## Purpose

`scsiglue.h` declares the SCSI glue helpers exported by `scsiglue.c` for usb-storage core and subdrivers.

## Important APIs, Types, and Functions

It declares `usb_stor_report_device_reset()`, `usb_stor_report_bus_reset()`, `usb_stor_host_template_init()`, and the shared fixed sense buffer `usb_stor_sense_invalidCDB`.

## Control Flow

The header has no executable flow. Its functions are called when subdrivers need the default host template or when transport/protocol code must notify the SCSI midlayer about reset events.

## State and Persistence Behavior

It defines no state, but exposes `usb_stor_sense_invalidCDB`, a static invalid-field-in-CDB sense payload used by callers that need to fail unsupported commands predictably.

## Dependencies and Integration Points

The declarations reference `struct us_data` and `struct scsi_host_template`, supplied by the including usb-storage/SCSI headers. It is included by generic protocol code and many device-specific subdrivers.

## Risks and Test Signals

Risk is limited to ABI/prototype drift and misuse of reset-reporting lock preconditions. Build coverage should catch declaration mismatches; runtime tests should ensure reset reports are called with the lock expectations documented in `scsiglue.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sddr09.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/sddr09.c

## Purpose

`sddr09.c` supports SanDisk SDDR-09 SmartMedia readers and the SmartMedia LUN of some DPCM combo readers. It translates normal SCSI block commands into the reader's vendor SCSI commands, builds NAND logical-to-physical maps, and computes SmartMedia ECC/control bytes during writes.

## Important APIs, Types, and Functions

`struct nand_flash_dev` describes supported NAND IDs and geometry. `struct sddr09_card_info` stores capacity, page/block geometry, LBA/PBA maps, LBA count, and write-protect flags. Vendor-command helpers include `sddr09_send_command()`, `sddr09_read20/21/22()`, `sddr09_writeX()`, `sddr09_read_status()`, and `sddr09_read_deviceID()`. Mapping and media helpers include `sddr09_get_cardinfo()`, `sddr09_read_map()`, `sddr09_get_wp()`, `sddr09_read_data()`, `sddr09_write_data()`, and `sddr09_write_lba()`.

## Control Flow

Initialization resets configuration, allocates card state, and initializes ECC lookup tables. READ_CAPACITY reads write-protect status and card ID, selects NAND geometry, reads the control area of every physical block, builds LBA/PBA maps, and returns logical capacity. READ_10 maps logical pages through `lba_to_pba` and reads zeros for never-written LBAs. WRITE_10 allocates or reuses a PBA, reads the whole physical block including control data, patches user pages and ECC bytes, and writes the whole block back. The DPCM transport routes LUN 0 to CompactFlash through CB transport and LUN 1 to SDDR09 after temporarily rewriting the SCSI LUN.

## State and Persistence Behavior

Per-device state is held in `us->extra`. The LBA/PBA maps are volatile reconstructions from card control bytes and are rebuilt after capacity discovery. Writes persist to SmartMedia and update in-memory maps. Static fake-sense variables in `sddr09_transport()` and static `lastpba` in `sddr09_find_unused_pba()` are process-global, which can cross-contaminate multiple devices.

## Dependencies and Integration Points

The file depends on usb-storage control/bulk helpers, SCSI opcode handling, scatterlist buffer utilities, `unusual_sddr09.h`, NAND geometry constants embedded locally, and CB reset/transport for combo devices.

## Risks and Test Signals

Risks include hand-built NAND ECC, whole-block rewrite exposure on power loss, static global fake sense and allocation cursor, limited/old NAND ID table, map corruption handling, and writing PBA 1 being silently ignored. Tests should cover each supported card size, no-media and write-protect states, duplicated/bad map entries, unwritten LBA reads, partial-block writes with ECC repair, DPCM LUN routing, and REQUEST_SENSE after faked failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sddr09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sddr55.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/sddr55.c

## Purpose

`sddr55.c` supports SanDisk SDDR-55 SmartMedia readers. It exposes SmartMedia as a SCSI disk by synthesizing common SCSI responses, reading device capacity IDs, maintaining logical-to-physical maps, and translating READ_10/WRITE_10 into reader-specific block commands.

## Important APIs, Types, and Functions

`struct sddr55_card_info` stores card capacity, geometry, read-only state, forced-read-only/fatal-error flags, last-access timestamp, sense data, and LBA/PBA maps. Core helpers include `sddr55_status()`, `sddr55_read_deviceID()`, `sddr55_get_capacity()`, `sddr55_read_map()`, `sddr55_read_data()`, `sddr55_write_data()`, and `sddr55_transport()`.

## Control Flow

The transport lazily allocates card state. REQUEST_SENSE returns cached sense data and clears it. INQUIRY and MODE_SENSE_10 are synthesized. Before most commands, the driver checks media status if no map exists or if the previous access is older than half a second. READ_CAPACITY identifies card size, computes usable capacity as 250 logical blocks per 256 physical blocks, returns the final 512-byte sector, and rebuilds maps. READ_10 translates SCSI page to logical block/page and reads mapped PBAs or zeros for unallocated LBAs. WRITE_10 rejects read-only/fatal states, finds spare PBAs for new LBAs, sends write commands, reads back device-reported new PBA, and updates both maps.

## State and Persistence Behavior

State is volatile in `us->extra`, but writes persist to SmartMedia and alter card-level block mappings. Media removal frees maps and clears fatal/forced-read-only flags. Map inconsistencies set `force_read_only`; severe write-map conflicts set `fatal_error`.

## Dependencies and Integration Points

The file depends on usb-storage bulk helpers, SCSI command constants, `usb_stor_access_xfer_buf()`, `fill_inquiry_response()`, `unusual_sddr55.h`, and the generic usb-storage lifecycle. It uses no external MTD layer; SmartMedia geometry and map policy are implemented locally.

## Risks and Test Signals

Risks include trusting device-returned PBAs, manual zone math, partial map updates on write failure, capacity assumptions for unknown IDs, and forcing read-only after duplicate LBA detection. Tests should cover all listed device IDs, media removal/reinsertion, read-only cards, unallocated reads, write allocation exhaustion, bad-block status, new-PBA out-of-range reports, map inconsistency, and sense codes for no media/incompatible medium/illegal command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sddr55.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/shuttle_usbat.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/shuttle_usbat.c

## Purpose

`shuttle_usbat.c` supports SCM Microsystems/Shuttle USBAT bridges used for ATAPI CD drives such as HP 8200e and USBAT02 CompactFlash readers. It initializes the bridge, identifies the attached device type, and installs either an ATAPI packet transport or a flash ATA-sector transport.

## Important APIs, Types, and Functions

`struct usbat_info` stores device type, flash capacity/sector size, and cached sense data. Common bridge helpers include `usbat_read()`, `usbat_write()`, `usbat_execute_command()`, `usbat_multiple_write()`, `usbat_set_shuttle_features()`, `usbat_wait_not_busy()`, `usbat_read_block()`, `usbat_write_block()`, `usbat_read_blocks()`, and `usbat_write_blocks()`. Flash helpers include `usbat_flash_check_media()`, `usbat_flash_get_sector_count()`, `usbat_flash_read_data()`, `usbat_flash_write_data()`, and `usbat_flash_transport()`. CD/ATAPI helpers include `usbat_hp8200e_transport()` and `usbat_hp8200e_handle_read10()`.

## Control Flow

Probe installs placeholder transport and lets unusual-device init call `init_usbat_cd()` or `init_usbat_flash()`. Initialization allocates state, toggles user I/O reset/card-detect lines, tests ATA registers, detects device type with IDENTIFY PACKET DEVICE if needed, sets the final transport, and programs Shuttle feature registers. Flash transport fakes INQUIRY, checks media through UIO pins, returns IDENTIFY-derived capacity, chunks READ/WRITE through 64 KiB bounce buffers, and returns cached sense on REQUEST_SENSE. HP8200e transport wraps ATAPI packet commands by writing ATA packet registers and command bytes, handles large READ_10/READ_CD by splitting into sub-64 KiB reads, and waits for long operations such as BLANK.

## State and Persistence Behavior

Per-device state lives in `us->extra`; the global `transferred` counter tracks HP8200e transfer progress across calls. Flash writes persist to media. UIO resets and feature programming alter bridge/device state but are not host-persistent.

## Dependencies and Integration Points

The driver depends on usb-storage control/bulk helpers, SCSI and CD-ROM opcodes, scatterlist utilities, `unusual_usbat.h`, and CB reset handling. It integrates both as a SCSI disk-like flash transport and as an ATAPI packet bridge.

## Risks and Test Signals

Risks include global `transferred`, long busy waits, many magic register sequences, 28-bit LBA limits, media-change races, len truncation above 64 KiB, and device-type misidentification. Tests should cover HP8200e packet commands, blank/synchronize long waits, large READ_10 splitting, flash media absent/changed/present states, READ/WRITE_10 and _12 chunking, unknown commands with REQUEST_SENSE, and init failures at each UIO/register-test step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/shuttle_usbat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sierra_ms.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/sierra_ms.c

## Purpose

`sierra_ms.c` handles Sierra Wireless TRU-Install devices that expose a mass-storage image before modem operation. It decides whether to keep storage mode or switch to modem mode based on a module parameter and device-reported SWoC package information.

## Important APIs, Types, and Functions

`struct swoc_info` models the vendor control response containing revision, Linux SKU, and version. `containsFullLinuxPackage()` classifies SKU ranges that contain a full Linux package. `sierra_set_ms_mode()` sends the vendor SetSwocMode control request. `sierra_get_swoc_info()` reads SWoC info and endian-converts fields. `truinst_show()` exposes current info through a read-only sysfs attribute. `sierra_ms_init()` is the unusual-device init hook.

## Control Flow

Initialization checks `swi_tru_install`. Force-modem mode sends SetSwocMode(Modem) and returns `-EIO` to stop storage binding. Force-mass-storage mode skips switching and creates the `truinst` sysfs file. Normal mode allocates `swoc_info`, retries GetSwocInfo up to three times with 2-second sleeps, logs decoded values, and switches to modem mode if the device lacks a full Linux package. Otherwise it keeps storage mode and creates the sysfs attribute.

## State and Persistence Behavior

The driver keeps no per-device private state after init. The module parameter controls policy. A successful vendor request changes device mode and usually causes re-enumeration. The sysfs file performs fresh control reads on demand rather than returning cached state.

## Dependencies and Integration Points

It depends on USB vendor control messages, usb-storage unusual init flow, module parameters, sysfs device attributes, SCSI includes from the surrounding storage stack, and `sierra_ms.h` for the exported initializer declaration.

## Risks and Test Signals

Risks include no cleanup path for the created `truinst` attribute in this file, fixed SKU policy ranges, returning `-EIO` even after intentional successful modem switching, and sleeping retries during probe. Tests should cover all module parameter modes, SWoC query failures and retries, endian conversion, SKU boundaries, sysfs output after probe, and device re-enumeration after forced or policy-driven switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sierra_ms.c -->
