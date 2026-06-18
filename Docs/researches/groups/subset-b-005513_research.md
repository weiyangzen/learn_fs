# subset-b-005513 research: USB host controller sources

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/sl811-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/sl811-hcd.c

## Purpose
`sl811-hcd.c` implements a USB 1.1 host-controller driver for the Cypress/ScanLogic SL811HS embedded controller. It is a PIO-only HCD: the CPU copies every packet into or out of the controller's small register-backed packet buffers, arms a transfer register bank, and advances URBs from interrupt context. The driver is exposed as a platform driver named `sl811-hcd` and is also exported so the PCMCIA glue in `sl811_cs.c` can bind a CF card instance to it.

## Important APIs, Types, And Functions
The file implements a `struct hc_driver` named `sl811h_hc_driver` with `.irq`, `.start`, `.stop`, `.urb_enqueue`, `.urb_dequeue`, `.endpoint_disable`, `.get_frame_number`, `.hub_status_data`, and `.hub_control`. Its private state is `struct sl811` from `sl811.h`; per-endpoint state is `struct sl811h_ep`. Packet setup helpers (`setup_packet()`, `status_packet()`, `in_packet()`, `out_packet()`) program SL811 transfer registers and packet buffers. `start()` selects the next endpoint from the periodic or async software schedule, and `start_transfer()` arms the A transfer bank, with optional B-bank support compiled out by default. `done()` consumes a packet completion and either schedules the next PID or calls `finish_request()`. `sl811h_irq()` is the main interrupt routine. Root-hub behavior is handled by `sl811h_hub_status_data()`, `sl811h_hub_control()`, and `sl811h_timer()`. `sl811h_probe()` maps IO or MMIO resources, validates chip revision, and calls `usb_add_hcd()`.

## Control Flow
Probe obtains two one-byte controller windows, one for the address latch and one for data, initializes the private lock/schedules/timer, powers the chip down, reads `SL11H_HWREVREG`, then registers the HCD. Starting the HCD marks it running and powers the port through `port_power()`. URB enqueue allocates or reuses a `sl811h_ep`, links the URB to usbcore, initializes PID/toggle/maxpacket/type state, inserts the endpoint into either the async list or periodic table, starts transfer if possible, and writes the current interrupt mask. Interrupts acknowledge SL811 status bits, call `done()` for completed banks, update periodic-frame state on SOF, process insert/remove and resume-detect events, then run `start_transfer()` again while the port is enabled. Root-hub requests manipulate the single virtual port: power on/off, reset by SE0 signaling, resume by K signaling, suspend by disabling SOF, and report status/change bits to usbcore.

## State And Persistence Behavior
No durable state is persisted. Runtime state is split between software fields in `struct sl811` and volatile chip registers. `port1` mirrors USB hub status/change bits. `ctrl1`, `ctrl2`, and `irq_enable` mirror hardware controls so the driver can rewrite them after resets and event handling. `active_a`/`active_b` track armed endpoints and watchdog jiffies for missing completions. `async`, `periodic[]`, `load[]`, `next_async`, and `next_periodic` are the complete scheduling model. Statistics are exposed only through debugfs and reset by VBUS sessions.

## Dependencies And Integration Points
The driver integrates with the USB HCD core, platform devices, debugfs, board-specific `struct sl811_platform_data`, and SL811 register definitions from `sl811.h`. Board hooks can drive VBUS and reset lines. `sl811_cs.c` depends on the exported `sl811h_driver` symbol. The code depends on usbcore endpoint queues, URB linking/unlinking helpers, root-hub polling, timers, and spinlock discipline around register access.

## Risks And Edge Cases
The implementation intentionally handles old or marginal hardware: missing DONE interrupts are mitigated through `QUIRK3` root-hub watchdog polling, SOF interrupts are throttled, and packet timing is estimated from `SL11H_SOFTMRREG`. It ignores `urb->iso_frame_desc[]` in packet construction, so ISO support is incomplete and build-gated. Only one transfer bank is active by default, limiting throughput. Packet scheduling uses simple time estimates and may overrun periodic frames under interrupt latency. Root-hub power and reset behavior depends heavily on board platform data; missing hooks force generic SE0 reset. There is a suspicious unreachable B-bank path compiled out by default, so enabling `USE_B` would need careful review.

## Test Signals
Useful signals are successful platform probe, chip revision detection, enumeration through the single root hub, control/bulk/interrupt traffic, disconnect cleanup, suspend/resume hub requests, and debugfs `sl811h` output showing stable schedules and low lost/overrun counters. Regression testing should include low-speed devices behind hubs, storage bulk transfers, hotplug during active URBs, forced URB dequeue, root-port reset, and systems using IORESOURCE_IO rather than MMIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/sl811-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/sl811.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/sl811.h

## Purpose
`sl811.h` is the private hardware contract for the SL811 host-controller driver. It defines SL811/SL11H register offsets, bit masks, packet buffer layout, private HCD state, endpoint state, and small register access helpers. It lets `sl811-hcd.c` express controller operations symbolically instead of scattering magic register constants.

## Important APIs, Types, And Functions
Register definitions cover transfer-bank registers (`SL11H_HOSTCTLREG`, `SL11H_BUFADDRREG`, `SL11H_BUFLNTHREG`, `SL11H_PKTSTATREG`, `SL11H_PIDEPREG`, `SL11H_XFERCNTREG`, `SL11H_DEVADDRREG`), host control registers (`SL11H_CTLREG1`, `SL11H_IRQ_ENABLE`, `SL11H_IRQ_STATUS`, `SL11H_HWREVREG`, `SL811HS_CTLREG2`), and packet PID encodings (`SL_SETUP`, `SL_IN`, `SL_OUT`, `SL_SOF`). Buffer constants split the 240-byte data window into two 120-byte packet buffers through `SL811HS_PACKET_BUF()`. `struct sl811` is the HCD-private controller state; it stores IO windows, board data, statistics, timers, active endpoints, root-port state, and async/periodic schedules. `struct sl811h_ep` stores endpoint queue state, current PID, toggles, packet size, periodic placement, and async list node. Inline helpers translate between `usb_hcd` and `sl811` and perform register or data-buffer IO.

## Control Flow
This header does not drive control flow directly, but its structure explains how the HCD operates. Callers must hold `sl811->lock` for register access. `sl811_write_buf()` and `sl811_read_buf()` latch a buffer address, then stream bytes through the data register, relying on SL811 autoincrement. The schedule fields define two scheduling paths: a list for control/bulk async traffic and a small `PERIODIC_SIZE` tree for interrupt/ISO traffic. Active-bank pointers map software endpoint state to the hardware A/B banks.

## State And Persistence Behavior
State is entirely in memory or device registers; nothing persists across driver unload or hardware reset. The header separates hardware mirrors (`ctrl1`, `ctrl2`, `irq_enable`, `frame`) from software scheduling (`async`, `periodic`, `load`) and debug counters (`stat_*`). Endpoint state persists only while a USB endpoint has outstanding or reusable HCD private data.

## Dependencies And Integration Points
The header depends on Linux USB HCD types, platform data from `<linux/usb/sl811.h>`, MMIO accessors (`readb`, `writeb`), timers, lists, and spinlocks. Its endian/PIO assumptions are tightly coupled to the SL811 two-register access model. `sl811-hcd.c` is the main consumer; platform glue must provide the address and data register windows that these helpers access.

## Risks And Edge Cases
The inline IO helpers assume the caller serialized all access and that the underlying platform maps the address and data windows correctly. Buffer size constants cap non-ISO packets to 120 bytes; callers must reject larger maxpacket values or risk overruns. `PERIODIC_SIZE` is small and arbitrary, so periodic scheduling resolution is limited. Because the header mirrors both SL11H and SL811HS concepts, using the wrong register-set mode would produce subtle failures.

## Test Signals
Compile coverage should exercise IO and MMIO configurations. Runtime signals include valid chip revision reads, stable packet buffer transfers, correct low-speed `DSWAP`/preamble behavior, and debugfs schedule output that matches `struct sl811` fields. Static checks should verify all register helpers are called with the controller lock held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/sl811.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/sl811_cs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/sl811_cs.c

## Purpose
`sl811_cs.c` is PCMCIA/CardBus glue for SL811HS-based CompactFlash USB host cards, specifically the RATOC/REX-CFU1U style device. It does not implement USB transfer logic. Instead, it claims PCMCIA resources, constructs a singleton platform device with IRQ and two IO registers, and lets the exported `sl811-hcd` platform driver probe the actual controller.

## Important APIs, Types, And Functions
The file registers a `struct pcmcia_driver` named `sl811_cs`. `sl811_cs_probe()` allocates a small `local_info_t` and calls `sl811_cs_config()`. `sl811_cs_config()` uses PCMCIA core helpers to select a configuration, require an IRQ and at least two IO ports, enable the device, and call `sl811_hc_init()`. `sl811_hc_init()` fills static `resources[]`, assigns the parent, uses `sl811h_driver.driver.name` for the platform device name, and registers `platform_dev`. `sl811_cs_release()` disables the PCMCIA device and unregisters the platform device. Static `platform_data` describes power-on-to-power-good and a 100 mA power budget.

## Control Flow
The PCMCIA core calls probe for matching manufacturer/card IDs. Probe allocates private bookkeeping and immediately configures the card. Configuration sets auto flags for IRQ, VPP, VCC, and IO; `pcmcia_loop_config()` calls `sl811_cs_config_check()` until a valid config index and IO request are accepted. Once the card is enabled, platform resources map IRQ, address port, and data port. The platform device then triggers the already-linked `sl811-hcd` driver to probe. Remove calls release, unregistering the platform child before freeing private state.

## State And Persistence Behavior
The driver uses static singleton platform resources and platform device storage, which implies only one such PCMCIA SL811 controller is supported at a time. There is no persistent state. The PCMCIA card state lives in `pcmcia_device`, while the actual HCD state lives in `sl811-hcd` after platform registration.

## Dependencies And Integration Points
Integration points are the PCMCIA core, platform-device core, SL811 platform data ABI, and the exported `sl811h_driver` symbol. Link order matters: the reference to `sl811h_driver` intentionally ensures the host-controller driver is initialized before this glue tries to register a matching platform device. The platform device resource ordering must match `sl811h_probe()` expectations: IRQ plus address and data register windows.

## Risks And Edge Cases
The singleton static `platform_dev` returns `-EBUSY` if already parented, so multi-card systems are unsupported. The reset hook is marked FIXME, so cards that require CF reset sequencing may be fragile. Error handling funnels many resource failures to `sl811_cs_release()`, which calls `platform_device_unregister()` even when registration may not have succeeded; the singleton design makes ordering important. The power budget is hardcoded to 100 mA and may not reflect all cards or attached devices.

## Test Signals
Test by inserting/removing a matching PCMCIA card, verifying IO and IRQ resources are assigned, confirming platform probe of `sl811-hcd`, and checking clean unregister on eject. Negative tests should cover missing IRQ, insufficient IO window size, repeated insertion, and failure of `platform_device_register()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/sl811_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ssb-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ssb-hcd.c

## Purpose
`ssb-hcd.c` is Sonics Silicon Backplane glue for Broadcom USB host cores. It enables SSB USB cores, applies Broadcom-specific workarounds, and creates child `ohci-platform` and, for USB 2.0 cores, `ehci-platform` devices. The actual USB scheduling and root-hub behavior are delegated to the generic OHCI/EHCI platform drivers.

## Important APIs, Types, And Functions
The main private type is `struct ssb_hcd_device`, holding child OHCI/EHCI platform-device pointers and the enable flags needed for resume. `ssb_hcd_init_chip()` enables the SSB core and sets host mode for USB11 host/device cores. `ssb_hcd_usb20wa()` and `ssb_hcd_5354wa()` program undocumented Broadcom registers for USB 2.0 PHY/core reset sequencing and BCM5354 revision 2 failures. `ssb_hcd_create_pdev()` allocates a platform device, attaches MEM/IRQ resources and empty EHCI/OHCI platform data, and registers it. `ssb_hcd_probe()` validates supported embedded chip families, sets a 32-bit DMA mask, initializes the chip, and creates the child HCD devices. Remove, shutdown, suspend, and resume disable or re-enable the SSB core.

## Control Flow
The SSB bus matches Broadcom USB11 hostdev, USB11 host, and USB20 host cores. Probe rejects non-0x4700/0x5300 embedded chips, sets DMA constraints, allocates `ssb_hcd_device`, and enables the core. It reads address-match data from `SSB_ADMATCH0`; USB20 maps the first 0x800 bytes to OHCI and the next 0x800 bytes to EHCI, while USB11 uses the advertised size. If EHCI creation fails, OHCI is unregistered before returning. Remove unregisters children, then disables the SSB device.

## State And Persistence Behavior
No state persists beyond device lifetime. Runtime state is child platform-device ownership plus the SSB enable flags used on PM resume. Hardware state is reset on probe, shutdown, suspend, and remove through `ssb_device_enable()`/`ssb_device_disable()` and direct SSB register writes.

## Dependencies And Integration Points
The file integrates with the SSB bus, platform-device core, DMA mask APIs, and generic OHCI/EHCI platform HCDs. It relies on Broadcom SSB register definitions and address-match helpers. The child device names (`ohci-platform`, `ehci-platform`) must match corresponding platform drivers. The code also conditionally depends on `CONFIG_SSB_DRIVER_MIPS` for a BCM5354 workaround.

## Risks And Edge Cases
The Broadcom workarounds use fixed offsets and bit masks, so they depend on core revisions matching expectations. The code comments note that USB11 host/device cores are always attached as host OHCI; there is no client-mode branch. Suspend disables the SSB core, while resume only calls `ssb_device_enable()` and does not repeat all USB20 workaround writes, which may be relevant if hardware loses more state than expected. Error paths must keep child platform devices balanced.

## Test Signals
Probe should create OHCI for USB11 and both OHCI/EHCI for USB20. Resource ranges should be non-overlapping and IRQ shared with the SSB core IRQ. Runtime tests should include hub/device enumeration behind both child HCDs, remove/unregister, system suspend/resume, and BCM5354 rev2 hardware if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ssb-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-debug.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-debug.c

## Purpose
`uhci-debug.c` supplies UHCI schedule introspection. It is included directly by `uhci-hcd.c`, giving it access to static UHCI helpers and private types. With dynamic debug and debugfs enabled, it formats TDs, QHs, root-hub registers, periodic load tables, frame-list contents, and skeleton queues for debug logs or `/sys/kernel/debug/uhci/<bus>`.

## Important APIs, Types, And Functions
`uhci_show_td()` prints hardware TD link/status/token/buffer fields and decodes status flags, PID, endpoint, device address, toggle, and expected length. `uhci_show_urbp()` summarizes per-URB private state and TD lists. `uhci_show_qh()` prints QH hardware pointers, queue type, periodic parameters, URB chains, and dummy TD. `uhci_show_status()` dumps controller registers and first two port status registers. `uhci_sprint_schedule()` is the central formatter for root-hub state, HC status, load table, frame list consistency, and skeleton QH lists. Debugfs file operations allocate a snapshot buffer in open, allow read/lseek, and free it on release.

## Control Flow
When `CONFIG_DYNAMIC_DEBUG` is active, debug helpers emit detailed schedule snapshots. `uhci_irq()` uses `uhci_sprint_schedule()` to log a schedule after fatal halt conditions when debug level is high. `uhci_start()` creates a debugfs file per bus when `UHCI_DEBUG_OPS` is available. Opening that file grabs `uhci->lock`, snapshots the schedule into a 64 KiB buffer, then releases the lock so user reads do not hold controller state. When dynamic debug is disabled, stub versions compile away formatting.

## State And Persistence Behavior
The file owns `uhci_debugfs_root` and temporary debug buffers only. It does not alter controller state except by reading registers and private structures under lock. Debug output is a point-in-time snapshot; no persistent state is stored.

## Dependencies And Integration Points
The code relies on UHCI private types and macros from `uhci-hcd.h`, controller register access helpers, Linux debugfs, dynamic debug, and user-copy helpers. Since it is included into `uhci-hcd.c`, its static symbols are local to the UHCI translation unit. `uhci_hcd_init()` creates the root debugfs directory, and `release_uhci()` removes per-controller files.

## Risks And Edge Cases
Formatting uses `sprintf()` into fixed buffers while checking after writes, so the code reserves `EXTRA_SPACE` and truncates with ellipses. Debug output walks hardware/software schedules that may be inconsistent during failures; it must tolerate mismatched frame-list links and empty queues. Because it reads hardware registers, callers must ensure the controller is accessible before invoking detailed status dumps. Pointer output is intentionally diagnostic and not an ABI.

## Test Signals
Build combinations with and without `CONFIG_DYNAMIC_DEBUG` and `CONFIG_DEBUG_FS` should compile. Runtime signals include a debugfs `uhci/<bus>` file, readable schedule output, no lockdep complaints while opening under traffic, and useful fatal-halt log output when debug level is elevated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-grlib.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-grlib.c

## Purpose
`uhci-grlib.c` is UHCI bus glue for the GRLIB GRUSBHC controller on SPARC/LEON systems. It maps Open Firmware resources, detects controller endianness, configures the shared UHCI engine for MMIO and possible big-endian descriptors, and registers a platform driver named `grlib-uhci`.

## Important APIs, Types, And Functions
`uhci_grlib_init()` is the HCD `.reset` callback. It probes `USBPORTSC1` to detect byte-swapped MMIO and descriptor format, counts root-hub ports, assigns generic reset/check callbacks, and calls shared `check_and_reset_hc()`. `uhci_grlib_hc_driver` reuses UHCI core operations for IRQ, start, stop, URB enqueue/dequeue, endpoint disable, frame number, and root-hub control. `uhci_hcd_grlib_probe()` parses OF address and IRQ, creates the HCD, maps registers with `devm_ioremap_resource()`, stores `uhci->regs`, and calls `usb_add_hcd()`. Remove disposes the IRQ mapping and releases the HCD.

## Control Flow
The platform driver matches OF names `GAISLER_UHCI` and `01_027`. Probe validates USB is enabled, obtains MMIO resource and IRQ from the device tree, gives the platform device a coherent DMA mask, creates the HCD, maps registers, and starts the shared UHCI stack. During HCD reset, endian probing occurs before port counting. Shutdown calls `uhci_hc_died()` without locking to quiesce DMA and interrupts for kexec-like consumers.

## State And Persistence Behavior
No persistent state is kept. Runtime state includes mapped registers, IRQ mapping, and UHCI private flags (`big_endian_mmio`, `big_endian_desc`, reset callbacks, root-port count). Hardware state is reset through the shared generic UHCI reset path. Remove tears down the HCD and IRQ mapping.

## Dependencies And Integration Points
This file depends on OF address/IRQ APIs, platform devices, GRLIB naming conventions, and the shared UHCI implementation included by `uhci-hcd.c`. It depends on `CONFIG_USB_UHCI_BIG_ENDIAN_MMIO` and `CONFIG_USB_UHCI_BIG_ENDIAN_DESC` support in `uhci-hcd.h` for endian-correct register and descriptor access.

## Risks And Edge Cases
Endianness detection assumes `USBPORTSC1` bit 7 is always one and bit 15 is zero; bad hardware state could mis-detect and corrupt all descriptor/register access. The probe manually sets `dma_mask`, which may hide missing DMA binding detail. IRQ disposal must match successful `irq_of_parse_and_map()`. This glue has no clock/reset-control handling; it assumes firmware/platform already prepared the controller.

## Test Signals
Tests should verify OF matching, resource mapping, IRQ delivery, correct endian detection on both little and big endian GRUSBHC variants, root-port enumeration, URB traffic, remove, and shutdown quiescence. Debugfs UHCI schedule output should show valid descriptor pointers after endian probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-grlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hcd.c

## Purpose
`uhci-hcd.c` is the shared core of the Linux UHCI USB 1.1 host-controller driver. It owns controller lifecycle, root-hub power-management state, interrupt handling, schedule allocation, debug initialization, module registration, and inclusion of the UHCI debug, queue, hub, and bus-glue implementation files.

## Important APIs, Types, And Functions
The file exposes shared operations consumed by bus glue through `struct hc_driver` instances: `uhci_start()`, `uhci_stop()`, `uhci_irq()`, `uhci_rh_suspend()`, `uhci_rh_resume()`, `uhci_hcd_endpoint_disable()`, `uhci_hcd_get_frame_number()`, and `uhci_count_ports()`. `finish_reset()`, `uhci_hc_died()`, `check_and_reset_hc()`, and generic non-PCI reset helpers handle hardware reset state. `configure_hc()` programs frame length, frame-list base, frame number, and optional bus-specific setup. `suspend_rh()`, `start_rh()`, and `wakeup_rh()` manage root-hub state transitions. Module init creates debugfs/cache state and registers platform and/or PCI drivers depending on configuration.

## Control Flow
At compile time this file includes `uhci-debug.c`, `uhci-q.c`, `uhci-hub.c`, and one or more bus glue files. Module init rejects `usb_disabled()`, allocates the `urb_priv` slab cache, creates debugfs root when applicable, registers platform glue first and PCI glue second. HCD start allocates the 1024-entry frame list, CPU-side ISO frame pointers, TD/QH DMA pools, terminating TD, skeleton QHs, and initializes hardware frame entries. It then configures the HC, marks state initialized, and starts the root hub. IRQ handling acknowledges UHCI status, detects fatal hardware errors, handles resume-detect by polling the root hub, and otherwise scans the schedule. Stop kills the controller, scans remaining work, synchronizes IRQs, deletes timers, and releases DMA/debug resources.

## State And Persistence Behavior
The core maintains all persistent runtime state in `struct uhci_hcd`: frame list DMA, skeleton QHs, TD/QH pools, root-hub state, frame counters, FSBR flags, quirk flags, port resume bitmaps, load accounting, wait queues, clocks/resets from platform glue, and function pointers supplied by bus glue. No state persists across unload or reset. `frame_number` expands the 10/11-bit hardware frame counter by requiring periodic polling.

## Dependencies And Integration Points
The file integrates with usbcore HCD APIs, DMA pools, coherent DMA allocation, debugfs, timers, PCI/platform bus glue, root-hub polling, and PM. The bus glue must supply register mapping, root-port count, reset/check/config callbacks, and quirks. Queue and hub logic are included into the same translation unit so static helpers can be shared.

## Risks And Edge Cases
UHCI hardware has multiple quirks: persistent HCH status, old Intel QH advancement bugs handled in `uhci-q.c`, overcurrent/resume-detect issues, ASpeed stale status, and controllers that lose state across suspend/hibernate. `suspend_rh()` must balance remote-wakeup policy against broken EGSM/RD behavior and may force root-hub polling. Resource unwinding in `uhci_start()` is multi-stage and depends on DMA pool/frame allocation order. `uhci_count_ports()` probes ambiguous registers and clamps impossible counts.

## Test Signals
Build all configured glue combinations: PCI-only, platform, GRLIB, and non-PCI support. Runtime tests should cover enumeration, control/bulk/interrupt/ISO traffic, suspend/resume with and without wakeup, controller halt error handling, endpoint disable waiting, port-count detection, debugfs creation/removal, and module load/unload without DMA leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hcd.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hcd.h

## Purpose
`uhci-hcd.h` is the shared private ABI for the UHCI driver. It defines UHCI register offsets and bit fields, host-controller pointer encoding, TD/QH hardware descriptors, skeleton queue layout, root-hub state machine values, the `struct uhci_hcd` controller state, per-URB state, register accessors for PCI/MMIO/ASpeed/big-endian variants, and descriptor endian conversion helpers.

## Important APIs, Types, And Functions
Key register constants include `USBCMD`, `USBSTS`, `USBINTR`, `USBFRNUM`, `USBFLBASEADD`, `USBSOF`, and `USBPORTSC*`. Link pointer helpers (`UHCI_PTR_TERM`, `UHCI_PTR_QH`, `UHCI_PTR_DEPTH`, `LINK_TO_QH()`, `LINK_TO_TD()`) encode schedule addresses. `struct uhci_qh` represents both endpoint queues and skeleton queues, including hardware link/element fields and software queue, period, phase, load, state, and toggle flags. `struct uhci_td` represents UHCI transfer descriptors. `struct uhci_hcd` is the complete controller state and bus-glue callback table. Inline register functions abstract IO-port, MMIO, big-endian, and ASpeed register maps. `cpu_to_hc32()` and `hc32_to_cpu()` abstract descriptor endianness.

## Control Flow
The header enables the rest of the driver to treat PCI and non-PCI UHCI similarly. Queue code allocates and links `struct uhci_qh`/`struct uhci_td`; core code uses `uhci_readw()`/`uhci_writew()` for hardware control; hub code uses port bit constants; bus glue fills callback pointers and quirk flags in `struct uhci_hcd`. The skeleton queue numbering determines how interrupt, async, ISO, unlinking, and terminating queues are inserted into the hardware schedule.

## State And Persistence Behavior
No durable state is defined. The structures describe runtime state that exists while an HCD instance is alive. Descriptor fields are DMA-visible and can be asynchronously changed by hardware, which is why `qh_element()` and `td_status()` use `READ_ONCE()`. Software state tracks QH lifecycle (`IDLE`, `UNLINKING`, `ACTIVE`), root-hub lifecycle, bandwidth load, FSBR activity, and platform quirks.

## Dependencies And Integration Points
The header depends on Linux USB, list, clock, reset-control, endian, MMIO, and optional IO-port support. It is consumed by all UHCI implementation files. It supports PCI, generic platform, ASpeed, and GRLIB-style endian variations, so configuration macros strongly affect compiled accessors.

## Risks And Edge Cases
The non-PCI accessor block contains several configuration-sensitive paths; incorrect `CONFIG_HAS_IOPORT`/`HAS_IOPORT` combinations or missing big-endian flags would produce bad register access. ASpeed uses a nonstandard register map translated by `uhci_aspeed_reg()` and warns on unsupported registers. Hardware-updated descriptor fields require careful memory ordering and one-time reads. Skeleton queue constants are semantic; mistakes in queue placement affect bandwidth and traversal order.

## Test Signals
Static build coverage across endian/MMIO/PCI/ASpeed options is critical. Runtime signals include correct register access, valid DMA descriptor endianness, stable frame list traversal, proper QH state transitions, accurate root-port count, and no sparse/endian warnings around `__hc32` conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hub.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hub.c

## Purpose
`uhci-hub.c` implements the virtual root-hub interface for UHCI controllers. It translates usbcore hub class requests into UHCI port status/control register operations, handles port reset/resume timing, detects root-hub status changes, and participates in the UHCI auto-stop state machine.

## Important APIs, Types, And Functions
`uhci_hub_status_data()` is the HCD root-hub change bitmap callback. It scans schedules, checks hardware accessibility, updates port reset/resume completion through `uhci_check_ports()`, computes change bits with `get_hub_status_data()`, and advances root-hub power states. `uhci_hub_control()` handles `GetHubStatus`, `GetPortStatus`, `GetHubDescriptor`, `SetPortFeature`, `ClearPortFeature`, and hub feature requests. Helper macros `CLR_RH_PORTSTAT()` and `SET_RH_PORTSTAT()` preserve write-zero and write-clear semantics. `uhci_finish_suspend()` ends resume signaling and updates change state. `any_ports_active()` feeds auto-stop decisions.

## Control Flow
Root-hub polling calls `uhci_hub_status_data()`. The function scans completed transfers first, then checks reset/resume timers and port change bits. In suspended state, a change asks usbcore to resume the root hub. In auto-stopped state, a change wakes the controller. In running state, absence of connected or changed ports transitions to `UHCI_RH_RUNNING_NODEVS`; after one second with no active ports, it auto-stops unless the HP reset quirk is active. Hub-control requests directly read or write `USBPORTSCn` registers under `uhci->lock`, converting UHCI-specific bits to USB hub status words.

## State And Persistence Behavior
Port state lives primarily in hardware `USBPORTSC` registers plus software bitmaps in `struct uhci_hcd`: `port_c_suspend`, `resuming_ports`, and `ports_timeout`. The code does not persist state across reset. Change bits are cleared by writing register values with UHCI R/WC rules or clearing software bitmaps.

## Dependencies And Integration Points
This file is included by `uhci-hcd.c` and depends on the shared register helpers, root-hub state functions (`suspend_rh()`, `wakeup_rh()`), `ignore_oc`, usbcore hub constants, and HCD polling APIs. It uses `uhci_scan_schedule()` from queue code because root-hub polling is also a convenient completion scan point.

## Risks And Edge Cases
UHCI has no explicit `C_RESET` reporting and no port power switching, so the code synthesizes standard hub behavior. Resume signaling must be stopped by software after USB-specified timeouts; delayed or disabled ports require special handling. Overcurrent polarity varies by vendor and may be ignored globally. The HP iLO2 quirk delays reset completion. Auto-stop depends on polling cadence and could miss wakeups if RD/EGSM behavior is broken, which core code handles by forcing polling.

## Test Signals
Test hub descriptor and status requests, port connect/disconnect changes, reset completion, suspend/resume completion, overcurrent-change behavior with `ignore_oc`, auto-stop after no devices, wake from auto-stop, and HP reset-delay systems. Lockdep and race testing should cover hub requests while URBs complete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-pci.c

## Purpose
`uhci-pci.c` is the PCI bus glue for the shared UHCI driver. It binds PCI class-code UHCI controllers, initializes PCI-specific legacy/wakeup behavior, supplies reset and quirk callbacks to `struct uhci_hcd`, and delegates HCD probing/removal/PM to usbcore PCI helpers.

## Important APIs, Types, And Functions
`uhci_pci_init()` is the HCD `.reset` callback. It stores `io_addr`, counts ports, sets vendor quirks (`oc_low`, `wait_for_hp`, Intel wakeup capability), fills reset/configuration/resume-detect/global-suspend callback pointers, and calls shared `check_and_reset_hc()`. `uhci_pci_configure_hc()` writes `USBLEGSUP` and disables Intel non-PME wakeup. `uhci_pci_resume_detect_interrupts_are_broken()` handles Genesys and Intel OC/resume-detect issues. `uhci_pci_global_suspend_mode_is_broken()` applies a DMI quirk for Asus A7V8X boards. PM callbacks disable/restore PCI legacy IRQ routing and wake bits. `uhci_driver` is the PCI `struct hc_driver`.

## Control Flow
The PCI driver matches any PCI device with class `PCI_CLASS_SERIAL_USB_UHCI`. Probe calls `usb_hcd_pci_probe()` with `uhci_driver`, which invokes `uhci_pci_init()` and then shared `uhci_start()`. Suspend clears PIRQ, optionally enables Intel USBRES wake bits, marks hardware inaccessible, synchronizes IRQs, and handles wakeup races by resuming and returning `-EBUSY`. Resume marks hardware accessible, resets on hibernation restore or checks/reconfigures otherwise, reports lost root-hub power if reset occurred, and polls root-hub status.

## State And Persistence Behavior
PCI-specific runtime state is stored in `struct uhci_hcd` quirk flags and callbacks plus PCI config space (`USBLEGSUP`, `USBRES_INTEL`). No durable driver state exists. Resume may intentionally discard root-hub state and force re-enumeration if the controller was reset or restored from hibernation.

## Dependencies And Integration Points
The file depends on PCI core, usbcore PCI HCD helpers, `pci-quirks.h` UHCI reset helpers, DMI, and the shared UHCI core. `MODULE_SOFTDEP("pre: ehci_pci")` encourages EHCI to bind before UHCI on companion-controller systems.

## Risks And Edge Cases
Vendor quirks materially affect wake behavior. Intel overcurrent and Genesys resume-detect issues can force root-hub polling. The DMI workaround disables EGSM on affected Asus boards with connected devices. `uhci_shutdown()` intentionally avoids locking because it may run in damaged-kernel contexts, but it assumes PCI driver data is still valid. `io_addr` requires IO-port UHCI; this file is built only when PCI and IO ports exist.

## Test Signals
Tests should cover PCI enumeration, legacy handoff, vendor quirks, suspend/resume with remote wakeup, hibernate restore, kexec/shutdown quiescence, EHCI/UHCI companion ordering, and root-hub re-enumeration after reset. Config-space inspection should show expected `USBLEGSUP`/`USBRES_INTEL` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-platform.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-platform.c

## Purpose
`uhci-platform.c` provides generic MMIO platform-device glue for UHCI controllers, including device-tree-described generic/platform UHCI and ASpeed variants. It maps resources, sets DMA masks, handles optional clocks and reset controls, parses port/quirk data from DT, and registers the shared UHCI HCD.

## Important APIs, Types, And Functions
`uhci_platform_init()` sets generic reset/check callbacks, counts ports if DT did not provide them, disables bus-specific PM quirk callbacks, and calls `check_and_reset_hc()`. `uhci_platform_hc_driver` reuses shared UHCI operations with `HCD_MEMORY | HCD_DMA | HCD_USB11`. `uhci_hcd_platform_probe()` performs device setup: DMA mask coercion, HCD allocation, resource mapping, DT property parsing, optional clock enable, optional reset deassertion, IRQ lookup, and `usb_add_hcd()`. Remove asserts reset, disables clock, removes the HCD, and releases it. Shutdown calls `uhci_hc_died()`.

## Control Flow
Probe rejects disabled USB, chooses a 64-bit DMA mask if match data is present, creates the HCD, maps the first resource, stores `uhci->regs`, optionally reads `#ports`, detects ASpeed-compatible strings and sets `is_aspeed`, enables clock and reset resources, gets IRQ 0, and adds the HCD with shared IRQ. Error paths unwind reset, clock, and HCD allocation. The OF table matches `generic-uhci`, `platform-uhci`, and `aspeed,ast2700-uhci` with match data for 64-bit DMA.

## State And Persistence Behavior
State is runtime-only: mapped registers, optional `clk`, optional reset-control array, root-port count, and ASpeed flag in `struct uhci_hcd`. Remove and error paths assert resets and disable clocks. No state persists across unload.

## Dependencies And Integration Points
The file depends on platform devices, OF helpers, clock framework, reset framework, DMA mask APIs, and shared UHCI non-PCI register accessors. ASpeed support depends on `uhci-hcd.h` translating UHCI register offsets to ASpeed-specific MMIO offsets when `uhci->is_aspeed` is set. `MODULE_SOFTDEP("pre: ehci_platform")` mirrors companion-controller ordering.

## Risks And Edge Cases
DT `#ports` can override probing, so bad firmware can misrepresent the root hub. Only ASpeed AST2700 has match data for 64-bit DMA in this table, while older ASpeed compatibles enable only the workaround flag. Remove asserts reset before `usb_remove_hcd()`, which may quiesce hardware before usbcore teardown and should be reviewed against shared HCD expectations. Optional resets are requested shared, so board-level reset topology matters.

## Test Signals
Test generic and ASpeed DT binding, DMA mask selection, clock/reset error unwinds, IRQ sharing, port-count parsing, ASpeed register access, enumeration, suspend/resume if enabled, remove, and shutdown. Runtime logs should report DT port detection and ASpeed workaround enablement when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-q.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-q.c

## Purpose
`uhci-q.c` is the UHCI transfer scheduler and completion engine. It allocates TDs and QHs, builds TD chains for control/bulk/interrupt/isochronous URBs, links QHs into the UHCI frame/skeleton schedule, manages bandwidth and full-speed bandwidth reclamation, handles URB dequeue, scans completed transfers, maps TD errors to Linux statuses, and gives URBs back to usbcore.

## Important APIs, Types, And Functions
Public-to-core callbacks are `uhci_urb_enqueue()` and `uhci_urb_dequeue()`. Allocation helpers include `uhci_alloc_td()`, `uhci_free_td()`, `uhci_alloc_qh()`, `uhci_free_qh()`, `uhci_alloc_urb_priv()`, and `uhci_free_urb_priv()`. Submit paths are `uhci_submit_control()`, `uhci_submit_common()`, `uhci_submit_bulk()`, `uhci_submit_interrupt()`, and `uhci_submit_isochronous()`. Completion paths are `uhci_result_common()`, `uhci_result_isochronous()`, `uhci_scan_qh()`, and `uhci_scan_schedule()`. Schedule maintenance includes `uhci_activate_qh()`, `uhci_unlink_qh()`, `uhci_make_qh_idle()`, `link_interrupt()`, `link_async()`, ISO frame-list insertion/removal helpers, and FSBR helpers.

## Control Flow
Enqueue links the URB to usbcore, allocates per-URB state, finds or creates an endpoint QH, builds the correct TD sequence, adds the URB to the QH queue, and activates the QH if it can run immediately. Control TDs include SETUP, data, status, and a new dummy TD. Bulk and interrupt TDs support scatter-gather, zero-length packet termination, data toggle management, and interrupt-on-complete. ISO TDs are inserted directly into frame-list slots rather than through hardware QHs. Dequeue marks an URB unlinked, removes ISO TDs early, and unlinks the QH so hardware has time to stop referencing descriptors. Schedule scans walk skeleton lists, detect advancement/timeouts, collect TD results, perform toggle fixups after short/error/dequeued transfers, give back completed URBs, release bandwidth, and eventually move unlinked QHs to idle.

## State And Persistence Behavior
All state is in `struct uhci_hcd`, `struct uhci_qh`, `struct uhci_td`, and `struct urb_priv`. Hardware-visible state is DMA descriptors in pools and the frame list. Software state tracks queue membership, dummy/post TDs, QH state, unlink frame, bandwidth reservations, FSBR state, last ISO frame, and toggle fixup needs. No state persists after HCD stop; descriptors are freed or recycled through pools.

## Dependencies And Integration Points
The queue engine depends on usbcore URB/endpoint APIs, DMA mappings already prepared by usbcore, UHCI descriptor/register definitions, timers, root-hub timer for forced scans, and the `uhci_up_cachep` slab from module init. It is included by `uhci-hcd.c`, so it directly calls shared core functions and is called by interrupt/root-hub polling paths.

## Risks And Edge Cases
This file carries most UHCI correctness risk. Hardware asynchronously updates descriptors, so memory barriers and `READ_ONCE()` accessors matter. QHs must remain unlinked for more than one frame before becoming idle. Short transfers require careful TD pruning and data-toggle repair. Old Intel controllers may leave QH elements pointing at inactive completed TDs; `uhci_advance_check()` advances them manually. FSBR modifies async skeleton links and must be timed out carefully. ISO scheduling can fail if too far in the future or if frames fall behind. Error unwinds must avoid freeing active dummy TDs.

## Test Signals
Test all transfer types, scatter-gather bulk, control short reads, `URB_SHORT_NOT_OK`, `URB_ZERO_PACKET`, ISO ASAP and non-ASAP scheduling, interrupt bandwidth exhaustion, dequeues before and during execution, endpoint disable waits, stuck queue recovery, FSBR enable/timeout, and controller stop with pending URBs. Debugfs schedule checks are useful for detecting QH/TD link mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/uhci-q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xen-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xen-hcd.c

## Purpose
`xen-hcd.c` implements a Xen paravirtual USB host controller frontend. It presents USB 1.1 or USB 2.0 HCDs to Linux, but forwards URB work to a Xen backend through shared rings and grant references. It also emulates a virtual root hub whose port events arrive over a Xen connection ring.

## Important APIs, Types, And Functions
`struct xenhcd_info` is the HCD-private state: pending/in-progress/giveback lists, lock, watchdog timer, virtual port/device arrays, xenbus device, URB and connection rings, event channel/IRQ, request shadows, freelist, and error flag. `struct urb_priv` tracks one URB's request IDs, unlink status, and giveback status. Hub helpers manage port connection, power, suspend, resume, reset, descriptor/status/control. Grant/ring helpers include `xenhcd_map_urb_for_request()`, `xenhcd_gnttab_map()`, `xenhcd_gnttab_done()`, `xenhcd_do_request()`, `xenhcd_urb_request_done()`, and `xenhcd_conn_notify()`. HCD callbacks are `xenhcd_setup()`, `xenhcd_run()`, `xenhcd_stop()`, `xenhcd_urb_enqueue()`, `xenhcd_urb_dequeue()`, and `xenhcd_get_frame()`. Xenbus lifecycle is handled by probe, backend-state changes, connect, disconnect, ring setup/destruction, and module init/exit.

## Control Flow
Probe creates an HCD after reading backend `num-ports` and `usb-ver`, initializes shadow freelist, stores driver data, and calls `usb_add_hcd()`. Backend transition to connected sets up URB/connection rings, allocates an event channel, publishes ring refs and event channel in xenstore, primes connection requests, and switches frontend state. URB enqueue allocates `urb_priv`, then either sends a ring request immediately or queues it if the ring is full or earlier requests are pending. Mapping grants backend access to transfer buffers and ISO descriptors. IRQ handling drains URB responses and connection responses until no more work, ending grant access and polling root-hub status when ports change. Dequeue sends an unlink request or moves not-yet-submitted URBs to giveback waiting.

## State And Persistence Behavior
State is runtime-only and shared between frontend memory, Xen rings, and backend-visible grant references. `shadow[]` tracks outstanding ring slots and their URBs. `pending_submit_list`, `pending_unlink_list`, `in_progress_list`, and `giveback_waiting_list` define the URB lifecycle. Virtual root-hub state is synthesized in `ports[]` and `devices[]`. The watchdog timer retries pending work and gives back already-unlinked URBs. Protocol errors set `info->error`, after which IRQs are treated as handled but no new work should proceed.

## Dependencies And Integration Points
The driver depends on Xen domain detection, xenbus, event channels, grant table APIs, Xen USB interface definitions, Linux USB HCD core, timers, slabs, and root-hub polling. The backend must implement the `vusb` protocol, publish valid xenstore keys, consume grants, and return well-formed ring responses.

## Risks And Edge Cases
Grant lifetime is critical: failure to release grants marks protocol error, while overlarge segment counts return `-E2BIG`. Ring overflow is handled with pending lists and watchdog timers, but ordering between submit and unlink queues is subtle. `xenhcd_pipe_urb_to_xenusb()` uses a static local variable, but callers hold `info->lock`; future lockless use would be unsafe. Root-hub resume/reset completion is timer-driven through `GetPortStatus`. On backend close, `usb_remove_hcd()` precedes ring destruction in remove/disconnect paths, so lifecycle ordering must remain balanced.

## Test Signals
Test xenbus probe with invalid and valid `num-ports`/`usb-ver`, backend connection and close, URB submit/completion for all transfer types, ISO descriptor grant mapping, ring-full queuing, URB unlink before submit and after submit, backend protocol errors, hotplug connection ring events, root-port reset/resume/power, suspend/resume, and module unload with pending grants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xen-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-caps.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-caps.h

## Purpose
`xhci-caps.h` defines bit extractors and capability masks for xHCI host-controller capability registers, following xHCI specification section 5.3. It is a low-level header used by xHCI code to decode controller limits and feature support from MMIO capability registers.

## Important APIs, Types, And Functions
Macros decode `hc_capbase` (`HC_LENGTH`, `HC_VERSION`), `HCSPARAMS1` (`HCS_MAX_SLOTS`, `HCS_MAX_INTRS`, `HCS_MAX_PORTS`), `HCSPARAMS2` (`HCS_IST_VALUE`, `HCS_IST_UNIT`, `HCS_ERST_MAX`, `HCS_MAX_SCRATCHPAD`), `HCSPARAMS3` (`HCS_U1_LATENCY`, `HCS_U2_LATENCY`), `HCCPARAMS1` feature bits (`HCC_64BIT_ADDR`, `HCC_64BYTE_CONTEXT`, `HCC_PPC`, `HCC_LTC`, `HCC_MAX_PSA`, `HCC_EXT_CAPS`), doorbell/runtime offsets (`DBOFF_MASK`, `RTSOFF_MASK`), and `HCCPARAMS2` feature bits (`HCC2_U3C`, `HCC2_CMC`, `HCC2_LEC`, `HCC2_ETC`, `HCC2_GSC`, `HCC2_VTC`, `HCC2_EUSB2_DIC`, `HCC2_E2V2C`).

## Control Flow
The header has no executable control flow. Its macros are used after code reads xHCI capability registers. Callers mask and shift raw little-endian register values to size arrays, choose context size, discover scratchpad requirements, locate operational/runtime/doorbell regions, and enable/avoid features based on advertised capabilities.

## State And Persistence Behavior
No state is stored. The macros interpret hardware capability state that is stable for the life of a controller instance. The decoded values affect runtime allocations and feature paths elsewhere in the xHCI driver.

## Dependencies And Integration Points
The header includes `<linux/bits.h>` for `BIT()`. It integrates with xHCI register definitions and initialization paths that read the capability MMIO space. Because it encodes spec bit positions, correctness depends on keeping definitions aligned with xHCI revision 1.2 and any later feature additions.

## Risks And Edge Cases
Incorrect masks or shifts would cause systemic xHCI misconfiguration: wrong context size, wrong number of ports/slots/interrupters, undersized scratchpad allocation, bad runtime/doorbell offsets, or enabling unsupported features. Some comments contain typos, but the macro values are the important contract. Callers must pass CPU-endian register values; using raw little-endian values without conversion would decode incorrectly on big-endian systems.

## Test Signals
Compile-time users should build cleanly. Runtime validation can compare decoded values against known controller register dumps, verify context-size decisions, scratchpad allocation counts, port counts, doorbell/runtime offsets, and feature-gated code paths on controllers with and without HCCPARAMS2 capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-caps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbg.c

## Purpose
`xhci-dbg.c` is a small xHCI debug helper file. In this snapshot it provides a slot-state string helper and an exported trace bridge that sends formatted messages to both xHCI debug logging and an arbitrary trace callback.

## Important APIs, Types, And Functions
`xhci_get_slot_state()` takes an xHCI controller and container context, retrieves the slot context with `xhci_get_slot_ctx()`, extracts `dev_state`, decodes `GET_SLOT_STATE()`, and returns the string from `xhci_slot_state_string()`. `xhci_dbg_trace()` is exported GPL. It accepts an xHCI pointer, a trace function taking `struct va_format *`, and a printf-style format string. It builds a `va_format`, emits the message through `xhci_dbg()`, then invokes the trace callback with the same formatted payload.

## Control Flow
Both helpers are direct utility functions. `xhci_dbg_trace()` opens a varargs list, initializes `struct va_format`, logs through the normal xHCI debug path, calls the supplied tracing function, then closes the varargs. There is no state machine, locking, or scheduling behavior in this file.

## State And Persistence Behavior
No persistent or mutable state is owned. The functions inspect xHCI context memory supplied by callers and transiently format debug arguments on the stack.

## Dependencies And Integration Points
The file includes `xhci.h` and relies on xHCI core helpers/macros such as `xhci_get_slot_ctx()`, `GET_SLOT_STATE()`, `xhci_slot_state_string()`, and `xhci_dbg()`. `EXPORT_SYMBOL_GPL(xhci_dbg_trace)` allows other GPL xHCI-related code to reuse the trace bridge.

## Risks And Edge Cases
`xhci_get_slot_state()` assumes the supplied container context contains a valid slot context. `xhci_dbg_trace()` passes a `va_format` to both debug and trace consumers before `va_end()`, which is valid for immediate consumption but callers must not store the pointer. The trace callback is mandatory by type usage; a NULL callback would crash.

## Test Signals
Build coverage should verify symbol export and xHCI helper declarations. Runtime testing should exercise tracepoints or callers that use `xhci_dbg_trace()`, confirm messages appear in both debug logs and trace output, and validate slot-state strings across enabled, addressed, configured, and disabled slot states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbg.c -->
