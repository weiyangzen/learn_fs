# subset-b-005519 USB misc research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/brcmstb-usb-pinmap.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/brcmstb-usb-pinmap.c

Purpose: Broadcom STB platform driver that maps USB controller override register bits to board GPIOs in both directions. Device tree supplies `brcm,in-functions`, `brcm,out-functions`, matching GPIO arrays, and mask arrays. `brcmstb_usb_pinmap_probe()` allocates a single managed state block, maps one MMIO resource, parses pins, synchronizes initial hardware/GPIO state, then installs one override IRQ plus per-input GPIO IRQs.

Important APIs and types: `struct brcmstb_usb_pinmap_data`, `struct in_pin`, `struct out_pin`, `pinmap_set()`, `pinmap_unset()`, `sync_in_pin()`, `sync_all_pins()`, `brcmstb_usb_pinmap_ovr_isr()`, and `brcmstb_usb_pinmap_gpio_isr()`. It depends on platform resources, Open Firmware properties, gpiod consumers, `readl()`/`writel()`, and devm IRQ/memory helpers.

Control flow: input GPIO IRQs call `sync_in_pin()` to mirror GPIO value into a register value bit after the override enable bit has been set. The override IRQ scans each output pin, checks its changed bit, pulses the clear-changed mask, reads the value mask, and drives the GPIO. Probe validates nonzero pin counts, parses all masks in strict order, enables overrides, clears pending changed bits, and seeds all output GPIOs from the register.

State and persistence: state is volatile hardware state plus devm-managed arrays. There is no remove path because `platform_driver_probe()` is used for init-only probe binding, and there is no persistent storage. Risks include fragile DT mask ordering, a likely misleading error message using `pin->name` in an output GPIO failure path, repeated full-register read/modify/write without locking around IRQ paths, and dependency on edge-triggered GPIO IRQs for input synchronization. Test signals include DT binding coverage for missing/malformed properties, IRQ-triggered GPIO/register propagation, and suspend/resume register retention if platform power state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/brcmstb-usb-pinmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/chaoskey.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/chaoskey.c

Purpose: USB driver for Altus Metrum ChaosKey and Araneus Alea I random-number devices. It registers both a `/dev/chaoskey%d` class device and a kernel `hwrng`, letting userspace and the random subsystem consume the same bulk-IN entropy stream.

Important APIs and types: `struct chaoskey` tracks interface lifetime, hwrng registration, autosuspend, one bulk read URB, shared buffer cursors, and open/present flags. Core functions are `chaoskey_probe()`, `chaoskey_disconnect()`, `chaoskey_open()`, `chaoskey_release()`, `_chaoskey_fill()`, `chaoskey_read()`, `chaoskey_rng_read()`, `chaos_read_callback()`, and PM resume handling.

Control flow: probe finds a bulk-IN endpoint, caps packet size to 64 bytes, allocates the URB/buffer/name, registers the char device and hwrng, and enables autosuspend. Reads and hwrng calls serialize through `rng_lock` and `lock`; when the buffer is empty `_chaoskey_fill()` wakes the interface, submits the URB, waits for completion or timeout, and exposes `valid/used` bytes. Alea devices use a longer timeout on first read and after resume.

State and persistence: buffer contents are transient entropy bytes, protected by mutexes and completion via `wait_q`. Disconnect unregisters hwrng, deregisters the char device, marks `present=false`, poisons the URB, and frees immediately only if no open fd remains. Risks include shared consumption between hwrng and direct readers, timeout mapping to `-EAGAIN` for userspace, reliance on a write memory barrier before `reading=false`, and no entropy quality validation in this driver. Test signals include hot-unplug while blocking in read, autosuspend wake failure, nonblocking read behavior, hwrng registration failure, Alea first-read timeout, and concurrent hwrng/user reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/chaoskey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/cypress_cy7c63.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/cypress_cy7c63.c

Purpose: Generic sysfs driver for AK Modul-Bus Cypress CY7C63xxx "Port-Chip" devices, exposing two simple I/O ports as `port0` and `port1` attributes.

Important APIs and types: `struct cypress` stores `udev` and cached port values. `vendor_command()` sends vendor control reads, `write_port()` validates decimal byte input and sends `CYPRESS_WRITE_PORT`, while `read_port()` sends `CYPRESS_READ_PORT` and formats the cached byte. The USB driver uses `dev_groups = cypress_groups`.

Control flow: probe allocates state and stores it in interface data. Sysfs reads allocate an 8-byte transfer buffer, issue a vendor IN control request, update `dev->port[]` from `iobuf[1]`, and return the value. Sysfs writes parse 0..255 and send a vendor command with the port ID and byte value.

State and persistence: cached port values are in memory only; actual device state is owned by firmware. Disconnect clears intfdata after sysfs removal and frees state. Risks include no mutex around sysfs access, `read_port()` ignoring negative command results when formatting cached data, legacy `sprintf()`, and ambiguous `USB_RECIP_OTHER` vendor control recipient. Test signals include sysfs read/write return values, invalid input, short control responses, disconnect racing with sysfs access, and validation on both supported port IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/cypress_cy7c63.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/cytherm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/cytherm.c

Purpose: Cypress USB thermometer/demo-board driver exposing board RAM/port functions through sysfs attributes: `brightness`, `temp`, `button`, `port0`, and `port1`.

Important APIs and types: `struct usb_cytherm` stores `udev`, interface pointer, and cached brightness. `vendor_command()` wraps one-byte Cypress vendor control requests. Attribute handlers read/write RAM addresses `TEMP`, `SIGN`, `BUTTON`, `BRIGHTNESS`, `BRIGHTNESS_SEM` and ports 0/1.

Control flow: probe binds vendor/product `04b4:0002`, allocates state, caches default brightness `0xff`, and attaches sysfs groups. `brightness_store()` writes brightness to RAM then writes a semaphore byte. Temperature reads issue two RAM reads and format signed half-degree values. Port stores clamp parsed values to one byte and write through vendor control messages.

State and persistence: only brightness is cached in driver memory; sensor/button/port state is read from the device on demand and lost on unplug. Risks include no locking, returning 0 instead of `-ENOMEM` on allocation failure in sysfs paths, use of `simple_strtoul()` with ineffective negative checks, ignoring failed vendor reads before using `buffer[1]`, and legacy formatting without trailing newlines. Test signals include sysfs ABI reads/writes, malformed input, short/failing control requests, hot unplug during sysfs operations, and verifying temp sign/half-degree formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/cytherm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/ehset.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/ehset.c

Purpose: USB-IF EHSET high-speed electrical test fixture driver. When a fixture PID enumerates, probe sends the appropriate hub class command to place the parent port or device into a USB 2.0 compliance test state.

Important APIs and types: test PIDs map to `USB_TEST_SE0_NAK`, `USB_TEST_J`, `USB_TEST_K`, `USB_TEST_PACKET`, suspend/resume, single-step descriptor, and single-step set-feature paths. `ehset_prepare_port_for_testing()` suspends the port for normal hubs or disables power for a small quirk list.

Control flow: `ehset_probe()` derives the parent hub and child port number, switches on the device PID, performs required delays for timing-sensitive tests, sends `USB_REQ_SET_FEATURE` or `CLEAR_FEATURE` to the parent hub, or sends a descriptor request directly to the fixture for single-step descriptor testing. The single-step set-feature test is rejected unless the parent is the root hub.

State and persistence: no per-device state is kept; probe side effects are immediate hub-port state changes. Risks include intentionally disruptive port state manipulation, fixed 15-second sleeps in probe, dependence on hub behavior, no cleanup on disconnect, and an external declaration for `usb_device_match_id()`. Test signals are mostly hardware compliance-lab signals: correct PID selection, hub quirk behavior, root-hub-only rejection, and expected control-transfer traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/ehset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/emi26.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/emi26.c

Purpose: Firmware-loader-only USB driver for Emagic EMI 2|6 devices before their real audio firmware is active. It downloads EZ-USB loader, FPGA bitstream, and final firmware, then deliberately returns an error from probe so the functional audio driver can bind after re-enumeration or firmware activation.

Important APIs and types: `emi26_writememory()`, `emi26_set_reset()`, `emi26_load_firmware()`, `emi26_probe()`, and firmware declarations for `emi26/loader.fw`, `emi26/bitstream.fw`, and `emi26/firmware.fw`. It uses Intel HEX records, vendor requests `ANCHOR_LOAD_INTERNAL`, `ANCHOR_LOAD_EXTERNAL`, and `ANCHOR_LOAD_FPGA`, and EZ-USB `CPUCS_REG`.

Control flow: firmware load asserts CPU reset, writes the loader into internal RAM, releases reset, streams the FPGA bitstream in up-to-1023-byte chunks, reloads the loader, writes external firmware records while CPU runs, asserts reset, writes internal firmware records, releases reset, delays, and returns positive `1`. Probe ignores the return and returns `-EIO` by design.

State and persistence: no state survives probe; firmware is transiently requested and released. Device state is the loaded controller/FPGA RAM. Risks include legacy `usb_control_msg()` writes with short timeout, treating positive lengths as success without exact-length checks, a chunking loop that assumes non-null bitstream records, and intentionally failed probe confusing generic test expectations. Test signals include missing firmware diagnostics, USB control write traces, re-enumeration/real-driver bind behavior, and loader/FPGA/final firmware ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/emi26.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/emi62.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/emi62.c

Purpose: Firmware-loader-only USB driver for Emagic EMI 6|2m devices. It is structurally similar to `emi26.c`, but selects `emi62/spdif.fw` at compile time through `SPDIF` and otherwise would use `emi62/midi.fw`.

Important APIs and types: `emi62_writememory()`, `emi62_set_reset()`, `emi62_load_firmware()`, `emi62_probe()`, and firmware files `emi62/loader.fw`, `emi62/bitstream.fw`, and `FIRMWARE_FW`. It uses EZ-USB reset register `CPUCS_REG` and Anchor vendor memory load commands.

Control flow: probe calls firmware load and returns `-EIO` so ownership is handed to the real driver. Load asserts reset, loads the FPGA helper, releases reset, streams the FPGA bitstream, reloads helper code, releases reset, loads external final firmware, asserts reset, loads internal-address final records, releases reset, and returns positive `1` on success.

State and persistence: no driver state is registered after probe; all effects are on device RAM/FPGA state. Risks include hard-coded SPDIF/MIDI selection, `ANCHOR_LOAD_EXTERNAL` used for internal records in the final pass, no exact-length control-transfer validation, and intentionally failed probe semantics. Test signals include firmware request paths, successful post-load handoff, device timing delays, and failure logs for each control-transfer phase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/emi62.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/ezusb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/ezusb.c

Purpose: Shared helper module for Cypress/Anchor EZ-USB firmware loading, primarily FX1. It exports reset and Intel HEX download helpers for other USB drivers.

Important APIs and types: `struct ezusb_fx_type`, `ezusb_writememory()`, `ezusb_set_reset()`, exported `ezusb_fx1_set_reset()` and `ezusb_fx1_ihex_firmware_download()`. Disabled FX2 variants document possible future support. It depends on `request_ihex_firmware()`, `ihex_next_binrec()`, and `usb_control_msg_send()`.

Control flow: firmware download requests an ihex firmware blob, clears reset, writes records above the internal RAM limit with external-RAM request, asserts reset, writes internal RAM records, then clears reset to run firmware. The split external-first/internal-second order lets the CPU be stopped while internal code is rewritten.

State and persistence: this file keeps no state and exports symbols only; persistence is entirely in target device RAM. Risks include misleading error strings that swap internal/external wording, a misspelled `max_internal_adress` field, no exact transfer-length accounting beyond helper return status, and FX2 support compiled out. Test signals include exported symbol users, missing firmware handling, device reset sequencing, and control-transfer failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/ezusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/idmouse.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/idmouse.c

Purpose: Character driver for Siemens/Cherry ID Mouse FingerTIP fingerprint sensors. It captures one grayscale PGM fingerprint image at open time and serves that image via read from `/dev/idmouse%d`.

Important APIs and types: `struct usb_idmouse`, `idmouse_create_image()`, `idmouse_open()`, `idmouse_read()`, `idmouse_release()`, `idmouse_probe()`, and vendor `FTIP_*` control commands. It registers a USB class device at minor base 132 and uses autosuspend around image capture.

Control flow: probe binds only the data interface (`bInterfaceClass == 0x0A`), finds a bulk-IN endpoint, allocates a buffer large enough for the PGM image plus bulk transfer headroom, and registers the char device. Open is exclusive, wakes the device, runs a command sequence to acquire/reset the sensor, bulk-reads until the full image size, validates expected black/right and white/bottom borders, then stores the image in the device buffer. Reads use `simple_read_from_buffer()` over the captured image.

State and persistence: `bulk_in_buffer` holds the latest captured image for the open file; open/present flags are mutex protected. Disconnect deregisters the node and defers freeing if open. Risks include long blocking capture in open, heuristic image validation returning `-EAGAIN`, no retry loop in kernel, no URB cancellation because bulk reads are synchronous, and legacy sensor command assumptions. Test signals include capture success with known image borders, open exclusivity, partial read offsets, autosuspend get/put, disconnect while open, and fallback from 0x200 packet size to original endpoint size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/idmouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/iowarrior.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/iowarrior.c

Purpose: Native character driver for Code Mercenaries IO-Warrior HID-like USB I/O controllers. It exposes `/dev/iowarrior%d` nodes, read/write report traffic, poll, and ioctls from `linux/usb/iowarrior.h`.

Important APIs and types: `struct iowarrior` contains endpoint descriptors, interrupt URB, report queue, atomic queue indices, write throttle, serial info, product ID, and anchored async writes. Core functions are `iowarrior_probe()`, `iowarrior_open()`, `iowarrior_read()`, `iowarrior_write()`, `iowarrior_ioctl()`, callbacks, poll, release, and disconnect.

Control flow: probe finds interrupt-IN, conditionally finds interrupt-OUT for newer/full-speed products, derives report size with product-specific overrides, allocates one read URB and a circular queue of 16 reports plus serial byte, reads the chip serial string, sets HID idle on interface 0, and registers the class device. Open is exclusive and submits the read URB. The read callback filters duplicate interface-0 reports, handles queue overflow by dropping oldest, appends a software serial byte, and resubmits. Writes use synchronous HID `SET_REPORT` for IOW24/40-family devices and anchored async interrupt-OUT URBs with max four in flight for IOW56/28/100-family devices.

State and persistence: queue indices and write counters are in-memory only; device I/O state persists in hardware. Disconnect marks `present=false`, kills read/anchored write URBs, wakes waiters, and defers deletion until release if open. Risks include complex atomic queue semantics without a single spinlock, old `-ERESTART` return usage, strict report-size ABI, duplicate filtering that may suppress legitimate same-valued reports, and product-specific endpoint requirements. Test signals include per-product report size and endpoint discovery, blocking/nonblocking read/write, poll readiness, `IOW_READ`, `IOW_WRITE`, `IOW_GETINFO`, overflow behavior, async write throttling, and hot unplug while blocked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/iowarrior.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/isight_firmware.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/isight_firmware.c

Purpose: Firmware loader for Apple built-in USB iSight cameras that enumerate as `05ac:8300` before UVC firmware is loaded. After loading `isight.fw`, the device detaches and returns as a UVC-compatible camera for `uvcvideo`.

Important APIs and types: `isight_firmware_load()` is the probe routine and only substantial function. It uses `request_firmware()`, vendor control request `0xa0`, a 50-byte staging buffer, and a simple firmware record format with 4-byte length/address headers.

Control flow: probe requests `isight.fw`, writes `1` to CPUCS-like address `0xe600` to initialize/hold the loader, iterates firmware records until `len == 0x8001`, skips zero-length records, writes each record in up-to-50-byte chunks to the requested address, then writes `0` to `0xe600` to complete/run the firmware.

State and persistence: no device state is retained in the driver after probe; loaded firmware changes the device's runtime identity. Risks include `release_firmware(firmware)` in the out path even when firmware request failed and `firmware` was never initialized, raw `printk()` diagnostics, no exact final success marker enforcement if the loop ends by size, and no class-device state. Test signals include missing/malformed firmware, chunk boundary handling, expected disconnect/re-enumeration, and UVC driver bind after load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/isight_firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/ldusb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/ldusb.c

Purpose: Generic character driver for LD Didactic raw interrupt-report devices. It emulates Windows HID-style raw interrupt report access for many LD educational/lab devices.

Important APIs and types: `struct ld_usb`, module parameters for ring/write buffer sizing and minimum interrupt intervals, callbacks, `ld_usb_open()`, `ld_usb_read()`, `ld_usb_write()`, `ld_usb_poll()`, probe/release/disconnect, and optional control-endpoint fallback for output reports.

Control flow: probe allocates state, applies a firmware workaround for old CASSY/COM3LAB devices, finds the last interrupt-IN endpoint and optional interrupt-OUT endpoint, allocates a ring buffer of reports, URBs, and buffers, sets intervals, and registers `/dev/ldusb%d`. Open is exclusive and starts continuous interrupt-IN polling. The IN callback copies each report and actual length into a ring buffer, resubmits until overflow or shutdown, and wakes readers. Reads wait for a complete ring entry, copy at most one report, advance tail, and restart polling after overflow. Writes wait for the output path, truncate to configured capacity, and either send HID `SET_REPORT` over control endpoint or submit an interrupt-OUT URB.

State and persistence: ring contents, overflow flag, busy flags, and open/disconnected state are volatile. Disconnect poisons URBs, deregisters the node, and defers freeing while open. Risks include ring overflow stopping input until a read restarts the URB, truncation semantics on writes/reads, no autosuspend integration, legacy `printk()` errors, and control fallback using fixed report parameters. Test signals include each supported VID/PID, endpoint variants, blocking/nonblocking read/write, poll, overflow recovery, old-firmware workaround, and disconnect while waiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/ldusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/legousbtower.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/legousbtower.c

Purpose: Character driver for the LEGO USB Tower infrared transceiver. It exposes `/dev/legousbtower%d` for legacy robotics tools and manages packetizing, read timeouts, write buffering, and interrupt URBs.

Important APIs and types: `struct lego_usb_tower`, module parameters `read_buffer_size`, `write_buffer_size`, `packet_timeout`, `read_timeout`, and interrupt intervals; `tower_open()`, `tower_read()`, `tower_write()`, callbacks, poll, release, probe, and disconnect. Vendor requests reset the tower and read firmware version.

Control flow: probe finds interrupt-IN/OUT endpoints in reverse, allocates buffers/URBs, reads firmware version, and registers a USB class node. Open is exclusive, sends a reset control request, clears read buffers, and starts the interrupt-IN URB. The IN callback appends received bytes into a shared read buffer, records arrival time, and resubmits. `tower_check_for_read_packet()` exposes bytes only after packet timeout or when the buffer is full. Reads wait for packetized bytes and shift the remaining buffer after copy. Writes serialize one interrupt-OUT URB at a time.

State and persistence: read buffer length, packet length, last-arrival jiffies, busy flags, open/disconnected state, and endpoint buffers are in memory. Disconnect poisons URBs and defers freeing if open. Risks include O(n) buffer shifting after every read, dropped bytes on read buffer overflow, long timeout-dependent ABI behavior, mutable module parameters affecting allocation and timing, and no autosuspend. Test signals include firmware-version control request, reset-on-open, packet timeout behavior, nonblocking read/write, poll readiness, partial reads, disconnect while open, and long packet writes up to buffer limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/legousbtower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/lvstest.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/lvstest.c

Purpose: Link Layer Validation System test driver for SuperSpeed root hubs. It exposes sysfs triggers for USB 3 link validation actions such as U1/U2 timeouts, U3 entry/exit, hot/warm reset, compliance mode, and device descriptor fetch.

Important APIs and types: `struct lvs_rh`, `create_lvs_device()`, `destroy_lvs_device()`, sysfs store handlers, `lvs_rh_work()`, `lvs_rh_irq()`, probe, and disconnect. It integrates with root-hub class requests, HCD `enable_device/free_dev`, `usb_phy_notify_connect/disconnect`, and root-hub interrupt polling.

Control flow: probe only binds SuperSpeed root hubs with no parent, reads the SS hub descriptor, allocates an interrupt URB, and schedules work on root-hub interrupt activity. Work scans all ports, clears change bits, tracks which port has an LVS device, notifies the PHY, and resubmits the interrupt URB. Sysfs triggers send root-hub port feature requests; some create a temporary SuperSpeed `usb_device` so the HCD can issue device-scoped operations such as descriptor fetch or U3 transitions.

State and persistence: present flag, port number, cached hub descriptor/status, URB, and work item are volatile. Risks include lab-only operations that intentionally disrupt root hub ports, hand-built `usb_device` lifecycle, sysfs write-only ABI without payload semantics for most commands, and reliance on HCD optional hooks. Test signals include binding only to SS root hubs, port change detection, feature request traces, HCD enable/free invocation, sysfs error propagation, and disconnect flushing work after URB poison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/lvstest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev.c

Purpose: Power-management driver for discrete onboard USB devices represented in device tree. It has a platform driver that sequences regulators/clock/reset/I2C initialization and a generic USB device driver that associates enumerated USB devices with their platform power owner.

Important APIs and types: `struct onboard_dev`, `struct usbdev_node`, `onboard_dev_power_on/off()`, suspend/resume, sysfs `always_powered_in_suspend`, USB5744 I2C helpers, platform probe/remove, `_find_onboard_dev()`, `onboard_dev_usbdev_probe/disconnect()`, and module init/exit that registers both USB and platform drivers.

Control flow: platform probe retrieves match pdata, regulators, optional clock, reset GPIO, powers on, optionally performs Microchip USB5744 SMBus configuration/attach, and schedules a deferred `driver_attach()` for the USB device driver. USB-device probe only matches DT-backed devices, finds the platform instance or peer-hub platform device, stores the driver data, links the USB device under platform sysfs, and adds it to `udev_list`. Suspend powers hubs off only if `always_powered_in_suspend` is false and no wakeup-enabled descendants require power.

State and persistence: `is_powered_on`, `going_away`, `always_powered_in_suspend`, and the list of associated USB devices are in memory; sysfs can change suspend policy for hubs. Hardware state includes regulator/clock/reset and USB5744 runtime flags. Risks include two-driver ordering races handled by `-EPROBE_DEFER`, careful lock dropping during unbind in remove, global deferred attach work, platform/USB lifetime coupling through drvdata, and I2C init only compiled with `CONFIG_USB_ONBOARD_DEV_USB5744`. Test signals include DT match data, regulator count limits, USB5744 I2C transaction failures, peer-hub association, suspend wakeup policy, unbind while USB children exist, sysfs link creation/removal, and module unload ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev.h -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev.h

Purpose: Shared private header defining onboard USB device platform data and the OF match table used by both the platform driver and platform-device creation helper.

Important APIs and types: `MAX_SUPPLIES`, `struct onboard_dev_pdata`, per-device static pdata constants, and `onboard_dev_match[]`. Pdata includes reset pulse duration, power-on delay, regulator supply names, supply count, and whether the target is a hub.

Control flow: not executable by itself; match entries map USB-style DT compatibles such as `usb424,5744`, `usbbda,179`, `usb1da0,5511`, and `usb5986,1198` to pdata consumed by `onboard_usb_dev.c`. `onboard_usb_dev_pdevs.c` also calls `of_match_node()` on this table to decide whether to instantiate a platform device.

State and persistence: all data is compile-time static and read-only. Risks include table drift between this match table and the USB ID table in `onboard_usb_dev.c`, `MAX_SUPPLIES` limiting future devices to two supplies, and missing `is_hub` on `usb_a_conn_data` causing non-hub suspend policy. Test signals include each compatible selecting intended supplies/delays, build coverage for all table users, and DT binding tests for peer hubs and supply names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev_pdevs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev_pdevs.c

Purpose: Exported helper API for USB hub code to create and destroy platform devices for supported onboard USB children beneath a parent hub.

Important APIs and types: `struct pdev_list_entry`, `of_is_onboard_usb_dev()`, exported `onboard_dev_create_pdevs()`, and exported `onboard_dev_destroy_pdevs()`. It depends on USB/HCD OF helpers, `of_platform_device_create()`, and the shared `onboard_dev_match[]` table.

Control flow: creation returns early if the parent hub has no OF node or is a secondary root HCD. It iterates child ports, resolves each child OF node, skips unsupported nodes, handles `peer-hub` de-duplication so one physical dual-speed hub gets one platform device, creates the platform device with the parent hub as parent, and records it in the caller-owned list. Destruction walks the list, destroys each platform device, and frees the list entry.

State and persistence: only the caller-owned list persists created platform devices; no global state is kept. Risks include subtle primary/secondary HCD and peer-hub de-duplication logic, partial failure behavior that skips failed nodes but continues, and reliance on parent hub maxchild/OF mappings. Test signals include root hub primary/secondary cases, nested hubs, peer-hub duplicate prevention, destroy cleanup, and unsupported child-node skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/onboard_usb_dev_pdevs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/qcom_eud.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/qcom_eud.c

Purpose: Qualcomm Embedded USB Debug platform driver. It exposes sysfs control to enable EUD, programs secure mode-manager registers, handles EUD interrupts, and drives a USB role switch between host/device based on attach status.

Important APIs and types: `struct eud_chip`, `enable_eud()`, `disable_eud()`, sysfs `enable`, `usb_attach_detach()`, `pet_eud()`, hard IRQ/threaded IRQ handlers, `eud_probe()`, and `eud_remove()`. It depends on MMIO, `qcom_scm_io_writel()`, `usb_role_switch`, IRQ wake, and OF compatible `qcom,eud`.

Control flow: probe gets the USB role switch, maps EUD registers, records a second memory resource as the SCM mode-manager physical base, requests a threaded IRQ, enables wake, and exposes sysfs. Writing `1` to `enable` writes secure enable, sets EUD enable/int masks, and switches USB role to device. IRQ top half reads status: VBUS changes schedule the thread, safe-mode interrupts call `pet_eud()`. The thread switches USB role to device or host and clears the VBUS interrupt latch.

State and persistence: `enabled` and `usb_attached` are in-memory flags; hardware registers and role switch state persist until disabled or platform reset. Risks include `enable_store()` not clearing `chip->enabled` on disable, no locking around sysfs/IRQ state, secure monitor failures requiring rollback, and wakeup state setup without a matching `device_init_wakeup(true)`. Test signals include sysfs enable/disable, SCM write failures, role-switch failure logs, VBUS and safe-mode IRQs, wake IRQ behavior, and remove while enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/qcom_eud.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/Kconfig

Purpose: Kconfig entry for the `sisusbvga` USB2VGA dongle driver targeting Net2280/SiS315 hardware.

Important APIs and types: defines `CONFIG_USB_SISUSBVGA` as a tristate option named "USB 2.0 SVGA dongle support (Net2280/SiS315)" and depends on `USB_MUSB_HDRC || USB_EHCI_HCD`. Help text states that USB 2.0 host support is required and module name is `sisusbvga`.

Control flow: build-system selection only; enabling this symbol causes the sibling Makefile to build `sisusbvga.o`. No runtime state exists in this file.

State and persistence: kernel configuration persists the selected tristate value. Risks include dependency coverage limited to MUSB/EHCI, which may exclude other USB 2.0-capable host-controller configurations, and the old specialized hardware option defaulting to off by user choice. Test signals include Kconfig dependency visibility, module build with `M`, built-in build with `Y`, and absence when dependencies are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/Makefile

Purpose: Build glue for the in-tree sisusb driver.

Important APIs and types: single assignment `obj-$(CONFIG_USB_SISUSBVGA) += sisusbvga.o`, tying the Kconfig symbol to the object built from the implementation source.

Control flow: kbuild includes `sisusbvga.o` only when `CONFIG_USB_SISUSBVGA` is enabled as built-in or module. No runtime behavior or state exists.

State and persistence: build output depends on `.config`. Risks are minimal; missing helper object names would matter only if the implementation were split. Test signals are compile/link success for `CONFIG_USB_SISUSBVGA=m` and `=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb.h -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb.h

Purpose: Main private/public definitions for the sisusb USB2VGA driver, covering versioning, buffers, USB endpoints, packet format, pseudo PCI address layout, VGA register offsets, device state, and ioctl ABI.

Important APIs and types: `struct sisusb_usb_data`, `struct sisusb_urb_context`, `struct sisusb_packet`, `struct sisusb_info`, `struct sisusb_command`, endpoint constants, buffer sizes, kref helper, endian correction macro, and ioctl numbers `SISUSB_COMMAND`, `SISUSB_GET_CONFIG_SIZE`, and `SISUSB_GET_CONFIG`.

Control flow: this header is consumed by the implementation and userspace ABI consumers. The implementation uses `sisusb_usb_data` to track USB interface/device, kref lifetime, URBs and buffers, readiness flags, framebuffer/MMIO/I/O bases, and chip identity. Command structures define register get/set/mask operations, clear-screen, text-mode handling, and mode setting.

State and persistence: no executable state, but it defines the runtime state layout and stable ioctl ABI. Risks include packed 10-byte USB command packets with endian-sensitive fields, fixed minor 133, fixed large output buffer sizes, legacy pseudo-PCI address assumptions, and ABI compatibility obligations for `struct sisusb_info` and commands. Test signals include ioctl structure size checks, big-endian packet conversion, endpoint mapping, open/disconnect kref paths in implementation, and userspace tool compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb_struct.h -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb_struct.h

Purpose: Mode-setting structure definitions shared by sisusb initialization and mode table code. These structures describe standard VGA modes, extended modes, reference timings, CRTC tables, VCLK programming, and a private context that points to all tables.

Important APIs and types: `struct SiS_St`, `SiS_StandTable`, `SiS_StResInfo_S`, `SiS_Ext`, `SiS_Ext2`, `SiS_CRT1Table`, `SiS_VCLKData`, `SiS_ModeResInfo`, and `SiS_Private`. `SiS_Private` stores I/O port bases, current mode flags, and const pointers to all table arrays.

Control flow: the implementation fills a `SiS_Private` context with register port addresses and table pointers, then mode-setting code indexes these structures by mode IDs, reference indices, and timing selectors to program the SiS315 graphics core through the USB bridge.

State and persistence: definitions only; actual mode state lives in driver/device registers. Risks include compact legacy VGA table layouts with many implicit indices, signed fields for ROM mode indexes, and no compile-time relationship enforcement between table indices and table lengths. Test signals include mode-switch coverage across table entries, structure layout compatibility with `sisusb_tables.h`, and build coverage for all referenced fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb_tables.h -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb_tables.h

Purpose: Static register and timing data for sisusb mode initialization. It contains DAC palettes, standard VGA table entries, mode resolution metadata, extended mode IDs, reference timing indices, CRT1 register sequences, and VCLK data.

Important APIs and types: arrays `SiS_MDA_DAC`, `SiS_CGA_DAC`, `SiS_EGA_DAC`, `SiS_VGA_DAC`, `SiSUSB_SModeIDTable`, `SiSUSB_ModeResInfo`, `SiSUSB_StandTable`, `SiSUSB_EModeIDTable`, `SiSUSB_RefIndex`, `SiSUSB_CRT1Table`, and `SiSUSB_VCLKData`. It depends on the structures in `sisusb_struct.h` and resolution constants/macros from the implementation context.

Control flow: mode-setting code indexes these arrays to translate requested SiS/VESA/display modes into VGA sequencer, graphics, attribute, CRTC, pixel-clock, and timing values. Sentinel entries such as mode ID `0xff`, ref flag `0xffff`, and zero VCLK entries terminate or reserve table ranges.

State and persistence: all content is read-only compile-time data. Hardware state changes only when implementation code programs registers from these tables. Risks include hand-maintained legacy timing constants, implicit cross-table indices (`REFindex`, CRTC indexes, VCLK indexes), custom VCLK slot filled at runtime, and high regression risk from mechanical edits. Test signals include comparing programmed modes to known-good timings, table sentinel handling, all supported depths/resolutions, and ensuring no index points past table bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb_tables.h -->
