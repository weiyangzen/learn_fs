# subset-b-003812 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dev.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dev.c

Purpose: Intel Touch Host Controller common MMIO/regmap support. It initializes `struct thc_device`, clears controller state, exports PIO transactions, interrupt setup/decoding, LTR control, SPI port configuration, I2C sub-IP setup, and optional I2C Rx throttling features to QuickSPI/QuickI2C transports.

Important APIs: `thc_dev_init()`, `thc_tic_pio_read()`, `thc_tic_pio_write()`, `thc_tic_pio_write_and_read()`, `thc_interrupt_config()`, `thc_interrupt_handler()`, `thc_port_select()`, `thc_spi_read_config()`, `thc_spi_write_config()`, `thc_i2c_subip_init()`, save/restore helpers, and I2C max-size/interrupt-delay toggles are namespace-exported as `INTEL_THC`.

Control flow: `thc_dev_init()` allocates, binds regmap to MMIO, clears stale status/counters, initializes locks/waitqueues, and creates DMA context. PIO paths serialize on `thc_bus_lock`, call `prepare_pio()`, start the software sequence, poll for done, then harvest data/status. Interrupt handling prioritizes non-DMA device interrupts and fatal/transaction errors before DMA completion and I2C sub-IP raw status bits.

State and persistence: persistent runtime state lives in `struct thc_device`: port type, PIO interrupt support, waitqueue completion flags, performance limit, I2C sub-IP register shadow, and feature-enable flags. I2C sub-IP save/restore preserves register state across suspend-like flows. Hardware state is modified through write-one-to-clear status registers and bitfield updates.

Dependencies and integration: depends on regmap, MMIO accessors, `intel-thc-hw.h` register definitions, and `intel-thc-dma.h`. Protocol drivers call these helpers after PCI resource mapping and before HID report exchange.

Risks: many paths rely on correct register W1C semantics and fixed timeouts. `thc_interrupt_quiesce()` waits for HW status even in the unquiesce path before clearing the enable bit, so sequencing matters. PIO buffer sizes are expressed in bytes but bulk reads/writes operate in dwords. Interrupt handler returns early for several error classes, so callers must handle partial status coverage.

Test signals: boot/probe logs, PIO read/write success, interrupt bit classification, resume restore of I2C sub-IP registers, DMA waitqueue wakeups, and hardware tests that cover SPI and I2C ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dev.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dev.h

Purpose: public interface and central device state for Intel THC common helpers. It defines port types, interrupt bit positions, `struct thc_device`, and prototypes exported by `intel-thc-dev.c`.

Important APIs/types: `enum thc_port_type` selects SPI or I2C operation. `enum thc_int_type` maps returned interrupt flags. `struct thc_device` owns regmap/MMIO pointers, bus mutex, DMA context, wake-on-touch data, write/SWDMA waitqueues, performance throttling, I2C sub-IP register shadow, and I2C feature flags.

Control flow: protocol drivers include this header, allocate the context through `thc_dev_init()`, select/configure a port, configure interrupts/DMA, perform PIO/DMA I/O, and use save/restore helpers for power-management paths.

State and persistence: the header makes explicit which state survives across helper calls: DMA context, WOT state, `i2c_subip_regs`, and enable flags used to restore features temporarily disabled during SWDMA.

Dependencies and integration: includes DMA and WOT headers and Linux locking/workqueue headers. It is the shared ABI between Intel THC common code and transport-specific QuickSPI/QuickI2C drivers.

Risks: exported prototypes expose low-level hardware operations without type-level sequencing guarantees, so callers must configure port type, max packet sizes, DMA allocation, and interrupt mode in the correct order.

Test signals: compile coverage for all prototypes, namespace export resolution, and integration tests that instantiate both SPI and I2C ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dma.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dma.c

Purpose: DMA engine support for Intel THC. It allocates PRD tables and scatterlists, programs DMA base/control registers, starts/stops RXDMA/TXDMA/SWDMA channels, copies data between scatterlists and caller buffers, and waits for interrupt-driven completion.

Important APIs: `thc_dma_init()`, `thc_dma_set_max_packet_sizes()`, `thc_dma_allocate()`, `thc_dma_configure()`, `thc_dma_unconfigure()`, `thc_dma_release()`, `thc_rxdma_read()`, `thc_swdma_read()`, and `thc_dma_write()` are exported in the Intel THC namespace.

Control flow: initialization seeds per-channel register offsets and directions. Allocation creates coherent PRD memory and SG lists for enabled channels, then mirrors SG DMA addresses into PRD entries. Configure resets engines, writes PRD base/control values, and starts RXDMA2. Reads derive pending PRD index from hardware read/write pointers, copy a single frame, refresh PRD descriptors, and advance the write pointer. SWDMA quiesces interrupts and pauses normal RXDMAs, performs a write/read sequence, then restores RXDMA2 and I2C feature state. TXDMA fills a one-table PRD, optionally quiesces interrupts for performance-delay constraints, starts hardware, and waits for `write_done`.

State and persistence: `struct thc_dma_context` persists channel configuration and temporary SWDMA feature-state flags. DMA buffers are held until release. Waitqueue flags are in `struct thc_device` and are set by the common interrupt handler.

Dependencies and integration: relies on DMA mapping, scatterlist helpers, `intel-thc-dev.h` waitqueues/feature toggles, and `intel-thc-hw.h` register bits. Protocol drivers call DMA helpers after controller setup.

Risks: partial allocation failures in `setup_dma_buffers()` return without freeing allocations already made inside the same channel until higher-level unwinding reaches previous channels only. Pointer wrap rules are hardware-specific and easy to regress. SWDMA temporarily disables I2C Rx max-size and interrupt-delay features, so restore paths must run on failures. TXDMA currently always waits for interrupt completion despite `use_write_interrupts` handling in start-bit setup.

Test signals: DMA allocation/unwind tests, RX pointer wrap tests, SWDMA timeout paths, TXDMA completion wakeups, and hardware input/output report transfer validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dma.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dma.h

Purpose: DMA data model for Intel THC. It defines PRD layout, channel IDs, pointer constants, per-channel configuration, aggregate DMA context, and exported DMA helper prototypes.

Important APIs/types: `enum thc_dma_channel` covers RXDMA1, RXDMA2, TXDMA, and SWDMA. `struct thc_prd_entry` is a bitfield hardware descriptor with shifted destination address, length, end-of-PRD, IOC, and status fields. `struct thc_dma_configuration` stores SG lists, PRD memory, register offsets, direction, table count, and max packet size. `struct thc_dma_context` groups all channels and SWDMA restore flags.

Control flow: callers set max packet sizes to enable channels, allocate buffers, configure hardware, exchange data, unconfigure, and release.

State and persistence: channel enablement and allocated DMA resources persist in the context. Temporary `rx_max_size_en` and `rx_int_delay_en` preserve I2C feature state during SWDMA.

Dependencies and integration: depends on Linux DMA mapping, sizes, and time constants. Included by `intel-thc-dev.h` and implemented by `intel-thc-dma.c`.

Risks: PRD bitfield layout must match hardware and compiler ABI assumptions. `PRD_ENTRIES_NUM` and `PRD_TABLES_NUM` constrain maximum transfer size and buffering depth. Address shifting assumes 1 KiB alignment.

Test signals: build-time layout sanity from compiler, DMA mapping tests on IOMMU/non-IOMMU systems, and transfer sizes spanning multiple SG entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-hw.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-hw.h

Purpose: register map and bitfield contract for Intel THC hardware. It names common and per-port MMIO offsets, interrupt/status bits, DMA control fields, SPI/I2C configuration fields, default constants, PIO opcodes, SPI I/O modes/dividers, and I2C sub-IP offsets.

Important APIs/types: this header exports no functions, but it is the authoritative macro set consumed by THC common and DMA code. Key enums include `enum thc_pio_opcode`, `enum thc_spi_iomode`, `enum thc_spi_frq_div`, and `enum THC_I2C_SPEED_MODE`.

Control flow: helper code composes values with `FIELD_PREP()`/`FIELD_GET()` against these masks and writes them through regmap. The register layout separates common LTR control from port-specific control, SPI config, software sequencing, write DMA, RXDMA1/RXDMA2/SWDMA, counters, coalescing, and I2C sub-IP registers.

State and persistence: all persistent state is hardware state described by offsets and W1C/reset bits. Software shadows are held in `struct thc_device`/DMA context, not here.

Dependencies and integration: depends only on `<linux/bits.h>`. It integrates the Intel THC driver with hardware documentation and is included by `intel-thc-dev.c` and `intel-thc-dma.c`.

Risks: macro drift from hardware specification can silently corrupt register programming. Several comments have typos, but the important risk is bit reuse across SPI and I2C modes, such as I2C max-size fields sharing the SPI opcode register offset.

Test signals: compile coverage, regmap trace comparison against hardware programming guides, and device-level smoke tests across SPI/I2C, DMA, interrupt, and PM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-wot.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-wot.c

Purpose: optional Wake-on-Touch setup for Intel THC ACPI devices. It manually registers ACPI GPIO mappings, looks up a wake-capable GPIO interrupt, enables device wakeup, and installs a dedicated wake IRQ.

Important APIs: `thc_wot_config()` and `thc_wot_unconfig()` are exported in namespace `INTEL_THC`.

Control flow: config exits early for missing THC device or ACPI companion. It calls `acpi_dev_add_driver_gpios()`, retrieves `"wake-on-touch"` IRQ and wakeability, then calls `device_init_wakeup()` and `dev_pm_set_dedicated_wake_irq()`. Unconfig disables wakeup and clears/removes wake IRQ/GPIO mappings when they were established.

State and persistence: wake IRQ number and wakeable flag are stored in `thc_dev->wot`. PM wake state persists in the device core until unconfigured.

Dependencies and integration: depends on ACPI GPIO helpers and PM wakeirq support. Transport drivers provide the ACPI GPIO mapping and call this during probe/remove or PM setup.

Risks: failures are warnings, not probe blockers, so wake functionality can silently be absent while normal HID operation works. Mapping removal only happens when `gpio_irq > 0`.

Test signals: ACPI resource lookup logs, `/sys` wakeup state, suspend/resume wake tests using touch input, and remove/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-wot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-wot.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-wot.h

Purpose: Wake-on-Touch state and API declarations for Intel THC.

Important APIs/types: `struct thc_wot` stores `gpio_irq` and `gpio_irq_wakeable`. `thc_wot_config()` and `thc_wot_unconfig()` are declared for use by THC transport drivers.

Control flow: included by `intel-thc-dev.h`, making WOT state part of the main THC device object.

State and persistence: the struct records the ACPI-derived IRQ and whether it should be treated as wake-capable.

Dependencies and integration: includes Linux types and GPIO consumer declarations; uses a forward declaration for `struct thc_device`.

Risks: minimal, but the API assumes callers provide a valid ACPI GPIO mapping compatible with the `"wake-on-touch"` lookup.

Test signals: build coverage and WOT setup/unsetup on ACPI THC platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-wot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/Kconfig

Purpose: Kconfig menu for Surface Aggregator HID transports.

Important symbols: `SURFACE_HID` builds the generic SSAM HID transport and depends on `SURFACE_AGGREGATOR_REGISTRY`; `SURFACE_KBD` builds the legacy Surface Laptop 1/2 keyboard transport; both select hidden `SURFACE_HID_CORE`. The menu depends on `SURFACE_AGGREGATOR`.

Control flow: configuration choice determines whether generic SSAM HID devices, legacy keyboard devices, and the shared core are compiled.

State and persistence: no runtime state; it controls kernel build state.

Dependencies and integration: integrates with the Surface Aggregator subsystem and HID subsystem via selected objects in the Makefile.

Risks: `SURFACE_KBD` has no explicit `SURFACE_AGGREGATOR_REGISTRY` dependency because it is platform/ACPI based; build coverage must ensure selected core dependencies remain sufficient.

Test signals: `olddefconfig`, module build, and boot probing on Surface Laptop generations covered by help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/Makefile

Purpose: object selection for Surface HID support.

Important entries: `surface_hid_core.o` follows `CONFIG_SURFACE_HID_CORE`, `surface_hid.o` follows `CONFIG_SURFACE_HID`, and `surface_kbd.o` follows `CONFIG_SURFACE_KBD`.

Control flow: Kconfig selections drive which translation units are compiled into built-in code or modules.

State and persistence: no runtime state.

Dependencies and integration: pairs with `Kconfig` and the parent HID Makefile to include SSAM HID transports in the kernel build.

Risks: core must be selected whenever either frontend transport is enabled; Kconfig handles that.

Test signals: kernel build with `SURFACE_HID=m/y`, `SURFACE_KBD=m/y`, and both disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid.c -->
# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid.c

Purpose: generic Surface Aggregator Module HID transport for HID target category devices on newer Surface systems.

Important APIs/types: `struct surface_hid_buffer_slice` defines chunked descriptor transfer payloads. SSAM command IDs cover output report, get/set feature report, and descriptor retrieval. Probe fills `struct surface_hid_device` ops and notifier before calling `surface_hid_device_add()`.

Control flow: descriptor reads loop over 128-byte SSAM payload slices until the device marks `end` or expected length is reached. Raw report operations translate HID output/feature operations into SSAM synchronous requests. Event notifier accepts command `0x00` and forwards event data to `hid_input_report()`.

State and persistence: per-device SSAM UID, controller, notifier, and ops are stored in the shared core object. No persistent storage beyond the HID device lifetime.

Dependencies and integration: depends on SSAM controller/device APIs and the shared Surface HID core. It registers as an `ssam_device_driver` for HID category devices and uses `surface_hid_pm_ops`.

Risks: descriptor slice parsing must reject bogus length/offset to avoid buffer misuse; report set mutates `buf[0]` to the report ID. Event filtering is command-id-only because SSAM registry matching carries the device identity.

Test signals: descriptor length/type validation in core, input event delivery from SSAM, output and feature report requests, async probe, hot remove, and PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid_core.c -->
# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid_core.c

Purpose: shared HID low-level driver for Surface SSAM HID transports.

Important APIs: `surface_hid_device_add()` loads descriptors/attributes, allocates `hid_device`, fills bus/vendor/product/version/name/phys and registers it. `surface_hid_device_destroy()` destroys it. `surface_hid_pm_ops` forwards PM events to HID driver callbacks.

Control flow: load HID descriptor, validate type/count/report descriptor metadata, load attributes, allocate HID device, attach `surface_hid_ll_driver`, and call `hid_add_device()`. HID `.start` registers SSAM notifier; `.stop` unregisters unless hot-removed; `.parse` fetches report descriptor and calls `hid_parse_report()`; `.raw_request` dispatches output/get feature/set feature through transport ops.

State and persistence: descriptor and attribute copies live in `struct surface_hid_device`; the HID core owns the registered `hid_device`. Hot-remove state is queried from SSAM devices before control requests.

Dependencies and integration: depends on HID core, USB HID descriptor constants, and Surface Aggregator controller/device helpers. Frontend transports provide descriptor/report operations and event notifiers.

Risks: core assumes exactly one report descriptor and validates fixed descriptor sizes. `surface_hid_device_destroy()` assumes `shid->hid` was either added or is destroyable. PM callbacks require driver data to be set by the frontend.

Test signals: descriptor protocol tests, `hid_add_device()` probe path, notifier registration/unregistration, raw report request results, hot-remove behavior, and PM callback forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid_core.h -->
# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid_core.h

Purpose: shared declarations for Surface SSAM HID transports.

Important APIs/types: descriptor entry enum identifies HID descriptor, report descriptor, and attributes. Packed descriptor structs model the SSAM-provided HID metadata. `struct surface_hid_device_ops` abstracts transport operations. `struct surface_hid_device` carries device/controller UID, descriptor data, notifier, HID device pointer, and ops.

Control flow: frontend drivers populate the structure and call `surface_hid_device_add()`; the core calls ops during parse/raw request/start/stop.

State and persistence: all per-device transport and HID registration state is centralized here.

Dependencies and integration: includes Linux HID/PM types and Surface Aggregator controller/device APIs.

Risks: packed descriptor layouts are enforced with `static_assert`; any firmware protocol change requires header updates and validation.

Test signals: compile-time size assertions and successful generic plus legacy transport probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_kbd.c -->
# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_kbd.c

Purpose: legacy SSAM keyboard HID transport for Surface Laptop 1 and 2.

Important APIs: SSAM KBD command IDs cover descriptor retrieval, caps-lock LED set, generic/hotkey input events, and feature report retrieval. Probe binds to the SSAM controller from an ACPI platform device, synthesizes a fixed SSAM UID, configures notifier/ops, and calls the shared core.

Control flow: descriptor and feature report operations issue synchronous SSAM requests and require exact response lengths. Input notifier manually filters target category/id/instance because registry and target category do not align. Output reports are limited to caps-lock LED; the code locates the LED field in the HID report and sends `SET_CAPSLOCK_LED`.

State and persistence: all state lives in `struct surface_hid_device`; feature report is hard-coded size and read-only. The platform driver matches ACPI ID `MSHW0096`.

Dependencies and integration: depends on Surface Aggregator controller client binding, platform driver core, HID helpers, and shared Surface HID core/PM ops.

Risks: only caps LED output reports are supported, so other output reports return `-EIO`. Manual UID filtering must stay aligned with firmware event routing. Feature report size/report ID assumptions are firmware-specific.

Test signals: ACPI platform probe defer/success, keyboard input and hotkey events, caps-lock LED toggling, feature report readback, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_kbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/uhid.c -->
# sources/distributed-fs/ceph-client/drivers/hid/uhid.c

Purpose: user-space HID transport exposed as `/dev/uhid`. It lets a userspace process create a virtual HID device, feed input reports to the HID core, and service output/get/set report requests emitted by HID drivers.

Important APIs/types: `struct uhid_device` tracks per-open instance state: dev mutex, running flag, report descriptor, HID device, output event ring, blocking report request state, and worker. `uhid_hid_driver` implements HID low-level callbacks. `uhid_fops` implements char-device open/read/write/poll/release. The misc device is registered with `module_misc_device()`.

Control flow: userspace writes `UHID_CREATE`/`CREATE2`; the driver copies descriptor data, allocates `hid_device`, marks it running, and schedules worker-based `hid_add_device()` so probe-time feature requests can round-trip to userspace. HID start/open/close/output/request callbacks enqueue events to the userspace-readable ring. Blocking get/set report callbacks serialize on `report_lock`, enqueue a request with an ID, wait up to 5 seconds, and are completed by userspace reply events. Input events written by userspace are passed to `hid_input_report()`.

State and persistence: each file descriptor owns one virtual device. `running` gates HID callbacks and is cleared on destroy, failed add, or release. Ring state is protected by spinlock; high-level lifecycle by `devlock`.

Dependencies and integration: depends on miscdevice, HID core, input, waitqueues, compat syscall handling, and `uapi/linux/uhid.h`. It integrates unprivileged-ish userspace device emulators with normal HID drivers.

Risks: `UHID_CREATE` contains a userspace pointer and is rejected when file credentials differ from current credentials; `CREATE2` avoids that. Queue overflow drops events. Failed `hid_add_device()` intentionally leaves `hid` allocated until close/reinit to avoid races. Blocking report operations depend on userspace timely replies.

Test signals: uhid selftests/userspace samples, create/destroy loops, compat `UHID_CREATE`, poll/read event ordering, get/set report timeout and reply handling, and input report delivery to HID/input subsystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/uhid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hid/usbhid/Kconfig

Purpose: build configuration for USB HID transport, optional hiddev/PID support, and legacy boot-protocol keyboard/mouse drivers.

Important symbols: `USB_HID` is the generic USB HID transport and defaults to yes when USB and HID are present. `HID_PID` enables PID force feedback support. `USB_HIDDEV` enables `/dev/usb/hiddevX`. `USB_KBD` and `USB_MOUSE` are expert boot-protocol alternatives when generic USB HID is not built in.

Control flow: Kconfig choices decide whether `usbhid`, `hiddev`, `hid-pidff`, `usbkbd`, and `usbmouse` objects are compiled.

State and persistence: no runtime state; it shapes kernel configuration.

Dependencies and integration: depends on USB, HID, and INPUT for boot-protocol input devices.

Risks: boot-protocol drivers are intentionally discouraged because they bypass generic HID functionality. `USB_HIDDEV` depends on generic USB HID.

Test signals: config matrix builds and runtime module loading for generic USB HID, hiddev, PID, usbkbd, and usbmouse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hid/usbhid/Makefile

Purpose: object composition for USB HID support.

Important entries: `usbhid-y := hid-core.o`; optional `hiddev.o` and `hid-pidff.o` are appended based on `CONFIG_USB_HIDDEV` and `CONFIG_HID_PID`; standalone `usbkbd.o` and `usbmouse.o` follow their boot-protocol configs.

Control flow: kernel build system links selected objects into modules or built-in code according to Kconfig.

State and persistence: no runtime state.

Dependencies and integration: ties the USB HID Kconfig symbols to compiled transport objects.

Risks: optional object ordering is simple, but missing Kconfig dependencies would surface as unresolved symbols.

Test signals: build with optional hiddev/PID enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-core.c -->
# sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-core.c

Purpose: generic USB HID transport driver. It binds USB HID interfaces to Linux HID devices, parses USB HID descriptors, manages interrupt/control URBs, queues report transfers, handles I/O errors/reset/PM, and registers the `usbhid` USB driver.

Important APIs: low-level HID driver callbacks include parse/start/stop/open/close/power/request/wait/raw_request/output_report/idle/may_wakeup. USB callbacks include probe/disconnect/suspend/resume/reset paths. Exported helpers include `hid_is_usb()` and `usbhid_find_interface()`. Module parameters tune mouse/joystick/keyboard poll intervals, LED autosuspend behavior, and boot quirks.

Control flow: probe requires an interrupt IN endpoint, allocates a HID device and `usbhid_device`, then calls `hid_add_device()`. Parse retrieves class/report descriptors and applies quirks. Start allocates coherent buffers and URBs, discovers interrupt endpoints, sets up control URB, handles always-poll and boot-keyboard LED/wakeup behavior. Open enables polling and remote wake; input URB completions feed `hid_safe_input_report()` and resubmit. Output/control reports are queued in FIFOs, submitted asynchronously with autosuspend refs, and advanced by completion callbacks. Error handling backs off, clears halts, or queues reset work.

State and persistence: `struct usbhid_device` stores URBs, buffers, queue heads/tails, lock/mutex, waitqueue, flags in `iofl`, retry timer/work, last transfer timestamps, interface and HID pointers. USB device/interface PM state is updated via autosuspend references and wakeup flags.

Dependencies and integration: depends on USB core, HID core, hidraw/hiddev, input, PID force feedback, workqueues, timers, and quirk infrastructure. It is the canonical USB transport below generic HID drivers.

Risks: concurrency is high: interrupt completions, spinlocked queues, autosuspend, reset work, timers, and disconnect paths all interact. Queue timeout recovery intentionally drops locks around URB unlink. Report descriptor changes across reset force rebind. Autosuspend rejects when LEDs/keys/queues/reset are active unless `ignoreled` permits.

Test signals: USB HID device enumeration, descriptor parse failures, continuous input, output/control report queueing, autosuspend/resume with pressed keys and LEDs, stall/reset recovery, disconnect races, hiddev/PID optional paths, and module quirk parameter parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-core.c -->
