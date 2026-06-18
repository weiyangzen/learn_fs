# Research: subset-b-005926 USB kernel headers

This grouped report covers forty USB-related Linux kernel headers under `sources/distributed-fs/ceph-client/include/linux/usb/`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/gadget.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/gadget.h`

## Purpose

`gadget.h` is the core device-side USB controller and gadget-driver contract. It defines the portable abstractions that function drivers use to talk to USB device controller hardware: `usb_request`, `usb_ep`, `usb_gadget`, `usb_gadget_driver`, endpoint capability matching, descriptor/string helpers, DMA mapping helpers, and UDC registration APIs.

## Important APIs, Types, and Constants

- `struct usb_request` is the gadget-side analogue of a host URB, carrying buffer, DMA, scatter-gather, stream, completion, status, and byte-count fields.
- `struct usb_ep_ops` and `struct usb_ep` define endpoint operations, endpoint capabilities, descriptor binding, max packet limits, burst/stream metadata, and driver-private storage.
- Endpoint wrappers include `usb_ep_enable()`, `usb_ep_disable()`, request allocation/free, queue/dequeue, halt/clear/wedge, FIFO status, and FIFO flush; disabled `CONFIG_USB_GADGET` builds get inert inline stubs.
- `struct usb_gadget_ops` exposes controller-wide hooks for frame number, remote wakeup, VBUS, pullup, UDC start/stop, speed/SSP rate, async callbacks, endpoint matching, and configuration checks.
- `struct usb_gadget` is the persistent UDC object with ep0, endpoint list, speed/state, OTG flags, controller quirks, power/wakeup/connection state, IRQ, and driver-model state.
- `struct usb_gadget_driver` defines bind/unbind, ep0 `setup()`, disconnect, suspend/resume, reset, UDC name matching, and single-bind state.
- Utility APIs cover gadget registration, string descriptors, descriptor copying/assignment/freeing, OTG descriptor creation, request DMA map/unmap, state changes, reset notification, request giveback, endpoint lookup, descriptor matching, VBUS notification, and endpoint autoconfiguration.

## Control Flow and Lifetimes

A UDC driver initializes a `usb_gadget`, adds it to the UDC core, and exposes endpoints in `gadget->ep_list`. A gadget function driver registers a `usb_gadget_driver`; the UDC core binds it to a matching gadget, invokes `bind()`, then ep0 `setup()` callbacks drive enumeration and configuration. Non-control traffic flows by allocating `usb_request` objects from an endpoint, filling buffers and flags, queueing them with `usb_ep_queue()`, and receiving completion callbacks with interrupts disabled. Teardown reverses this: disconnect/deactivate, disable endpoints, dequeue or complete pending requests, unbind the gadget driver, remove the gadget, and release descriptors/requests.

## State and Persistence Behavior

State is in memory and hardware, not on disk. `usb_gadget` persists for the UDC lifetime; endpoint enabled/claimed/descriptor state persists while configurations are active; requests persist from allocation until explicit free. Completion callbacks are interrupt-context sensitive. `state_lock` protects `state` and `teardown`, while endpoint queues and hardware FIFOs are controlled by UDC implementations. DMA mapping flags in `usb_request` prevent double mapping/unmapping.

## Dependencies and Integration Points

The header depends on Linux device model, configfs, workqueue, list, scatterlist, and USB Chapter 9 definitions. It integrates with UDC drivers, composite gadget functions, configfs USB gadget configuration, OTG support, DMA APIs, and platform-specific UDC controller headers. `gadget_configfs.h` builds on its string/configfs helpers.

## Risks and Edge Cases

Ep0 `setup()` and request completion callbacks may run in interrupt context and must not sleep. Request ownership must be clear: queued requests cannot be freed until completion/dequeue. Controller quirks such as no ZLP, no stall, no altsettings, or OUT alignment affect function driver behavior. DMA mapping helpers must match direction and request lifetime. Misdescribed endpoint descriptors can overrun controller limits or produce invalid enumeration.

## Test Signals

Useful signals include `CONFIG_USB_GADGET` builds with several UDCs and composite functions, configfs gadget creation/removal, ep0 enumeration tests, endpoint autoconfig tests across FS/HS/SS/SSP, request queue/dequeue cancellation tests, DMA and scatter-gather transfers, suspend/resume/remote wakeup tests, disconnect during active I/O, and builds with gadget support disabled to verify stub users.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/gadget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/gadget_configfs.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/gadget_configfs.h`

## Purpose

`gadget_configfs.h` provides macro helpers for configfs-backed USB gadget string attributes and per-language string groups. It is a small metaprogramming header used by gadget configfs implementations to avoid repeating show/store and group creation boilerplate.

## Important APIs, Types, and Constants

- `GS_STRINGS_W()` emits a configfs store method that resolves the owning structure with `to_<struct>()` and updates a string field through `usb_string_copy()`.
- `GS_STRINGS_R()` emits a show method returning the string field or an empty string.
- `GS_STRINGS_RW()` combines read/write generation with `CONFIGFS_ATTR()`.
- `USB_CONFIG_STRING_RW_OPS()` emits config item operations and item type objects for language-specific string entries.
- `USB_CONFIG_STRINGS_LANG()` emits `make_group`, `drop_item`, group operations, and type objects for creating language-specific string groups while enforcing duplicate-language and `MAX_USB_STRING_LANGS` limits.

## Control Flow and Lifetimes

When userspace creates a configfs string language directory, generated `*_strings_make()` allocates a language structure, validates the directory name through `check_user_usb_string()`, initializes the config group, checks for duplicate language IDs in the parent string list, enforces the maximum language count, and links the new object. Dropping the configfs item releases it through normal configfs reference handling.

## State and Persistence Behavior

The macros maintain in-kernel configfs object state only. The generated code stores language objects in the parent object's `string_list` and stores mutable string values in fields selected by the macro caller. Persistence is configfs lifetime persistence: objects exist while userspace keeps the configfs entries and references alive.

## Dependencies and Integration Points

The header depends on `linux/configfs.h`, USB gadget string helpers, `usb_string_copy()`, `check_user_usb_string()`, `MAX_USB_STRING_LANGS`, config item release callbacks, and caller-provided object layouts with `group`, `list`, `stringtab_dev`, `strings_group`, and `string_list` members.

## Risks and Edge Cases

Because it generates C identifiers and assumes structure names, misusing the macros fails at compile time or creates wrong object ownership. The language creation path must free allocation on every validation failure. String store semantics depend on `usb_string_copy()` sanitizing and allocating correctly. Duplicate-language checks are list-based and require external list locking/serialization from configfs operations.

## Test Signals

Build gadget configfs users, create/remove multiple language directories, test duplicate language IDs, exceed `MAX_USB_STRING_LANGS`, write/read generated string attributes, verify cleanup under allocation or validation failure, and run configfs reference-count diagnostics during gadget removal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/gadget_configfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/hcd.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/hcd.h`

## Purpose

`hcd.h` is the internal USB host-controller-driver contract used by usbcore and HCD implementations. It defines host controller state, host-driver callback vectors, URB enqueue/unlink/giveback helpers, DMA buffer pools, root hub support, transaction translator state, bandwidth calculations, monitor hooks, PCI/platform integration, and shared host-side enumeration utilities.

## Important APIs, Types, and Constants

- USB PID constants and hub request macros describe protocol-level values used by host controller and hub code.
- `struct usb_hcd` embeds `struct usb_bus`, reference counts, root hub polling/work state, driver hooks, PHY links, atomic flags, authorization defaults, MSI state, DMA pools, controller state, shared-HCD pointers, local memory pool, and controller-private tail storage.
- `struct hc_driver` is the HCD vtable: reset/start/stop/shutdown, IRQ, URB enqueue/dequeue, DMA mapping override, endpoint disable/reset, root hub control, suspend/resume, stream management, bandwidth management, address/enable/update/reset device, link power management, port power, and EH test-mode support.
- HCD flags describe memory/DMA/shared hardware and USB speed generation; runtime flags track hardware accessibility, root-hub polling, wakeup, dead state, authorization defaults, and deferred root hub registration.
- URB and endpoint helpers include `usb_hcd_link_urb_to_ep()`, unlink checks, submit/unlink/giveback, DMA map/unmap, endpoint flush/disable/reset, unlink synchronization, bandwidth allocation, frame number, and toggle macros.
- Creation and teardown APIs include `usb_create_hcd()`, `usb_create_shared_hcd()`, `usb_get_hcd()`, `usb_put_hcd()`, `usb_add_hcd()`, `usb_remove_hcd()`, PCI probe/remove/shutdown, and platform shutdown.
- Root hub/TT support includes `struct usb_tt`, `struct usb_tt_clear`, `usb_hub_clear_tt_buffer()`, hub class requests, `usb_calc_bus_time()`, power-management helpers, usbmon operations, and global usbcore IDR/kill queues.

## Control Flow and Lifetimes

An HCD driver allocates an HCD object, fills `hc_driver`, maps resources, initializes PHY/power, adds the HCD, and registers the root hub. usbcore submits URBs through `usb_hcd_submit_urb()`, which maps buffers, links URBs to endpoints, and calls `hc_driver->urb_enqueue()`. Completion flows back through the HCD, `usb_hcd_giveback_urb()`, optional BH work, usbmon hooks, and client completion callbacks. Unlink paths validate status with `usb_hcd_check_unlink_urb()`, call driver dequeue hooks, unlink from endpoint lists, and synchronize before endpoint teardown. Removal stops root hub polling, disables endpoints, tears down DMA pools, unmaps resources, and drops HCD references.

## State and Persistence Behavior

Runtime state includes root hub timer/status URB, controller flags, authorization policy, controller state machine, DMA pools, endpoint queues, bandwidth schedule, transaction translator clear work, and shared primary/secondary HCD relationships. No disk persistence exists. Concurrency is central: flags use atomic bit operations, URB lists use endpoint locks in implementation, giveback BH has spinlock-protected lists, bandwidth and address0 paths use mutexes, and usbcore globals use IDR locks and wait queues.

## Dependencies and Integration Points

The header depends on usbcore data structures, Linux interrupt, IDR, rwsem, DMA pool, gen_pool, PM, PCI, platform, PHY, hub Chapter 11 definitions, and optional usbmon. It is consumed by EHCI/OHCI/UHCI/xHCI and platform HCD glue, hub enumeration code, USB monitor, power-management paths, and PHY/OTG integration.

## Risks and Edge Cases

URB lifetime races are the main risk: completion, unlink, endpoint disable, and device disconnect can all converge. Shared HCDs must preserve primary/secondary ownership and resource teardown ordering. DMA mapping overrides must match unmapping and handle setup packets. Root hub polling flags can miss wakeups if not synchronized. Bandwidth callbacks must follow add/drop/check/reset sequencing. PCI AMD wakeup quirks and controller-dead handling are hardware-specific failure paths.

## Test Signals

Run builds for multiple HCDs and `CONFIG_USB_PCI`, `CONFIG_PM`, `CONFIG_USB_MON`, and `CONFIG_USB_HCD_TEST_MODE` combinations. Exercise device enumeration, disconnect during URB traffic, URB unlink storms, endpoint disable/reset, suspend/resume, root hub wakeup, transaction translator clear-buffer recovery, bandwidth-heavy isochronous endpoints, shared xHCI HCDs, DMA mapping debug, usbmon traces, and HCD remove/reprobe cycles.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/hcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/input.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/input.h`

## Purpose

`input.h` bridges USB device descriptors to the Linux input subsystem identity format. It contains one inline helper used by USB HID and other input-oriented drivers.

## Important APIs, Types, and Constants

- `usb_to_input_id(const struct usb_device *dev, struct input_id *id)` fills `input_id` with `BUS_USB`, USB vendor ID, product ID, and device BCD version.

## Control Flow and Lifetimes

The helper is called during input device setup before registering the input device. It copies immutable descriptor fields from the already-enumerated `usb_device` into caller-owned `input_id` storage.

## State and Persistence Behavior

No persistent state is stored in this header. It performs endian conversion from USB little-endian descriptor fields to CPU-native input IDs.

## Dependencies and Integration Points

It depends on `linux/usb.h`, `linux/input.h`, and byteorder helpers. It integrates USB device enumeration with input device registration, udev matching, and userspace-visible input identity fields.

## Risks and Edge Cases

The helper assumes `dev` points to a valid enumerated USB device and `id` is writable. It does not include interface subclass/protocol, so drivers needing more specific identity must add fields elsewhere.

## Test Signals

Validate with USB HID/input device registration, inspect `/sys/class/input/*/id`, verify endian-correct vendor/product/version values, and build drivers including this header across USB/input configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/iowarrior.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/iowarrior.h`

## Purpose

`iowarrior.h` defines the userspace ioctl ABI for Code Mercenaries IOWarrior USB devices. It describes read/write ioctls and the legacy-compatible information structure returned by `IOW_GETINFO`.

## Important APIs, Types, and Constants

- `CODEMERCS_MAGIC_NUMBER` is the ioctl type value.
- `IOW_WRITE` and `IOW_READ` pass `__u8 *` buffers for device report writes and reads.
- `struct iowarrior_info` exposes vendor, product, nine-byte serial string, revision, USB speed, power draw, interface number, and report size.
- `IOW_GETINFO` returns `struct iowarrior_info` to userspace.

## Control Flow and Lifetimes

Userspace opens the IOWarrior character device and issues ioctls. The driver copies data between userspace buffers and USB reports, or fills the info structure from probed descriptor/interface state. This header only fixes the ABI; implementation handles USB URB submission and device lifetime.

## State and Persistence Behavior

The ioctl definitions are persistent ABI. Device information is runtime state derived from descriptors and driver bookkeeping. There is no on-disk state.

## Dependencies and Integration Points

It depends on ioctl encoding macros and fixed-size UAPI integer types. It integrates the USB IOWarrior driver with legacy 2.4-era userspace tools that expect this info ioctl.

## Risks and Edge Cases

ABI changes would break userspace. The `serial[9]` field is fixed and may be empty. Read/write ioctls use raw pointers, so driver implementation must validate copy sizes and disconnected-device paths carefully.

## Test Signals

Compile the IOWarrior driver, run ioctl ABI tests for all commands, verify 32/64-bit userspace compatibility, disconnect during ioctl, inspect info fields against descriptors, and test devices with and without serial numbers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/iowarrior.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/irda.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/irda.h`

## Purpose

`irda.h` defines USB IrDA bridge class constants, class-specific requests, class descriptor layout, capability bitmasks, and inbound/outbound data headers. It is a protocol binding header for USB-to-IrDA bridge drivers.

## Important APIs, Types, and Constants

- Class metadata includes `USB_SUBCLASS_IRDA`, class-specific request IDs, and descriptor type `USB_DT_CS_IRDA`.
- Capability masks describe supported data sizes, window sizes, minimum turnaround times, baud rates, and additional BOF counts.
- `struct usb_irda_cs_descriptor` is the packed class-specific descriptor with spec revision, capability bitmaps, rate sniffing, and max unicast list size.
- Data-format constants define media-busy status, link-speed encodings, and outbound extra-BOF encodings.
- `struct usb_irda_inbound_header` and `struct usb_irda_outbound_header` wrap per-packet IrDA status/change bytes.

## Control Flow and Lifetimes

During probe, a driver parses the class-specific descriptor and negotiates link capabilities with class requests. During data I/O, inbound packets carry `bmStatus`; outbound packets carry `bmChange` to request speed or BOF changes. Lifetimes follow USB interface binding and URB buffers.

## State and Persistence Behavior

The header defines wire-format state, not persistent kernel state. Device capabilities persist for the bound device session after descriptor parsing; negotiated link speed and BOF changes are runtime protocol state.

## Dependencies and Integration Points

It depends on packed USB integer types and integrates USB application-specific class devices with IrDA stack drivers. The little-endian fields must be converted by consumers.

## Risks and Edge Cases

Packed descriptor parsing must validate lengths before dereference. Reserved speed/BOF values must be rejected or ignored. Media-busy and rate-change status can race with queued packets. Bitmaps are capability sets, not scalar values, so choosing an unsupported mode breaks interoperability.

## Test Signals

Test descriptor parsing with valid and malformed descriptors, class request handling, speed change paths, media-busy reporting, all supported baud masks, short packet handling, endian conversion, and disconnect during active IrDA traffic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/irda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/isp116x.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/isp116x.h`

## Purpose

`isp116x.h` defines platform data for the Philips/NXP ISP116x USB host controller driver. Board code uses it to describe electrical and timing quirks for platform-bus devices.

## Important APIs, Types, and Constants

- `struct isp116x_platform_data` exposes flags for internal downstream pull-down resistors, on-chip overcurrent detection, interrupt polarity, interrupt trigger mode, and remote wakeup.
- `delay(struct device *dev, int delay)` is a board-provided callback for strict inter-I/O timing between register accesses.

## Control Flow and Lifetimes

Platform setup attaches this structure to the device before driver probe. The ISP116x driver reads the flags during initialization and calls `delay()` around register accesses when the board requires precise bus timing. The data must outlive probe and normal driver operation.

## State and Persistence Behavior

The structure is static platform configuration. It does not store mutable runtime state, but selected flags affect controller power, interrupt, and wakeup behavior for the lifetime of the device.

## Dependencies and Integration Points

It integrates board initialization code, platform bus registration, and the ISP116x host controller driver. It references `struct device` in the delay callback.

## Risks and Edge Cases

Incorrect interrupt polarity or edge/level selection can lose interrupts. Omitting required I/O delays can corrupt register access. Remote wakeup increases suspend power because clocks remain active. Overcurrent and resistor flags must match board wiring.

## Test Signals

Probe on boards using internal/external resistors, verify interrupt delivery, run register stress with timing-sensitive accesses, test suspend/resume and remote wakeup, and validate overcurrent behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/isp116x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/isp1301.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/isp1301.h`

## Purpose

`isp1301.h` defines I2C register addresses, bit masks, and a device-tree lookup helper for the NXP ISP1301 USB transceiver. It is used by PHY/OTG drivers that need to program mode, pull-up/down, VBUS, and interrupt behavior.

## Important APIs, Types, and Constants

- Mode control register definitions cover speed, suspend, DAT/SE0, transparent/UART modes, audio, power switch, and 2.7 V regulator controls.
- OTG control definitions cover D+/D- pullups and pulldowns, ID pulldown, VBUS drive/discharge/charge, and session-valid status bits.
- Interrupt source/latch/falling/rising registers and masks cover VBUS, session, line states, ID state, B-disconnect/A-connect, and comparator interrupts.
- `ISP1301_I2C_REG_CLEAR_ADDR` identifies the register-address modifier used for clear accesses.
- `isp1301_get_client(struct device_node *node)` resolves the I2C client from device tree.

## Control Flow and Lifetimes

Consumers obtain an I2C client, configure mode and OTG registers, enable interrupt edge/latch masks, and read status during cable/session events. Set/clear register addressing allows individual bits to be toggled without full read-modify-write when the hardware supports it.

## State and Persistence Behavior

Hardware registers hold transceiver state until changed, reset, or power-cycled. Kernel state resides in the driver that owns the I2C client. This header only defines register ABI.

## Dependencies and Integration Points

It depends on OF device-node support and integrates ISP1301 I2C client drivers with USB PHY/OTG controller code. It is commonly paired with `usb/phy.h` and `usb/otg.h` consumers.

## Risks and Edge Cases

Set/clear register aliases must be used correctly or bits may be overwritten. OTG VBUS drive/discharge settings are board-sensitive and can damage or confuse external power circuitry. Interrupt latch handling must clear events without losing edges. Device-tree lookup can fail if the node relationship is wrong.

## Test Signals

Validate I2C register reads/writes, OTG ID/VBUS transitions, interrupt edge/latch behavior, suspend/resume, session-valid thresholds, and device-tree client resolution with missing or malformed nodes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/isp1301.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ljca.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/ljca.h`

## Purpose

`ljca.h` defines the client-facing API for Intel La Jolla Cove Adapter USB devices. LJCA exposes auxiliary child devices for GPIO, I2C, SPI, and event-driven functions, and this header describes client identity, auxiliary-device conversion, event callbacks, and command transfer helpers.

## Important APIs, Types, and Constants

- `LJCA_MAX_GPIO_NUM` fixes the GPIO bitmap capacity.
- `auxiliary_dev_to_ljca_client()` converts an auxiliary device to its enclosing `ljca_client`.
- `ljca_event_cb_t` is an interrupt-context callback receiving command ID and transient event payload.
- `struct ljca_client` stores client type/id, adapter link, `auxiliary_device`, adapter backpointer, callback context, callback pointer, and spinlock.
- `struct ljca_gpio_info`, `struct ljca_i2c_info`, and `struct ljca_spi_info` describe child-device capabilities.
- `ljca_register_event_cb()`, `ljca_unregister_event_cb()`, `ljca_transfer()`, and `ljca_transfer_noack()` are the exported client operations.

## Control Flow and Lifetimes

The parent LJCA USB driver discovers adapter functions and registers auxiliary devices. Child drivers obtain `ljca_client`, register optional event callbacks, issue synchronous command/response transfers with `ljca_transfer()`, or fire no-ack commands with `ljca_transfer_noack()`. Event payloads are valid only for the callback invocation, so clients must copy data they retain.

## State and Persistence Behavior

Client objects persist while the auxiliary device is registered. Callback state is protected by `event_cb_lock`. Transfer state and firmware responses are transient. No disk persistence exists.

## Dependencies and Integration Points

It depends on Linux auxiliary bus, lists, spinlocks, bitmaps, and fixed-width types. It integrates the LJCA USB adapter core with GPIO, I2C, SPI, and other auxiliary child drivers.

## Risks and Edge Cases

Callbacks run in interrupt context and cannot sleep. Event payload lifetime is short. Register/unregister must be synchronized with in-flight events to avoid callback-after-free. `ljca_transfer()` requires callers to size input buffers correctly because return value is the actual response length.

## Test Signals

Probe LJCA devices, bind GPIO/I2C/SPI auxiliary drivers, run synchronous and no-ack transfers, generate firmware events, unregister callbacks during event storms, test disconnect during transfer, and use lockdep for callback spinlock paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ljca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/m66592.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/m66592.h`

## Purpose

`m66592.h` defines platform data for the Renesas M66592 USB device controller. It lets board code describe chip placement, endian behavior, oscillator selection, voltage interface, and write-strobe wiring.

## Important APIs, Types, and Constants

- `M66592_PLATDATA_XTAL_12MHZ`, `_24MHZ`, and `_48MHZ` encode external oscillator choices.
- `struct m66592_platdata` contains `on_chip`, `endian`, `xtal`, `vif`, and `wr0_shorted_to_wr1` bitfields.

## Control Flow and Lifetimes

Board/platform code provides the structure before UDC driver probe. The driver reads it during initialization to program controller clock, bus width/endian access mode, voltage interface, and external-controller wiring assumptions.

## State and Persistence Behavior

The data is static platform configuration. Runtime controller state lives in the M66592 driver and hardware registers.

## Dependencies and Integration Points

It integrates platform device registration with the Renesas M66592 gadget driver. It has no direct includes beyond kernel integer types supplied by including context.

## Risks and Edge Cases

Wrong oscillator, endian, or voltage flags can prevent enumeration or corrupt register I/O. The external-only fields should not be applied to on-chip variants. Board wiring for write strobes must match `wr0_shorted_to_wr1`.

## Test Signals

Build and probe M66592 platform devices for on-chip and external variants, test register access endian paths, enumerate gadget functions, verify oscillator setup, and exercise suspend/resume and disconnect.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/m66592.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/mctp-usb.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/mctp-usb.h`

## Purpose

`mctp-usb.h` defines common protocol constants for the DMTF MCTP-over-USB transport binding. It can be shared by host and gadget implementations.

## Important APIs, Types, and Constants

- `struct mctp_usb_hdr` is the packed transport header with big-endian DMTF ID, reserved byte, and payload length.
- `MCTP_USB_XFER_SIZE` fixes USB transfer size at 512 bytes.
- `MCTP_USB_BTU`, `MCTP_USB_MTU_MIN`, and `MCTP_USB_MTU_MAX` define transport payload limits.
- `MCTP_USB_DMTF_ID` identifies the DMTF binding.

## Control Flow and Lifetimes

Transmitters prepend `mctp_usb_hdr`, set the DMTF ID and length, and send within the transfer/MTU limits. Receivers validate ID, reserved fields, and length before handing payload to the MCTP core. This header does not implement flow control.

## State and Persistence Behavior

Only wire-format state is defined. Runtime packet queues, endpoint state, and MCTP network state live in host/gadget drivers.

## Dependencies and Integration Points

It depends on kernel fixed-width types and endian annotations. It integrates USB transport drivers with the MCTP stack and DMTF DSP0283 framing.

## Risks and Edge Cases

The `len` field is one byte, so maximum MTU must account for header size and cannot exceed `U8_MAX - sizeof(header)`. Consumers must validate big-endian ID and avoid trusting malformed lengths. Reserved-byte handling should follow the binding specification.

## Test Signals

Test host/gadget loopback, minimum and maximum MTU packets, malformed IDs, oversized lengths, short transfers, endian conversion, and MCTP stack registration over USB endpoints.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/mctp-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/midi-v2.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/midi-v2.h`

## Purpose

`midi-v2.h` defines USB MIDI 2.0 class descriptor constants and packed descriptor layouts. It extends the older USB MIDI definitions with group terminal block descriptors, MIDIStreaming 2.0 revisions, protocol identifiers, and helper fields used by ALSA USB MIDI parsing.

## Important APIs, Types, and Constants

- Descriptor constants include class-specific group terminal block descriptor type `USB_DT_CS_GR_TRM_BLOCK`, endpoint subtype `USB_MS_GENERAL_2_0`, group terminal block subtypes, and MIDIStreaming revisions.
- Protocol constants identify MIDI 1.0 over UMP variants, MIDI 2.0, and jitter-reduction timestamp variants.
- Group terminal block type constants identify bidirectional, input-only, and output-only groups.
- The header includes USB MIDI 1.0 definitions and builds on their jack/interface subtype values.
- Packed descriptor structs define group terminal block headers and block entries for parsing class-specific descriptors.

## Control Flow and Lifetimes

USB audio/MIDI drivers parse interface and endpoint descriptors during probe. For MIDI 2.0, they locate group terminal block descriptors, read revision/protocol/group counts, and map UMP groups to ALSA rawmidi/UMP endpoints. Descriptor data is immutable for the device configuration lifetime.

## State and Persistence Behavior

The header defines descriptor ABI and constants. Runtime MIDI endpoint state, UMP group mappings, and stream state live in the ALSA USB MIDI implementation.

## Dependencies and Integration Points

It depends on `linux/types.h` and `linux/usb/midi.h`. It integrates USB class descriptor parsing with ALSA MIDI 2.0/UMP support and generic USB descriptor walking.

## Risks and Edge Cases

Packed descriptor parsing must check `bLength` before accessing trailing fields. Drivers must distinguish MIDI 1.0 and 2.0 revisions and handle unknown protocol values. Group counts and first-group indexes can describe invalid or overlapping ranges if not validated.

## Test Signals

Probe MIDI 2.0 devices, parse descriptors with multiple group terminal blocks, validate fallback for MIDI 1.0 descriptors, fuzz descriptor lengths/protocol IDs, verify ALSA UMP group exposure, and test hot unplug during active MIDI streams.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/midi-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/musb-ux500.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/musb-ux500.h`

## Purpose

`musb-ux500.h` provides platform glue declarations for the UX500 variant of the Mentor USB MUSB controller. It exists so board/platform code and the MUSB driver can exchange UX500-specific resources.

## Important APIs, Types, and Constants

- The header is intentionally small and primarily declares the UX500 platform interface consumed by the MUSB glue driver.
- It sits next to `musb.h`, which defines the generic MUSB platform data and mode constants.

## Control Flow and Lifetimes

Platform code registers the UX500 MUSB device and passes platform data/resources to the glue driver. The glue driver then initializes the generic MUSB core with UX500-specific clocks, interrupts, DMA, and mode configuration.

## State and Persistence Behavior

No direct state is stored in this header. Runtime state is in the UX500 glue driver and generic MUSB core.

## Dependencies and Integration Points

It integrates ST-Ericsson UX500 platform code with `drivers/usb/musb/` and the generic `musb_hdrc_platform_data` contract from `musb.h`.

## Risks and Edge Cases

The main risk is platform/API drift: if the UX500 glue driver expects fields or callbacks not matched by board code, probe fails or role switching is broken. Because the header is glue-only, test coverage must come from platform driver builds.

## Test Signals

Build UX500 MUSB glue, probe on relevant platform/device-tree configuration, exercise host/peripheral mode, suspend/resume, and DMA/PIO transfer paths through the generic MUSB core.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/musb-ux500.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/musb.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/musb.h`

## Purpose

`musb.h` defines board/platform data and mode constants for Mentor Graphics MUSB HDRC controllers. It is the public configuration contract between platform glue and the MUSB core.

## Important APIs, Types, and Constants

- Mode constants describe undefined, host, peripheral, OTG, and dual-role operation.
- Power and endpoint limit constants describe MUSB capability and board power assumptions.
- `struct musb_hdrc_eps_bits` and endpoint configuration structures describe FIFO sizing and endpoint capabilities.
- `struct musb_hdrc_config` describes multipoint support, dynamic FIFO, soft connect, DMA mode, endpoint count, RAM bits, and FIFO configuration.
- `struct musb_hdrc_platform_data` carries mode, power budget, min power, platform-specific config pointer, board callbacks, and PHY/clock-related integration fields.

## Control Flow and Lifetimes

Platform glue fills `musb_hdrc_platform_data` and registers the controller. The MUSB core reads mode, FIFO, endpoint, and power data during probe, initializes PHY and controller registers, then exposes host, gadget, or OTG behavior depending on mode. The platform data must remain valid while the controller is active.

## State and Persistence Behavior

The header defines static controller configuration. Runtime role, endpoint queue, DMA, and PHY state live in the MUSB driver. Mode selection and FIFO layout persist for the driver instance.

## Dependencies and Integration Points

It integrates MUSB platform glue, USB host/gadget/OTG subsystems, PHY providers, and board power management. It is used by SoC-specific MUSB headers such as `musb-ux500.h`.

## Risks and Edge Cases

Incorrect FIFO or endpoint configuration can break enumeration or transfer scheduling. Host/peripheral/OTG mode mismatches with hardware wiring cause role-switch failures. Power budget fields affect bus power advertisements. Dynamic FIFO assumptions must match controller synthesis options.

## Test Signals

Build MUSB host, gadget, and OTG configurations; probe platform devices with static and dynamic FIFOs; run bulk/control/interrupt transfers; test VBUS/session changes, suspend/resume, disconnect/reconnect, and DMA fallback to PIO.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/musb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/net2280.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/net2280.h`

## Purpose

`net2280.h` maps the PLX/NetChip NET2280/USB3380 PCI USB device-controller register layout. It provides packed C structures and bit definitions for device, PCI, DMA, dedicated endpoint, and configurable endpoint registers used by the gadget controller driver.

## Important APIs, Types, and Constants

- Register structs include device/interrupt registers, USB control/status registers, PCI master registers, DMA channel registers, dedicated endpoint registers, and configurable endpoint registers.
- Bit definitions cover PCI interrupts/errors, DMA channel enable/status/count/descriptor fields, USB standard request auto-response controls, VBUS/suspend/resume/remote wakeup state, GPIO controls, endpoint configuration, endpoint response bits, FIFO status, endpoint interrupt enables, and endpoint transfer status.
- The register structs are packed to mirror BAR offsets and hardware register spacing.

## Control Flow and Lifetimes

The net2280 driver maps PCI BARs and casts/register-offsets into these structures. Probe configures PCI, USB, DMA, endpoint, and interrupt registers. During I/O, endpoint IRQs and DMA completion bits drive request completion. Control endpoint handling uses setup registers and standard-response bits. Teardown disables interrupts, endpoints, DMA, and PCI mastering before unmapping.

## State and Persistence Behavior

State lives in hardware registers and driver memory. Register bits persist until changed by software, hardware events, reset, or PCI power transitions. DMA descriptors and endpoint FIFOs represent transient transfer state.

## Dependencies and Integration Points

It integrates PCI gadget controller code with `usb/gadget.h`, DMA APIs, interrupt handling, and platform differences between NET2280 and USB3380-style register variants.

## Risks and Edge Cases

Packed register structures must match hardware offsets exactly. Interrupt status bits are often write-to-clear or latched, so wrong ordering can lose events. DMA descriptor/count fields require endian and alignment discipline. Endpoint FIFO overflow/underflow and control status phase bits are timing-sensitive. PCI error bits must not be ignored.

## Test Signals

Probe NET2280/USB3380 hardware, enumerate several gadget functions, run DMA and PIO transfers on all configurable endpoints, exercise control requests, suspend/resume/remote wakeup, GPIO interrupts, PCI error injection, endpoint stall/clear, FIFO flush, and hot removal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/net2280.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/of.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/of.h`

## Purpose

`of.h` declares Open Firmware/device-tree helpers for USB controllers, hubs, devices, interfaces, PHYs, OTG capabilities, connect types, and companion devices.

## Important APIs, Types, and Constants

- `of_usb_get_dr_mode_by_phy()`, `of_usb_get_phy_mode()`, and `of_usb_update_otg_caps()` parse USB role, PHY mode, and OTG capability properties.
- `of_usb_host_tpl_support()` checks target peripheral list support.
- `usb_of_get_connect_type()`, `usb_of_get_device_node()`, `usb_of_has_combined_node()`, and `usb_of_get_interface_node()` map USB topology to firmware nodes.
- `usb_of_get_companion_dev()` resolves companion devices.
- Non-OF or non-USB builds provide safe default stubs returning unknown/false/null/zero.

## Control Flow and Lifetimes

Controller and hub code call these helpers during probe/enumeration to interpret device-tree properties. Returned device nodes or devices are used to configure role, PHY, OTG, port connect type, and interface-specific child devices. Lifetime/refcount details are implemented in OF helper code.

## State and Persistence Behavior

The header itself stores no state. It converts static firmware description into runtime USB configuration decisions.

## Dependencies and Integration Points

It depends on USB, Chapter 9, OTG, PHY, and OF configuration. It integrates device-tree bindings with host controllers, gadget controllers, hubs, onboard devices, and USB interface child devices.

## Risks and Edge Cases

Callers must handle stub defaults when `CONFIG_OF` or `CONFIG_USB_SUPPORT` is disabled. Firmware nodes may be absent, combined, or mismatched with dynamic USB topology. Role and PHY mode parsing must tolerate unknown values. Node reference handling must be correct in implementation users.

## Test Signals

Build with and without OF/USB support, parse `dr_mode`, `phy_type`, OTG capability, and connect-type properties, test hub port child nodes, combined node detection, interface node lookup, companion device resolution, and malformed device-tree data.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/of.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ohci_pdriver.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/ohci_pdriver.h`

## Purpose

`ohci_pdriver.h` defines platform data for generic OHCI host controller platform drivers. It captures endian quirks, port count, and board-specific power callbacks.

## Important APIs, Types, and Constants

- `struct usb_ohci_pdata` contains `big_endian_desc`, `big_endian_mmio`, `no_big_frame_no`, and `num_ports`.
- `power_on()`, `power_off()`, and `power_suspend()` callbacks manage clocks, regulators, and suspend-only hotplug/VBUS power.

## Control Flow and Lifetimes

Platform code attaches `usb_ohci_pdata` before probe. The OHCI platform driver reads endian and port fields while initializing the HCD and calls power callbacks during probe, remove, and suspend transitions.

## State and Persistence Behavior

The structure is static platform configuration. Runtime HCD and OHCI register state live in the host controller driver.

## Dependencies and Integration Points

It integrates generic OHCI platform glue with board/SoC power management and endian-specific OHCI accessors. It references `struct platform_device`.

## Risks and Edge Cases

Wrong endian flags corrupt descriptor or MMIO interpretation. Power callbacks must be ordered with HCD registration/removal to avoid interrupts against unpowered hardware. `power_suspend()` must leave enough circuitry alive for hotplug/wakeup if promised.

## Test Signals

Probe OHCI platform controllers on endian variants, enumerate devices, suspend/resume with wakeup, test remove after failed probe, validate port count, and use DMA/API debugging for descriptor endian mistakes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ohci_pdriver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/onboard_dev.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/onboard_dev.h`

## Purpose

`onboard_dev.h` declares helpers for creating and destroying platform devices that represent onboard USB devices attached below a USB parent device.

## Important APIs, Types, and Constants

- `onboard_dev_create_pdevs(struct usb_device *parent_dev, struct list_head *pdev_list)` creates platform devices for onboard children.
- `onboard_dev_destroy_pdevs(struct list_head *pdev_list)` tears them down.
- Stubs are no-ops when `CONFIG_USB_ONBOARD_DEV` is disabled.

## Control Flow and Lifetimes

Hub or USB core code calls create when a parent USB device appears and destroy during disconnect/removal. The caller supplies a list to track created platform devices for later cleanup.

## State and Persistence Behavior

Runtime state is the list of created platform devices. The header has no persistent state and compiles to no-op behavior without onboard-device support.

## Dependencies and Integration Points

It integrates USB device enumeration with platform drivers for fixed onboard components, often described by firmware. It uses `struct usb_device` and `struct list_head`.

## Risks and Edge Cases

Create/destroy calls must be paired to avoid leaked platform devices. Callers must handle disabled-config stubs. Disconnect ordering matters because child platform devices may still hold references to resources under the USB parent.

## Test Signals

Build with and without `CONFIG_USB_ONBOARD_DEV`, enumerate boards with onboard USB child devices, verify platform child creation/removal, hot unplug parent hubs, and check leak/refcount diagnostics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/onboard_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/otg-fsm.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/otg-fsm.h`

## Purpose

`otg-fsm.h` defines the USB OTG finite state machine state container, timer identifiers, operation callbacks, inline operation wrappers, protocol constants, and the `otg_statemachine()` entry point.

## Important APIs, Types, and Constants

- Protocol constants identify undefined, host, and gadget modes.
- OTG status selector, host request flag, and HNP polling interval constants support OTG/EH flows.
- `enum otg_fsm_timer` enumerates standard and auxiliary timers such as A_WAIT_VRISE, A_WAIT_BCON, B_SE0_SRP, and A_WAIT_ENUM.
- `struct otg_fsm` stores hardware inputs, application inputs, auxiliary inputs, outputs, internal variables, timeout flags, ops, `usb_otg` pointer, current protocol, mutex, host request flag, HNP delayed work, and state-change flag.
- `struct otg_fsm_ops` supplies VBUS, local connect/SOF, SRP/ADP, timer, host, and gadget control callbacks.
- Inline wrappers validate optional callbacks, update output state where appropriate, and return `-EOPNOTSUPP` when unsupported.

## Control Flow and Lifetimes

An OTG controller owns `struct otg_fsm`, updates input bits from hardware/application events, schedules or cancels timers through callbacks, and calls `otg_statemachine()` under the FSM lock. The FSM toggles outputs through wrappers, starts/stops host or gadget roles, and uses delayed HNP polling when initialized.

## State and Persistence Behavior

The FSM object is persistent runtime state for the OTG controller. Inputs mirror hardware and policy state; outputs cache last-applied hardware actions to avoid redundant callbacks; timer timeout fields drive transitions. No disk persistence exists.

## Dependencies and Integration Points

It depends on mutex, errno, delayed work through including context, and `struct usb_otg`. It integrates OTG transceiver/controller drivers with host and gadget controller start/stop paths.

## Risks and Edge Cases

Missing callbacks produce `-EOPNOTSUPP` and can block required state transitions. Input bits must be updated atomically with FSM execution. Timer callbacks must match OTG timing requirements. HNP polling work must be canceled during teardown. Cached output fields must not diverge from actual hardware state after reset.

## Test Signals

Exercise A-device and B-device state transitions, SRP, HNP, ADP probing/sensing, timer expiration paths, host/gadget start failures, ID/VBUS changes, teardown with delayed work pending, and lockdep around the FSM mutex.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/otg-fsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/otg.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/otg.h`

## Purpose

`otg.h` defines the shared USB OTG object and capability model used between USB host controllers, gadget controllers, and PHY/transceiver drivers. It also declares dual-role mode parsing helpers.

## Important APIs, Types, and Constants

- `struct usb_otg` stores default-A role, generic PHY, legacy `usb_phy`, host bus, gadget, current OTG state, and callbacks to set host/peripheral, set VBUS, start SRP, and start HNP.
- `struct usb_otg_caps` records OTG revision and HNP/SRP/ADP support.
- `usb_otg_state_string()` converts OTG state to text.
- Inline wrappers `otg_start_hnp()`, `otg_set_vbus()`, `otg_set_host()`, `otg_set_peripheral()`, and `otg_start_srp()` dispatch optional callbacks or return `-ENOTSUPP`.
- `usb_bus_start_enum()` starts host enumeration on a port.
- `enum usb_dr_mode`, `usb_get_dr_mode()`, and `usb_get_role_switch_default_mode()` describe host/peripheral/OTG/default role policy.

## Control Flow and Lifetimes

PHY/OTG glue creates a `usb_otg`, binds host and gadget sides through `set_host()` and `set_peripheral()`, then role changes drive VBUS, SRP, HNP, and enumeration callbacks. Device-tree or firmware role parsing chooses the initial mode/default.

## State and Persistence Behavior

OTG state is runtime in memory and attached hardware. Host/gadget pointers must remain valid while bound. Capability data may come from firmware and remains stable for the controller.

## Dependencies and Integration Points

It depends on generic PHY, legacy USB PHY, USB bus/gadget definitions, and `usb_phy` OTG state enums. It integrates dual-role controller glue, role-switch code, host enumeration, gadget UDCs, and OF helpers.

## Risks and Edge Cases

Callbacks are optional; callers must handle `-ENOTSUPP`. Binding host/gadget out of order can leave partial OTG state. HNP/SRP should only be attempted when capability and role permit it. Role parsing must tolerate absent or invalid firmware properties.

## Test Signals

Test host-only, peripheral-only, and OTG modes; bind/unbind host and gadget; SRP/HNP role swaps; VBUS control; enum start; firmware `dr_mode` parsing; and disabled callback paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/otg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/pd.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/pd.h`

## Purpose

`pd.h` is the central USB Power Delivery protocol definition header. It defines PD control/data/extended message types, message headers, extended headers, wire-format PD messages, source/sink extended data blocks, PDO/RDO/APDO helpers, status/PPS/country structures, timers, and many bitfield helpers used by TCPM/TCPCI and Type-C drivers.

## Important APIs, Types, and Constants

- Enums define PD control messages, data messages, and extended messages across PD revisions.
- Header macros encode/decode message type, power role, data role, revision, message ID, data-object count, and extended-header bit; inline helpers decode little-endian headers.
- Extended header macros encode/decode chunking, chunk number, request-chunk, and data size.
- `struct pd_message` and `struct pd_chunked_ext_message_data` describe the on-wire packed message layout.
- `count_chunked_data_objs()` computes data-object count for chunked extended data.
- PDO helpers cover fixed, battery, variable, programmable supply, and adjustable supply objects, with units for voltage/current/power.
- RDO helpers encode fixed, battery, programmable, and adjustable requests and expose flags such as giveback, capability mismatch, USB suspend, communications capable, and no-suspend.
- Additional packed structures describe sink caps extended, PPS status, status messages, country info/codes, revision, and battery-related payloads.

## Control Flow and Lifetimes

TCPM and TCPC drivers construct PD headers and payload objects, transmit them through a port controller, parse received messages, and advance the PD policy engine. PDOs advertise capabilities; RDOs request a selected object; extended messages may be chunked and require size/count calculations. The header supplies encoding/decoding primitives while policy and retransmission live in implementation files.

## State and Persistence Behavior

PD protocol state such as message IDs, negotiated revision, power/data roles, partner capabilities, and selected PDOs lives in TCPM runtime state. The header defines immutable wire-format constants and helper macros. Packed structs are transient buffers as seen on the wire.

## Dependencies and Integration Points

It depends on bitfield helpers, kernel types, and Type-C role enums. It is included by `tcpm.h`, `tcpci.h`, `pd_vdo.h`, and Type-C/PD policy code. It bridges USB PD wire encoding to Type-C power, data, and alt-mode management.

## Risks and Edge Cases

Bitfield units are easy to misuse: fixed PDO voltage is in 50 mV units, current in 10 mA units, and APDO/AVS have different units. Header count must match payload size. Extended chunk sizing must include the extended header offset. PD revision gates message types and fields. Packed structures require endian conversion before arithmetic.

## Test Signals

Run TCPM PD negotiation tests for source/sink roles, fixed/PPS/AVS PDOs, RDO selection, extended messages, chunked payloads, hard/soft reset, role swaps, malformed headers, endian conversion, and PD revision compatibility.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/pd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/pd_ado.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/pd_ado.h`

## Purpose

`pd_ado.h` defines USB PD Alert Data Object bitfields and helper macros. ADOs carry partner alerts for battery, OCP, OTP, operating-condition changes, and related PD status events.

## Important APIs, Types, and Constants

- Macros define alert bits and masks for fixed batteries, hot-swappable batteries, battery status changes, OCP, OTP, operating condition, source input, overvoltage, and extended alerts.
- Helper macros construct ADO values and extract alert domains for TCPM policy handling.

## Control Flow and Lifetimes

When a PD partner sends an Alert message, TCPM parses the ADO using these masks and dispatches policy actions such as querying battery status or responding to protection events. The header does not implement policy.

## State and Persistence Behavior

ADO values are transient PD payloads. Persistent alert handling state lives in TCPM/Type-C policy and power-supply code.

## Dependencies and Integration Points

It integrates PD alert messages from `pd.h` with TCPM policy and Type-C power-supply/partner-management code. It depends on bit macros from kernel headers through including context.

## Risks and Edge Cases

Different alert fields overlap in a single 32-bit object, so masks and shifts must be used precisely. Unsupported extended alerts should not be treated as fatal. Battery slot bitmaps require validation against known partner battery count.

## Test Signals

Inject PD Alert messages with each alert bit set, validate battery and protection event dispatch, fuzz reserved bits, and test partners with no batteries or hot-swappable battery reports.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/pd_ado.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/pd_bdo.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/pd_bdo.h`

## Purpose

`pd_bdo.h` defines USB PD Battery Data Object helpers. BDOs encode battery present/capability/status information exchanged through PD battery messages.

## Important APIs, Types, and Constants

- Macros encode and decode battery status/capability fields, including invalid/unknown states where defined by the PD specification.
- The header supplies field positions and masks used by TCPM when parsing or constructing PD battery payloads.

## Control Flow and Lifetimes

PD policy code receives battery status/capability messages, decodes BDO fields, and updates partner/power-supply status. For outbound responses, policy code encodes BDOs from local battery information.

## State and Persistence Behavior

BDOs are transient 32-bit PD payload objects. Battery state persistence belongs to power-supply drivers and TCPM partner state.

## Dependencies and Integration Points

It integrates USB PD extended battery messages with Type-C partner management and Linux power-supply reporting.

## Risks and Edge Cases

Unknown or invalid battery values must be distinguished from real capacity/status values. Policy code must validate battery references against partner capabilities. Reserved bits should be ignored on receive and zeroed on transmit.

## Test Signals

Test battery capability/status PD exchanges, unknown-capacity handling, invalid battery indexes, reserved-bit fuzzing, and power-supply updates from decoded BDOs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/pd_bdo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/pd_ext_sdb.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/pd_ext_sdb.h`

## Purpose

`pd_ext_sdb.h` defines USB PD extended Status Data Block fields. It supports decoding status extended messages that report internal temperature, power state, battery state, and event flags.

## Important APIs, Types, and Constants

- The header provides packed/status field definitions and masks for extended status payload interpretation.
- Constants describe event and status bit positions used by TCPM and Type-C partner status logic.

## Control Flow and Lifetimes

After receiving a PD extended Status message, TCPM validates the extended-message length, decodes the status data block through these definitions, and updates policy or user-visible partner status.

## State and Persistence Behavior

The status data block is transient wire data. Cached partner status lives in TCPM/Type-C runtime objects.

## Dependencies and Integration Points

It integrates with `pd.h` extended message framing, TCPM receive paths, and Type-C partner status reporting.

## Risks and Edge Cases

Extended messages may be chunked or shorter than expected. Temperature/power fields must be interpreted using PD-defined units and sentinel values. Reserved bits should be preserved only where required and ignored otherwise.

## Test Signals

Inject status extended messages with normal, warning, and reserved values; test short/chunked payload handling; verify partner status updates; and fuzz event bits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/pd_ext_sdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/pd_vdo.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/pd_vdo.h`

## Purpose

`pd_vdo.h` defines USB PD Vendor Defined Object and Structured VDM helpers. It covers identity headers, certification/stat VDOs, product VDOs, cable VDOs, active cable VDOs, AMA/VPD VDOs, SVID discovery, USB-IF SIDs, modal command encodings, and VDM timing constants.

## Important APIs, Types, and Constants

- VDM header macros encode VID/SID, structured/unstructured type, version, object position, command type, and command.
- Identity helpers build/extract ID headers, product VDOs, cable VDOs, active cable VDOs, alternate-mode adapter VDOs, and VPD VDOs.
- Cable constants describe connector type, latency, termination, VCONN requirements, VBUS voltage/current, USB signaling capability, USB4/USB2/USB3 support, lane count, optical isolation, redriver/retimer state, and operating temperature.
- SVID helpers pack/unpack two SVIDs per VDO and define USB-IF SIDs for PD, DisplayPort, and MHL.
- VDM timeout constants describe expected command response windows.

## Control Flow and Lifetimes

TCPM and alt-mode managers send Discover Identity/SVIDs/Modes/Enter/Exit/Attention VDMs, then parse returned VDOs with these macros to identify partner, cable, and modal capabilities. Cable/partner identity is cached while the Type-C connection remains attached.

## State and Persistence Behavior

VDOs are transient PD payloads, but decoded identity and mode capability state persists in Type-C partner/cable/plug objects for the connection lifetime.

## Dependencies and Integration Points

It integrates PD message handling with the Type-C class, alt-mode drivers such as DisplayPort, cable discovery, VCONN swap policy, and USB4/retimer/redriver decisions.

## Risks and Edge Cases

The same bit positions can mean different things for passive cable, active cable, AMA, and VPD objects, so consumers must select the correct decoder. PD revision and VDO version gate field validity. Identity discovery can happen over SOP or SOP prime, and cable communication may be unsupported. Timeouts are policy-sensitive.

## Test Signals

Test Discover Identity/SVID/Modes flows for partners, passive cables, active cables, VPDs, and AMAs; verify DisplayPort SVID discovery; fuzz VDO versions and reserved bits; check VCONN swap policy; and validate timeout/retry behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/pd_vdo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/phy.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/phy.h`

## Purpose

`phy.h` defines the legacy USB PHY abstraction used by host, gadget, OTG, charger, and extcon-aware controller drivers. It provides PHY type/interface/event enums, OTG state enum, `struct usb_phy`, I/O access hooks, registration/get/put APIs, power/suspend/wakeup helpers, connect/disconnect notification, charger-current helpers, and notifier registration.

## Important APIs, Types, and Constants

- `enum usb_phy_interface`, `enum usb_phy_events`, `enum usb_phy_type`, and `enum usb_otg_state` describe PHY mode, cable events, PHY class, and OTG state machine states.
- `struct usb_phy_io_ops` supplies low-level register read/write hooks for ULPI-style PHY access.
- `struct usb_charger_current` records current ranges for SDP, DCP, CDP, and ACA charger types.
- `struct usb_phy` holds device metadata, flags, type, last event, OTG pointer, I/O device/ops, extcon devices and notifiers, charger state/current/work, atomic notifier chain, root-hub port status/change, multi-PHY list node, and callbacks for init/shutdown/VBUS/power/suspend/wakeup/connect/disconnect/charger detection.
- Registration and lookup APIs include `usb_add_phy()`, `usb_add_phy_dev()`, `usb_remove_phy()`, `usb_get_phy()`, devm getters, node/phandle getters, and `usb_put_phy()`.
- Inline helpers wrap I/O, init/shutdown, VBUS, set power, suspend, wakeup, connect/disconnect, notifier registration, and type-to-string conversion; disabled `CONFIG_USB_PHY` builds return `-ENXIO` or no-op.

## Control Flow and Lifetimes

PHY providers initialize `struct usb_phy`, register it, and implement callbacks. Controllers obtain a PHY by type, phandle, or node, call `usb_phy_init()`, drive VBUS/power/suspend/wakeup as role and PM state changes, notify connect/disconnect, and release it with `usb_put_phy()` or devm cleanup. Extcon and charger events update `last_event`, charger state, and notifier chains.

## State and Persistence Behavior

`usb_phy` is persistent runtime state for a PHY device. Charger current/state, last event, extcon notifiers, OTG pointer, port status/change, and notifier chain are mutable in memory. Hardware PHY registers persist until reset/power loss.

## Dependencies and Integration Points

It depends on extcon, notifier chains, USB core types, and UAPI charger definitions. It integrates with host controllers, gadget UDCs, OTG glue, device-tree PHY lookup, charger detection, root-hub status propagation, and legacy PHY drivers.

## Risks and Edge Cases

The legacy `usb_phy` API coexists with generic PHY, so mixed users must avoid double power management. Optional callbacks silently no-op in many wrappers, which can hide missing board support. Notifiers are atomic and callbacks must be context-safe. Charger current updates are side effects of `usb_phy_set_power()`. Disabled-config stubs must be handled.

## Test Signals

Build with and without `CONFIG_USB_PHY`, register/get/put PHYs, exercise extcon VBUS/ID events, charger detection and current reporting, host/gadget connect notifications, suspend/wakeup, ULPI read/write failures, notifier chains, and devm phandle/node cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/phy_companion.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/phy_companion.h`

## Purpose

`phy_companion.h` defines a minimal companion object for PHY comparator/OTG helper hardware that handles VBUS and SRP capabilities alongside a USB PHY.

## Important APIs, Types, and Constants

- `struct phy_companion` exposes `set_vbus()` for A-peripheral VBUS control and `start_srp()` for B-device session request protocol.

## Control Flow and Lifetimes

An OTG/PHY driver attaches a companion object when external comparator hardware owns VBUS or SRP signaling. Role or session changes call the companion callbacks while the parent PHY remains registered.

## State and Persistence Behavior

The header defines callback shape only. Runtime state is owned by the companion driver/hardware.

## Dependencies and Integration Points

It depends on `usb/otg.h` and integrates legacy PHY code with external VBUS/ID/SRP support hardware.

## Risks and Edge Cases

Callbacks are optional by structure convention but consumers must check before use. VBUS control must match board power topology. SRP calls are valid only in B-device contexts.

## Test Signals

Test VBUS enable/disable through companion hardware, SRP initiation, missing-callback paths, role switching, and suspend/resume with external comparator state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/phy_companion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/quirks.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/quirks.h`

## Purpose

`quirks.h` defines device-wide USB quirk bits used by usbcore and drivers to compensate for non-compliant devices. Interface-specific quirks belong elsewhere; this header covers whole-device behavior.

## Important APIs, Types, and Constants

- Quirks cover string descriptor fetch size, reset-on-resume, no SetInterface, bad configuration/interface strings, no reset, honoring `bNumInterfaces`, delayed init, linear interrupt intervals, no device qualifier, ignoring remote wakeup, no LPM, disconnect before suspend, delayed control messages, slow hub reset, ignored endpoints, short SetAddress timeout, no BOS request, and force-one-configuration.

## Control Flow and Lifetimes

USB device ID tables or core matching set quirk bits during enumeration. usbcore checks these bits while reading descriptors, choosing configurations, setting interfaces, suspending/resuming, resetting ports, enabling LPM, and handling endpoint descriptors.

## State and Persistence Behavior

Quirk bits are runtime flags associated with a `usb_device` instance and persist until disconnect. The definitions are stable kernel ABI between quirk tables and usbcore behavior.

## Dependencies and Integration Points

It depends on `BIT()` from kernel bitops through including context. It integrates usbcore enumeration, hub, PM, descriptor parsing, and device-specific quirk tables.

## Risks and Edge Cases

Applying quirks too broadly can disable features for good devices. Missing quirks can break enumeration or resume. Some quirks change security- or power-relevant behavior such as ignoring remote wakeup or skipping BOS/LPM.

## Test Signals

Test devices listed in quirk tables, enumeration descriptor paths, resume/reset behavior, LPM enable/disable, SetInterface handling, slow hub reset, endpoint-ignore behavior, and regression tests ensuring unrelated devices are unaffected.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/r8152.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/r8152.h`

## Purpose

`r8152.h` defines shared constants for Realtek RTL8152/RTL8153 USB Ethernet devices and exposes a version lookup helper when the driver is reachable.

## Important APIs, Types, and Constants

- USB vendor request constants define read/write request types and register get/set request IDs.
- Byte-enable masks describe dword, word, byte, six-byte, start, and end byte lanes.
- MCU type constants distinguish PLA and USB register spaces.
- Vendor ID constants list Realtek and OEM-branded devices.
- `rtl8152_get_version(struct usb_interface *intf)` is exported when `CONFIG_USB_RTL8152` is reachable.

## Control Flow and Lifetimes

The r8152 driver uses vendor requests to access device registers in PLA or USB MCU spaces. Other code can query the detected chip version through the helper when the driver is built in or as a reachable module.

## State and Persistence Behavior

Constants define vendor protocol ABI. Device version state is runtime state held by the r8152 driver for a bound USB interface.

## Dependencies and Integration Points

It integrates USB Ethernet driver code, USB interface objects, and potentially consumers that need chip revision decisions. It depends on USB and Kconfig reachability through including context.

## Risks and Edge Cases

Vendor requests must use correct byte-enable masks and MCU space or can corrupt device registers. The version helper is unavailable when the driver is not reachable. OEM IDs require matching the same protocol behavior despite different vendor IDs.

## Test Signals

Probe multiple RTL8152/RTL8153/OEM adapters, run register read/write tests, verify version reporting, test suspend/resume and link changes, and build with driver built-in, module, and disabled configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/r8152.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/r8a66597.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/r8a66597.h`

## Purpose

`r8a66597.h` defines platform data and a full register/bit map for the Renesas R8A66597 USB controller, including USB core, FIFO, pipe, interrupt, device-address, and SUDMAC DMA registers.

## Important APIs, Types, and Constants

- `struct r8a66597_platdata` carries port power callback, bus wait, on-chip/external selection, oscillator, voltage interface, endian, write-strobe wiring, and SUDMAC enable flags.
- Register offsets cover system config/status, device state, test mode, pin/DMA config, CFIFO/DxFIFO, interrupt enables/status, frame numbers, setup request registers, default control pipe, pipe selection/config/buffer/maxpacket/period/control, transaction counters, device address registers, and SUDMAC registers.
- Bit definitions cover clock/PLL, speed mode, pullups/pulldowns, VBUS, resume/reset, line state, DMA bus modes, FIFO control, interrupt classes, device states, control-transfer stages, pipe types/directions/buffers, sequence toggles, transaction counters, and DMA status/interrupt controls.

## Control Flow and Lifetimes

The driver reads platform data at probe, configures bus timing, clocks, endian mode, and optional SUDMAC, then programs pipes and interrupts. Transfer flow selects a pipe/FIFO, configures endpoint type/direction/maxpacket, reacts to BRDY/NRDY/BEMP/CTR events, and optionally uses SUDMAC for data movement. Remove disables interrupts, pipes, DMA, clocks, and port power.

## State and Persistence Behavior

Register bits and pipe/FIFO state are runtime hardware state. Platform data is static. SUDMAC channel registers hold transient DMA transfer state. No disk persistence exists.

## Dependencies and Integration Points

It integrates Renesas platform code with host/gadget controller drivers and board-specific power/endian/timing choices. It uses kernel integer types and platform data.

## Risks and Edge Cases

The macro namespace is broad and generic, so include-order conflicts are possible. Wrong endian/oscillator/buswait settings break register access. FIFO/pipe selection is stateful; changing `PIPESEL` or FIFO selection at the wrong time can corrupt transfers. DMA status clear ordering matters.

## Test Signals

Probe on supported Renesas boards, exercise control/bulk/interrupt/isochronous pipes, SUDMAC and non-DMA modes, endian variants, port power callback, VBUS/detach/attach interrupts, suspend/resume, and control-transfer error stages.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/r8a66597.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/renesas_usbhs.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/renesas_usbhs.h`

## Purpose

`renesas_usbhs.h` defines platform callbacks and driver parameters for Renesas USBHS controllers. It describes host/gadget ID detection, VBUS/power/PHY hooks, pipe configuration, DMA alignment, polling delays, SoC feature flags, and platform info passed to the USBHS driver.

## Important APIs, Types, and Constants

- Module IDs distinguish `USBHS_HOST` and `USBHS_GADGET`.
- `struct renesas_usbhs_platform_callback` supplies hardware init/exit, power control, PHY reset, ID detection, VBUS detection/control, and extcon notifier callbacks.
- `struct renesas_usbhs_driver_pipe_config` and `RENESAS_USBHS_PIPE()` describe endpoint type, buffer size/number, and double buffering.
- `struct renesas_usbhs_driver_param` carries pipe arrays, bus wait, detection delays, DMA channel names, D0/D1/D2 callbacks, pio/dma tuning, multi-clk flags, and hardware feature flags.
- `USBHS_USB_DMAC_XFER_SIZE` fixes a DMA transfer granularity used by the driver.
- `struct renesas_usbhs_platform_info` groups callbacks and parameters for platform registration.

## Control Flow and Lifetimes

Platform code provides callbacks and parameters. During probe, the driver initializes hardware, powers clocks, resets PHY, builds pipe resources from the config array, determines host/gadget mode from ID/VBUS callbacks or extcon notifications, and starts the appropriate role. Runtime role changes call notifier/ID/VBUS hooks and may start/stop host or gadget paths.

## State and Persistence Behavior

The platform info is static configuration. Runtime state includes selected role, pipe allocation, DMA channel use, VBUS state, and power/clock state in the driver and hardware.

## Dependencies and Integration Points

It depends on notifier blocks, platform devices, and USB Chapter 9 endpoint types. It integrates Renesas SoC board code, extcon, host/gadget controllers, DMA engines, and PHY/power management.

## Risks and Edge Cases

Pipe configuration must match hardware buffer RAM. Incorrect ID/VBUS callbacks cause wrong role selection. DMA transfer-size and alignment assumptions can corrupt data. Platform power callbacks must be safe across probe failure and suspend/resume. Extcon notifier paths must not race role teardown.

## Test Signals

Probe USBHS in host and gadget modes, validate pipe allocation, VBUS and ID transitions, extcon notifications, DMA and PIO transfers, suspend/resume, probe failure unwinds, and boards with multiple clocks or SoC feature flags.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/renesas_usbhs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/rndis_host.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/rndis_host.h`

## Purpose

`rndis_host.h` defines Remote NDIS message layouts and host-side helper declarations for USB RNDIS networking. It includes control/data message structures, timeouts, default packet filters, driver-data flags, and usbnet integration functions.

## Important APIs, Types, and Constants

- Packed/little-endian message structs cover message header, data packets, initialize/complete, halt, query/complete, set/complete, reset/complete, indicate status, keepalive, and keepalive complete.
- `CONTROL_BUFFER_SIZE` and `RNDIS_CONTROL_TIMEOUT_MS` define control exchange sizing and timeout.
- `RNDIS_DEFAULT_FILTER` selects directed, broadcast, all multicast, and promiscuous-related packet filters as defined in the header.
- Driver flags describe physical-medium assumptions, polling status before control, and destination-MAC fixup behavior.
- Exported helpers include `rndis_status()`, `rndis_command()`, `generic_rndis_bind()`, `rndis_unbind()`, `rndis_rx_fixup()`, and `rndis_tx_fixup()`.

## Control Flow and Lifetimes

During bind, usbnet RNDIS code initializes the device with control messages, queries capabilities, sets packet filters, and opens data endpoints. RX fixup strips RNDIS data headers and validates offsets/lengths before handing packets to networking. TX fixup wraps sk_buffs in RNDIS data headers. Status URBs deliver unsolicited indications and keepalive/status events.

## State and Persistence Behavior

Wire messages are transient. usbnet device state stores negotiated parameters, flags, filters, MAC handling, and endpoint URBs for the interface lifetime. No disk persistence exists.

## Dependencies and Integration Points

It depends on USB networking (`usbnet`), URBs, sk_buffs, and little-endian wire fields. It integrates CDC/RNDIS USB devices with Linux netdev and usbnet generic bind/unbind paths.

## Risks and Edge Cases

RNDIS devices are often non-compliant. Header offsets and lengths must be validated to avoid skb overreads. Control commands can time out or require polling. Some devices ignore configured MAC addresses. Reset/indicate/keepalive messages may arrive asynchronously with disconnect.

## Test Signals

Bind several RNDIS devices, test init/query/set/reset/keepalive exchanges, RX/TX fixups with malformed lengths, control timeout handling, MAC fixup devices, suspend/resume, unplug during control command, and netdev traffic under stress.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/rndis_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/role.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/role.h`

## Purpose

`role.h` defines the USB role-switch framework API used by dual-role controllers and Type-C/OTG glue to select none/host/device roles through firmware-described switch objects.

## Important APIs, Types, and Constants

- `enum usb_role` defines `USB_ROLE_NONE`, `USB_ROLE_HOST`, and `USB_ROLE_DEVICE`.
- Callback types `usb_role_switch_set_t` and `usb_role_switch_get_t` define setter/getter signatures.
- `struct usb_role_switch_desc` describes firmware node, device, set/get callbacks, driver data, name, module owner, and option flags such as allowing userspace control.
- APIs include set/get role, get by device or fwnode, put, register, unregister, set/get driver data, and `usb_role_string()`.
- Disabled `CONFIG_USB_ROLE_SWITCH` builds provide stubs returning `-EOPNOTSUPP`, `USB_ROLE_NONE`, `ERR_PTR(-ENODEV)`, or no-op.

## Control Flow and Lifetimes

A provider registers a role switch with callbacks. Consumers acquire it from a device or fwnode, call `usb_role_switch_set_role()` when Type-C/OTG policy changes, query current role as needed, and release with `usb_role_switch_put()`. Provider unregisters during teardown.

## State and Persistence Behavior

Role state is runtime hardware/framework state. Driver data persists for the switch lifetime. Firmware node links provide discovery but no mutable persistence.

## Dependencies and Integration Points

It depends on device/fwnode infrastructure and optional role-switch Kconfig. It integrates Type-C port managers, dual-role USB controllers, mux/orientation code, and userspace-controllable role switching.

## Risks and Edge Cases

Consumers must handle absent role-switch support and error pointers. Role changes may require coordinated VBUS, PHY, host, and gadget sequencing outside this API. Userspace control can conflict with policy engines if not gated.

## Test Signals

Build with/without role switch support, register provider switches, get by fwnode/device, set host/device/none roles, test userspace role changes, unregister while consumers hold references, and verify string conversion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/role.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/rzv2m_usb3drd.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/rzv2m_usb3drd.h`

## Purpose

`rzv2m_usb3drd.h` declares the reset helper for Renesas RZ/V2M USB3 dual-role-device glue. It lets USB3 DRD users reset the controller for host or device role.

## Important APIs, Types, and Constants

- `struct rzv2m_usb3drd` stores at least a `void __iomem *` register base for implementation users.
- `rzv2m_usb3drd_reset(struct device *dev, bool host)` resets the DRD block for host or non-host operation when `CONFIG_USB_RZV2M_USB3DRD` is enabled.
- Disabled builds provide an empty inline stub.

## Control Flow and Lifetimes

Role glue or controller code calls the reset helper during probe or role transition. The helper locates device-private DRD state and toggles reset/register state according to the `host` argument.

## State and Persistence Behavior

Hardware reset state is transient but affects controller role and register contents. The header itself stores no state beyond the implementation structure definition.

## Dependencies and Integration Points

It integrates Renesas RZ/V2M USB3 DRD glue with host/device controller drivers and device-model state. It uses `struct device`.

## Risks and Edge Cases

The disabled stub silently does nothing, so callers must ensure Kconfig matches hardware needs. Reset during active transfers can lose state. Host/device argument must match current role policy.

## Test Signals

Build with and without the DRD driver, call reset during host and device probe, test role switching, suspend/resume, and verify no active I/O is reset unexpectedly.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/rzv2m_usb3drd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/serial.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/serial.h`

## Purpose

`serial.h` defines the USB serial core contract for USB-to-serial drivers. It describes serial devices, ports, endpoint discovery, driver callbacks, TTY integration helpers, generic read/write implementations, console hooks, bus registration, debugging, and module registration macros.

## Important APIs, Types, and Constants

- `MAX_NUM_PORTS` fixes the maximum port count per USB serial device; port flag bits track write-busy and throttled state.
- `struct usb_serial_port` contains serial backpointer, minor number, endpoint descriptors, bulk/interrupt URBs and buffers, write FIFO, write waitqueue, work, TTY port, async icount, mutexes/spinlocks, and device model state.
- `struct usb_serial` stores USB device/interface, kref, driver pointer, port array, num_ports, private data, suspend state, and interface claims.
- `struct usb_serial_endpoints` summarizes discovered bulk/interrupt endpoint descriptors.
- `struct usb_serial_driver` provides probe/attach/disconnect/release, port probe/remove, open/close, write, write_room, chars_in_buffer, throttle/unthrottle, ioctl, break, modem control, tiocm wait/get icount, process_read_urb, prepare_write_buffer, read/write callbacks, suspend/resume/reset_resume, and metadata.
- Core APIs register/deregister driver arrays, get ports by minor, claim interfaces, suspend/resume, and provide generic open/write/close/read/write callback implementations.

## Control Flow and Lifetimes

A USB serial subdriver registers a `usb_serial_driver`. On matching USB interface probe, the core discovers endpoints, allocates `usb_serial` and port objects, calls subdriver probe/attach/port_probe hooks, and registers TTY ports. TTY open starts reads; writes fill buffers and submit bulk URBs; completion callbacks free space and wake waiters. Disconnect shuts down TTYs, kills URBs, releases minors, calls cleanup hooks, and drops references.

## State and Persistence Behavior

Serial and port objects persist while the USB interface is bound and while references remain. TTY buffers, URBs, FIFO state, throttling, write-busy flags, icount, and private data are mutable runtime state. No disk persistence exists.

## Dependencies and Integration Points

It integrates USB core, TTY core, krefs, URBs, workqueues, FIFOs, waitqueues, consoles, sysrq/break handling, and module registration. Subdrivers for specific USB serial chips implement or reuse generic callbacks.

## Risks and Edge Cases

Disconnect races with TTY open/write/read callbacks are central. URB callbacks must respect port lifetime and throttling. Minor lookup requires references. Subdrivers must not sleep in interrupt callback contexts. Multi-port devices and extra claimed interfaces complicate cleanup.

## Test Signals

Bind generic and chip-specific USB serial devices, open/close TTYs, run bidirectional traffic, throttle/unthrottle, disconnect under write load, suspend/resume/reset_resume, console operation, sysrq/break handling, multi-port devices, and lockdep/refcount checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/sl811.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/sl811.h`

## Purpose

`sl811.h` defines platform data for the SL811 USB host controller. It lets board code provide power, reset, and overcurrent behavior for platform-attached controllers.

## Important APIs, Types, and Constants

- `struct sl811_platform_data` contains board-specific callbacks and configuration fields used by the SL811 HCD, including port power/reset/overcurrent style hooks in the implementation contract.

## Control Flow and Lifetimes

Board code attaches platform data before probe. The SL811 host driver reads the configuration during initialization and invokes callbacks for port power, reset, and status transitions as devices attach or detach.

## State and Persistence Behavior

The data is static board configuration; mutable bus and port state lives in the HCD and hardware.

## Dependencies and Integration Points

It integrates platform-bus registration with the SL811 host controller driver and usbcore HCD framework.

## Risks and Edge Cases

Wrong board callbacks can leave VBUS off, reset lines asserted, or overcurrent unhandled. Platform data lifetime must outlive the driver instance.

## Test Signals

Probe SL811 platform devices, enumerate low/full-speed devices, test port power/reset callbacks, overcurrent reporting, suspend/resume, and remove during active devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/sl811.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/storage.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/storage.h`

## Purpose

`storage.h` defines USB mass-storage subclass/protocol constants and Bulk-Only Transport command/status wrapper layouts. It is shared by USB storage drivers and related transport code.

## Important APIs, Types, and Constants

- Subclass constants cover RBC, 8020 CD-ROM, QIC, UFI, 8070 removable, transparent SCSI, lockable, ISD200, Cypress ATACB, and use-device value.
- Protocol constants cover CBI, CB, bulk-only, UAS, USBAT, SDDR09/55, DPCM, Freecom, Datafab, Jumpshot, Alauda, Karma, and use-device value.
- `struct bulk_cb_wrap` is the packed command block wrapper with signature, tag, transfer length, flags, LUN, CDB length, and command block bytes.
- `struct bulk_cs_wrap` is the packed command status wrapper with signature, tag, residue, and status.
- Constants define wrapper lengths/signatures, direction flags, status values, bulk reset and max-LUN requests, and max-LUN limit.

## Control Flow and Lifetimes

For bulk-only transport, the driver sends a CBW over bulk OUT, transfers data in the indicated direction and length, then reads a CSW over bulk IN and validates signature/tag/status/residue. Reset and get-max-LUN class requests manage error recovery and LUN discovery.

## State and Persistence Behavior

CBW/CSW structs are transient wire buffers. Device subclass/protocol selection persists for the USB interface lifetime. SCSI and transport state live in usb-storage/UAS code.

## Dependencies and Integration Points

It integrates USB interface descriptor parsing with SCSI, usb-storage, UAS, and transport-specific drivers. It depends on packed fixed-width USB types.

## Risks and Edge Cases

CBW/CSW validation must reject bad signatures, wrong tags, invalid statuses, and impossible residue. Max LUN is four bits with upper limit `0x0f`. Some devices misreport subclass/protocol and need unusual-device handling outside this header.

## Test Signals

Run usb-storage BOT enumeration, SCSI read/write, reset recovery, max-LUN queries, malformed CSW injection, short transfers, UAS protocol selection, and devices across listed subclasses/protocols.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/storage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/tcpci.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/tcpci.h`

## Purpose

`tcpci.h` defines the USB Type-C Port Controller Interface register map, bitfields, TCPCI helper data structure, registration API, IRQ entry point, and CC-status conversion helper. It is the bridge between generic TCPM policy and TCPCI-compatible port controller chips.

## Important APIs, Types, and Constants

- Register constants cover vendor/product/revision IDs, alert/mask/status registers, role control, power control/status/faults, CC status, commands, capabilities, message header info, RX/TX buffers, transmit control, and VBUS voltage/alarm thresholds.
- Bit masks cover alerts, VCONN, discharge, FRS, CC pull states, power presence/sourcing/sinking, fault reset/VCONN overcurrent, RX SOP types, transmit retry/type, and orientation output.
- `tcpc_presenting_rd()` tests whether a role-control register presents Rd on a selected CC pin.
- `struct tcpci_data` supplies regmap, feature flags, and chip-specific callbacks for init, VCONN, DRP toggling, VBUS, FRS sourcing, partner USB communication capability, contaminant checks, VCONN-swap discovery policy, and orientation setting.
- APIs include `tcpci_register_port()`, `tcpci_unregister_port()`, `tcpci_irq()`, and `tcpci_get_tcpm_port()`.
- `tcpci_to_typec_cc()` maps TCPCI CC encoded values to Type-C CC status depending on sink/source interpretation.

## Control Flow and Lifetimes

A chip driver creates a regmap-backed `tcpci_data` and registers a TCPCI port. The TCPCI core exposes a `tcpc_dev` to TCPM, programs TCPC registers for CC, VCONN, VBUS, RX/TX, and roles, and handles interrupts through `tcpci_irq()`. Alerts are decoded into TCPM events such as CC change, VBUS change, PD receive, transmit complete, hard reset, and faults.

## State and Persistence Behavior

TCPC registers hold role, power, RX/TX, alert, and VBUS threshold state. `tcpci_data` persists for the port lifetime and carries chip-specific capability flags. TCPM port state is accessible through `tcpci_get_tcpm_port()`.

## Dependencies and Integration Points

It depends on Type-C and TCPM headers, regmap through `struct tcpci_data`, IRQ handling, and chip-specific I2C/SPI drivers. It integrates generic TCPM policy with TCPCI-compliant hardware.

## Risks and Edge Cases

Alert bits must be acknowledged in correct order to avoid missing PD messages or faults. Some chips hide TX buffer bytes behind I2C write count. VBUS discharge and VSAFE0V support are optional and policy-sensitive. CC interpretation differs for source versus sink. Contaminant checks can block normal toggling until `tcpm_port_clean()`.

## Test Signals

Test TCPCI chip probe, TCPM registration, CC attach/detach, PD RX/TX, hard reset, VCONN/VBUS control, FRS, auto discharge thresholds, orientation output, contaminant detection, cable communication, interrupt storms, and regmap error injection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/tcpci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/tcpm.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/tcpm.h`

## Purpose

`tcpm.h` defines the Type-C Port Manager interface between low-level Type-C/PD port controllers and the generic TCPM policy engine. It describes CC status, polarity, transmit types/status, mux flags, TCPC callback vector, registration APIs, and event notification functions.

## Important APIs, Types, and Constants

- `enum typec_cc_status` defines open, Ra, Rd, and Rp current levels; `SINK_TX_NG` and `SINK_TX_OK` encode collision-avoidance thresholds.
- `enum typec_cc_polarity` identifies CC1/CC2 orientation.
- Timeouts define TCPC transmit, role-swap, and augmented power-supply control waits.
- `enum tcpm_transmit_status` and `enum tcpm_transmit_type` describe PD transmission completion and SOP/hard-reset/cable-reset/BIST targets.
- Mux flags identify USB, DisplayPort, and polarity-inverted states.
- `struct tcpc_dev` is the low-level callback vector: init, VBUS/current, CC set/get, polarity/orientation, VCONN/VBUS/current limit, PD RX enable, roles, toggling, try-role, PD transmit, BIST, FRS, auto discharge, VSAFE0V, partner USB communication, contaminant check, cable communication, and VCONN-swap discovery policy.
- APIs register/unregister ports and notify TCPM of VBUS, CC, FRS, sourcing VBUS, PD receive, transmit complete, hard reset, TCPC reset, clean port, toggling state, and error recovery.

## Control Flow and Lifetimes

A TCPC driver fills `tcpc_dev` and registers it with `tcpm_register_port()`. TCPM drives callbacks to configure CC, roles, VBUS/VCONN, PD RX/TX, mux policy, and discharge. The low-level driver reports interrupts or hardware changes through notification functions, causing TCPM policy transitions and PD message handling. Unregister stops policy and releases the port.

## State and Persistence Behavior

TCPM owns persistent runtime state for attachment, roles, negotiated PD revision, capabilities, message IDs, timers, and policy. The low-level `tcpc_dev` must remain valid until unregister completes. Hardware CC/VBUS/PD state is managed through callbacks.

## Dependencies and Integration Points

It depends on Type-C class definitions and `pd.h`. It integrates TCPCI and non-TCPCI port controllers, Type-C mux/alt-mode code, power-supply control, USB role switching, DisplayPort modes, and PD policy.

## Risks and Edge Cases

Callbacks have optional versus mandatory semantics; missing mandatory operations break policy. Hardware interrupts can race unregister. VBUS discharge, FRS, PPS/AVS, contaminant recovery, and VCONN-swap discovery are policy-heavy and hardware-dependent. PD transmit completion must be reported exactly once per transmit.

## Test Signals

Run TCPM attach/detach, source/sink negotiation, PD message RX/TX, hard reset, role swaps, VCONN swap, FRS, PPS/AVS current-limit updates, mux changes, contaminant recovery, unregister during events, and low-level callback failure injection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/tcpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/tegra_usb_phy.h -->
# `sources/distributed-fs/ceph-client/include/linux/usb/tegra_usb_phy.h`

## Purpose

`tegra_usb_phy.h` defines SoC configuration, UTMI tuning, port-speed enums, and runtime state for NVIDIA Tegra USB PHY drivers. It describes the knobs needed to initialize Tegra UTMI/ULPI/HSIC PHY variants and integrate them with clocks, regulators, reset, PMC, and legacy USB PHY APIs.

## Important APIs, Types, and Constants

- `struct tegra_phy_soc_config` records SoC-specific behavior: whether CAR owns UTMI PLL setup, HOSTPC support, USBMODE setup requirement, extra tuning requirement, PMC AO power-up, HSIC register offset, HSIC tuning values, and PORTSC1 offset.
- `struct tegra_utmip_config` stores UTMI timing and signal-integrity tuning values such as sync start delay, elastic limit, idle wait, term range, fuse usage, XCVR setup, LS slew, HS slew, squelch, and disconnect levels.
- `enum tegra_usb_phy_port_speed` identifies full, low, and high speed.
- `struct tegra_usb_phy` stores IRQ, instance, crystal frequency, MMIO bases, clocks, regulator, PMC regmap, role mode, config pointer, SoC config, ULPI PHY, embedded `usb_phy`, legacy flag, interface type, reset GPIO, pad reset, wakeup and power flags.

## Control Flow and Lifetimes

The Tegra PHY driver allocates and fills `tegra_usb_phy`, maps registers, obtains clocks/regulators/resets/PMC regmap, applies SoC and UTMI tuning, initializes the embedded `usb_phy`, and manages power/wakeup through callbacks. Controllers use the embedded legacy PHY object for host/gadget operation.

## State and Persistence Behavior

`tegra_usb_phy` is persistent runtime state for a PHY instance. `powered_on`, `wakeup_enabled`, and `pad_wakeup` track mutable hardware power state. Register configuration persists while powered and may be lost on reset or deep power collapse.

## Dependencies and Integration Points

It depends on clocks, regmap, resets, regulators through forward declarations/includes, GPIO descriptors, OTG role mode, and legacy USB PHY. It integrates Tegra SoC USB controllers, PMC power management, pad controls, ULPI/UTMI/HSIC PHY modes, and board tuning data.

## Risks and Edge Cases

Tuning values are SoC- and board-specific; wrong values can cause marginal high-speed signaling. Clock/reset/regulator ordering is critical. Legacy and non-legacy PHY paths must not double-control pads. Wakeup and AO power flags affect suspend behavior. USBMODE/HOSTPC register offsets vary by SoC.

## Test Signals

Probe Tegra PHY instances across UTMI/ULPI/HSIC modes, run host and device traffic, validate high-speed signal tuning, suspend/resume and wakeup, regulator/clock/reset failure unwinds, PMC AO power behavior, and role-mode transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/tegra_usb_phy.h -->
