# Research: subset-b-001066

Work item `subset-b-001066` covers Bluetooth transport and vendor support files under `sources/distributed-fs/ceph-client/drivers/bluetooth/`. Each section is source-tree aligned and wrapped for reconciliation into the mapped per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btrtl.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btrtl.c

## Purpose

`btrtl.c` is the Realtek Bluetooth support library used by transport drivers, especially `btusb` and HCI UART integrations. It identifies Realtek controller generations, loads matching firmware and optional config blobs, parses Realtek EPATCH formats, downloads firmware over vendor HCI commands, exposes UART config extraction, and installs Realtek-specific HCI quirks and devcoredump metadata.

## Important APIs, Types, and Functions

- `struct id_table` is the chip database. Match fields combine LMP subversion, HCI revision/version, bus type, and optional chip type with firmware/config names and capability flags such as `has_rom_version` and `has_msft_ext`.
- `struct btrtl_device_info` is the runtime firmware context. It owns selected `ic_info`, ROM version, firmware/config buffers, project ID, security key ID, and the ordered patch subsection list for EPATCH v2.
- `btrtl_initialize()` is the main discovery and firmware load entry point. It reads Realtek vendor registers, HCI local version, optional chip type and ROM version, matches `ic_id_table`, handles a "drop firmware" retry path, loads firmware/config files, and sets Microsoft vendor opcode support.
- `btrtl_download_firmware()` chooses the legacy RTL8723A download path or EPATCH path, then registers devcoredump support.
- `rtlbt_parse_firmware()` parses EPATCH v1 and dispatches v2 to `rtlbt_parse_firmware_v2()`. It validates signatures, parses the extension trailer for project ID, verifies project-to-LMP compatibility, selects the ROM-specific patch, and appends firmware version bytes.
- `rtlbt_parse_firmware_v2()`, `btrtl_parse_section()`, and `btrtl_insert_ordered_subsec()` parse prioritized patch/security/dummy subsections filtered by ECO and key ID.
- `rtl_download_firmware()` fragments payloads into `RTL_FRAG_LEN` 252-byte vendor command chunks using opcode `0xfc20`, marks the final fragment with bit `0x80`, and logs the post-download version.
- `btrtl_get_uart_settings()` parses Realtek config entries, especially offset `0x0c`, to return encoded device baudrate, converted controller baudrate, and flow-control state.
- `btrtl_set_quirks()`, `btrtl_setup_realtek()`, `btrtl_shutdown_realtek()`, and `btrtl_set_driver_name()` are exported helpers used by transport drivers.

## Control Flow

Initialization starts with vendor register `RTL_CHIP_SUBVER` and sometimes `RTL_CHIP_REV`; otherwise it reads `HCI_OP_READ_LOCAL_VERSION`. Some LMP IDs require an extra chip-type vendor command. The resulting identity is matched against `ic_id_table`. If no table entry is found on the first pass, the driver sends vendor command `0xfc66`, waits 200 ms, and retries version detection, allowing controllers in an odd initial firmware state to expose their normal identity.

For recognized chips, the helper reads ROM version if required, reads `RTL_SEC_PROJ` for `key_id`, loads firmware, and conditionally loads a config blob. Config files may be mandatory for UART chips, while USB chips often operate without one. `btrtl_download_firmware()` then chooses a setup routine by LMP family. RTL8723A expects a raw firmware file. Newer chips expect EPATCH data that is parsed, optionally concatenated with config, and sent in HCI vendor fragments.

## State and Persistence

State is transient and bound to `struct btrtl_device_info`; firmware/config buffers are copied from Linux firmware files and freed by `btrtl_free()`. The helper stores controller and firmware version strings in the transport-private `struct btrealtek_data` devcoredump area. Persistent behavior is entirely external: firmware files under `rtl_bt/` and optional config files determine runtime programming. No source-local persistent files or NVRAM writes are performed here.

## Dependencies and Integration Points

The file depends on the Bluetooth HCI core (`__hci_cmd_sync`, `hci_recv`, quirks, Microsoft opcode hooks, devcoredump), Linux firmware loading, unaligned access helpers, and `btrtl.h` wire-format declarations. Transport drivers call into it after their HCI device exists but before normal operation. `btusb.c` uses it for Realtek USB setup, shutdown, reset/coredump naming, WBS flags, Microsoft extension address filtering, and ALT6 mSBC behavior.

## Risks

Firmware parsing is security-sensitive because controller firmware blobs drive lengths, offsets, subsection counts, and pointer movement. The implementation has several size checks, but risks remain around malformed EPATCH v2 section accounting, integer/length mismatches, and trusting firmware-internal subsection pointers until copied. The `drop_fw` retry path sends a raw HCI command through `hdev->send` before normal setup, so transport readiness matters. Config handling skips config load when `key_id` is nonzero; regressions there can break UART baudrate extraction. Adding table entries is also risky because incorrect LMP/HCI/bus matching can load incompatible firmware.

## Test Signals

Useful signals include successful firmware request logs, `rom_version` and firmware version logs after download, absence of `EPATCH signature`, project mismatch, mandatory config, or fragment download errors, and working `HCI_OP_READ_LOCAL_VERSION` after download. Tests should cover known chip table matches, fallback firmware names such as `_v2.bin`, missing optional versus mandatory config, malformed EPATCH v1/v2 files, UART config offset parsing, and Realtek USB probe through `btusb_setup_realtek()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btrtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btrtl.h -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btrtl.h

## Purpose

`btrtl.h` is the public interface and shared wire-format header for Realtek Bluetooth support. It provides firmware/config structure definitions, Realtek logging wrappers, Realtek private HCI data, flag helpers, and exported function declarations or disabled stubs depending on `CONFIG_BT_RTL`.

## Important APIs, Types, and Functions

- `RTL_FRAG_LEN` defines the 252-byte payload fragment size used by Realtek firmware download commands.
- Packed structures such as `rtl_download_cmd`, `rtl_download_response`, `rtl_rom_version_evt`, `rtl_epatch_header`, `rtl_epatch_header_v2`, `rtl_vendor_config`, and subsection headers describe controller command responses and firmware/config file formats.
- `struct rtl_subsection` and `struct rtl_iovec` support EPATCH v2 parsing in `btrtl.c`.
- `struct btrealtek_data` is the HCI private area used by transports that allocate Realtek private data. It stores a bitmap of Realtek flags and devcoredump metadata.
- Flag helpers `btrealtek_set_flag()`, `btrealtek_get_flag()`, and `btrealtek_test_flag()` wrap `hci_get_priv()` access.
- Public helpers include `btrtl_initialize()`, `btrtl_free()`, `btrtl_download_firmware()`, `btrtl_set_quirks()`, `btrtl_setup_realtek()`, `btrtl_shutdown_realtek()`, `btrtl_get_uart_settings()`, and `btrtl_set_driver_name()`.

## Control Flow

There is no runtime control flow beyond macros and inline stubs. Compile-time flow is important: when `CONFIG_BT_RTL` is enabled, transports link against the real helper functions. When disabled, stubs return `-EOPNOTSUPP` or `-ENOENT` and do nothing for cleanup, quirks, or driver naming.

## State and Persistence

The header defines state layout but does not allocate or persist anything itself. `struct btrealtek_data` is stored as HCI private data by transport drivers, and `struct btrtl_device_info` remains opaque to callers.

## Dependencies and Integration Points

The header assumes Bluetooth HCI core types (`struct hci_dev`, private data, quirks), kernel list/bitmap support, and packed little-endian kernel integer types. It is consumed by `btrtl.c`, `btusb.c`, and UART drivers needing Realtek firmware and config support.

## Risks

The flag macros assume the HCI private area is a valid `struct btrealtek_data`; using them on an HCI device allocated without the Realtek private size will corrupt memory or crash. Packed firmware structure definitions are ABI-like, so field changes can break firmware parsing. Stub behavior is also externally visible: callers must treat `-EOPNOTSUPP` as feature absence, not a fatal transport failure unless Realtek support is mandatory.

## Test Signals

Build coverage should include both `CONFIG_BT_RTL=y/m` and disabled configurations. Runtime tests should confirm Realtek transports allocate enough private data before using flag helpers, and disabled builds should still compile callers that include the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btrtl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btsdio.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btsdio.c

## Purpose

`btsdio.c` is a generic Bluetooth SDIO transport driver for class A and class B Bluetooth SDIO functions. It binds SDIO functions, registers an HCI device with bus type `HCI_SDIO`, sends HCI frames through SDIO write registers, receives interrupt-driven frames from SDIO read registers, and handles open/close/flush lifecycle.

## Important APIs, Types, and Functions

- `btsdio_table` matches `SDIO_CLASS_BT_A` and `SDIO_CLASS_BT_B`.
- `struct btsdio_data` holds the `hci_dev`, `sdio_func`, deferred TX work item, and TX queue.
- Register constants (`REG_RDAT`, `REG_TDAT`, `REG_PC_RRT`, `REG_PC_WRT`, `REG_INTRD`, `REG_EN_INTRD`, `REG_MD_SET`) describe the simple SDIO data/control interface.
- `btsdio_send_frame()` validates outgoing packet types, updates HCI stats, queues SKBs, and schedules work.
- `btsdio_work()` drains the TX queue under `sdio_claim_host()`.
- `btsdio_tx_packet()` prepends the 4-byte Type-A SDIO header and writes to `REG_TDAT`.
- `btsdio_interrupt()` reads interrupt status, clears receive interrupt, and calls `btsdio_rx_packet()`.
- `btsdio_rx_packet()` reads the 4-byte header, validates length and HCI packet type, reads payload, and forwards frames to `hci_recv_frame()`.
- `btsdio_probe()` and `btsdio_remove()` allocate/register and unregister/free the HCI device.

## Control Flow

Probe ignores certain non-removable Broadcom SDIO Bluetooth functions because those boards use UART for Bluetooth. Otherwise it allocates driver data, initializes TX queue/work, creates an HCI device, installs open/close/flush/send callbacks, sets a reset-on-close quirk for one vendor/device pair, registers with HCI core, and stores SDIO driver data.

Open claims the SDIO host, enables the function, claims the IRQ, optionally sets Type-B mode, and enables receive interrupts. Transmit path queues HCI frames and a workqueue serially writes Type-A framed packets. Receive path is IRQ driven: the interrupt handler clears interrupt state, reads and validates one packet, and requests read retry on errors. Close disables interrupts, releases IRQ, disables the function, and releases the SDIO host.

## State and Persistence

Runtime state consists of TX queue contents, the work item, SDIO function pointer, and HCI stats. There is no firmware loading or persistent configuration. SDIO retry control registers provide transient device-side state for failed reads/writes.

## Dependencies and Integration Points

The file integrates Linux MMC/SDIO APIs, Bluetooth HCI core, sk_buff queues, and module SDIO registration. It is a transport-only driver; vendor-specific firmware setup is not implemented here.

## Risks

RX length accepts up to `65543`, allocating `len - 4`; malformed devices can cause large allocations or repeated retry loops. `btsdio_tx_packet()` pushes a header into the SKB and pulls it back only on write failure, so callers must supply sufficient headroom. The IRQ handler processes only the indicated receive event per interrupt and relies on device retry registers for recovery. Work cancellation during remove is covered, but close does not explicitly cancel TX work before disabling the function.

## Test Signals

Signals include successful SDIO probe/registration, IRQ claim, frame TX/RX stat increments, no retry storms on malformed RX, and correct ignore behavior for non-removable Broadcom IDs. Functional tests should exercise Type-A and Type-B classes, invalid HCI packet types, SDIO write failures, remove during queued TX, and open/close cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btsdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btusb.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/btusb.c

## Purpose

`btusb.c` is the generic Bluetooth USB HCI transport driver plus vendor integration hub for Broadcom, CSR, Intel, Realtek, MediaTek, Qualcomm/Atheros, Marvell, and other USB Bluetooth controllers. It binds USB interfaces, registers an HCI device, manages interrupt/bulk/isochronous/diagnostic URBs, implements suspend/resume and autosuspend behavior, performs selected vendor firmware setup, handles controller reset and coredump flows, and exposes HCI driver-specific commands for USB isochronous alternate settings.

## Important APIs, Types, and Functions

- `btusb_table` and `quirks_table` map generic class devices and vendor/product IDs to `BTUSB_*` driver flags.
- `struct btusb_data` is the central runtime object. It tracks USB interfaces, endpoint descriptors, anchors for RX/TX/control/deferred URBs, TX/RX locks, partial event/ACL/SCO SKBs, work items, vendor callback hooks, OOB wake IRQ, reset GPIO, isochronous state, debug poll-sync state, and QCA dump metadata.
- Core lifecycle callbacks are `btusb_probe()`, `btusb_disconnect()`, `btusb_open()`, `btusb_close()`, `btusb_flush()`, `btusb_suspend()`, and `btusb_resume()`.
- RX functions `btusb_recv_intr()`, `btusb_recv_bulk()`, and `btusb_recv_isoc()` reassemble HCI event, ACL, and SCO frames from USB buffers. Completion callbacks resubmit URBs while corresponding running flags are set.
- TX helpers `alloc_ctrl_urb()`, `alloc_bulk_urb()`, `alloc_isoc_urb()`, `submit_tx_urb()`, `submit_or_queue_tx_urb()`, and `btusb_send_frame()` route HCI command, ACL, SCO, and ISO packets to the correct USB endpoint.
- `btusb_work()`, `btusb_switch_alt_setting()`, and `__set_isoc_interface()` select SCO/WBS USB alternate settings based on connection count, air mode, endpoint availability, and vendor flags.
- Vendor setup hooks include `btusb_setup_csr()`, `btusb_setup_realtek()`, `btusb_mtk_setup()`, `btusb_setup_qca()`, Broadcom patchram callbacks, Intel `btintel_configure_setup()`, and address setters for Marvell/Atheros/WCN6855.
- Coredump and reset paths include Realtek devcoredump allocation, QCA ramdump packet collection, Intel ACPI/GPIO reset, QCA reset, MediaTek subsystem reset, and generic `usb_queue_reset_device()`.
- `force_poll_sync` debugfs and `btusb_hci_drv` commands support poll-synchronized ACL delivery and runtime altsetting inspection/switching.

## Control Flow

Probe begins by filtering interface numbers and applying quirk-table matches for generic IDs. It skips ignored devices and old ATH3012 devices that should be handled by the older firmware loader. It allocates `btusb_data`, discovers common endpoints, sets the command request type, initializes work items, anchors, queues, and locks, then allocates an HCI device with optional vendor-private data. Based on `driver_info`, it installs callbacks, quirks, setup/shutdown/reset hooks, receive overrides, firmware setup paths, wake handling, isochronous/diagnostic companion interfaces, and debugfs. Finally it registers the HCI device and stores USB interface data.

Open takes a runtime PM reference, optionally runs `setup_on_usb` before HCI URBs, enables remote wake, submits interrupt and bulk RX URBs, and starts diagnostic RX when present. RX completion callbacks parse data, update stats, resubmit URBs, and cancel HCI command sync on serious submission errors. TX callbacks update byte/error stats and free SKBs. While suspending, outgoing URBs are anchored on `deferred` and replayed on resume.

SCO/WBS control is driven by HCI notify events. `btusb_work()` runtime-resumes the isochronous interface, chooses altsetting 1/3/6 for transparent WBS or altsetting based on SCO count for CVSD, kills stale isochronous URBs on changes, clears partial SCO reassembly state, and starts two isochronous RX URBs. With no SCO connections it returns altsetting 0 and releases the runtime PM reference.

Suspend blocks autosuspend while connections or discovery are active, marks `BTUSB_SUSPENDING`, stops traffic, kills TX URBs, enables OOB wake if configured, and applies Realtek remote-wakeup/reset-resume policy. Resume restarts interrupt/bulk/isoc URBs, calls vendor resume, replays deferred TX, clears suspending, and schedules SCO work.

## State and Persistence

Most state is in `btusb_data` and HCI private vendor areas. USB anchors are the ownership model for live and deferred URBs. Partial HCI reassembly is stored in `evt_skb`, `acl_skb`, and `sco_skb` under `rxlock`. Persistent inputs are external firmware files for vendor setup and device tree or DMI data for wake/reset behavior. The driver writes no persistent files, but it can change controller state through firmware download, BDADDR vendor commands, and reset/shutdown commands.

## Dependencies and Integration Points

The file sits between Linux USB core and Bluetooth HCI core. It depends on `btintel`, `btbcm`, `btrtl`, and `btmtk` helpers, Linux firmware loading indirectly through vendor helpers, GPIO/regulator-like reset lines, PM runtime, OF/DMI matching, debugfs, and devcoredump. It exposes standard USB driver registration and HCI transport callbacks and also integrates HCI driver-specific command handlers for user/kernel consumers that query or switch altsettings.

## Risks

The highest-risk areas are concurrency and lifecycle edges: URB resubmission during close/suspend/disconnect, deferred TX replay under `txlock`, multiple claimed USB interfaces, and vendor reset paths that intentionally disconnect/replug devices. RX reassembly must reject malformed sizes without leaking or desynchronizing partial SKBs. Vendor setup is broad and table-driven; incorrect flags can route devices to incompatible firmware loaders or quirks. QCA memdump handling consumes ACL/event packets and disables autosuspend during dumps, so sequence handling and cleanup must be robust. The debugfs `force_poll_sync` control only works while down; changing this rule could reorder ACL/event delivery.

## Test Signals

Signals include successful HCI registration for class and vendor devices, endpoint discovery failures for malformed descriptors, continuous interrupt/bulk URB resubmission, correct HCI stats, clean open/close/suspend/resume cycles, and no URB leaks on disconnect. Vendor-specific tests should validate CSR fake detection, Realtek firmware setup and devcoredumps, QCA rampatch/NVM names and ramdump sequences, MediaTek ISO interface claim/release, Intel bootloader command routing, Broadcom diagnostics, OOB wake IRQ behavior, and HCI driver altsetting commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/dtl1_cs.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/dtl1_cs.c

## Purpose

`dtl1_cs.c` is a PCMCIA driver for Nokia Connectivity Card DTL-1/DTL-4 and compatible Socket cards. It exposes a PC Card UART-like device as an HCI transport, using a Nokia-specific 4-byte header around HCI frames and direct I/O port access for transmit, receive, and interrupt handling.

## Important APIs, Types, and Functions

- `struct dtl1_info` stores the PCMCIA device, HCI device, spinlock, Nokia flow mask, ring indicator latch, TX queue/state bits, and RX reassembly state.
- `struct nsh` is the Nokia Specific Header: packet type, zero byte, and 16-bit payload length.
- TX state bits `XMIT_SENDING`, `XMIT_WAKEUP`, and `XMIT_WAITING` serialize FIFO writes and controller flow control.
- RX states `RECV_WAIT_NSH` and `RECV_WAIT_DATA` drive byte-by-byte packet reassembly.
- `dtl1_write()` fills the UART TX FIFO when `UART_LSR_THRE` is set.
- `dtl1_write_wakeup()` drains queued frames while respecting waiting/sending state and PCMCIA presence.
- `dtl1_receive()` reads UART bytes, reconstructs NSH-framed packets, handles Nokia control packets, forwards HCI frames, and drops unknown packet types.
- `dtl1_interrupt()` handles UART receive, transmitter-ready, line-status, and ring-indicator changes under the spinlock.
- `dtl1_open()`, `dtl1_close()`, `dtl1_probe()`, `dtl1_config()`, and `dtl1_detach()` manage PCMCIA and HCI lifecycle.

## Control Flow

Probe allocates `dtl1_info`, stores it in `link->priv`, sets PCMCIA config flags, and calls `dtl1_config()`. Configuration requests an 8-byte I/O window, IRQ, and enables the card, then `dtl1_open()` initializes queues/state, allocates the HCI device, configures UART registers, enables receive/transmit interrupts, waits two seconds before first traffic, and registers the HCI device.

Outgoing HCI command/ACL/SCO frames are wrapped in NSH type `0x81`, `0x82`, or `0x83`, padded to even length if needed, queued, and pushed into the UART FIFO by `dtl1_write_wakeup()`. Incoming NSH type `0x80` is control data that updates `flowmask`; types `0x82` to `0x84` are converted to normal HCI packet types and passed to HCI core.

## State and Persistence

The driver maintains volatile TX/RX state in memory and device UART registers. The Nokia flow mask and ring indicator latch affect when queued data resumes. There is no firmware loading, persistent storage, or sysfs/debugfs configuration.

## Dependencies and Integration Points

It depends on PCMCIA card services, legacy UART register definitions, direct port I/O, sk_buff queues, and Bluetooth HCI core. It registers as `dtl1_cs` using product ID tuples.

## Risks

This is interrupt-context, direct-I/O code. Risks include malformed NSH lengths causing oversized packet buildup within `HCI_MAX_FRAME_SIZE`, FIFO partial writes requiring correct SKB pull/requeue handling, races between detach and interrupt, and legacy flow-control behavior via `flowmask` and RI that is hard to test on modern systems. `dtl1_confcheck()` has a suspicious condition involving resource 1 end/size that should be treated carefully if refactored.

## Test Signals

Signals include PCMCIA tuple match, successful I/O and IRQ request, HCI registration after the 2-second delay, TX state transitions out of `XMIT_WAITING`, RX of NSH control and HCI packets, and clean unregister/disable on detach. Hardware or emulated UART tests should exercise odd-length padding, partial FIFO writes, ring-indicator wakeups, shared IRQ returning `IRQ_NONE`, and card removal during queued TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/dtl1_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_ag6xx.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_ag6xx.c

## Purpose

`hci_ag6xx.c` implements the HCI UART protocol support and setup sequence for Intel AG6xx/iBT 2.1 devices. It provides H4-style packet framing, firmware/BD data application, Intel manufacturing-mode setup, memory patch writes, and HCI UART protocol registration.

## Important APIs, Types, and Functions

- `struct ag6xx_data` holds the RX reassembly SKB and TX queue.
- `struct pbn_entry` describes Intel PBN patch entries: target address, payload length, and payload bytes.
- `ag6xx_open()`, `ag6xx_close()`, `ag6xx_flush()`, `ag6xx_enqueue()`, and `ag6xx_dequeue()` provide HCI UART queue lifecycle and prepend H4 packet type on transmit.
- `ag6xx_recv()` uses `h4_recv_buf()` with ACL/SCO/event packet descriptors.
- `intel_mem_write()` sends vendor opcode `0xfc8e` memory writes in chunks up to 247 bytes.
- `ag6xx_setup()` enters manufacturing mode, reads Intel version, validates AG6xx identity, applies optional `.bddata`, applies `.pbn` patch entries, exits manufacturing mode with reset, sets vendor event mask, and checks BDADDR.
- `ag6xx_init()` and `ag6xx_deinit()` register/unregister `HCI_UART_AG6XX`.

## Control Flow

Opening allocates private data and initializes the TX queue. Setup assigns Intel diagnostic and BDADDR callbacks, enters manufacturing mode, reads version data, and rejects unsupported hardware platform/variant. It first tries to request a board-data file named from hardware platform and variant; failure is nonfatal and patching continues. If the controller already reports a firmware patch number, setup exits manufacturing mode without applying patch firmware. Otherwise it requests the PBN patch file named from hardware and firmware version fields, iterates entries until address `0xffffffff`, writes each patch to controller memory, and exits manufacturing mode with a reset and patched flag.

## State and Persistence

State is per-UART instance: queued TX SKBs and current RX reassembly SKB. Firmware and BD data are loaded from external firmware files but not persisted by this driver. Controller state changes happen through manufacturing mode commands and memory writes.

## Dependencies and Integration Points

The file integrates with `hci_uart`, H4 receive helpers, Intel Bluetooth helper functions in `btintel.h`, Linux firmware loading, and HCI command sync APIs. It registers a protocol rather than a platform/serdev driver.

## Risks

Patch parsing trusts PBN entry lengths after a bounds check that rejects entries whose end reaches or passes the firmware end; this edge condition must remain exact to avoid out-of-bounds reads or rejecting valid terminators. `intel_mem_write()` uses pointer arithmetic on `const void *data`, a GNU C extension accepted by the kernel but sensitive to style changes. Returning early after `btintel_enter_mfg()` failures can leave manufacturing-mode cleanup to the caller/controller reset path. Missing BD data is tolerated, while missing patch firmware is tolerated only by completing without patching, so bring-up failures may appear later.

## Test Signals

Signals include version logs, unsupported platform/variant rejection, successful `.bddata` command, PBN entry progress logs, `Patching complete`, manufacturing-mode exit, vendor event mask setup, and BDADDR checks. Tests should cover already-patched devices, missing optional BD data, missing patch file, malformed PBN lengths, memory write fragmentation boundaries, and UART RX frame reassembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_ag6xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_aml.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_aml.c

## Purpose

`hci_aml.c` is the Amlogic Bluetooth HCI UART/serdev driver. It controls platform power resources, downloads ICCM/DCCM firmware over Amlogic TCI vendor commands, configures RF and baudrate, starts the controller, handles BDADDR operations, and registers both an HCI UART protocol and a serdev device driver for Amlogic device-tree compatible controllers.

## Important APIs, Types, and Functions

- `struct aml_serdev` combines `struct hci_uart`, device resources, enable GPIO, regulator, LPO clock, match data, and firmware name.
- `struct aml_data` stores per-protocol RX SKB and TX queue.
- `struct aml_device_data` provides ICCM/DCCM offsets and coexistence RF behavior from OF match data.
- `aml_send_tci_cmd()` is the central command helper for private TCI read/write/baud/reset/download opcodes.
- Firmware helpers `aml_download_firmware()`, `aml_send_firmware()`, and `aml_send_firmware_segment()` load the named firmware and write ICCM/DCCM sections in 248-byte operations, enforcing a 512 KiB max.
- Setup helpers include `aml_power_on()`, `aml_power_off()`, `aml_set_baudrate()`, `aml_config_rf()`, `aml_start_chip()`, `aml_dump_fw_version()`, `aml_send_reset()`, and `aml_check_bdaddr()`.
- HCI UART callbacks `aml_open()`, `aml_close()`, `aml_setup()`, `aml_recv()`, `aml_enqueue()`, and `aml_dequeue()` implement protocol lifecycle and H4 framing.
- `aml_serdev_probe()`, `aml_serdev_remove()`, and `aml_serdev_shutdown()` bind serdev devices and register/unregister the HCI UART device.

## Control Flow

Serdev probe allocates `aml_serdev`, stores it as serdev driver data, registers an HCI UART device with `aml_hci_proto`, then assigns match data. Protocol open parses device tree resources, requires UART flow control, allocates protocol data, and initializes the TX queue. Setup powers the chip, changes controller and host baudrate to `oper_speed`, downloads firmware, configures RF based on coexistence, starts the chip via memory transaction enable and reset bits, waits for startup, logs firmware version, sends HCI reset, and marks the default Amlogic BDADDR invalid when detected.

TX queues SKBs and prepends the H4 packet type when dequeued. RX uses `h4_recv_buf()` for ACL, SCO, event, and ISO packets. Close purges queues, frees partial RX, releases private data, and powers off the device. Shutdown also powers off platform resources.

## State and Persistence

Runtime state includes platform resource enablement, UART baudrate, TX/RX SKB state, firmware download progress, and controller RAM contents. Firmware name is provided by device property. The driver does not persist settings locally; BDADDR setting is issued through a vendor command if requested by HCI core.

## Dependencies and Integration Points

The driver integrates Linux serdev, device properties/OF match data, GPIO, regulator, clock APIs, firmware loading, HCI UART core, H4 receive helpers, and Bluetooth HCI command sync. Device-tree compatibles include `amlogic,w155s2-bt` and `amlogic,w265s2-bt`.

## Risks

Ordering is critical: power, baudrate, firmware download, RF config, start, reset, and BDADDR validation must remain synchronized with controller expectations. `aml_download_firmware()` assumes firmware layout begins with `struct aml_fw_len` followed by ICCM and DCCM images; malformed firmware could produce invalid offsets/lengths unless size checks are strengthened. `aml_serdev_probe()` assigns `aml_dev_data` after registering the HCI UART device; if registration can trigger open/setup immediately, match data may be observed unset. Power-on error paths do not unwind partially enabled resources in every failure case. TCI response parsing treats missing response payload as success in some helpers because `err` remains zero.

## Test Signals

Signals include successful GPIO/regulator/clock acquisition, flow-control requirement enforcement, firmware size and segment download success, RF single/double antenna writes, firmware version log, HCI reset completion, invalid default BDADDR quirk, and clean power-off on close/remove/shutdown. Tests should cover malformed firmware lengths, missing DT properties, baudrate command failure, partial power-on failure, coexistence match data, and RX/TX H4 framing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_aml.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_ath.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_ath.c

## Purpose

`hci_ath.c` implements the Atheros AR300x HCI UART protocol extension (`HCI_UART_ATH3K`). It is an H4-derived transport with controller sleep/wakeup handling using UART modem-control lines, drops unsupported SCO transmit packets, provides a vendor BDADDR writer, and registers the protocol with HCI UART core.

## Important APIs, Types, and Functions

- `struct ath_struct` stores the owning `hci_uart`, current sleep flag, RX reassembly SKB, TX queue, and work item used for context-switch/wakeup.
- `ath_wakeup_ar3k()` toggles RTS and checks CTS to wake a sleeping controller.
- `ath_hci_uart_work()` verifies wakeup when sleep is enabled, clears `HCI_UART_SENDING`, and calls `hci_uart_tx_wakeup()`.
- `ath_open()`, `ath_close()`, and `ath_flush()` manage private data, flow-control requirement, queue purging, RX SKB cleanup, and work cancellation.
- `ath_vendor_cmd()` sends opcode `0xfc0b` with a tag-write payload; `ath_set_bdaddr()` writes `INDEX_BDADDR`.
- `ath_setup()` installs the HCI BDADDR setter.
- `ath_recv()` uses `h4_recv_buf()` for ACL/SCO/event packets.
- `ath_enqueue()` filters SCO, tracks sleep enable commands (`HCI_OP_ATH_SLEEP`), prepends packet type, queues data, marks sending, and schedules wakeup work.
- `ath_dequeue()` returns queued SKBs to the HCI UART core.

## Control Flow

Open requires UART flow control, allocates private data, initializes the TX queue, stores the back pointer, and initializes work. Setup only installs the BDADDR vendor hook. On transmit, SCO packets are discarded, command packets are inspected for the Atheros sleep vendor opcode to update `cur_sleep`, and all queued packets are prefixed with the H4 type. The worker wakes the controller if sleep mode is active and CTS is low, then clears the sending bit and asks the HCI UART core to transmit.

## State and Persistence

The only driver state is volatile UART protocol state: sleep enabled/disabled, partial RX SKB, queued TX SKBs, and scheduled work. BDADDR writes are sent to the controller through a vendor command; persistence depends on controller behavior and is not managed by the driver.

## Dependencies and Integration Points

The file depends on `hci_uart`, tty modem-control operations, H4 receive helpers, workqueues, sk_buffs, and Bluetooth HCI core. It registers as manufacturer 69 and protocol ID `HCI_UART_ATH3K`.

## Risks

The wakeup sequence assumes tty driver modem-control callbacks are present and meaningful. SCO packets are silently freed, which is intentional for this protocol but can surprise higher-level tests expecting an error. `ath_enqueue()` reads command headers directly and assumes command SKBs are at least header-sized. Work and close ordering must keep `ath` valid until `cancel_work_sync()` completes.

## Test Signals

Signals include open rejection without flow control, successful protocol registration, RTS/CTS wake behavior when sleep is enabled, `HCI_UART_SENDING` clearing, BDADDR vendor command success, SCO drop behavior, and correct H4 RX reassembly. Tests should include sleep command enqueue, CTS low/high cases, close with pending work, and malformed short command SKBs if fuzzing the transport boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_ath.c -->
