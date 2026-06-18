# subset-b-005534 Research

Grouped source research for selected USB serial and USB storage drivers under `sources/distributed-fs/ceph-client/drivers/usb`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/whiteheat.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/whiteheat.c

## Purpose

`whiteheat.c` is the Linux usb-serial driver for Connect Tech WhiteHEAT four-port USB serial adapters. It handles both the pre-renumeration firmware-loader device and the post-firmware serial device, then translates tty operations into WhiteHEAT firmware commands sent over a dedicated command endpoint.

## Important APIs, Types, and Functions

The file registers two `struct usb_serial_driver` instances: `whiteheat_fake_device` for firmware download and `whiteheat_device` for the real four-port adapter. `whiteheat_firmware_download()` loads `whiteheat_loader.fw` and `whiteheat.fw` through EZ-USB helpers. `whiteheat_attach()` probes firmware state by issuing `WHITEHEAT_GET_HW_INFO`, creates `struct whiteheat_command_private` for the command port, and installs custom command URB callbacks. Per-data-port `struct whiteheat_private` stores cached modem control bits. Runtime entry points include `whiteheat_open()`, `whiteheat_close()`, `whiteheat_set_termios()`, `whiteheat_tiocmget()`, `whiteheat_tiocmset()`, and `whiteheat_break_ctl()`. Firmware command helpers include `firm_send_command()`, `firm_open()`, `firm_close()`, `firm_setup_port()`, `firm_set_rts()`, `firm_set_dtr()`, `firm_set_break()`, `firm_purge()`, `firm_get_dtr_rts()`, and `firm_report_tx_done()`.

## Control Flow

Before firmware is loaded, the fake device probe downloads both firmware images and intentionally returns an attach failure so the pre-renumeration device does not remain bound. After the adapter reappears with the real product ID, attach sends a synchronous hardware-info command over command port 4 and initializes command-port state. Opening a tty starts the shared command read URB, sends firmware open and purge commands, pushes termios settings, clears data endpoint halts, and then delegates data streaming to `usb_serial_generic_open()`. Command submission serializes on `command_info->mutex`, writes a command byte plus payload through the command-port write URB, waits on `wait_command`, and interprets command-complete/failure replies from `command_port_read_callback()`. Closing reports TX completion, sends close, closes the generic data path, and decrements the command-port user count so the command read URB is killed when no ports are open.

## State and Persistence Behavior

All persistent state is runtime-only. The command port keeps a mutex, a shared open count, a command-completion flag, a wait queue, and a 64-byte result buffer. Each user port keeps only an unlocked cached MCR byte for DTR/RTS. Firmware remains resident on the device after upload until unplug or reset, which is why attach clears endpoint halts before probing firmware version. No on-disk or nonvolatile host state is maintained by the driver.

## Dependencies and Integration Points

The driver depends on usb-serial core registration, tty termios/modem-control callbacks, generic usb-serial bulk data handling, EZ-USB firmware download support, and the firmware protocol definitions in `whiteheat.h`. It integrates with userspace as normal ttyUSB ports and with firmware through a fifth bulk-in/out command endpoint separate from the four data ports.

## Risks and Test Signals

Risks include `whiteheat_private.mcr` being explicitly noted as unlocked, command-port lifetime coupling across multiple open data ports, command timeouts leaving firmware or host state ambiguous, fixed assumptions about command port index 4 and five bulk endpoints, and failures if firmware files are missing. Test signals include pre-renumeration firmware download, real-device attach reporting firmware version, concurrent opens on multiple ports, termios parity/baud/flow-control changes producing `WHITEHEAT_SETUP_PORT`, DTR/RTS get/set round trips, command timeout/error handling, and disconnect while command URBs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/whiteheat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/whiteheat.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/whiteheat.h

## Purpose

`whiteheat.h` defines the host-to-firmware command protocol, payload layouts, event formats, and firmware reply structures used by the Connect Tech WhiteHEAT usb-serial driver.

## Important APIs, Types, and Functions

The header enumerates command IDs such as `WHITEHEAT_OPEN`, `WHITEHEAT_CLOSE`, `WHITEHEAT_SETUP_PORT`, modem-signal commands, `WHITEHEAT_GET_HW_INFO`, `WHITEHEAT_EVENT`, and command-complete/failure replies. Request payloads include `struct whiteheat_simple`, `struct whiteheat_port_settings`, `struct whiteheat_set_rdb`, `struct whiteheat_dump`, `struct whiteheat_purge`, `struct whiteheat_echo`, and `struct whiteheat_test`. Reply/event payloads include `struct whiteheat_status_info`, `struct whiteheat_dr_info`, `struct whiteheat_hw_info`, `struct whiteheat_event_info`, and `struct whiteheat_test_info`.

## Control Flow

The header has no executable flow. It establishes the byte-level ABI consumed by `whiteheat.c`: command helpers fill these packed structures, the command port sends command ID plus payload, and the read callback interprets the first response byte against the reply constants.

## State and Persistence Behavior

No state is stored in the header. Its structures describe transient USB command and response packets. The protocol includes firmware-visible state such as port settings, UART modem control, purge requests, hardware/EEPROM information, and unsolicited events, but persistence is owned by the WhiteHEAT firmware or hardware.

## Dependencies and Integration Points

The definitions depend on kernel integer types and little-endian annotations. The host driver maps tty settings to parity, software flow, hardware flow, break, DTR, and RTS constants from this file, while firmware must interpret the same numeric command and layout contract.

## Risks and Test Signals

Risks are protocol drift between host and firmware, packed-layout or endian mistakes, and fields whose comments expose firmware-specific constraints such as dump address ranges and 8051 side effects. Test signals are compile coverage from `whiteheat.c`, packet-size checks for command endpoint buffers, successful hardware-info parsing, and termios/modem operations matching expected command payloads on USB traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/whiteheat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/wishbone-serial.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/wishbone-serial.c

## Purpose

`wishbone-serial.c` is a minimal usb-serial driver for the GSI Wishbone-Serial adapter. Its main device-specific job is to notify Etherbone firmware when a serial stream opens or closes so Wishbone negotiation and bus-cycle state are reset cleanly.

## Important APIs, Types, and Functions

The driver matches one vendor-specific interface using `USB_DEVICE_AND_INTERFACE_INFO(0x1D50, 0x6062, 0xFF, 0xFF, 0xFF)`. `usb_gsi_openclose()` sends vendor request `GSI_VENDOR_OPENCLOSE` to endpoint zero with `wValue` set to open or closed. `wishbone_serial_open()` issues the open notification before `usb_serial_generic_open()`, and unwinds by sending close if generic open fails. `wishbone_serial_close()` closes the generic stream then sends the close notification. `wishbone_serial_device` registers a single-port usb-serial driver.

## Control Flow

Probe and disconnect are handled by the usb-serial core. On tty open, the driver sends the vendor control request to the current interface number, then starts the generic bulk read/write path. On tty close, it stops the generic path and sends the close request so firmware can drop the Wishbone cycle line even if userspace did not do so.

## State and Persistence Behavior

The file stores no private driver state. The only state transition is firmware-side open/closed status communicated over control endpoint zero. No host-side persistence or cached configuration exists.

## Dependencies and Integration Points

It depends on usb-serial core, tty open/close callbacks, generic usb-serial data transport, and the device firmware's vendor-specific control request. Userspace sees a normal tty port; Etherbone/Wishbone-specific semantics remain inside the adapter firmware.

## Risks and Test Signals

Risks include treating any nonzero `usb_control_msg()` return as an error even though control helpers can return transferred lengths in some contexts, firmware dependence on the exact interface number, and leaving firmware marked open if close control transfer fails. Test signals include USB control traces on open/close, generic tty data transfer after open, failure injection for the open request, and close behavior after userspace exits without an orderly protocol shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/wishbone-serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/xr_serial.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/xr_serial.c

## Purpose

`xr_serial.c` supports MaxLinear/Exar USB-to-serial devices in the XR21V141x, XR21B14xx, and XR2280x families. It binds CDC-style control/data interfaces, configures vendor UART registers, exposes modem-control and break handling, and implements RS-485 mode through tty ioctls.

## Important APIs, Types, and Functions

`struct xr_type` describes per-chip register width, request recipient, vendor request IDs, register addresses, and optional chip-specific operations. `struct xr_data` stores the selected type, channel number, and `struct serial_rs485` state per port. Low-level helpers `xr_set_reg()`, `xr_get_reg()`, `xr_set_reg_uart()`, and `xr_get_reg_uart()` issue vendor control transfers. UART lifecycle helpers include `xr_uart_enable()`, `xr_uart_disable()`, `xr_fifo_reset()`, and XR21V141x-specific FIFO/UART sequencing. TTY operations include `xr_open()`, `xr_close()`, `xr_set_termios()`, `xr_tiocmget()`, `xr_tiocmset()`, `xr_dtr_rts()`, `xr_break_ctl()`, and `xr_ioctl()` for `TIOCGRS485` and `TIOCSRS485`. Line configuration is split between `xr21v141x_set_line_settings()` for direct register programming and `xr_cdc_set_line_coding()` for CDC requests.

## Control Flow

`xr_probe()` parses CDC descriptors, finds the union slave data interface, claims it, and records the chip type from `id->driver_info`. `xr_port_probe()` allocates `struct xr_data`, derives the channel from interface number, optionally enables a custom-driver mode, and initializes GPIO mode/direction with DTR/RTS deasserted. Opening a tty resets FIFOs, enables the UART, applies termios, then starts generic usb-serial I/O. Termios changes program baud/format or CDC line coding, update flow-control GPIO mode, and toggle DTR/RTS around B0. RS-485 ioctl updates the sanitized RS-485 state under `termios_rwsem` and reapplies flow mode. Close shuts down generic I/O and disables the UART.

## State and Persistence Behavior

Per-port state is allocated during port probe and freed on port remove. RS-485 flags persist for the port until changed or the device is removed. Hardware registers hold the active UART, GPIO, flow-control, custom-driver, baud, and break state; the driver rewrites them on open/termios/ioctl rather than keeping a complete software mirror. No filesystem-backed persistence exists.

## Dependencies and Integration Points

The driver depends on usb-serial core, USB CDC descriptor parsing, tty termios and ioctl APIs, generic usb-serial bulk I/O, and MaxLinear/Exar vendor control registers. It integrates with userspace through ttyUSB ports plus standard modem-control and RS-485 ioctls, and with firmware/hardware through vendor register access and CDC `SET_LINE_CODING` for some variants.

## Risks and Test Signals

Risks include chip-family register-table mistakes, channel derivation from interface numbers, partial error handling inside `xr_set_flow_mode()` where some register-write failures are ignored, active-low modem-signal inversion, RS-485 support limited to flags without delays, and custom-driver-mode setup failures preventing probe. Test signals include CDC union parsing on every supported PID, open/close UART enable sequencing, baud-rate clamping and XR21V141x fractional divisor programming, CS5/CS6 fallback behavior on unsupported chips, hardware/software flow control, DTR/RTS and break control, RS-485 ioctl round trips, and suspend/disconnect cleanup through usb-serial remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/xr_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/xsens_mt.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/xsens_mt.c

## Purpose

`xsens_mt.c` is a small usb-serial binding driver for Xsens MT motion trackers. It binds known Xsens VID/PID pairs but only accepts the serial interface used by the device.

## Important APIs, Types, and Functions

The `id_table` lists MTi-10, MTi-20, MTi-30, MTi-100, MTi-200, MTi-300, and MTi-G-700 product IDs under vendor ID `0x2639`. `xsens_mt_probe()` checks the current alternate setting's interface number and returns success only for interface 1. `xsens_mt_device` registers a one-port usb-serial driver using default usb-serial behavior for data transfer.

## Control Flow

On USB match, usb-serial calls the probe hook. Interface 1 is accepted and exposed as a tty; all other matched interfaces are rejected with `-ENODEV`. Runtime open, close, read, and write handling is inherited from the usb-serial core.

## State and Persistence Behavior

The driver has no private state, no cached device settings, and no persistence. Device state remains entirely in the Xsens firmware and the usb-serial core's generic per-port structures.

## Dependencies and Integration Points

It depends on usb-serial core and the Xsens devices presenting a usable serial interface at USB interface number 1. Userspace interacts with the resulting tty using the device's native protocol.

## Risks and Test Signals

Risks include hard-coding interface number 1 for all listed devices, adding new Xsens products with different interface layouts, and relying on generic usb-serial defaults for all tty behavior. Test signals include binding only interface 1 for each PID, no tty exposure on other interfaces, basic open/read/write traffic with an Xsens protocol tool, and module autoload via `MODULE_DEVICE_TABLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/xsens_mt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/Kconfig

## Purpose

`drivers/usb/storage/Kconfig` defines build-time configuration for the USB Mass Storage core, optional verbose debugging, vendor-specific USB storage subdrivers, Realtek autosuspend support, and USB Attached SCSI.

## Important APIs, Types, and Functions

Important symbols include `USB_STORAGE`, `USB_STORAGE_DEBUG`, vendor modules such as `USB_STORAGE_DATAFAB`, `USB_STORAGE_FREECOM`, `USB_STORAGE_ALAUDA`, `USB_STORAGE_CYPRESS_ATACB`, `USB_STORAGE_ENE_UB6250`, and `USB_UAS`. `USB_STORAGE` is a tristate depending on `SCSI`; `USB_UAS` depends on both `SCSI` and `USB_STORAGE`; `REALTEK_AUTOPM` depends on Realtek reader support and PM.

## Control Flow

There is no runtime control flow. Kconfig selections determine which objects the Makefile builds, which help text appears in configuration tools, and whether debug code is compiled into the mass-storage core.

## State and Persistence Behavior

Configuration choices persist in the kernel `.config` and decide whether features are built in, modular, or absent. At runtime this file stores no state.

## Dependencies and Integration Points

The file integrates USB storage with the SCSI stack and block-device expectations, and lines up with Makefile object names such as `usb-storage`, `uas`, `ums-datafab`, `ums-freecom`, `ums-alauda`, `ums-cypress`, and `ums-eneub6250`. It also documents user-visible module names.

## Risks and Test Signals

Risks include dependency drift between Kconfig and Makefile entries, building UAS without the expected usb-storage support, user confusion when `USB_STORAGE` is enabled without `BLK_DEV_SD`, and optional vendor drivers being omitted for unusual devices. Test signals include `allmodconfig`/`allyesconfig` build coverage, menuconfig visibility checks, module names matching help text, and successful builds for each vendor symbol as `m` and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/Makefile

## Purpose

`drivers/usb/storage/Makefile` maps USB storage Kconfig symbols to core, UAS, and vendor-specific object files, and sets include paths and symbol namespace defaults for the USB_STORAGE namespace.

## Important APIs, Types, and Functions

`ccflags-y` adds the SCSI driver include path and defines `DEFAULT_SYMBOL_NAMESPACE="USB_STORAGE"`. `usb-storage-y` is composed from `scsiglue.o`, `protocol.o`, `transport.o`, `usb.o`, `initializers.o`, `sierra_ms.o`, `option_ms.o`, and `usual-tables.o`, with `debug.o` conditionally added for `CONFIG_USB_STORAGE_DEBUG`. Vendor module aggregates include `ums-alauda-y := alauda.o`, `ums-cypress-y := cypress_atacb.o`, `ums-datafab-y := datafab.o`, `ums-eneub6250-y := ene_ub6250.o`, and `ums-freecom-y := freecom.o`.

## Control Flow

There is no runtime flow. Kbuild uses the object lists to compile either built-in objects or loadable modules based on the selected Kconfig symbols.

## State and Persistence Behavior

The Makefile contributes no runtime state. Its build decisions persist only as generated build artifacts and module composition.

## Dependencies and Integration Points

The file integrates with Kbuild, the USB storage Kconfig symbols, the SCSI include tree, and module namespace handling. It ensures optional vendor modules link against the USB storage core interfaces they import.

## Risks and Test Signals

Risks include object-list drift from Kconfig, namespace mismatch for exported USB storage symbols, missing debug object when `CONFIG_USB_STORAGE_DEBUG` is enabled, and broken vendor module aggregation. Test signals include clean incremental builds across `USB_STORAGE_DEBUG` on/off, modpost namespace checks, and successful module generation for each `ums-*` target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/alauda.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/alauda.c

## Purpose

`alauda.c` implements a USB storage subdriver for RATOC/Olympus/Fujifilm Alauda-based xD and SmartMedia card readers. It converts a small SCSI disk command set into Alauda vendor control and bulk commands, including NAND flash LBA-to-PBA mapping and ECC handling.

## Important APIs, Types, and Functions

`struct alauda_media_info` tracks per-slot capacity, geometry, zone size, page/block shifts, and lazy `lba_to_pba`/`pba_to_lba` maps. `struct alauda_info` stores two port states, a write endpoint, sense data, and media initialization state. Media and mapping helpers include `alauda_get_media_status()`, `alauda_ack_media()`, `alauda_get_media_signature()`, `alauda_init_media()`, `alauda_check_media()`, `alauda_read_map()`, `alauda_ensure_map_for_zone()`, and `alauda_free_maps()`. Data path helpers include `alauda_read_block_raw()`, `alauda_read_block()`, `alauda_write_lba()`, `alauda_read_data()`, and `alauda_write_data()`. `nand_init_ecc()`, `nand_compute_ecc()`, and related helpers manage redundancy-area ECC. `alauda_transport()` dispatches SCSI commands, and `alauda_probe()` installs the transport into usb-storage.

## Control Flow

Probe uses `usb_stor_probe1()`, assigns `Alauda Control/Bulk` transport, sets `max_lun` to 1 for xD/SmartMedia ports, and completes with `usb_stor_probe2()`. On TEST UNIT READY, READ CAPACITY, READ_10, or WRITE_10, `alauda_check_media()` polls/acknowledges media status, initializes media geometry from a signature, allocates zone-map pointer arrays, and resets media after changes. Zone maps are generated lazily by reading redundancy data for every physical block in a zone. Reads translate logical pages to mapped PBAs and return zeroes for never-written blocks. Writes read or synthesize a full physical block, update page data and ECC, write a fresh unused PBA, update maps, and erase the old PBA.

## State and Persistence Behavior

Host state includes cached media geometry, per-zone mapping tables, sense key/ASC/ASCQ, and `media_initialized`. These caches are freed on media removal/change and device disconnect. Persistent storage state is the NAND card itself: block erase/write operations, logical-address metadata in redundancy bytes, bad/unusable block markings, and generated ECC persist on media. The driver does not persist maps to disk and rebuilds them from flash metadata.

## Dependencies and Integration Points

The driver depends on usb-storage core probe, transport, scatterlist-buffer helpers, unusual-device tables, SCSI command constants, and Alauda vendor control/bulk opcodes. It integrates with the SCSI disk layer by faking INQUIRY, REQUEST_SENSE, READ_CAPACITY, and allowing medium removal while exposing block I/O through READ_10/WRITE_10.

## Risks and Test Signals

Risks include reverse-engineered protocol assumptions, unchecked failure from `alauda_ensure_map_for_zone()` because it returns void, global ECC lookup tables initialized per device, media-change state shared across both ports, write amplification and power-loss exposure during remap/erase, and fragile redundancy parsing for unknown card IDs. Test signals include xD and SmartMedia LUN behavior, media insertion/removal/unit-attention sense, card signature detection across supported IDs, lazy map creation, reads from unwritten blocks returning zeroes, ECC regeneration on partial-block writes, bad duplicate LBA handling, and disconnect cleanup after maps are allocated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/alauda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/cypress_atacb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/cypress_atacb.c

## Purpose

`cypress_atacb.c` adds SAT-style ATA pass-through support for Cypress USB/ATA bridges that implement the vendor-specific ATACB protocol. Devices without usable ATACB fall back to normal transparent SCSI.

## Important APIs, Types, and Functions

The driver builds USB ID and unusual-device tables from `unusual_cypress.h`. `cypress_atacb_passthrough()` is the protocol handler: it intercepts SCSI `ATA_12` and `ATA_16`, validates supported ATA pass-through fields, rewrites the CDB to Cypress ATACB command `0x24`, forwards through `usb_stor_transparent_scsi_command()`, and optionally constructs ATA return descriptor sense data when CK_COND is requested. `cypress_probe()` selects either the ATACB protocol handler or transparent SCSI based on descriptor string-index heuristics for CY7C68300 A-revision devices.

## Control Flow

Probe initializes usb-storage state with the Cypress unusual-device entry. If the bridge is not the filtered A-revision descriptor layout, the transport protocol name and handler are changed to `Transparent SCSI with Cypress ATACB`; otherwise standard transparent SCSI is used. Runtime non-ATA commands pass through unchanged. ATA pass-through commands are saved, replaced with ATACB layout, executed, and then restored before return. Unsupported protocols, LBA48 high bytes, multiple count, and SET FEATURES transfer-mode commands return invalid-CDB sense.

## State and Persistence Behavior

The driver has no private persistent state beyond the selected `us->proto_handler` and protocol name. It temporarily rewrites `srb->cmnd` and `cmd_len`, preserving the original command in a stack buffer before restoring it.

## Dependencies and Integration Points

It depends on usb-storage core, SCSI error-handling command save/restore helpers, Linux ATA command constants, transparent SCSI transport, and Cypress unusual-device tables. It integrates ATA tools such as SMART/hdparm with selected USB/ATA bridges by translating SCSI ATA PASS THROUGH into the bridge vendor protocol.

## Risks and Test Signals

Risks include incomplete LBA48 support, hard-coded ATACB vendor signature defaults, descriptor-index filtering that may misclassify firmware revisions, temporary mutation of the SCSI CDB, and approximate ATA-to-SCSI sense mapping. Test signals include ATA_12 and ATA_16 pass-through, invalid field cases returning invalid CDB, CK_COND producing descriptor-format sense with ATA registers, fallback behavior for filtered revisions, and normal transparent SCSI for non-ATA commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/cypress_atacb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/datafab.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/datafab.c

## Purpose

`datafab.c` implements a usb-storage subdriver for Datafab USB CompactFlash readers. It exposes an ATA-like CompactFlash device as a SCSI disk by emulating core SCSI commands and issuing Datafab-specific bulk commands.

## Important APIs, Types, and Functions

`struct datafab_info` caches total sectors, sector size, selected LUN, and faked sense data. `datafab_bulk_read()` and `datafab_bulk_write()` wrap USB bulk transfers. `datafab_determine_lun()` probes dual-slot readers by trying IDENTIFY DEVICE on LUN 0 and 1. `datafab_id_device()` performs IDENTIFY and extracts capacity. `datafab_read_data()` and `datafab_write_data()` split transfers into at most 64 KiB bounce-buffer chunks and move data to/from the SCSI scatterlist. `datafab_handle_mode_sense()` fabricates a few mode pages. `datafab_transport()` dispatches SCSI commands, and `datafab_probe()` installs the custom transport and bulk reset handler.

## Control Flow

On first transport use, the driver allocates `struct datafab_info` and initializes `lun` to -1. INQUIRY and REQUEST_SENSE are faked. READ_CAPACITY identifies the CF media, stores 512-byte sector geometry, and returns last LBA plus sector size. READ_10/READ_12 and WRITE_10/WRITE_12 parse LBAs and sector counts, determine LUN if needed, issue 8-byte Datafab ATA-style commands, and transfer data in bounce-buffer windows. START_STOP is used as a media-change probe: a failed identify sets UNIT ATTENTION and check-condition result.

## State and Persistence Behavior

Runtime state is cached in `us->extra`: selected LUN, media capacity, sector size, and sense triplet. This cache survives across commands for a bound device but is not persisted. The physical CF card stores user data; the driver does not maintain metadata on the card beyond normal ATA-style read/write commands.

## Dependencies and Integration Points

The file depends on usb-storage probe/transport helpers, SCSI command constants, scatterlist transfer helpers, unusual-device tables, and Datafab's vendor bulk command protocol. It integrates with the SCSI disk layer by faking enough inquiry, capacity, mode-sense, sense, and medium-removal behavior for block devices.

## Risks and Test Signals

Risks include limited 28-bit LBA checks that compare sector counts rather than full address range, no READ_6/WRITE_6 support, a likely write-success condition bug using `&&` instead of `||` for reply validation, stale LUN selection after media changes, and simplistic sense data. Test signals include dual-slot LUN detection, READ_CAPACITY after insertion/removal, 64 KiB split reads/writes across scatterlists, MODE_SENSE page variants, START_STOP media-change behavior, and write-result error handling with malformed two-byte replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/datafab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/debug.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/debug.c

## Purpose

`debug.c` implements verbose debug output helpers for the USB Mass Storage core when `CONFIG_USB_STORAGE_DEBUG` is enabled. It prints readable SCSI command names, command bytes, and sense descriptions.

## Important APIs, Types, and Functions

`usb_stor_show_command()` maps many SCSI and ATAPI opcodes to strings and prints up to 16 command bytes. `usb_stor_show_sense()` uses SCSI library helpers to format sense key, ASC, and ASCQ. `usb_stor_dbg()` is the exported variadic debug printer using `dev_vprintk_emit(LOGLEVEL_DEBUG, &us->pusb_dev->dev, ...)`. `EXPORT_SYMBOL_GPL(usb_stor_dbg)` exposes the debug printer inside the USB_STORAGE namespace context.

## Control Flow

Debug callers invoke the helpers around command dispatch, error handling, or protocol-specific paths. The functions perform table/switch formatting and emit kernel debug logs; they do not affect transport results.

## State and Persistence Behavior

The file stores no state. Output persists only as kernel log messages subject to normal log buffering and dynamic log-level handling.

## Dependencies and Integration Points

It depends on SCSI opcode definitions, SCSI debug formatting helpers, the usb-storage `struct us_data`, and the declarations/macros in `debug.h`. It integrates with core and subdriver `usb_stor_dbg()`/`US_DEBUG()` call sites.

## Risks and Test Signals

Risks are low for device behavior because code is diagnostic, but command-name tables can become stale and debug logging can be noisy or reveal command data. Test signals include successful builds with `CONFIG_USB_STORAGE_DEBUG=y`, representative opcode name formatting, sense formatting for known and unknown ASC/ASCQ values, and vendor modules resolving `usb_stor_dbg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/debug.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/debug.h

## Purpose

`debug.h` declares and gates USB Mass Storage debug helpers so call sites compile both with and without verbose debugging enabled.

## Important APIs, Types, and Functions

When `CONFIG_USB_STORAGE_DEBUG` is set, the header declares `usb_stor_show_command()`, `usb_stor_show_sense()`, and `usb_stor_dbg()`, and expands `US_DEBUG(x)` to execute `x`. Otherwise it provides a typed no-op `_usb_stor_dbg()` and defines `usb_stor_dbg()` and `US_DEBUG(x)` so debug call sites compile away while preserving format checking.

## Control Flow

There is no runtime flow in the debug-enabled case beyond function declarations. In the disabled case, debug calls are wrapped in `do { if (0) ... } while (0)`, keeping expressions unreachable and optimized out.

## State and Persistence Behavior

The header has no state or persistence. It only controls conditional compilation and logging call visibility.

## Dependencies and Integration Points

It depends on kernel printf annotations and forward visibility of `struct us_data` from including translation units. It is included by usb-storage core and vendor transports to share a consistent debug interface.

## Risks and Test Signals

Risks include format-signature drift between declaration and implementation, debug-only expressions hiding side effects when disabled, and missing declarations for modules that call exported debug helpers. Test signals include builds with debug on/off, compiler format warnings on bad debug calls, and no generated code for disabled debug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/ene_ub6250.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/ene_ub6250.c

## Purpose

`ene_ub6250.c` is a usb-storage subdriver for ENE UB6250 card readers. It supports SD/MMC and MemoryStick media by loading device-side firmware snippets, emulating selected SCSI disk commands, and maintaining MemoryStick logical-to-physical block maps.

## Important APIs, Types, and Functions

`struct ene_ub6250_info` is the main per-device state, containing a bounce buffer, SD/MS/SM status bytes, SD geometry fields, MemoryStick map/control fields, firmware pattern state, last block count, sense status, and resume flags. `ene_load_bincode()` loads one of six firmware files and sends it to the device using a bulk-only command wrapper. `ene_send_scsi_cmd()` sends CBWs, optional data phases, and CSWs. Generic SCSI emulation helpers include `do_scsi_request_sense()` and `do_scsi_inquiry()`. SD paths include `ene_sd_init()`, `ene_get_card_status()`, `sd_scsi_read_capacity()`, `sd_scsi_read()`, and `sd_scsi_write()`. MemoryStick paths include `ene_ms_init()`, `ms_card_init()`, logical map allocation/scanning helpers, `ms_scsi_read_capacity()`, `ms_scsi_read()`, and `ms_scsi_write()`. `ene_transport()` routes commands to SD and/or MS handlers, while `ene_ub6250_probe()`, `ene_ub6250_resume()`, and `ene_ub6250_reset_resume()` handle usb-storage integration and PM.

## Control Flow

Probe allocates usb-storage state, creates `ene_ub6250_info` plus a 512-byte bounce buffer, installs the `ene_ub6250` transport, runs `usb_stor_probe2()`, then probes card status. Transport clears SCSI residue, initializes media if status is not ready, and dispatches the command to SD or MS handlers based on readiness bits. SD initialization loads two firmware patterns, executes device commands, parses status/CSD-like data, and computes capacity. SD read/write loads the SD R/W firmware, builds vendor CBWs with block addresses, and transfers the SCSI scatterlist. MS initialization loads MS firmware, distinguishes MS Pro from classic MS, reads boot/system information for classic MS, builds Phy2Log/Log2Phy maps, scans logical block numbers, and allocates write buffers. MS Pro read/write is direct block I/O; classic MS read/write translates logical blocks to physical blocks, allocates replacement blocks, copies pages, and updates maps. Resume/reset-resume zero media status so the next command reinitializes.

## State and Persistence Behavior

Runtime state includes cached firmware pattern (`BIN_FLAG`), media status, SD capacity fields, total block count, MemoryStick maps, write buffers, and the last sense status. Firmware blobs are loaded from the host filesystem on demand but not persisted by the driver. Persistent media changes happen on SD/MS card data blocks and, for classic MS, physical-block mappings and overwrite/management metadata. The driver drops status on resume to force reinitialization but frees only the main bounce buffer in its extra destructor; MemoryStick map/write allocations are managed by MS init/free helpers during reinitialization.

## Dependencies and Integration Points

The file depends on usb-storage bulk-only wrappers, SCSI command definitions, firmware loader APIs, unusual-device tables, and ENE-specific firmware files under `ene-ub6250/`. It integrates with the SCSI disk layer by faking inquiry, request sense, mode sense, capacity, TEST UNIT READY, and READ_10/WRITE_10, while importing USB_STORAGE namespace symbols.

## Risks and Test Signals

Risks include mandatory external firmware availability, many little-endian/unaligned parses from firmware buffers, sparse error propagation where helper status domains are mixed with USB transport constants, potential memory leaks for MS map/write buffers on disconnect, capacity and bounds checks limited to starting block, ambiguous routing when both SD and MS readiness bits are set, and classic MemoryStick remap/power-loss exposure. Test signals include missing-firmware probe/read failures, SD standard versus high-capacity capacity math, MMC and SD card status parsing, MS Pro direct read/write, classic MS boot-block scan and map rebuild, REQUEST_SENSE after illegal commands, resume forcing reinit, and disconnect after classic MS allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/ene_ub6250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/freecom.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/freecom.c

## Purpose

`freecom.c` implements the usb-storage subdriver for Freecom USB/IDE and USB/ATAPI adapters. It wraps SCSI/ATAPI commands in Freecom 64-byte command packets and performs the adapter-specific status and data phases.

## Important APIs, Types, and Functions

Packet layouts include `struct freecom_cb_wrap`, `struct freecom_xfer_wrap`, `struct freecom_ide_out`, `struct freecom_ide_in`, and `struct freecom_status`. `freecom_transport()` is the main transport handler. `freecom_readdata()` and `freecom_writedata()` issue Freecom input/output transfer commands before bulk data movement through `usb_stor_bulk_srb()`. `init_freecom()` performs the vendor reset/activation sequence. `usb_stor_freecom_reset()` is a placeholder reset hook returning `FAILED`. `freecom_probe()` installs the Freecom transport and limits max LUN to zero.

## Control Flow

Probe initializes usb-storage with the Freecom unusual-device table, sets transport name and reset hooks, then completes normal usb-storage setup. For each SCSI command, `freecom_transport()` sends a 64-byte ATAPI packet, reads a 4-byte status packet, loops with status-only packets while the adapter reports busy, checks failure/status bits, determines the data length, and performs an optional data-in or data-out phase based on SCSI direction. After data transfer it reads final status and validates status/reason fields.

## State and Persistence Behavior

The driver stores no private per-device state. It reuses `us->iobuf` for command/status wrappers. Persistent effects are limited to commands sent to the attached IDE/ATAPI device and the adapter reset sequence in `init_freecom()`.

## Dependencies and Integration Points

It depends on usb-storage core, unusual Freecom IDs, SCSI/ATAPI command buffers, bulk transfer helpers, and Freecom's packet protocol. It integrates with the SCSI layer as a custom transport and with the generic usb-storage reset/suspend/disconnect framework through `struct usb_driver`.

## Risks and Test Signals

Risks include no real transport reset support, long busy loops relying on device status without a host-side timeout beyond USB transfers, data length truncation for selected commands, incomplete write-direction status validation, and debug hexdump code using static shared storage. Test signals include initialization control-message sequence, INQUIRY/REQUEST_SENSE/MODE_SENSE length handling, long-running ATAPI commands that require repeated status packets, read and write data phases, failed status bit mapping to transport failed, and reset path behavior under SCSI error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/freecom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/initializers.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/initializers.c

## Purpose

`initializers.c` contains special one-off initialization hooks for unusual USB Mass Storage devices that need vendor commands before normal transport use.

## Important APIs, Types, and Functions

`usb_stor_euscsi_init()` sends a vendor control request to put Shuttle/SCM USB-SCSI bridge devices into multi-target mode. `usb_stor_ucr61s2b_init()` sends a custom bulk CBW-like packet containing a PCChips activation string and reads a CSW to activate all slots on the UCR-61S2B flash reader. `usb_stor_huawei_e220_init()` sends a standard device `SET_FEATURE` request to switch Huawei E220 devices into multi-port mode.

## Control Flow

These functions are called through unusual-device table init hooks during usb-storage setup. Each sends its device-specific command sequence and logs the result. The eUSCSI and Huawei helpers return success regardless of control request status, while the UCR helper returns `-EIO` on failed bulk command or status transfer.

## State and Persistence Behavior

No host-side state is stored. The functions change device firmware mode for the current attachment, such as multi-target, multi-slot, or multi-port behavior. That state normally lasts until reset or unplug.

## Dependencies and Integration Points

The file depends on usb-storage control and bulk transfer helpers, bulk-only wrapper structs, unusual-device init-function wiring, and `debug.h` logging. It integrates before normal SCSI scanning so the device presents the intended targets or interfaces.

## Risks and Test Signals

Risks include ignored failures in two initializers, hard-coded magic request values and strings, fixed timeouts, and reuse of `us->iobuf` for CBW/CSW overlays. Test signals include devices switching to the expected mode before scan, UCR slot visibility, Huawei interface mode change, eUSCSI target discovery, and failure injection for control/bulk transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/initializers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/initializers.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/initializers.h

## Purpose

`initializers.h` declares special USB Mass Storage initializer hooks used by unusual-device entries.

## Important APIs, Types, and Functions

The header declares `usb_stor_euscsi_init()`, `usb_stor_ucr61s2b_init()`, and `usb_stor_huawei_e220_init()`, each taking `struct us_data *` and returning an integer status.

## Control Flow

The header has no executable flow. It provides prototypes so unusual-device tables and usb-storage setup code can call the initializer implementations during probe.

## State and Persistence Behavior

No state is defined here. The declared functions may change device firmware mode at runtime, but the header stores nothing.

## Dependencies and Integration Points

It includes `usb.h` and `transport.h` for `struct us_data` and transfer-related declarations. It is the contract between unusual-device metadata and the initializer implementation file.

## Risks and Test Signals

Risks include prototype drift from `initializers.c`, unnecessary header dependencies causing rebuild coupling, and missing declarations when new unusual initializers are added. Test signals are compile coverage of unusual tables, successful linking of the initializer symbols, and probe-time invocation for devices that reference these hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/initializers.h -->
