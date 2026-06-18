# subset-b-001192 Comedi bus glue and board driver research

This grouped report covers the requested COMEDI core helper and low-level driver files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_pcmcia.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/comedi_pcmcia.c

## Purpose

This file is the bus glue between the COMEDI core and Linux PCMCIA drivers. It lets a low-level COMEDI driver recover its `struct pcmcia_device`, enable and disable PCMCIA resources, auto-create a COMEDI device during PCMCIA probe, tear it down during remove, and register/unregister the COMEDI and PCMCIA driver halves as a pair.

## Important APIs, types, and functions

The exported APIs are `comedi_to_pcmcia_dev()`, `comedi_pcmcia_enable()`, `comedi_pcmcia_disable()`, `comedi_pcmcia_auto_config()`, `comedi_pcmcia_auto_unconfig()`, `comedi_pcmcia_driver_register()`, and `comedi_pcmcia_driver_unregister()`. They operate on `struct comedi_device`, `struct pcmcia_device`, `struct comedi_driver`, and `struct pcmcia_driver`. The private `comedi_pcmcia_conf_check()` is the default `pcmcia_loop_config()` callback and rejects configuration index 0 before requesting I/O windows.

## Control Flow

A PCMCIA low-level driver normally calls the module helper macro that expands to paired registration. Registration first inserts the COMEDI driver with `comedi_driver_register()`, then calls `pcmcia_register_driver()`, rolling back COMEDI registration if PCMCIA registration fails. During PCMCIA probe, `comedi_pcmcia_auto_config()` calls `comedi_auto_config(&link->dev, driver, 0)`, so the COMEDI core allocates the device and invokes the driver's `auto_attach`. The `auto_attach` path may call `comedi_pcmcia_enable()`, which loops through socket configurations, requests I/O resources through the supplied or default callback, and activates the card with `pcmcia_enable_device()`. Removal calls `comedi_pcmcia_auto_unconfig()`, which delegates to `comedi_auto_unconfig()`.

## State and Persistence

No durable state is stored here. Runtime state is the reference from `dev->hw_dev` to the embedded PCMCIA device, PCMCIA resource allocation state inside the PCMCIA core, and paired driver registration in kernel lists. `comedi_pcmcia_disable()` is the cleanup companion for requested PCMCIA resources and is expected after failed enable paths.

## Dependencies and Integration Points

The file depends on `linux/comedi/comedi_pcmcia.h`, the PCMCIA core, and the COMEDI auto-configuration and driver-registration APIs. It is used by PCMCIA COMEDI low-level drivers listed in the drivers Makefile, and its exported symbols are GPL-only.

## Risks

The main risk is ordering: a failed `pcmcia_register_driver()` must unregister the COMEDI driver, and a failed `comedi_pcmcia_enable()` caller must still disable/release PCMCIA resources. `comedi_to_pcmcia_dev()` assumes `dev->hw_dev` really points to a `struct device` embedded in a `struct pcmcia_device`; using it with the wrong bus device is type-unsafe after the NULL check.

## Test Signals

Useful signals are successful module load/unload, a PCMCIA COMEDI card probing through `comedi_auto_config()`, valid I/O regions after `pcmcia_loop_config()`, correct cleanup on probe failure, and no stale COMEDI devices after PCMCIA remove or user-triggered COMEDI unconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_pcmcia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_usb.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/comedi_usb.c

## Purpose

This file is the USB bus helper layer for COMEDI drivers. It provides conversion helpers from a COMEDI device back to its USB interface or device, wrappers for auto-configuration and auto-unconfiguration, and paired registration of a COMEDI low-level driver with a `struct usb_driver`.

## Important APIs, types, and functions

The GPL-exported APIs are `comedi_to_usb_interface()`, `comedi_to_usb_dev()`, `comedi_usb_auto_config()`, `comedi_usb_auto_unconfig()`, `comedi_usb_driver_register()`, and `comedi_usb_driver_unregister()`. They bridge `struct comedi_device`, `struct usb_interface`, `struct usb_device`, `struct comedi_driver`, and `struct usb_driver`.

## Control Flow

USB driver probe calls `comedi_usb_auto_config(intf, driver, context)`, which passes `&intf->dev` and the context value into `comedi_auto_config()`. The COMEDI core allocates a device and invokes the low-level driver's `auto_attach`; that driver can recover the interface or USB device via the conversion helpers. USB disconnect calls `comedi_usb_auto_unconfig()`, delegating teardown to `comedi_auto_unconfig()`. Module registration first registers the COMEDI driver, then calls `usb_register()`, with COMEDI rollback on USB registration failure. Unregistration runs in the reverse order: USB first, COMEDI second.

## State and Persistence

This file has no private persistent state. State exists as kernel object references and registrations: `dev->hw_dev` links the COMEDI device to the USB interface's embedded device, the USB core tracks binding, and COMEDI tracks the allocated device and subdevices until unconfigured.

## Dependencies and Integration Points

It depends on `linux/comedi/comedi_usb.h`, the USB core, and COMEDI auto-configuration. It is the common integration point for USB COMEDI modules such as `dt9812`, `ni_usb6501`, `usbdux*`, and `vmk80xx`.

## Risks

The conversion helpers assume that `dev->hw_dev` is a USB interface device; using them from a non-USB auto-attach path would produce invalid container conversion. Driver-registration rollback is critical because a partially registered bus driver can otherwise leave COMEDI-visible board names without a matching USB probe path. Disconnect paths must tolerate devices already unconfigured through COMEDI user ioctls.

## Test Signals

Expected validation includes successful probe/disconnect cycles, `comedi_to_usb_dev()` returning the parent USB device in `auto_attach`, clean rollback when `usb_register()` fails, and no use-after-free or stale COMEDI device after cable disconnect while the device node is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers.c

## Purpose

This file is central COMEDI driver-management and low-level-driver support code. It owns the registered `comedi_driver` list, manual and automatic attachment flows, post-configuration normalization of subdevices, detach cleanup, helper allocation APIs, DIO/readback helpers, async scan accounting, event handling, firmware loading, legacy I/O-region helpers, and driver unregister cleanup.

## Important APIs, types, and functions

Important exported APIs include `comedi_set_hw_dev()`, `comedi_alloc_devpriv()`, `comedi_alloc_subdevices()`, `comedi_alloc_subdev_readback()`, `comedi_readback_insn_read()`, `comedi_timeout()`, `comedi_dio_insn_config()`, `comedi_dio_update_state()`, `comedi_bytes_per_scan_cmd()`, `comedi_bytes_per_scan()`, `comedi_nscans_left()`, `comedi_nsamples_left()`, `comedi_inc_scan_progress()`, `comedi_handle_events()`, `comedi_load_firmware()`, `__comedi_check_request_region()`, `comedi_check_request_region()`, `comedi_legacy_detach()`, `comedi_auto_config()`, `comedi_auto_unconfig()`, `comedi_driver_register()`, and `comedi_driver_unregister()`. Internal pieces include `comedi_device_detach_cleanup()`, `comedi_device_attach()`, `__comedi_device_postconfig()`, `__comedi_device_postconfig_async()`, `insn_rw_emulate_bits()`, and `comedi_recognize()`.

## Control Flow

Manual configuration enters `comedi_device_attach()` under `dev->mutex`, searches the global driver list under `comedi_drivers_list_lock`, recognizes board names through a driver board table, calls the selected driver's `attach`, then runs `comedi_device_postconfig()`. Auto-configured bus drivers call `comedi_auto_config()`, which allocates a COMEDI minor for the hardware device, sets driver and board name, invokes `auto_attach`, and runs the same postconfig path. Postconfig fills missing device and subdevice callbacks with invalid defaults, initializes DO `io_bits`, allocates async state and buffers for command-capable subdevices, assigns range tables, emulates one-channel read/write through `insn_bits` when possible, and marks the device attached under `attach_lock`.

Detach runs through `comedi_device_detach()` or unregister scanning. It cancels all activity, clears `attached`, increments `detach_count`, calls the low-level `detach`, and frees subdevice private data, minors, async buffers, readback arrays, device-private storage, pacer data, I/O/MMIO/IRQ bookkeeping, callback pointers, and the hardware-device reference. Async helpers compute scan lengths, remaining scans or samples, update scan progress and end-of-scan events, call low-level cancel on terminal events, and forward events to `_comedi_event()`.

## State and Persistence

Persistent storage is not used. Kernel runtime state includes the global `comedi_drivers` linked list, each `struct comedi_device`'s hardware reference, subdevice array, private data, async buffers, state/readback arrays, attachment flags, and counters such as `scans_done`, `scan_progress`, and `detach_count`. State is protected by `comedi_drivers_list_lock`, `dev->mutex`, `dev->attach_lock`, subdevice spin locks, and running-subdevice references. I/O regions, firmware contents, IRQs, and class-device minors are external resources managed by helper calls and cleanup paths.

## Dependencies and Integration Points

This file integrates with the COMEDI internal device/minor, buffer, async-event, and ioctl layers, Linux module references, firmware loading, I/O-port resource management, IRQ cleanup, DMA direction metadata, and low-level drivers on PCI, USB, PCMCIA, ISA, and other buses. Bus helper modules call `comedi_auto_config()` and `comedi_auto_unconfig()`; low-level drivers rely on its subdevice allocation, DIO, timeout, and readback helpers.

## Risks

The highest-risk areas are attach/detach locking, module reference lifetime, and async cleanup. Low-level driver attach failures must call detach and drop module references without leaving allocated minors or hardware references. `__comedi_device_postconfig_async()` allocates async structures before buffer allocation; error paths rely on later detach cleanup. DIO helpers only track up to 32 channels in `state` and `io_bits`; larger devices must split subdevices or handle state themselves. `comedi_timeout()` busy-waits for up to `COMEDI_TIMEOUT_MS`, so callbacks must be cheap and must return `-EBUSY` only while progress is plausible.

## Test Signals

Tests should cover manual `comedi_config` attach/detach, bus auto-probe/remove, low-level attach failure cleanup, driver unregister while devices are attached, async command setup and cancellation, scan accounting for finite and continuous commands, DIO input/output/query behavior, readback allocation and reads, firmware callback errors, I/O-region validation failures, and lockdep-clean detach from open devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/8255.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/8255.c

## Purpose

This standalone driver exposes one or more raw 8255 programmable peripheral interface chips as COMEDI digital I/O subdevices. It supports manual configuration through `comedi_config`, where each option is the I/O port base of one 8255 chip.

## Important APIs, types, and functions

The driver uses `subdev_8255_io_init()` and `subdev_8255_regbase()` from the shared 8255 helper, `__comedi_check_request_region()` for port ownership, `comedi_alloc_subdevices()` for one subdevice per chip, and `module_comedi_driver()` for legacy COMEDI registration. The main callbacks are `dev_8255_attach()` and `dev_8255_detach()`.

## Control Flow

Manual attach scans `it->options[]` until a zero base address, requiring at least one address. It allocates that many subdevices, then for each base requests a four-byte I/O region aligned to a four-byte boundary and initializes the subdevice with `subdev_8255_io_init()`. If initialization fails after requesting a region, the function releases that region immediately because the generic detach path cannot infer the base from an unused subdevice. Detach iterates initialized subdevices and releases each 8255 I/O region.

## State and Persistence

State is COMEDI subdevice state plus port ownership in the kernel resource tree. Direction and output state are handled by the shared 8255 helper. There is no persistent storage and no device-private allocation in this file.

## Dependencies and Integration Points

The file depends on `linux/comedi/comedidev.h` and `linux/comedi/comedi_8255.h`. Multifunction drivers can use the shared helper directly, while this module exists for simple ISA or PCI boards that map 8255 registers directly to known I/O ports.

## Risks

The driver only supports direct I/O-port mappings. Many PCI 8255 boards need PCI-specific BAR handling and should use a wrapper driver instead. Incorrect manual base addresses can conflict with other hardware, but `__comedi_check_request_region()` catches zero, out-of-range, misaligned, and already-owned regions. Cleanup depends on `s->type` not being left as a valid 8255 subdevice unless initialization completed.

## Test Signals

Validation includes manual configuration with one and multiple 8255 bases, direction changes in all four mode-0 port groups, input reads, output writes and readbacks, failure on missing options or conflicting I/O regions, and successful region release on detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/8255.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/8255_pci.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/8255_pci.c

## Purpose

This PCI wrapper supports generic PCI digital I/O boards built around one, two, or four 8255 chips. It maps the board's DIO BAR, performs optional NI MITE setup, and exposes each 8255 as a 24-channel COMEDI DIO subdevice.

## Important APIs, types, and functions

Key objects are `enum pci_8255_boardid`, `struct pci_8255_boardinfo`, the `pci_8255_boards[]` table, `pci_8255_mite_init()`, `pci_8255_auto_attach()`, `pci_8255_pci_table[]`, `pci_8255_driver`, and `pci_8255_pci_driver`. It calls `comedi_pci_enable()`, `pci_ioremap_bar()`, `subdev_8255_mm_init()`, `subdev_8255_io_init()`, and `module_comedi_pci_driver()`.

## Control Flow

PCI probe passes `id->driver_data` to `comedi_pci_auto_config()`. Auto-attach validates the board-table index, enables the PCI device, optionally programs the NI MITE I/O window so BAR 0 forwards to the main register BAR, chooses MMIO or port I/O from the DIO BAR flags, allocates `n_8255` subdevices, and initializes each subdevice at `i * I8255_SIZE`. Remove delegates to `comedi_pci_auto_unconfig()` and generic PCI detach.

## State and Persistence

Runtime state includes `dev->board_ptr`, `dev->board_name`, `dev->mmio` or `dev->iobase`, and each 8255 subdevice's direction/output state from the shared helper. MITE programming writes hardware bridge state but no persistent disk or NVRAM data.

## Dependencies and Integration Points

The driver depends on COMEDI PCI helpers, the shared 8255 helper, PCI IDs, optional `CONFIG_HAS_IOPORT`, and NI MITE-compatible boards. It integrates with ADLINK, Measurement Computing, and National Instruments PCI/PXI DIO devices through the PCI ID table.

## Risks

Board-table BAR numbers and chip counts must match each PCI ID. I/O-port boards are hidden when `CONFIG_HAS_IOPORT` is disabled, while MMIO-capable NI boards still work. MITE setup temporarily maps BAR 0 and writes `MITE_IODWBSR`; wrong BAR assumptions would redirect access incorrectly. Interrupt and 8254 timer features on some boards are intentionally unsupported.

## Test Signals

Expected signals are probe on representative one-, two-, and four-chip boards, correct number of 24-channel subdevices, valid MMIO and port-I/O operation, NI MITE boards responding after window setup, output/readback consistency, direction configuration by 8255 groups, and clean detach/unmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/8255_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/Makefile -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/Makefile

## Purpose

This Makefile maps COMEDI Kconfig symbols to individual low-level driver objects and helper modules. It is the build manifest for standalone helpers, misc drivers, ISA, PCI, PCMCIA, USB, National Instruments shared support, common helper objects, and COMEDI tests.

## Important APIs, types, and functions

The important interface is Kbuild's `obj-$(CONFIG_...) += ...` syntax. `ccflags-$(CONFIG_COMEDI_DEBUG) := -DDEBUG` enables debug builds. Composite object lists such as `ni_routing-objs` define multi-object modules. The requested files are wired by entries such as `CONFIG_COMEDI_8255_PCI`, `CONFIG_COMEDI_ADDI_*`, `CONFIG_COMEDI_ADL_*`, `CONFIG_COMEDI_8255`, and `CONFIG_COMEDI_8255_SA`.

## Control Flow

During kernel build, Kbuild evaluates enabled COMEDI config symbols and includes the matching objects. Helper modules like `comedi_8254.o`, `comedi_isadma.o`, `comedi_8255.o`, and `addi_watchdog.o` are built only when their symbols are enabled. Bus-specific groups are organized by comments but all produce ordinary Kbuild object lists. The tests directory is included through `obj-$(CONFIG_COMEDI_TESTS) += tests/`.

## State and Persistence

There is no runtime state. The persistent behavior is the source-controlled build mapping from configuration to modules. The list determines which drivers can be compiled into the kernel or as modules and which shared helper objects are available to low-level drivers.

## Dependencies and Integration Points

This file integrates with COMEDI Kconfig definitions, Linux Kbuild, and source files under `drivers/comedi/drivers/`. Ordering generally does not impose runtime load order, but missing helper entries or wrong config symbols can cause unresolved symbols or silently unavailable drivers.

## Risks

The risk is build coverage and dependency drift. A driver using a shared helper must have the helper selectable through Kconfig and listed here. Renames must update both Kconfig and Makefile entries. Composite modules such as `ni_routing` require all component paths to stay in sync. Conditional I/O-port-only drivers must still compile correctly under configurations that disable port I/O.

## Test Signals

Signals include `make drivers/comedi/drivers/` for multiple config sets, `COMEDI_DEBUG` builds showing `-DDEBUG`, all enabled requested objects appearing in build output, no unresolved symbols for `addi_watchdog` or `comedi_8255`, and successful `modinfo`/module load for selected low-level drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1032.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1032.c

## Purpose

This driver supports the ADDI-DATA APCI-1032 32-channel digital input PCI board. It exposes a normal 32-bit DI subdevice and, when an IRQ is available, an asynchronous change-of-state interrupt subdevice for channels 0-15.

## Important APIs, types, and functions

Key register definitions cover DI, interrupt mode, status, and control registers. `struct apci1032_private` stores AMCC interrupt-controller I/O base plus cached mode/control masks. Important functions are `apci1032_reset()`, `apci1032_cos_insn_config()`, `apci1032_cos_cmdtest()`, `apci1032_cos_cmd()`, `apci1032_cos_cancel()`, `apci1032_interrupt()`, `apci1032_di_insn_bits()`, `apci1032_auto_attach()`, and `apci1032_detach()`.

## Control Flow

PCI probe calls COMEDI PCI auto-config. Auto-attach allocates private data, enables the PCI device, records AMCC BAR 0 and board BAR 1 bases, resets interrupt hardware, requests a shared IRQ if present, and allocates two subdevices. The first subdevice reads all 32 digital inputs. The second is a command-capable DI subdevice only if IRQ setup succeeded. Users configure COS mode with `INSN_CONFIG_DIGITAL_TRIG`; command start writes mode masks and enables the selected OR-edge or AND-level interrupt mode. The ISR verifies AMCC interrupt assertion, disables the board interrupt, reads the status, writes one sample, handles COMEDI events, and reenables the interrupt.

## State and Persistence

State includes cached `mode1`, `mode2`, and `ctrl` in `dev->private`, `s->state` for the last COS status sample, `dev->iobase`, `dev->irq`, and AMCC I/O base. Hardware interrupt configuration persists until reset, cancel, or detach; no nonvolatile state is touched.

## Dependencies and Integration Points

The file depends on COMEDI PCI helpers, Linux IRQ APIs, and `amcc_s5933.h` for interrupt assertion checks. It integrates with COMEDI async buffers through `comedi_buf_write_samples()` and `comedi_handle_events()`.

## Risks

COS configuration uses bit shifts from user data; out-of-range shifts deliberately clear new masks but preserve behavior should be tested. AND and OR modes are mutually exclusive and switching modes wipes old channel masks. IRQ handling assumes `dev->read_subdev` exists and that the AMCC interrupt bit correctly identifies the board on shared IRQ lines. The driver is marked untested, so register semantics are a hardware risk.

## Test Signals

Validation should include probe, 32-channel DI reads, no-IRQ fallback with the COS subdevice unused, OR edge and AND level interrupt commands, cancel disabling interrupts, shared IRQ rejection when AMCC does not assert, and detach resetting mode/control registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1032.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1500.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1500.c

## Purpose

This driver supports the ADDI-DATA APCI-1500 16-channel DI / 16-channel DO PCI board with Zilog Z8536-based pattern interrupts and three counter/timer channels. It exposes DI, DO, and timer subdevices, with optional async DI interrupt support.

## Important APIs, types, and functions

`struct apci1500_private` stores AMCC and add-on BAR bases, clock source, and AND/OR trigger pattern masks. Z8536 access is serialized by `z8536_read()`, `z8536_write()`, and `z8536_reset()`. Other important functions include `apci1500_ack_irq()`, `apci1500_interrupt()`, `apci1500_di_cfg_trig()`, `apci1500_di_inttrig_start()`, `apci1500_di_cmdtest()`, `apci1500_di_cmd()`, `apci1500_di_cancel()`, `apci1500_timer_insn_config()`, `apci1500_timer_insn_read()`, `apci1500_timer_insn_write()`, and `apci1500_auto_attach()`.

## Control Flow

Auto-attach enables the PCI device, records BAR 0 AMCC, BAR 1 Z8536, and BAR 2 add-on bases, resets the Z8536, requests an IRQ, allocates three subdevices, initializes DI and DO, clears DO state, and sets up a three-channel timer subdevice. DI async commands are two-stage: users first configure AND or OR trigger patterns with `INSN_CONFIG_DIGITAL_TRIG`, then `do_cmd` installs an internal trigger callback. When the internal trigger fires, the driver writes Z8536 pattern masks, enables matching port interrupts, enables ports, and authorizes the main interrupt. The ISR acknowledges port A/B interrupt status, distinguishes port B diagnostic errors from input events, writes a status sample, and handles events.

## State and Persistence

Cached state includes trigger pattern mask/transition/polarity arrays, selected clock source, DO state in the subdevice, and Z8536 mode/counter registers. Hardware state is reset at attach and interrupt disable on detach. No disk persistence exists.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, AMCC S5933 definitions, Z8536 register definitions, COMEDI command validation helpers, DIO state helpers, and counter/timer instruction conventions including 8254 mode constants.

## Risks

Z8536 indexed control access is sensitive and protected by `dev->spinlock`; missing serialization would corrupt register selection. Pattern configuration is complex: AND trigger edge mode allows only one edge-detect channel per port, and invalid shifts must be rejected. `INSN_CONFIG_SET_GATE_SRC` appears to preserve only the gate-enable bit when updating mode, so mode-bit handling is a change-sensitive area. Timer clock-source mapping stores hardware value 3 for user source 2, which must remain documented by tests.

## Test Signals

Signals include DI reads, DO writes, OR/AND pattern interrupt samples for both ports, voltage and short-circuit diagnostic status bits, timer arm/disarm/read/write, all supported 8254-mode translations, clock-source get/set round trips, IRQ disable on cancel/detach, and no shared-IRQ handling when AMCC does not assert.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1516.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1516.c

## Purpose

This driver supports the ADDI-DATA APCI-1016, APCI-1516, and APCI-2016 PCI digital I/O boards. Depending on board ID, it exposes digital input, digital output, and an ADDI watchdog subdevice.

## Important APIs, types, and functions

The board table `apci1516_boardtypes[]` describes per-board DI channel count, DO channel count, and watchdog presence. `struct apci1516_private` stores the watchdog BAR base. Main functions are `apci1516_di_insn_bits()`, `apci1516_do_insn_bits()`, `apci1516_reset()`, `apci1516_auto_attach()`, and `apci1516_detach()`. Watchdog setup delegates to `addi_watchdog_init()` and reset to `addi_watchdog_reset()`.

## Control Flow

PCI probe passes the board table index as context. Auto-attach validates the index, sets the board name, allocates private data, enables PCI resources, records BAR 1 as the DIO base and BAR 2 as the watchdog base, allocates three subdevices, and marks unsupported per-board subdevices as unused. DO writes read the current hardware state, update masked bits with `comedi_dio_update_state()`, and write the result back. Attach finishes by resetting outputs/watchdog as applicable. Detach resets the board before generic PCI cleanup.

## State and Persistence

State is limited to `dev->iobase`, watchdog base, subdevice `state`, and hardware output/watchdog registers. No persistent configuration is stored.

## Dependencies and Integration Points

The file depends on COMEDI PCI helpers and the shared ADDI watchdog helper. It integrates with three PCI IDs through the PCI ID table and with COMEDI DIO instruction handling.

## Risks

`apci1516_reset()` returns early for boards without watchdog, so APCI-1016 output reset is irrelevant because it has no DO channels, but future board-table changes could make that control flow surprising. The driver assumes BAR 1 and BAR 2 layouts are consistent across the three IDs. DO state is initialized lazily from hardware during writes rather than during attach.

## Test Signals

Validation includes each PCI ID selecting the right subdevice mix, DI reads for APCI-1016/APCI-1516, DO writes for APCI-1516/APCI-2016, watchdog arm/disarm/ping on watchdog boards, outputs reset to zero on attach/detach, and unused subdevices for absent functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1516.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1564.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1564.c

## Purpose

This driver supports the ADDI-DATA APCI-1564 digital I/O board. It handles 32 DI, 32 DO, change-of-state interrupts for channels 4-19, a 12-bit timer, optional revision-2 counters, an 8-bit watchdog, and two diagnostic inputs.

## Important APIs, types, and functions

`struct apci1564_private` stores EEPROM, timer, optional counter bases, and cached COS masks/control. Important functions are `apci1564_reset()`, `apci1564_interrupt()`, `apci1564_di_insn_bits()`, `apci1564_do_insn_bits()`, `apci1564_diag_insn_bits()`, `apci1564_cos_insn_config()`, `apci1564_cos_cmdtest()`, `apci1564_cos_cmd()`, `apci1564_cos_cancel()`, `apci1564_timer_insn_config()`, `apci1564_counter_insn_config()`, timer/counter read/write handlers, and `apci1564_auto_attach()`.

## Control Flow

Auto-attach enables PCI, reads the EEPROM revision nibble, chooses revision-1 or revision-2 register mapping, resets all hardware blocks, optionally requests a shared IRQ, and allocates seven subdevices: DI, DO, COS event DI, timer, counter, watchdog, and diagnostics. COS configuration caches mode masks from `INSN_CONFIG_DIGITAL_TRIG`, masks them to channels 4-19, and `do_cmd` writes the masks/control to hardware. The ISR collects COS, timer, and counter interrupt sources into a single 32-bit event sample in `dev->read_subdev`, clears each source by toggling its control register, and calls `comedi_handle_events()` when any event bit was set.

## State and Persistence

Runtime state includes the revision-dependent register bases, cached COS `mode1`, `mode2`, `ctrl`, subdevice states, watchdog private state, and timer/counter control registers. The event sample encodes event flags plus COS input state. Attach/detach reset outputs, interrupt masks, watchdog, timer, and counters. There is no nonvolatile state modification.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, Linux IRQs, `addi_tcw.h` for timer/counter/watchdog register offsets, and `addi_watchdog.h` for the watchdog subdevice. It integrates COMEDI async command flow for COS but controls timer and counters through synchronous `insn_config`.

## Risks

The revision-dependent BAR map is a major risk; wrong EEPROM revision interpretation moves every register base. The timer and counter portions carry FIXME notes that the datasheet does not fully define `ADDI_TCW_TIMEBASE_REG` or counter operation, so raw values may not behave as user-visible COMEDI conventions imply. The shared `read_subdev` event stream mixes COS, timer, and counters, so consumers must parse flags correctly. COS command validation allows no command unless masks/control are configured.

## Test Signals

Useful tests include revision-1 and revision-2 probe, DI/DO reads/writes, COS edge and level interrupts only for channels 4-19, timer arm/disarm/status/read/write, revision-2 counter arm/disarm/status/read/write, watchdog operation, diagnostic input reads, and detach resetting all interrupt and output state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1564.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_16xx.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_16xx.c

## Purpose

This driver supports ADDI-DATA APCI-1648 and APCI-1696 TTL digital I/O boards. It splits 48 or 96 digital channels into COMEDI DIO subdevices of up to 32 channels each.

## Important APIs, types, and functions

The board table `apci16xx_boardtypes[]` describes board names and total channel counts. Register macros compute per-subdevice input, output, and direction registers. Main callbacks are `apci16xx_insn_config()`, `apci16xx_dio_insn_bits()`, and `apci16xx_auto_attach()`.

## Control Flow

PCI auto-attach selects board data from context, enables the PCI device, stores BAR 0 as `dev->iobase`, computes the number of subdevices needed for all channels, allocates them, and initializes each as readable/writable DIO. Each subdevice defaults all channels to input by writing zero to its direction register. Direction configuration maps the target channel to an eight-bit port mask and updates the whole port via `comedi_dio_insn_config()` before writing `s->io_bits` to the per-subdevice direction register. Bit I/O updates output state when the mask changes, then reads current input state from the input register.

## State and Persistence

State is held in each subdevice's `io_bits` and `state` plus the hardware direction and output registers. There is no private allocation and no persistent storage. Detach uses generic PCI cleanup and does not explicitly reset outputs.

## Dependencies and Integration Points

The file depends on COMEDI PCI helpers and generic COMEDI DIO helpers. It integrates through PCI IDs for APCI-1648 and APCI-1696.

## Risks

The calculation of the last subdevice's channel count deserves attention for non-multiple-of-32 boards; for these board counts it produces 16 for APCI-1648's second subdevice and three full subdevices for APCI-1696. Direction granularity is eight channels, not per channel, and users need query behavior to reflect grouped configuration. Lack of explicit detach reset may leave output states until PCI removal/hardware reset.

## Test Signals

Test signals include correct subdevice/channel counts for both boards, default input direction after attach, grouped direction changes per 8-bit port, output writes, input reads, DIO query results, and clean behavior under `CONFIG_HAS_IOPORT`/PCI resource variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_16xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_2032.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_2032.c

## Purpose

This driver supports the ADDI-DATA APCI-2032 32-channel digital output board with an ADDI watchdog and two diagnostic interrupt/status channels for VCC and short-circuit/current-condition errors.

## Important APIs, types, and functions

Key functions are `apci2032_do_insn_bits()`, `apci2032_int_insn_bits()`, `apci2032_int_cmdtest()`, `apci2032_int_cmd()`, `apci2032_int_cancel()`, `apci2032_interrupt()`, `apci2032_reset()`, `apci2032_auto_attach()`, and `apci2032_detach()`. `struct apci2032_int_private` tracks async activity and enabled interrupt sources under a spinlock. Watchdog support uses `addi_watchdog_init()` and `addi_watchdog_reset()`.

## Control Flow

Auto-attach enables PCI, sets BAR 1 as the device I/O base, resets outputs/interrupts/watchdog, requests a shared IRQ if present, and allocates DO, watchdog, and diagnostic DI subdevices. The interrupt subdevice is command-capable only with an IRQ. A command builds an enabled-source mask from the channel list, marks the subdevice active, and writes the mask to the interrupt control register. The ISR verifies the device IRQ status, reads diagnostic status, disables triggered level-sensitive sources to prevent interrupt storms, writes packed scan bits corresponding to channel-list indices, and sets end-of-acquisition when finite scans complete.

## State and Persistence

State includes hardware DO register value, interrupt enable/status registers, watchdog registers, and `apci2032_int_private` fields. Triggered diagnostic interrupt sources are intentionally disabled after firing. Detach resets hardware and frees the manually allocated interrupt private data after generic PCI cleanup.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, Linux IRQ/spinlock APIs, generic DIO helpers, async command helpers, and the ADDI watchdog module. It integrates diagnostic status with COMEDI's packed digital async buffer format.

## Risks

The ISR checks `dev->attached` before using subdevices, which avoids early shared IRQ races. Finite-count completion depends on `scans_done` being advanced by COMEDI event handling after samples are written; changes in event ordering could affect EOA timing. Manual `kfree(dev->read_subdev->private)` must not conflict with automatic subdevice private cleanup; the allocation uses raw `kzalloc_obj`, not `comedi_alloc_spriv`, so the explicit free is required. Level-sensitive diagnostic interrupts are not reenabled automatically after firing.

## Test Signals

Validation includes DO writes/readback, watchdog arm/disarm/ping, diagnostic status reads, async commands for each diagnostic channel and both channels, level-sensitive source disabling after interrupt, finite and continuous stop modes, cancel disabling interrupts, and detach freeing private state without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_2032.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_2200.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_2200.c

## Purpose

This driver supports the ADDI-DATA APCI-2200 relay board with 8 digital inputs, 16 digital outputs, and an ADDI watchdog/timer block exposed as a watchdog subdevice.

## Important APIs, types, and functions

The file defines simple register offsets for DI, DO, and watchdog. Main functions are `apci2200_di_insn_bits()`, `apci2200_do_insn_bits()`, `apci2200_reset()`, `apci2200_auto_attach()`, and `apci2200_detach()`. Watchdog handling is delegated to `addi_watchdog_init()` and `addi_watchdog_reset()`.

## Control Flow

PCI probe invokes COMEDI PCI auto-config. Auto-attach enables PCI resources, sets BAR 1 as `dev->iobase`, allocates three subdevices, initializes the DI and DO subdevices, initializes the watchdog subdevice at the watchdog offset, and resets outputs/watchdog. DO writes read the current output state, update requested bits through `comedi_dio_update_state()`, and write the new 16-bit state. Detach resets hardware before generic PCI cleanup.

## State and Persistence

Runtime state is output state in hardware and `s->state`, watchdog private state, and `dev->iobase`. There is no persistent storage. Outputs and watchdog reload/control are cleared on attach and detach.

## Dependencies and Integration Points

The driver depends on COMEDI PCI helpers, COMEDI DIO helpers, and the shared ADDI watchdog helper. It binds one ADDI-DATA PCI device ID.

## Risks

The implementation assumes BAR 1 layout exactly matches the register map. DO state is initialized from hardware on each write, which is robust to external state changes but can surprise tests that expect attach-time `s->state` initialization. The watchdog helper uses an 8-bit reload value and a fixed 20 ms time base.

## Test Signals

Signals include successful probe, 8-bit DI reads, 16-bit DO masked writes, outputs reset to zero, watchdog arm/read/ping/disarm, and detach resetting output and watchdog registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_2200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3120.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3120.c

## Purpose

This driver supports ADDI-DATA APCI-3120 and APCI-3001 analog input boards. It provides analog input instruction and command support, optional DMA through an AMCC S5933 bridge, optional analog output for APCI-3120, 4-bit DI/DO, and a timer subdevice.

## Important APIs, types, and functions

Key types are `struct apci3120_board`, `struct apci3120_dmabuf`, and `struct apci3120_private`. Important functions include `apci3120_addon_write()`, `apci3120_init_dma()`, `apci3120_setup_dma()`, `apci3120_ns_to_timer()`, timer read/write/mode/enable helpers, `apci3120_set_chanlist()`, `apci3120_interrupt_dma()`, `apci3120_interrupt()`, `apci3120_ai_cmdtest()`, `apci3120_ai_cmd()`, `apci3120_cancel()`, `apci3120_ai_insn_read()`, `apci3120_ao_insn_write()`, DIO handlers, timer `insn_config`, DMA allocation/free, reset, auto-attach, and detach.

## Control Flow

Auto-attach selects board data, allocates private state, enables PCI, sets bus master, records AMCC/add-on/main BARs, resets interrupt/control state, requests an IRQ, allocates coherent DMA buffers when IRQ setup succeeds, detects oscillator base from board revision/status, and allocates AI, AO, DI, DO, and timer subdevices. AI instruction reads set a one-channel chanlist, configure timer 0 for a 10 us software-triggered conversion, poll EOC with `comedi_timeout()`, and read FIFO data. AI commands validate start/scan/convert/stop triggers, program chanlist, optional external trigger, scan and conversion timers, DMA or EOS interrupt mode, then enable acquisition. The ISR handles AMCC DMA completion, EOS PIO sampling, timer2 cleanup, abort diagnostics, finite stop, and COMEDI events.

## State and Persistence

State includes cached `ctrl`, `mode`, timer mode, 4-bit DO state, oscillator base, DMA buffer descriptors, DMA mode flags, current DMA buffer selector, and hardware AMCC/add-on counters. DMA buffers are coherent memory tied to `dev->hw_dev` and freed at detach. No persistent storage is modified.

## Dependencies and Integration Points

The driver depends on COMEDI PCI helpers, AMCC S5933 definitions, DMA coherent allocation, COMEDI async buffers/events, range tables, trigger validation, and readback allocation for AO. It integrates tightly with COMEDI command semantics for finite and continuous AI acquisition.

## Risks

The DMA path is high risk: transfer counts are bytes, sample size is 16 bits, odd byte counts are fatal, and double-buffer sizing changes for `CMDF_WAKE_EOS` and finite stop counts. `apci3120_ai_eoc()` treats EOC bit clear as completion, so polarity must match hardware. Detach calls generic PCI detach before DMA free, but DMA buffers use `dev->hw_dev`; lifetime assumptions should be preserved. Timer divisor rounding and minimum divisor constraints define acquisition timing and can affect user-visible rates.

## Test Signals

Validation should cover APCI-3120 and APCI-3001 probe, revision A/B oscillator timing, single AI reads across ranges/reference modes, command AI with PIO and DMA, finite stop counts, `CMDF_WAKE_EOS`, external trigger gating, AO writes/readback on APCI-3120, 4-bit DIO, timer arm/disarm/mode/status/read, DMA abort logging, cancel quiescing DMA/timers, and coherent buffer cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3120.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3501.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3501.c

## Purpose

This driver supports the ADDI-DATA APCI-3501 analog output board variants with 4 or 8 AO channels, 2 digital inputs, 2 digital outputs, and an EEPROM memory subdevice. The timer/watchdog hardware is recognized in comments but not supported as a COMEDI subdevice.

## Important APIs, types, and functions

`struct apci3501_private` stores the AMCC base. Important functions are `apci3501_wait_for_dac()`, `apci3501_ao_insn_write()`, DIO handlers, `apci3501_eeprom_wait()`, `apci3501_eeprom_readw()`, `apci3501_eeprom_get_ao_n_chan()`, `apci3501_eeprom_insn_read()`, `apci3501_reset()`, `apci3501_auto_attach()`, and `apci3501_detach()`.

## Control Flow

Auto-attach enables PCI, records AMCC BAR 0 and board BAR 1, reads AMCC NVRAM user data to determine analog-output channel count, allocates five subdevices, initializes AO if the EEPROM reports channels, initializes 2-bit DI and DO, leaves timer/watchdog unused, adds a 256-word internal memory subdevice for EEPROM reads, and resets outputs. AO writes set board-wide range mode, wait until the DAC ready bit is set, write channel/value data, and update readback. Reset clears DO and drives all eight possible AO channels to 0 V bipolar.

## State and Persistence

Runtime state is AO readback, DO state, board-wide AO range mode, and AMCC EEPROM read state. The driver reads EEPROM but does not write it. Reset writes current analog/digital outputs but no nonvolatile data.

## Dependencies and Integration Points

The file depends on COMEDI PCI, AMCC S5933 NVRAM register definitions, COMEDI readback helpers, and range tables. It integrates with PCI ID `0x3001`, whose variants share IDs and require EEPROM feature discovery.

## Risks

`apci3501_wait_for_dac()` spins without an explicit timeout, unlike most COMEDI wait paths, so broken hardware can hang the caller. AO range is board-wide although exposed per-channel through chanspec; writing one channel can change all channels' output range. EEPROM parsing must match ADDI function descriptors or AO may be disabled. Reset loops over eight channels even when only four exist, relying on harmless writes.

## Test Signals

Signals include EEPROM-reported 4- and 8-channel variants, AO bipolar/unipolar writes with readback, rejection of >13-bit unipolar values, DI/DO bits, EEPROM memory reads, reset setting outputs to zero, and behavior when DAC ready never appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3501.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3xxx.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3xxx.c

## Purpose

This broad ADDI-DATA driver supports many APCI-3000/3002/3003/3006/3010/3016/3100/3106/3110/3116/3500 variants. It exposes variant-dependent AI, AO, isolated DI/DO, and 24-channel TTL DIO subdevices using PCI I/O and MMIO resources.

## Important APIs, types, and functions

The large `apci3xxx_boardtypes[]` table describes names, AI channel counts, resolution, supported conversion time units, minimum acquisition times, and optional AO/DIO features. Main functions include `apci3xxx_irq_handler()`, `apci3xxx_ai_started()`, `apci3xxx_ai_setup()`, `apci3xxx_ai_insn_read()`, `apci3xxx_ai_ns_to_timer()`, `apci3xxx_ai_cmdtest()`, `apci3xxx_ai_cmd()`, `apci3xxx_ao_insn_write()`, isolated DI/DO handlers, TTL DIO config/bits handlers, `apci3xxx_reset()`, `apci3xxx_auto_attach()`, and `apci3xxx_detach()`.

## Control Flow

PCI auto-attach selects board data, allocates private state, enables PCI, records BAR 2 as port I/O and maps BAR 3 as MMIO, optionally requests an IRQ, computes how many subdevices are required for the variant, and initializes each supported function in order. AI instruction reads call `apci3xxx_ai_setup()` for a single channel, start conversion, poll EOS, and read FIFO data. Command AI support is limited to a single channel with timer conversion and IRQ completion despite comments that hardware supports more scan modes. The IRQ handler checks a status bit, clears it, writes one sample from the FIFO, sets EOA, and handles events.

## State and Persistence

State consists of `ai_timer` and `ai_time_base` cached during command validation, AO readback arrays, DIO `state` and `io_bits`, MMIO/I/O mappings, and hardware FIFO/status/config registers. Reset disables IRQ around clearing start, interrupt flags, EOS, and FIFO entries. There is no persistent storage.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, MMIO accessors, COMEDI trigger validation, timeout polling, readback allocation, and DIO helpers. It binds many ADDI PCI IDs to table entries and uses board metadata rather than per-device code paths.

## Risks

The broad board table is the primary correctness surface: wrong feature flags or timing units create incorrect subdevices or invalid acquisition timing. `apci3xxx_ai_ns_to_timer()` stores `*ns = timer * time_base`, which uses the enum value rather than the nanosecond base and appears suspicious for command argument fixup. `apci3xxx_reset()` disables and enables `dev->irq` even if no IRQ was assigned, so no-IRQ paths need scrutiny. AI command support is intentionally limited and may not match hardware capabilities.

## Test Signals

Testing should include representative variants with and without AI/AO/DIO, AI single reads across range/reference settings, AI command timing validation and IRQ completion, AO writes/readback, isolated DI/DO reads/writes, TTL fixed input/output/programmed port behavior, reset with and without IRQ, and each PCI ID selecting the expected subdevice layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_tcw.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_tcw.h

## Purpose

This header centralizes register offsets and bit definitions for ADDI-DATA timer/counter/watchdog blocks used by several COMEDI drivers. It avoids duplicating TCW register layout constants in each board driver.

## Important APIs, types, and functions

There are no functions or types. The exported preprocessor interface includes offsets such as `ADDI_TCW_VAL_REG`, `ADDI_TCW_SYNC_REG`, `ADDI_TCW_RELOAD_REG`, `ADDI_TCW_TIMEBASE_REG`, `ADDI_TCW_CTRL_REG`, `ADDI_TCW_STATUS_REG`, `ADDI_TCW_IRQ_REG`, and warning-time registers. Bit and field macros cover sync trigger/enable/disable controls, control-mode fields, external clock/gate/trigger selection, timer/counter/watchdog enables, IRQ enable, status flags, and IRQ indication.

## Control Flow

The header has no control flow. Including drivers use these constants to construct `inl()`/`outl()` register accesses for watchdog, timer, and counter operations.

## State and Persistence

No state is stored. The definitions describe hardware register state managed by including drivers.

## Dependencies and Integration Points

The header assumes Linux `BIT()` is available through including source files. It is used by `addi_watchdog.c`, `addi_apci_1564.c`, and other ADDI TCW-capable drivers. The constants form a shared contract between board-specific offsets and common watchdog behavior.

## Risks

Incorrect bit masks here affect every driver using the TCW helper. Some register offsets alias by function, such as value and sync at offset zero, so call sites must know which TCW mode is active. Field macros mask only low bits of inputs, which is convenient but can hide invalid caller values if not separately checked.

## Test Signals

Signals are compile coverage for all including drivers, watchdog arm/ping/reset behavior, timer/counter status bits matching hardware, IRQ-bit recognition, and no divergent local copies of the same TCW constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_tcw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_watchdog.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_watchdog.c

## Purpose

This helper implements a reusable COMEDI watchdog subdevice for ADDI-DATA boards that expose a TCW-compatible watchdog register block.

## Important APIs, types, and functions

`struct addi_watchdog_private` stores the watchdog base and cached control value. Exported APIs are `addi_watchdog_reset()` and `addi_watchdog_init()`. Subdevice callbacks are `addi_watchdog_insn_config()`, `addi_watchdog_insn_read()`, and `addi_watchdog_insn_write()`.

## Control Flow

Board drivers call `addi_watchdog_init(s, iobase)`, which allocates subdevice private data, stores the base, and configures the subdevice as a writable one-channel timer with 8-bit maxdata and config/read/write handlers. `INSN_CONFIG_ARM` stores `ADDI_TCW_CTRL_ENA`, masks the reload value to 8 bits, writes the reload register, logs the effective timeout using a 20 ms base, and writes the control register. `INSN_CONFIG_DISARM` clears the cached control and writes it. Writes ping the watchdog by writing cached control ORed with `ADDI_TCW_CTRL_TRIG`; reads return the TCW status register.

## State and Persistence

State is subdevice-private `iobase` and `wdog_ctrl` plus hardware reload/control/status registers. `addi_watchdog_reset()` clears control and reload. There is no persistent storage.

## Dependencies and Integration Points

The helper depends on COMEDI subdevice-private allocation and `addi_tcw.h` register definitions. Board drivers use it for APCI-1516/2016, APCI-1564, APCI-2032, APCI-2200, and similar boards.

## Risks

The helper assumes an 8-bit reload and fixed 20 ms time base for all users. A write while disabled returns `-EINVAL`, so user-space must arm before pinging. The subdevice is marked only `SDF_WRITABLE` even though it installs an `insn_read`; that flag choice may affect discoverability. Since `data[1]` is masked rather than range-checked, too-large reloads silently wrap.

## Test Signals

Validation includes init allocating private data, arm writing reload/control and reporting timeout, read returning status, ping toggling trigger only when armed, disarm clearing control, reset clearing control/reload, and all dependent board drivers probing with watchdog subdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_watchdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_watchdog.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_watchdog.h

## Purpose

This header declares the shared ADDI-DATA watchdog helper API used by board drivers with TCW-compatible watchdog blocks.

## Important APIs, types, and functions

It forward-declares `struct comedi_subdevice` and declares `addi_watchdog_reset(unsigned long iobase)` plus `addi_watchdog_init(struct comedi_subdevice *s, unsigned long iobase)`.

## Control Flow

There is no runtime control flow. Including drivers call `addi_watchdog_init()` during subdevice setup and `addi_watchdog_reset()` from reset/detach paths.

## State and Persistence

The header stores no state. State is allocated and managed by `addi_watchdog.c`.

## Dependencies and Integration Points

The include guard `_ADDI_WATCHDOG_H` prevents duplicate declarations. The forward declaration keeps this header lightweight for board drivers that already include COMEDI headers indirectly.

## Risks

API changes here must be synchronized with all ADDI board drivers and the helper implementation. Since the reset API accepts a raw I/O base, callers are responsible for passing the watchdog block base, not the board main base unless the watchdog is at offset zero.

## Test Signals

Signals are clean compilation of all including drivers, correct symbol resolution when `CONFIG_COMEDI_ADDI_WATCHDOG` is enabled, and no duplicate prototype warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci6208.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci6208.c

## Purpose

This driver supports ADLINK PCI-6208/6216 analog output cards. It treats all supported IDs as a PCI-6216-style device with 16 AO channels, plus 4 digital inputs and 4 digital outputs.

## Important APIs, types, and functions

Important functions are `pci6208_ao_eoc()`, `pci6208_ao_insn_write()`, `pci6208_di_insn_bits()`, `pci6208_do_insn_bits()`, and `pci6208_auto_attach()`. It uses `comedi_offset_munge()` for bipolar AO data representation, `comedi_timeout()` for DAC readiness, `comedi_alloc_subdev_readback()`, and COMEDI PCI auto-config.

## Control Flow

Auto-attach enables the PCI device, stores BAR 2 as `dev->iobase`, allocates AO, DI, and DO subdevices, and initializes the DO subdevice state from the hardware DIO register. AO writes wait until the data-send status bit clears, convert the COMEDI offset-binary value to the hardware's two's-complement encoding, write the channel register, and update readback. DI reads the upper four DIO bits; DO writes the low four bits through the shared DIO state helper.

## State and Persistence

State is AO readback, DO subdevice state, and hardware DIO/AO registers. No persistent storage is used. The driver does not explicitly reset outputs at detach.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, COMEDI timeout/readback helpers, Linux delay headers, and ADLINK/PLX PCI IDs. It integrates two PCI ID forms: native ADLINK and PLX subsystem ID.

## Risks

The driver exposes 16 AO channels even though PCI-6208 hardware only has 8 usable channels; upper channels may write registers without DACs. AO readiness relies on `comedi_timeout()` and the `DATA_SEND` bit polarity. DO writes use the whole DIO register with low bits only; DI bits must not be corrupted by output writes.

## Test Signals

Signals include probe via both PCI IDs, AO write/readback and voltage verification on real channels, timeout behavior if DAC remains busy, 4-bit DI reads, 4-bit DO writes and initial state capture, and clean detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci6208.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci7250.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci7250.c

## Purpose

This driver supports ADLINK PCI-7250, LPCI-7250, and LPCIe-7250 relay output and isolated digital input boards. It exposes paired relay DO and DI subdevices with either 8 or 32 channels depending on the board variant.

## Important APIs, types, and functions

Key functions are `adl_pci7250_read8()`, `adl_pci7250_write8()`, `adl_pci7250_do_insn_bits()`, `adl_pci7250_di_insn_bits()`, and `pci7250_auto_attach()`. The access helpers abstract MMIO versus port I/O. PCI IDs distinguish older I/O-port variants and newer LPCIe MMIO subsystem ID `0x7000`.

## Control Flow

Auto-attach enables PCI, verifies BAR 2 length, maps BAR 2 as MMIO or records it as I/O port space, chooses `max_chans` as 8 for the newer LPCIe subsystem device and 32 for other variants, allocates two subdevices, initializes relay DO state by reading even offset registers, and initializes DI reads from odd offset registers. DO writes walk byte-wide banks and write only banks whose mask includes changed bits.

## State and Persistence

State is relay output state in `s->state` and hardware relay registers. Inputs are read directly. No persistent data is stored, and detach does not reset relays.

## Dependencies and Integration Points

The driver depends on COMEDI PCI helpers, optional `CONFIG_HAS_IOPORT`, MMIO byte accessors, and ADLINK/PLX PCI subsystem IDs. It integrates with both legacy port-I/O and newer MMIO board designs.

## Risks

Channel count depends on subsystem ID and an assumption that older boards may have PCI-7251 expansion modules. Missing modules simply make extra channels ineffective. The `insn_bits` callbacks return `2` rather than `insn->n`, matching the two-word bits instruction convention but worth preserving. MMIO and I/O-port paths must stay equivalent.

## Test Signals

Validation includes old and new subsystem IDs, 8-channel limit on newer LPCIe, 32-channel behavior on older variants, initial relay state readback, per-bank masked DO writes, DI reads from odd offsets, operation without I/O port support for MMIO boards, and clean unmap/release on detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci7250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci7x3x.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci7x3x.c

## Purpose

This driver supports ADLINK PCI-723x and PCI-743x isolated digital I/O boards. It creates one or two DI/DO subdevices depending on board width and, for PCI-7230, optional async interrupt subdevices for isolated input channels 0 and 1 through a PLX9052 bridge.

## Important APIs, types, and functions

The board table `adl_pci7x3x_boards[]` defines subdevice count and DI/DO/IRQ channel counts. Private types are `adl_pci7x3x_dev_private_data` for PLX local config register base and interrupt control, and `adl_pci7x3x_sd_private_data` for per-interrupt-subdevice state. Important functions are `adl_pci7x3x_interrupt()`, `process_irq()`, `adl_pci7x3x_asy_cmdtest()`, `adl_pci7x3x_asy_cmd()`, `adl_pci7x3x_asy_cancel()`, DI/DO instruction handlers, `adl_pci7x3x_reset()`, and `adl_pci7x3x_auto_attach()`.

## Control Flow

Auto-attach selects board metadata, allocates device private data, enables PCI, records BAR 2 for DIO and BAR 1 for PLX local configuration, resets interrupts, optionally requests an IRQ for boards with interrupt channels, allocates the board-defined number of subdevices, and initializes DI and/or DO subdevices in 32-channel banks. For IRQ subdevices, it allocates subdevice private data, sets their source port offset, and installs command callbacks when IRQ setup succeeded. Async command start enables the matching PLX local interrupt line and marks the subdevice running. The ISR checks PLX LINT status bits, clears board interrupt flags, and calls `process_irq()` for subdevices 2 and 3.

## State and Persistence

State includes PLX interrupt control cache, per-subdevice command-running flags, DIO output state, and hardware PLX/DIO registers. There is no persistent storage. Detach resets PLX interrupt enables before generic PCI cleanup.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, `plx9052.h`, COMEDI async APIs, spinlocks, and ADLINK PCI IDs. It integrates hardware external interrupts into COMEDI async DI buffers.

## Risks

Interrupt support is documented as only currently supporting PCI-7230 despite board comments mentioning others. `dev->read_subdev` is overwritten for each IRQ subdevice, so generic fields only point to the last one even though the ISR directly indexes subdevices 2 and 3. DO handling for 16-channel PCI-7230 writes the state in both halves of a 32-bit register due to hardware behavior. Shared IRQ handling must ignore interrupts before `dev->attached`.

## Test Signals

Signals include correct subdevice layouts for all six boards, DI reads from low and high banks, DO writes for 16/32/64-channel boards, PCI-7230 interrupt commands on IDI0 and IDI1, cancel disabling PLX lines, shared IRQ rejection when LINT bits are not active, and detach clearing interrupt control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci7x3x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci8164.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci8164.c

## Purpose

This experimental driver supports the ADLINK PCI-8164 four-axis motion-control board by exposing axis register windows as generic COMEDI procedure subdevices.

## Important APIs, types, and functions

Register macros define per-axis offsets and four register groups: command/status, output/status, buffer 0, and buffer 1. The shared callbacks are `adl_pci8164_insn_read()` and `adl_pci8164_insn_write()`. `adl_pci8164_auto_attach()` creates four `COMEDI_SUBD_PROC` subdevices, each with four channels, using `s->private` to store the register offset.

## Control Flow

PCI probe calls COMEDI PCI auto-config. Auto-attach enables PCI, stores BAR 2 as `dev->iobase`, allocates four subdevices, and assigns each subdevice to one register group. Reads and writes compute `dev->iobase + PCI8164_AXIS(chan) + offset` for the channel and perform 16-bit port I/O for each requested sample. Detach uses generic PCI cleanup.

## State and Persistence

The driver keeps no private state beyond each subdevice's register offset pointer. Hardware command, status, and buffer registers hold runtime motion-controller state. There is no persistent storage and no explicit reset.

## Dependencies and Integration Points

The file depends on COMEDI PCI helpers and port I/O accessors. It presents low-level register access rather than a higher-level motion-control API, so user space must understand the PCI-8164 register protocol.

## Risks

Because the driver exposes raw procedure registers, incorrect user writes can directly affect motion hardware. There is no validation beyond channel count, no interrupt support, no reset, and no semantic decoding of command/status registers. The use of integer offsets stored in `void *` is a common older COMEDI pattern but should not be expanded without care.

## Test Signals

Validation includes probe, correct four subdevices with four channels each, 16-bit reads and writes to each axis/register group, expected hardware status changes after commands, bounds behavior for channel selection through COMEDI core, and clean detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci8164.c -->
