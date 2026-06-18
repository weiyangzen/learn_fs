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
