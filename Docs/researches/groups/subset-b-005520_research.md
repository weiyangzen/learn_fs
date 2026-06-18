# Research Group subset-b-005520

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusbvga.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusbvga.c

## Purpose
`sisusbvga.c` is the main Linux USB character-device driver for Net2280/SiS315-based USB2VGA dongles. It binds specific USB IDs, verifies the expected bulk endpoints, registers `/dev/sisusbvga%d`, initializes the Net2280/SiS graphics core when possible, and exposes pseudo PCI, I/O port, MMIO, and VRAM spaces to user space through `read`, `write`, `llseek`, and private ioctls.

## Important APIs, Types, and Functions
The private device state is `struct sisusb_usb_data` from `sisusb.h`, containing USB device references, kref lifetime, a global mutex, wait queue, inbound/outbound URBs and buffers, URB status flags, VRAM/MMIO/I/O base metadata, and initialization flags. `struct sisusb_packet` is the packed 10-byte bridge/GFX command format.

USB transport is layered around `sisusb_bulkout_msg`, `sisusb_bulkin_msg`, `sisusb_send_bulk_msg`, and `sisusb_recv_bulk_msg`. These manage synchronous and asynchronous bulk URBs, wait-queue completion, timeout handling, and optional user/kernel buffer copying. Register and memory helpers such as `sisusb_write_memio_byte`, `sisusb_write_memio_word`, `sisusb_write_mem_bulk`, `sisusb_read_mem_bulk`, `sisusb_setidxreg*`, `sisusb_read_pci_config`, and `sisusb_write_pci_config` encode SiS/Net2280 packets and bridge transactions.

Device initialization is split between `sisusb_do_init_gfxdevice`, which programs bridge-side PCI BARs and command bits, and `sisusb_init_gfxcore`, which writes large SiS register tables, detects memory bus width and SDRAM size, enables refresh, and sets a 640x480 mode through `sisusb_set_default_mode`. Character-device entry points are `sisusb_open`, `sisusb_release`, `sisusb_read`, `sisusb_write`, `sisusb_lseek`, `sisusb_ioctl`, and optional `sisusb_compat_ioctl`.

## Control Flow
`sisusb_probe` checks for six required bulk endpoint addresses, allocates private state, registers the USB class minor, allocates one inbound buffer and up to `NUMOBUFS` outbound buffers/URBs, initializes the wait queue, stores interface data, takes a USB-device reference, and tries early graphics initialization if the device is high-speed or faster. `open` revalidates `present` and `ready`, enforces single-open semantics, lazily initializes high-speed devices if early init was deferred, then takes a kref and marks the device open.

I/O dispatch depends on `*ppos`. Offsets in the pseudo I/O range emulate byte/word/dword port reads and writes. Pseudo VRAM and MMIO ranges use bulk memory transfer helpers. Pseudo PCI config offsets require 4-byte access and use PCI config packets. The ioctl path returns version/config metadata or executes indexed-register commands and screen-clear commands.

On release and disconnect, the driver waits for outstanding outbound URBs and kills any still busy. Disconnect deregisters the minor, clears `present` and `ready`, removes interface data, and drops the kref.

## State and Persistence
All persistent runtime state is in `struct sisusb_usb_data`; there is no disk persistence. Important state includes `devinit`, `gfxinit`, `vramsize`, `isopen`, `present`, `ready`, and `flagb0` for bridge register caching. URB state is tracked manually with `SU_URB_BUSY` and `SU_URB_ALLOC`. Device register and VRAM changes persist only in hardware until reset or disconnect.

## Dependencies and Integration Points
The file depends on Linux USB core, kref, mutexes, wait queues, user-copy APIs, and the local `sisusb.h`/`sisusb_struct.h` definitions. It integrates with usbcore through `struct usb_driver` and `struct usb_class_driver`, with user space through the `sisusbvga%d` character node and private ioctls, and with SiS graphics hardware through Net2280 bridge packet endpoints.

## Risks and Edge Cases
The driver presents low-level hardware access directly to user space; malformed offsets and lengths are bounded by pseudo-region checks, but successful callers can still mutate PCI config, MMIO, and VRAM. It serializes file operations with one mutex and allows only one open, reducing internal races but also making long transfers block all other operations. Asynchronous outbound transfer accounting is intentionally relaxed under `SISUSB_DONTSYNC`, so the code relies on explicit wait points before reads and cleanup. Large VRAM writes reuse outbound buffers like a ring and depend on correct byte counts from USB completion. Memory-detection and graphics initialization include several fallback assumptions, especially DDR or failed SDRAM detection defaulting to 8 MB. Disconnect during a blocking operation is mitigated by `present` checks, URB kills, and krefs, but manual URB status flags must stay consistent across all timeout paths.

## Test Signals
Useful validation signals include probing only with the expected endpoint set, checking `/dev/sisusbvga%d` registration and single-open behavior, running `SISUSB_GET_CONFIG_SIZE`, `SISUSB_GET_CONFIG`, and representative `SISUSB_COMMAND` operations, reading and writing aligned and unaligned pseudo I/O/VRAM/MMIO ranges, and unplugging during long writes to verify URB kill and kref cleanup. Hardware tests should confirm high-speed initialization, VRAM clear, frame drawing, and expected logs for RAM configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusbvga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/trancevibrator.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/trancevibrator.c

## Purpose
`trancevibrator.c` is a minimal USB driver for the PlayStation 2 Trance Vibrator. It binds the ASCII Corporation vendor/product ID and exposes one sysfs attribute, `speed`, that sends a vendor control request to set vibration intensity.

## Important APIs, Types, and Functions
The only private state is `struct trancevibrator`, containing `struct usb_device *udev` and the last requested `speed`. `speed_show` reports the cached speed. `speed_store` parses decimal input with `kstrtoint`, clamps it to `[0, 255]`, updates the cached value, and sends `usb_control_msg` on endpoint zero using request `0x01`, `USB_DIR_OUT | USB_TYPE_VENDOR | USB_RECIP_OTHER`, `wValue = speed`, no data phase, and `USB_CTRL_SET_TIMEOUT`. On transfer failure it restores the old cached value.

`tv_probe` allocates state with `kzalloc_obj`, stores the USB device pointer, and attaches it with `usb_set_intfdata`. `tv_disconnect` clears interface data and frees the state. The `usb_driver` uses `dev_groups = tv_groups`, so the sysfs attribute is managed by the driver core.

## Control Flow
On probe, usbcore creates the device attribute group and the driver records interface state. User writes to `/sys/.../speed` synchronously send one vendor control transfer to the device. Reads return the cached speed, not a hardware query. Disconnect simply frees the private object after usbcore has detached the interface.

## State and Persistence
The driver keeps only an in-memory speed cache. The hardware vibration setting is changed by control transfer and may outlive the cached state until device reset or unplug. There is no locking around `speed`; concurrent sysfs writes can race, but the state is a single integer and failures roll back only relative to each writer's local `old` value.

## Dependencies and Integration Points
This file depends on Linux USB core, sysfs device attributes, allocation helpers, and vendor-specific endpoint-zero control transfers. Its integration surface is the USB ID table and the `speed` sysfs file.

## Risks and Edge Cases
The code does not take a reference to `udev`; it relies on interface lifetime during sysfs callbacks. Concurrent writes can reorder cached state and control messages. A failed control transfer restores the previous cached speed even if another writer has already succeeded. There is no suspend/resume handling, so the cached speed is not replayed after power management or reset. The request recipient is `USB_RECIP_OTHER`, which is device-specific and should not be generalized without hardware confirmation.

## Test Signals
Validation should cover sysfs reads/writes for negative, in-range, and greater-than-255 values, control-transfer failure injection to confirm rollback, disconnect while the sysfs attribute is active, and enumeration only for USB ID `0x0b49:0x064f`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/trancevibrator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usb-ljca.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/usb-ljca.c

## Purpose
`usb-ljca.c` is the Intel La Jolla Cove Adapter USB bridge driver. It binds the LJCA USB device, establishes a vendor message protocol over bulk endpoints, enumerates GPIO/I2C/SPI functions exposed by firmware, and creates auxiliary devices for subsystem-specific client drivers.

## Important APIs, Types, and Functions
`struct ljca_adapter` owns the USB interface, bulk pipes, one persistent RX URB, RX/TX buffers, command response buffer pointers, a spinlock for shared packet state, a mutex that serializes command transmission, a completion for command acknowledgements, a client list, a disconnect flag, and a reset sequence ID. The protocol header is `struct ljca_msg` with type, command, flags, length, and counted payload.

Exported APIs in namespace `LJCA` are `ljca_transfer`, `ljca_transfer_noack`, `ljca_register_event_cb`, and `ljca_unregister_event_cb`. They are used by auxiliary client drivers through `struct ljca_client` from `linux/usb/ljca.h`. Core internal functions include `ljca_send`, `ljca_recv`, `ljca_handle_cmd_ack`, `ljca_handle_event`, `ljca_reset_handshake`, `ljca_enumerate_gpio`, `ljca_enumerate_i2c`, `ljca_enumerate_spi`, and `ljca_new_client_device`.

## Control Flow
`ljca_probe` allocates the adapter and TX buffer, initializes locks and completion, finds the first bulk-in and bulk-out endpoints, allocates an RX buffer and URB, submits the RX URB, and then performs client enumeration. RX completion validates message length; ACK messages complete the current command after copying payload into the waiting external buffer, while non-ACK messages are dispatched as events to a matching client callback. `ljca_send` serializes commands with `adap->mutex`, prepares the TX header under spinlock, takes an autosuspend reference, sends a bulk message, optionally waits for ACK completion, clears transient response pointers, and releases runtime PM.

Enumeration first performs a management reset handshake with a monotonically increasing reset ID. It then asks firmware for GPIO, I2C, and SPI descriptors, validates response lengths with `struct_size`, builds platform data, binds ACPI companions where possible, initializes auxiliary devices, and adds them to the client list. Disconnect sets `disconnect`, kills the RX URB, deletes and uninitializes auxiliary devices in reverse order, frees the RX URB, and destroys the mutex. Suspend kills RX; resume resubmits it.

## State and Persistence
State is volatile and centered on the adapter object and auxiliary client list. Command response state (`ex_buf`, `ex_buf_len`, `actual_length`) is valid only while `ljca_send` holds the command mutex. Event callbacks are protected by each client's spinlock. ACPI companion binding persists in device model state for the lifetime of each auxiliary device. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on USB bulk messaging, runtime PM/autosuspend, ACPI enumeration, the Linux auxiliary bus, completions, mutexes, spinlocks, and exported LJCA headers. It integrates with GPIO, I2C, and SPI child drivers by auxiliary device names `ljca-gpio`, `ljca-i2c`, and `ljca-spi`, plus platform data structures describing valid pins, bus capacity, and interrupt pins.

## Risks and Edge Cases
The protocol supports only one in-flight command because a single TX buffer, response pointer pair, and completion are shared. Firmware events are matched only by client type; a comment notes that multiple clients of the same type would need an ID in the firmware message. `ljca_handle_event` calls the registered callback for a matching type; event arrival before callback registration or after unregistration is a key race to reason about. ACK mismatch logs an error but leaves the sender waiting for timeout. Enumeration treats SPI timeout as normal, but GPIO/I2C descriptor failures abort the whole adapter and tear down already-created clients. Suspend kills RX, so command users must tolerate failed or delayed transfers across PM transitions.

## Test Signals
Tests should cover successful reset handshake, GPIO/I2C/SPI descriptor parsing with exact and malformed lengths, auxiliary-device creation and ACPI companion matching, ACK mismatch and timeout behavior, event callback registration/unregistration, disconnect while a command waits, suspend/resume RX URB resubmission, and runtime PM reference balancing during `ljca_transfer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usb-ljca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usb251xb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/usb251xb.c

## Purpose
`usb251xb.c` configures Microchip USB2422/USB251xB/USB251xBi/USB2517 USB 2.0 hub controllers through SMBus/I2C or, in platform mode, by reset/default configuration. It parses devicetree properties into the hub's internal register image, controls reset and power, attaches the hub, and supports suspend/resume by disabling and re-enabling the regulator.

## Important APIs, Types, and Functions
`struct usb251xb` stores device/I2C/regulator/reset resources plus one field per hub configuration register. `struct usb251xb_data` describes per-compatible defaults: product ID, downstream port count, LED support, battery-charging support, and product string. Static data covers `usb2422`, `usb2512b/bi`, `usb2513b/bi`, `usb2514b/bi`, and `usb2517/i`.

Key functions are `usb251xb_get_ofdata`, which parses devicetree into register fields; `usb251xb_get_ports_field`, which converts port-list properties to bitmasks; `usb251xb_reset`, which asserts/deasserts reset while optionally locking the I2C segment; `usb251xb_connect`, which writes the register image in 16-byte SMBus blocks and issues attach; `usb251x_check_gpio_chip`, which rejects unsafe reset GPIO placement on the same I2C segment; and `usb251xb_probe`, which validates configuration, enables `vdd`, registers regulator cleanup, and connects the hub.

## Control Flow
Both I2C and platform probes allocate `struct usb251xb`, set `hub->dev`, and call the common probe. If OF match data is available, `usb251xb_get_ofdata` reads IDs, power mode, over-current settings, TT mode, EOP disable, port switching, power/current limits, language ID, boost values, UTF-16 string descriptors, non-removable/disabled/swapped ports, and skip-config. The common probe checks for an I2C/reset-GPIO deadlock hazard, enables the regulator, and calls `usb251xb_connect`.

In I2C mode, `connect` either writes a minimal attach command when `skip-config` is set, or builds a 256-byte register image and writes it in sixteen SMBus block transactions before attach. In platform-only mode, no register interface exists, so reset is toggled and the hub uses default configuration. Suspend disables `vdd`; resume enables it and reruns `connect`.

## State and Persistence
All configuration is held in memory until written to the hub. The hardware register image is re-applied on resume. The regulator is managed by devm cleanup through `devm_add_action_or_reset`. No filesystem state exists.

## Dependencies and Integration Points
The driver depends on devicetree matching/properties, I2C SMBus block writes, optional reset GPIO, regulator framework, UTF-8 to UTF-16 conversion, and platform-driver fallback. It integrates with board descriptions through compatibles and properties such as `self-powered`, `bus-powered`, `non-removable-ports`, `sp-disabled-ports`, `bp-disabled-ports`, `power-on-time-ms`, `manufacturer`, `product`, `serial`, and `swap-dx-lanes`.

## Risks and Edge Cases
The reset GPIO cannot safely be provided by a GPIO controller on the same I2C segment as the hub, because the driver locks the segment around reset timing; the explicit child-device check prevents that deadlock/config-latch hazard. In platform-only mode, OF configuration fields may be parsed but many cannot be programmed without I2C. String lengths use the original UTF-8 length while data is converted to UTF-16LE, so descriptor length assumptions should be checked against hardware expectations. The SMBus write payload includes a count byte plus 16 data bytes; controller support for that block size is required. Invalid port numbers only warn, leaving the rest of the bitmask active.

## Test Signals
Validation should include OF parsing for every compatible, reset GPIO timing and bus-lock behavior, regulator enable/disable and devm cleanup, `skip-config` attach-only mode, full 256-byte I2C programming, platform-mode default attach, suspend/resume reconfiguration, and failure injection for SMBus write errors at different blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usb251xb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usb3503.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/usb3503.c

## Purpose
`usb3503.c` drives SMSC USB3503/USB3503A/USB3803 USB 2.0 hub controllers. It supports I2C/regmap and platform instantiation, configures reference clock and GPIO control lines, optionally disables ports, and switches the hub between hub, standby, and bypass modes.

## Important APIs, Types, and Functions
`struct usb3503` tracks current mode, regmap, device, optional reference clock, disabled-port mask, optional GPIOs (`bypass`, `intn`, `reset`, `connect`), and whether a secondary reference clock is used. `usb3503_connect` writes regmap bits for SP_ILOCK, disabled ports, self-powered mode, and connect/config release, then asserts the optional connect GPIO. `usb3503_switch_mode` coordinates GPIO states for hub, standby, and bypass modes. `usb3503_probe` parses platform data or OF properties and acquires clock/GPIO resources. I2C and platform probe/remove functions wrap the common probe.

## Control Flow
I2C probe allocates state, initializes an 8-bit regmap up to register `USB3503_RESET`, sets `hub->dev`, and calls the common probe. Platform probe allocates state without regmap, so only GPIO/clock control is available. The common probe reads platform data or devicetree properties including `refclk-frequency`, `disabled-ports`, and `initial-mode`; obtains and enables an optional `refclk`; requests GPIOs with initial output values; waits at least 100 us after reset assertion; warns if disabled ports were requested without regmap; and switches to the requested mode.

Mode switching first deasserts connect when leaving hub mode, sets reset and bypass GPIOs, and for hub mode waits for hub logic stabilization before calling `usb3503_connect`. Suspend switches to standby and disables the clock. Resume enables the clock and switches back to the saved mode.

## State and Persistence
The driver's persistent runtime state is the selected mode, GPIO levels, optional clock state, and register configuration written to the hub. Devicetree/platform configuration is parsed only at probe. There is no disk persistence.

## Dependencies and Integration Points
The file depends on I2C, regmap, platform devices, devicetree, GPIO descriptors, clock framework, delay helpers, and `linux/platform_data/usb3503.h`. It integrates with boards through I2C IDs, OF compatibles, and optional platform data.

## Risks and Edge Cases
If `usb3503_switch_mode` fails during probe, the common probe currently does not propagate that return value; failures inside `usb3503_connect` can therefore be underreported at probe time. Resume calls `clk_prepare_enable` without checking the return value. Disabled ports require regmap; platform-only devices cannot apply the mask. Reference-clock frequency validation is strict and returns `-EINVAL` for unsupported values. GPIO polarity must match board descriptions because reset/connect/bypass behavior is entirely board-wired.

## Test Signals
Good tests include I2C regmap write/update failures, OF clock-rate validation, disabled-port mask programming, all three initial modes, platform-only GPIO mode switching, suspend/resume clock behavior, and probe behavior when optional GPIOs or clocks are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usb3503.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usb4604.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/usb4604.c

## Purpose
`usb4604.c` is a compact I2C driver for the SMSC USB4604 HSIC 4-port USB 2.0 hub controller. It controls reset and sends the vendor connect command that puts the hub into active hub mode.

## Important APIs, Types, and Functions
`enum usb4604_mode` defines unknown, hub, and standby modes. `struct usb4604` stores mode, device, and optional reset GPIO. `usb4604_reset` sets reset GPIO state and waits 250 ms after enabling reset logic. `usb4604_connect` resets the hub, sends the three-byte I2C connect command `{ 0xaa, 0x55, 0x00 }`, and marks hub mode. `usb4604_switch_mode` selects hub or standby. `usb4604_probe` obtains reset GPIO and reads `initial-mode`.

## Control Flow
I2C probe allocates state, stores it with `i2c_set_clientdata`, sets `hub->dev`, and calls the common probe. The common probe requests optional `reset` GPIO as output low, reads the optional OF `initial-mode` property, and switches to that mode. Hub mode asserts reset/logic, waits, and sends the connect command over I2C. Standby deasserts reset. Suspend switches to standby; resume switches back to the saved mode.

## State and Persistence
Runtime state is limited to the desired mode and reset GPIO level. The connect command affects hardware state until reset or power loss. There is no persistent storage.

## Dependencies and Integration Points
The driver depends on I2C, GPIO descriptors, devicetree matching, delay helpers, and the PM helper macros. It binds I2C ID `usb4604` and OF compatible `smsc,usb4604`.

## Risks and Edge Cases
`usb4604_reset` unconditionally calls `gpiod_set_value_cansleep`; optional GPIO absence should be evaluated against current gpiod helper behavior and board requirements. I2C send success is checked only for negative errors, not short positive writes. The saved mode is reused on resume, so invalid or unsupported `initial-mode` values lead to `-EINVAL` at probe or resume. There is no remove callback because devm allocations are sufficient and no extra power resource is tracked.

## Test Signals
Tests should check probe with and without reset GPIO, `initial-mode` hub and standby, I2C connect command failure and short-write behavior, suspend/resume mode transitions, and OF/I2C table matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usb4604.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usbio.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/usbio.c

## Purpose
`usbio.c` is the Intel USBIO Bridge driver. It binds USBIO bridge devices, negotiates firmware/control information, enumerates GPIO banks and I2C buses, exposes child functions as auxiliary devices, and exports bridge transfer helpers for those child drivers.

## Important APIs, Types, and Functions
`struct usbio_device` owns the USB interface, quirks, control and bulk mutexes, endpoint pipes and buffers, one persistent bulk-in URB, a completion for response packets, auxiliary client list, and discovered GPIO/I2C descriptors. `struct usbio_client` wraps each auxiliary device and protects its bridge pointer with a mutex.

Exported namespace `USBIO` APIs are `usbio_control_msg`, `usbio_bulk_msg`, `usbio_acquire`, `usbio_release`, `usbio_get_txrxbuf_len`, `usbio_get_quirks`, and `usbio_acpi_bind`. Internal protocol helpers include `usbio_ctrl_msg`, `usbio_bulk_recv`, `usbio_add_client`, `usbio_enum_gpios`, and `usbio_enum_i2cs`.

## Control Flow
Probe allocates and initializes `struct usbio_device`, determines endpoint-zero max packet for the control buffer, finds the first bulk-in/out endpoints, applies quirks such as 63-byte bulk max packet, allocates TX/RX buffers and a persistent RX URB, submits the URB, and performs serialized control commands: handshake, protocol version, firmware version, GPIO enumeration, and I2C enumeration. It then creates one `USBIO_GPIO_CLIENT` auxiliary device and one `USBIO_I2C_CLIENT` per bus descriptor.

`usbio_control_msg` locks the client, takes a runtime PM reference, serializes on `ctrl_mutex`, and sends an endpoint-zero vendor packet. `usbio_bulk_msg` is called while the client and bridge bulk mutex are already held by `usbio_acquire`; it optionally sends a bulk packet and waits for the persistent RX URB to complete a matching response. Disconnect completes any waiters, sets every client's bridge pointer to `NULL`, kills/frees the URB, and deletes/uninitializes auxiliary devices.

## State and Persistence
Bridge state is volatile: descriptors are cached from firmware, auxiliary devices point into those cached descriptor arrays as platform data, and the bridge pointer becomes `NULL` on disconnect. The persistent RX URB is resubmitted after every completion and again on resume. Quirks come from `usb_device_id.driver_info`.

## Dependencies and Integration Points
The driver depends on USB control/bulk APIs, auxiliary bus, ACPI companion matching, completions, mutexes, cleanup guards, and `linux/usb/usbio.h`. It integrates with child GPIO/I2C drivers through auxiliary device names and exported transfer APIs. USB IDs include Lattice NX40/NX33/NX33U and Synaptics Sabre variants with per-device quirks.

## Risks and Edge Cases
The split locking contract is important: `usbio_bulk_msg` asserts that callers hold both the client mutex and `bulk_mutex`, while `usbio_acquire` deliberately leaves the client locked until `usbio_release` to avoid ABBA deadlocks. Disconnect must not free `usbio_device` until clients can no longer enter bridge operations; it sets bridge pointers under each client mutex before killing the URB. `usbio_bulk_recv` resubmits the URB even after errors other than `-ENOENT`, and return handling of that resubmit is not checked. Control timeout is defined as zero, so endpoint-zero behavior depends on USB core semantics for zero timeout. Auxiliary creation return values in enumeration are ignored, which can hide partial child-device creation failures.

## Test Signals
Validation should cover control handshake and descriptor parsing, quirk-specific buffer sizing, bulk request/response matching, unsupported bulk-command `-EPIPE` behavior, acquire/release lock ordering under lockdep, disconnect while clients wait, suspend/resume URB lifecycle, ACPI binding by HID/UID, and partial auxiliary-device add failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usbio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usblcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/usblcd.c

## Purpose
`usblcd.c` is a USB character-device driver for USB LCD devices from vendor `0x10d2`, specifically product `0x0001`. It registers `/dev/lcd%d`, supports blocking bulk reads, asynchronous bulk writes, and ioctls for hardware and driver version strings.

## Important APIs, Types, and Functions
`struct usb_lcd` stores the USB device/interface, bulk-in buffer and endpoint addresses, bulk-out endpoint address, kref, write concurrency semaphore, submitted-URB anchor, I/O rwsem, and disconnected flag. File operations are `lcd_open`, `lcd_release`, `lcd_read`, `lcd_write`, `lcd_ioctl`, and `noop_llseek`. USB lifecycle functions are `lcd_probe`, `lcd_disconnect`, `lcd_suspend`, and `lcd_resume`.

`lcd_read` performs a synchronous `usb_bulk_msg` on the bulk-in endpoint with a 10-second timeout. `lcd_write` limits concurrent writes with `limit_sem`, allocates an URB and coherent buffer, copies user data, anchors the URB, submits it asynchronously, and frees its own URB reference. `lcd_write_bulk_callback` frees the coherent buffer and releases one semaphore slot. `lcd_draw_down` waits for anchored writes before suspend and kills remaining URBs after timeout.

## Control Flow
Probe allocates state, initializes kref/semaphore/rwsem/anchor, takes a USB-device reference, rejects unsupported products, finds the first bulk-in and bulk-out endpoints, allocates the read buffer, stores interface data, and registers the USB class minor. Open resolves the minor with `usb_find_interface`, increments kref, takes an autosuspend PM reference, and stores private data. Release drops autosuspend and kref. Disconnect deregisters the minor, marks `disconnected` under write lock, kills anchored write URBs, and drops the probe kref.

## State and Persistence
Runtime state is in `struct usb_lcd`; no disk state exists. The disconnected bit gates new reads/writes while allowing open file descriptors to unwind safely. Anchored URBs represent outstanding asynchronous writes. The driver does not cache display contents.

## Dependencies and Integration Points
The file depends on USB core, USB class minors, autosuspend, krefs, semaphores, anchors, rwsems, coherent DMA allocation, and user-copy helpers. User-space integration is through `/dev/lcd%d` and ioctl numbers `IOCTL_GET_HARD_VERSION` and `IOCTL_GET_DRV_VERSION`.

## Risks and Edge Cases
`lcd_write` accepts arbitrary `count` and allocates that much coherent memory per submitted URB, bounded only by memory and the five-write semaphore. The ioctl version strings are copied without a terminating NUL because `strlen` is used. Reads serialize only through the rwsem and share one bulk-in buffer, so concurrent reads on multiple file descriptors are protected by the read side only; because `down_read` permits concurrency, simultaneous reads can race on `bulk_in_buffer`. Disconnect handling uses the write side to exclude new operations when setting `disconnected`, but in-flight reads/writes must still tolerate USB errors.

## Test Signals
Tests should cover product filtering, minor registration, open/autosuspend reference balancing, synchronous read timeout and user-copy failures, write semaphore exhaustion/interruption, asynchronous write completion cleanup, suspend draining anchored URBs, disconnect during read/write, and ioctl buffer expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usblcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usbsevseg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/usbsevseg.c

## Purpose
`usbsevseg.c` drives a USB seven-segment display with vendor/product `0x0fc5:0x1227`. It exposes sysfs attributes for power, text, text mode, decimal points, and display mode bytes, and sends device-specific control requests to update the display.

## Important APIs, Types, and Functions
`struct usb_sevsegdev` stores the USB device/interface, power state, mode bytes, per-digit decimal bits, text mode, text buffer and length, suspend shadow-power flag, and runtime PM ownership flag. Display update helpers are `update_display_powered`, `update_display_mode`, and `update_display_visual`. Sysfs handlers include generated simple unsigned attributes for `powered`, `mode_msb`, and `mode_lsb`, plus explicit `text`, `decimals`, and `textmode` handlers.

The device protocol uses `usb_control_msg_send` with request `0x12`, request type `0x48`, and encoded values for power `(80,10)`, mode `(82,10)`, text `(85,10)`, and decimal bits `(86,10)`.

## Control Flow
Probe allocates state, stores interface data, sets `shadow_power = 1`, initializes defaults to ASCII mode and six-character scan mode, and relies on `dev_groups` to expose sysfs attributes. Writing `powered` may take or release a runtime PM reference and sends the power command only when not suspended. Text writes strip one trailing newline, reject input longer than eight bytes, reverse bytes because the hardware is right-to-left, and send text plus decimal state. Suspend sets `shadow_power = 0` to suppress USB I/O. Resume and reset-resume restore mode and visual state with `GFP_NOIO`.

## State and Persistence
The in-memory cache tracks intended display state and is replayed after resume/reset-resume except for power, where `shadow_power` gates transfers and `powered` controls runtime PM. There is no disk state. Sysfs writes update cached values before attempting USB transfer, and most transfer failures are logged but not returned to the sysfs writer.

## Dependencies and Integration Points
The driver depends on USB core, sysfs attribute groups, runtime PM, and synchronous control-message helpers. Integration is via USB ID table and sysfs files attached to the interface device.

## Risks and Edge Cases
Sysfs state is not protected by a mutex, so concurrent attribute writes can interleave cached mode/text/decimal updates and control transfers. `simple_strtoul` in generated stores accepts broad input and does not validate range for byte fields. `text_show` uses `%s` over an eight-byte buffer that is zeroed on writes, but binary raw mode can contain embedded NULs and make reads misleading. Transfer failures do not generally propagate to users, so sysfs can report state that hardware did not accept. Runtime PM ownership is tied to `powered`; mismatched suspend, failed autopm get, or concurrent power writes need testing.

## Test Signals
Tests should cover all sysfs attributes, text length and newline handling, raw/hex/ascii mode selection, decimal bit reversal, suspend/resume replay, reset-resume replay, runtime PM get/put balance during power changes, failed control transfers, and disconnect during sysfs writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usbsevseg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usbtest.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/usbtest.c

## Purpose
`usbtest.c` is a USB core and host-controller test driver. It binds known USB test/gadget devices or a module-parameter-selected generic device, then exposes an ioctl through usbfs to run numbered tests for control, bulk, interrupt, isochronous, scatter-gather, unlink, halt, toggle, DMA mapping, and unaligned-buffer behavior.

## Important APIs, Types, and Functions
`struct usbtest_info` describes endpoint expectations and supported test classes for a device. `struct usbtest_dev` stores the interface, selected pipes, endpoint descriptors, per-device mutex, and scratch buffer. User ABI structs are `usbtest_param_32` and compat `usbtest_param_64`, both used with `_IOWR('U', 100, ...)`.

Endpoint setup is handled by `get_endpoints`. URB helpers include `usbtest_alloc_urb`, `simple_alloc_urb`, `complicated_alloc_urb`, `simple_fill_buf`, `simple_check_buf`, `simple_io`, and `simple_free_urb`. Scatter-gather helpers are `alloc_sglist`, `perform_sglist`, and timer cancellation support. Control tests are implemented by `ch9_postconfig` and `test_ctrl_queue`. Unlink/halt/toggle tests use `unlink1`, `unlink_queued`, `halt_simple`, and `toggle_sync_simple`. Isochronous and queued transfer tests use `iso_alloc_urb`, `test_queue`, and `complicated_callback`.

## Control Flow
`usbtest_probe` optionally matches generic module parameters, allocates device state and scratch buffer, selects endpoints either from fixed endpoint numbers or descriptor autoconfiguration, stores interface data, and logs available test channels. `usbtest_ioctl` locks the per-device mutex, resets the preferred altsetting, translates 64-bit compat parameters to the 32-bit internal form when needed, records start time, calls `usbtest_do_ioctl`, and writes duration back on success.

`usbtest_do_ioctl` validates iterations and scatterlist depth and dispatches test numbers 0 through 29. Tests cover simple bulk reads/writes, variable-length bulk I/O, scatter-gather bulk I/O, USB chapter 9 descriptor/status sanity checks, queued control URBs with expected stalls/short reads, unlink behavior for single and queued URBs, endpoint halt set/clear, vendor control-out loopback, isochronous queues, odd-address DMA/core-map transfers, interrupt transfers, performance-oriented queued bulk, and data-toggle reset via clear-halt.

## State and Persistence
The driver keeps no persistent test results. Runtime state includes selected altsetting, module parameters (`alt`, `pattern`, `realworld`, `force_interrupt`, `vendor`, `product`), endpoint pipe selections, and scratch buffers. Each ioctl fills duration fields for that invocation. Test data patterns are deterministic zeros or mod-63 bytes.

## Dependencies and Integration Points
The file depends on usbcore URB/control/scatter-gather APIs, usbfs driver ioctl plumbing, timers, completions, spinlocks, mutexes, descriptor parsing helpers, and known USB gadget/test firmware behavior. It integrates with devices such as EZ-USB, dedicated USB test firmware, Gadget Zero, user-mode test drivers, and generic module-parameter-selected devices.

## Risks and Edge Cases
This is intentionally a stress and conformance test driver, so many tests can stall endpoints, consume bandwidth, or block for long periods. A source comment warns that usbfs locking can delay disconnect handling while an ioctl runs; aborting tests may require killing the userspace task. Some tests assume cooperative firmware, especially control-out loopback, isochronous source/sink, and bulk data patterns. Scatter-gather reads currently do not verify returned data. Isochronous tests tolerate up to a 10% packet error rate, so failures below that threshold are not fatal. Queued control tests intentionally allow some device-specific stalls when `realworld` mode is enabled. Test parameters can allocate many URBs and buffers up to `MAX_SGLEN`, so memory pressure is part of the risk profile.

## Test Signals
The file is itself a test harness. Useful signals are successful probe endpoint selection, ioctl return codes per numbered test, duration fields being populated, expected `-EOPNOTSUPP` when a requested endpoint class is unavailable, logs for descriptor validation failures, URB timeout/unlink statuses, guard-byte validation for unaligned buffers, lockdep behavior around per-device mutexing, and disconnect/suspend behavior while long-running tests are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/usbtest.c -->
