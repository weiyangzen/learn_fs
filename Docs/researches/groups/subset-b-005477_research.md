# Research Group: subset-b-005477

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/udc.c

Purpose: implements the ChipIdea USB device controller role for the kernel USB gadget framework. It exposes `usb_ep_ops` and `usb_gadget_ops`, owns endpoint queue-head and transfer-descriptor programming, handles setup packets and transfer completion interrupts, and plugs the gadget role into the ChipIdea role driver model.

Important APIs, types, and functions: hardware helpers program `OP_ENDPT*`, `OP_USB*`, and `OP_PORTSC` registers (`hw_device_state`, `hw_ep_enable`, `hw_ep_prime`, `hw_usb_reset`, `hw_ep_set_halt`). Request submission flows through `ep_queue` to `_ep_queue` and `_hardware_enqueue`, which maps DMA, builds TD lists, handles scatterlist bounce buffering for short-packet-limited controllers, links TDs into the endpoint QH, and primes hardware. Completion flows through `udc_irq`, `isr_tr_complete_handler`, `isr_tr_complete_low`, and `_hardware_dequeue`. Setup handling in `isr_setup_packet_handler` directly services standard requests such as GET_STATUS, SET_ADDRESS, endpoint halt, remote wakeup, test mode, and selected OTG features, delegating other requests to the bound gadget driver. Lifecycle entry points are `ci_hdrc_gadget_init` and `ci_hdrc_gadget_destroy`.

Control flow: initialization checks device capability, allocates DMA pools, creates endpoint objects and QHs, registers the gadget UDC, and installs a role driver. Gadget driver start enables EP0, records `ci->driver`, and connects if VBUS is active. IRQ handling clears active interrupt bits under `ci->lock`, prioritizes reset, handles port-change speed/suspend/resume state, then completes traffic and setup work. Disconnect, bus reset, stop, role switch, suspend, and resume all funnel through endpoint nuking, FIFO flush, interrupt disable, pullup, VBUS, and runtime PM paths.

State and persistence: persistent state is in `struct ci_hdrc` plus per-endpoint `ci_hw_ep` queues, QH DMA blocks, TD nodes, `ci->status`, EP0 direction/address/test-mode flags, speed/suspend/resume state, VBUS state, and OTG FSM fields. No disk persistence exists; state is MMIO, DMA memory, and in-memory kernel objects.

Dependencies and integration points: depends on the USB gadget core, ChipIdea register helpers from `ci.h`/`bits.h`, OTG FSM helpers, DMA pools, runtime PM, pinctrl, USB PHY charger/power notifications, and platform `notify_event` hooks. It is used by gadget function drivers through the UDC core and by ChipIdea role switching through `ci->roles[CI_ROLE_GADGET]`.

Risks: high-risk areas are DMA descriptor lifetime, delayed freeing of TDs still visible to hardware, scatterlist bounce/debounce correctness, EP0 direction and lock transitions, lost setup races, suspend/resume power-lost handling, and behavior on old controller revisions requiring reprime workarounds. Tests should exercise enumeration, standard control requests, bulk/interrupt/isoc transfers, scatter-gather and zero-length writes, disconnect while queued, role switching, runtime/system PM, remote wakeup, and fault injection around stalls, short packets, and DMA mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/udc.h

Purpose: defines the private DMA descriptor and request wrapper contract used by the ChipIdea UDC implementation. It is the narrow interface between generic gadget request objects and the hardware queue-head/transfer-descriptor format programmed by `udc.c`.

Important APIs, types, and constants: `CTRL_PAYLOAD_MAX` fixes EP0 max packet size at 64 bytes. `RX` and `TX` provide internal direction indexes. `struct ci_hw_td` mirrors a hardware transfer descriptor with `next`, `token`, and five page pointers plus status, IOC, active, halted, data-error, transaction-error, byte-count, mult, terminate, and address masks. `struct ci_hw_qh` mirrors a queue head with capability bits (`QH_IOS`, `QH_MAX_PKT`, `QH_ZLT`, `QH_MULT`), current TD pointer, overlay TD, reserved word, and setup packet storage. `struct td_node` wraps a DMA TD in a kernel list node and tracks remaining packed scatterlist room. `struct ci_hw_req` wraps `struct usb_request`, its endpoint queue link, TD list, and optional saved scatter-gather table used when bouncing.

Control flow: the header itself has no active control flow, but its layouts govern `udc.c` allocation, TD chaining, QH priming, setup-packet copying, completion decoding, and cleanup. When `CONFIG_USB_CHIPIDEA_UDC` is enabled it declares `ci_hdrc_gadget_init` and `ci_hdrc_gadget_destroy`; otherwise inline stubs make callers fail cleanly with `-ENXIO` and no-op destruction.

State and persistence: all state is volatile DMA or heap memory allocated by the controller driver. The packed/aligned attributes are part of the ABI to hardware and must remain stable. `ci_hw_req.sgt` preserves the original scatterlist only while a bounced request is in flight.

Dependencies and integration points: includes list infrastructure and relies on Linux USB request/control-request and DMA types from surrounding includes. It is consumed by the ChipIdea UDC implementation and indirectly by the ChipIdea core when registering the gadget role.

Risks: the main risks are layout drift, incorrect endian or alignment assumptions, and stale bit masks causing hardware-visible descriptor corruption. Test signals are mostly indirect: successful gadget enumeration, EP0 setup handling, DMA transfer completion, scatter-gather transfer tests, and build coverage with `CONFIG_USB_CHIPIDEA_UDC=y/m/n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ulpi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ulpi.c

Purpose: provides ChipIdea ULPI viewport access and registration with the Linux ULPI bus when the platform PHY mode is ULPI. It lets generic ULPI PHY code identify and access an external PHY through ChipIdea controller registers.

Important APIs and functions: `ci_ulpi_wait` polls `OP_ULPI_VIEWPORT` bits with a 10 ms timeout. `ci_ulpi_read` wakes the viewport, starts a read transaction for a ULPI address, waits for `ULPI_RUN` to clear, and returns bits 15:8 as data. `ci_ulpi_write` follows the same wake and run sequence with `ULPI_WRITE` and value bits. `ci_ulpi_init` checks `ci->platdata->phy_mode`, configures PORTSC via `hw_phymode_configure`, fills `ci->ulpi_ops`, and calls `ulpi_register_interface`. `ci_ulpi_exit` unregisters the interface, and `ci_ulpi_resume` waits up to 100 ms for `ULPI_SYNC_STATE`.

Control flow: initialization is conditional and returns success without side effects for non-ULPI modes. Read/write operations always wake the viewport before accessing the target register. Resume is a synchronization check rather than a full reinitialization.

State and persistence: persistent driver state is limited to `ci->ulpi`, `ci->ulpi_ops`, and hardware viewport state. No allocation is owned here beyond the registered ULPI interface object. Timeout failures are returned to callers and logged by init.

Dependencies and integration points: uses ChipIdea hardware helpers, `linux/ulpi/interface.h`, platform PHY mode configuration, and the device driver data that maps an ULPI device back to `struct ci_hdrc`. It integrates the ChipIdea controller with external ULPI PHY drivers.

Risks: busy-wait polling can fail on clocks, reset sequencing, or inaccessible viewport state; read/write paths assume `dev_get_drvdata(dev)` is the ChipIdea controller. Test signals include boot/probe with ULPI PHYs, ULPI ID reads, suspend/resume with sync-state recovery, timeout fault injection, and verifying non-ULPI platforms skip registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ulpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/usbmisc_imx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/usbmisc_imx.c

Purpose: implements the i.MX/NXP USB miscellaneous register driver used by ChipIdea i.MX glue code for non-core USB controls. It abstracts SoC-specific over-current polarity, power polarity, wakeup, HSIC, charger detection, pullup disconnect signaling, VBUS comparator, and power-lost recovery behind exported helper functions.

Important APIs, types, and functions: `struct usbmisc_ops` is the SoC operation table, and `struct imx_usbmisc` stores mapped base/blkctl registers, lock, and selected ops. Exported entry points are `imx_usbmisc_init`, `imx_usbmisc_init_post`, `imx_usbmisc_hsic_set_connect`, `imx_usbmisc_charger_detection`, `imx_usbmisc_pullup`, `imx_usbmisc_suspend`, and `imx_usbmisc_resume`. Per-SoC init functions include `usbmisc_imx25_init`, `usbmisc_imx53_init`, `usbmisc_imx6q_init`, `usbmisc_imx6sx_init`, `usbmisc_imx7d_init`, `usbmisc_imx7ulp_init`, and S32G variants. Charger detection on i.MX7-style PHYs runs data-contact, primary, and secondary detection against PHY status bits.

Control flow: platform probe maps register resources, optional block-control registers, selects ops from the OF match table, and stores driver data. Callers invoke exported helpers during host/device setup and PM. Init configures register fields according to `imx_usbmisc_data` board properties. Suspend disables optional VBUS comparator, enables wakeup, and turns HSIC clocks off; resume checks power loss, reinitializes if needed, disables wakeup, restores HSIC clocks, and reenables comparator.

State and persistence: register state persists in SoC MMIO across runtime, and some code detects power loss by comparing reset values. In-memory state is minimal: mapped bases, ops pointer, and spinlock. Charger state is written into `data->usb_phy->chg_state` and `chg_type`.

Dependencies and integration points: depends on platform devices, OF compatible matching, `ci_hdrc_imx.h` data, USB OTG/PHY definitions, and ChipIdea i.MX glue. It exports GPL symbols consumed by the controller glue rather than binding to USB interfaces directly.

Risks: this file is hardware-sensitive. Risks include wrong register offsets per SoC/index, preserving or overriding bootloader polarity incorrectly, wakeup-source mismatch when external ID/VBUS is used, charger-detection timing bugs, power-lost false positives, and missing second resource for i.MX95 wakeup block control. Test signals include DT-compatible probe coverage for each ops table, suspend/resume with wakeup enabled and disabled, HSIC connect/clock sequencing, charger-type detection, over-current and power polarity validation, and role/device pullup disconnect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/usbmisc_imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/class/Kconfig

Purpose: defines the build-time configuration menu for USB device class drivers under `drivers/usb/class`. It lets integrators select CDC ACM modem support, USB printer support, CDC WDM device-management support, and USB Test and Measurement Class support.

Important configuration symbols: `USB_ACM` is a tristate that depends on `TTY` and builds the CDC ACM modem/ISDN adapter driver as `cdc-acm`. `USB_PRINTER` is a tristate for USB printer support and builds `usblp`. `USB_WDM` is a tristate for CDC WMC/WDM management channels and builds `cdc-wdm`. `USB_TMC` is a tristate for USBTMC instruments and builds `usbtmc`.

Control flow: Kconfig has declarative dependency flow only. Menu visibility presents a "USB Device Class drivers" comment and makes each symbol available according to dependencies. The `TTY` dependency prevents enabling `USB_ACM` without the TTY core needed by `cdc-acm.c`.

State and persistence: selected values persist in the kernel `.config` and drive conditional compilation. There is no runtime state.

Dependencies and integration points: consumed by Kbuild in the sibling `Makefile`, by module naming in help text, and by downstream distro or board configurations that choose built-in or module class support.

Risks: missing dependencies can produce link failures or unusable menu choices; overly broad defaults could increase kernel footprint. Test signals include `allmodconfig`, `allyesconfig`, minimal configs with and without `TTY`, and verifying selected symbols produce the expected modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/class/Makefile

Purpose: maps USB class-driver Kconfig symbols to object files in the kernel build.

Important build rules: `obj-$(CONFIG_USB_ACM) += cdc-acm.o`, `obj-$(CONFIG_USB_PRINTER) += usblp.o`, `obj-$(CONFIG_USB_WDM) += cdc-wdm.o`, and `obj-$(CONFIG_USB_TMC) += usbtmc.o`. These rules let the same source build built-in, modular, or not at all according to tristate values.

Control flow: Kbuild evaluates the `obj-*` variables and includes matching object files in the directory build. No runtime code exists.

State and persistence: build state is derived from `.config` and Kbuild outputs. No runtime persistence exists.

Dependencies and integration points: tightly paired with `drivers/usb/class/Kconfig` symbols and module names. It integrates this directory into the broader USB driver build.

Risks and test signals: risks are simple but high impact: wrong symbol names or object names silently omit drivers or break builds. Test with `M=drivers/usb/class` builds for each symbol as module, built-in full kernel builds, and clean configs where symbols are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/cdc-acm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/class/cdc-acm.c

Purpose: implements the USB CDC Abstract Control Model host driver, exposing compatible modems, serial adapters, and selected vendor devices as `/dev/ttyACM*` TTY devices.

Important APIs and functions: global state includes the `acm_minors` IDR and `acm_tty_driver`. Probe (`acm_probe`) parses CDC descriptors, handles quirks, locates control/data interfaces and endpoints, allocates coherent buffers and URBs, creates sysfs attributes, claims the data interface, and registers a TTY device. TTY operations include install/open/close/hangup/write/write_room/throttle/unthrottle/break/ioctl/termios/modem-control and serial info handlers. URB callbacks include `acm_ctrl_irq` for CDC notifications, `acm_read_bulk_callback` for RX, and `acm_write_bulk` for TX. PM hooks are `acm_suspend`, `acm_resume`, and `acm_reset_resume`.

Control flow: module init allocates/registers a TTY driver, then registers the USB driver. On open, `tty_port_open` activates the port, powers the interface, starts the interrupt notification URB unless the always-poll quirk already does so, configures line coding, clears throttle state, and submits read URBs. Writes allocate one of 16 write buffers, copy user data, take an async autosuspend reference, and either anchor during suspend or submit a bulk/interrupt URB. RX callbacks push data into the TTY flip buffer and resubmit unless throttled. Notification callbacks reassemble fragmented CDC notifications, update control-line counters, hang up on DCD drop when not CLOCAL, and wake waiters.

State and persistence: state lives in `struct acm`: TTY port, USB interfaces/device, URBs, coherent buffers, minor, line coding, control line state, async counters, throttle/error flags, delayed work, suspend count, quirks, country-code sysfs data, and delayed write anchor. No persistent storage is used.

Dependencies and integration points: depends on USB core, CDC descriptor parsing, TTY core, line disciplines, IDR, autosuspend, sysfs, and quirk IDs. It intentionally rejects or ignores devices better handled by other drivers.

Risks: device descriptors are often broken, so probe heuristics and quirks are critical. Concurrency risks include disconnect versus open/write/work, suspended delayed writes, notification reassembly sizing, and unsynchronized `ctrlout` noted by a FIXME. Test signals include module load/unload, enumeration of normal and quirked CDC ACM devices, TTY open/close/hangup, termios and modem control ioctls, throttled RX, fragmented serial-state notifications, autosuspend/resume/reset, disconnect while open, and build coverage with optional conflicting drivers enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/cdc-acm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/cdc-acm.h -->
# sources/distributed-fs/ceph-client/drivers/usb/class/cdc-acm.h

Purpose: defines constants and private data structures for the CDC ACM TTY driver.

Important types and constants: `ACM_TTY_MAJOR` is 166, `ACM_TTY_MINORS` is 256, and `ACM_MINOR_INVALID` marks unallocated state. `USB_RT_ACM` defines class interface control request type. `ACM_NW` and `ACM_NR` set write and read URB ring counts to 16. `struct acm_wb` tracks an outgoing buffer, coherent DMA address, length, URB, owning ACM instance, and in-use flag. `struct acm_rb` tracks an incoming buffer, DMA address, index, and owner. `struct acm` is the driver state object shared by probe, TTY operations, URB callbacks, PM, disconnect, sysfs, and ioctl paths.

Control flow: the header has no executable logic, but its fields define the control flow in `cdc-acm.c`: read/write buffer allocation, URB callback ownership, minor lookup, line coding, delayed work, notification reassembly, modem status wait queues, autosuspend-delayed write anchors, and quirk-dependent behavior.

State and persistence: `struct acm` carries all runtime state for one CDC ACM function: device/interface pointers, TTY port, buffers, DMA handles, free-bitmaps, locks, mutexes, flags, counters, control lines, line coding, minor, suspend count, and quirks. State is in memory only and is destroyed after disconnect and final TTY port release.

Dependencies and integration points: the structures depend on USB core URBs and interfaces, TTY port and async counter types, wait queues, delayed work, anchors, DMA addresses, and CDC line-coding definitions from the including C file.

Risks and test signals: header risks are structure lifetime assumptions and fields accessed from different locking domains. Changes require tests for open/close lifetime, write buffer accounting, read URB bitmap handling, notification reassembly, modem-line ioctls, PM delayed writes, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/cdc-acm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/cdc-wdm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/class/cdc-wdm.c

Purpose: implements USB CDC WDM/WMC device-management support. It exposes management channels as `/dev/cdc-wdm*` character devices and can also register a WWAN control port for protocols such as MBIM or QMI when a parent driver registers it as a subdriver.

Important APIs and functions: `struct wdm_device` owns command, response, and interrupt URBs; buffers; locks; flags; wait queue; work items; optional WWAN port; and a power-management callback. File operations are `wdm_open`, `wdm_release`, `wdm_read`, `wdm_write`, `wdm_poll`, `wdm_flush`, `wdm_fsync`, and `wdm_ioctl`. USB callbacks are `wdm_int_callback`, `wdm_in_callback`, and `wdm_out_callback`. Creation is shared by standalone probe and `usb_cdc_wdm_register`, which exports a subdriver registration API.

Control flow: probe parses the CDC DMM descriptor for `wMaxCommand`, validates the interrupt IN endpoint, allocates the device, registers a USB class minor, and optionally creates a WWAN port. Open prevents concurrent legacy char-device and WWAN use, powers the interface, starts the notification URB on first opener, and increments open count. Writes submit `SEND_ENCAPSULATED_COMMAND` control URBs one at a time. Interrupt notifications for `RESPONSE_AVAILABLE` submit a `GET_ENCAPSULATED_RESPONSE` URB; completed responses append to the userspace buffer or forward to WWAN RX. Reads block or poll on `WDM_READ`, copy buffered data, compact remaining bytes, and service outstanding response notifications.

State and persistence: all state is in memory. Important flags include in-use, disconnecting, read-ready, interrupt stall, poll running, responding, suspending, resetting, overflow, and WWAN-in-use. `resp_count` tracks outstanding response notifications. Buffers hold pending user data only until read.

Dependencies and integration points: depends on USB core, CDC parsing, usb class device registration, wait queues, workqueues, autosuspend, sk_buffs, optional WWAN core, and `linux/usb/cdc-wdm.h` ioctl ABI. Parent drivers may call exported registration and then forward disconnect/PM/reset callbacks.

Risks: races around response notification counts, reset/suspend/disconnect while URBs are active, buffer overflow handling, dual exposure via char device and WWAN, and cleanup deferral when file descriptors remain open. Test signals include WDM device enumeration, nonblocking and blocking read/write, `IOCTL_WDM_MAX_COMMAND`, poll/flush/fsync behavior, multiple response notifications, zero-length and overflow responses, WWAN start/stop exclusivity, autosuspend, reset recovery, and disconnect while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/cdc-wdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/usblp.c -->
# sources/distributed-fs/ceph-client/drivers/usb/class/usblp.c

Purpose: implements the USB printer class host driver, exposing USB printers and compatible printer cables as `/dev/usb/lp*` character devices with legacy printer ioctls and IEEE 1284 device ID support.

Important APIs and functions: `struct usblp` stores device/interface pointers, locks, wait queues, anchored URBs, selected printer protocol, endpoints, buffers, status, flags, quirks, and cached device ID. File operations are `usblp_open`, `usblp_release`, `usblp_read`, `usblp_write`, `usblp_poll`, and `usblp_ioctl`. Probe helpers include `usblp_select_alts`, `usblp_set_protocol`, `usblp_cache_device_id_string`, and quirk lookup. URB callbacks are `usblp_bulk_read` and `usblp_bulk_write`. Control helpers issue GET_ID, GET_STATUS, RESET, and HP channel-change requests.

Control flow: probe allocates the device object and buffers, scans alternate settings for printer protocols 1, 2, and 3, applies `proto_bias` and quirks, sets the selected alternate setting, caches the IEEE 1284 ID, registers the USB class minor, and exposes `ieee1284_id` sysfs. Open enforces single opener, gets an autosuspend reference, marks the device used, and starts a read URB for bidirectional protocols. Writes serialize through `wmut`, split user data into 8 KiB URBs, anchor them, wait for completion unless nonblocking, and optionally poll printer status for paper-out behavior. Reads wait for a bidirectional read URB, copy data from the shared read buffer, and resubmit when drained.

State and persistence: runtime state is volatile and protected by `usblp_mutex`, `mut`, `wmut`, and `lock`. It includes presence/open flags, current protocol, bidirectional mode, completion/status fields, no-paper marker, read offset, anchored URBs, cached status buffer, and device ID string. There is no disk persistence; the device ID is refreshed by ioctl and cached in memory/sysfs.

Dependencies and integration points: depends on USB core, USB class minor registration, printer-class descriptors, Linux `lp` ioctl ABI, poll/wait queues, autosuspend, and a device quirk table. User-space integration is via `/dev/usb/lp*`, old and new `P` ioctls, and sysfs `ieee1284_id`.

Risks: printer firmware quirks are central. Risk areas include alternate-setting selection, bidirectional devices that misroute status into print buffers, write completion accounting with anchored URBs, nonblocking close semantics, disconnect while open, status polling under LP_ABORT, and cached device ID length handling. Test signals include protocol selection with `proto_bias`, unidirectional and bidirectional devices, large writes, nonblocking writes and poll, paper-out/status ioctls, soft reset, HP channel ioctl, device ID sysfs/ioctl, suspend/resume, and unplug while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/usblp.c -->
