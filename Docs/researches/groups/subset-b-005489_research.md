# subset-b-005489 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-hcd.c

## Purpose
`fotg210-hcd.c` is the Faraday FOTG210 USB 2.0 host controller driver. It is an EHCI-derived HCD implementation adapted to the FOTG210 OTG block, sharing the controller wrapper in `fotg210.h` and the EHCI-style register/descriptor definitions in `fotg210-hcd.h`. It registers a `struct hc_driver` with usbcore, drives host-mode MMIO registers, manages async and periodic schedules, handles the emulated root hub, and exposes debugfs/sysfs diagnostics.

## Important APIs, Types, and Functions
The usbcore entry point is `fotg210_fotg210_hc_driver`, with callbacks for `.irq`, `.reset`, `.start`, `.stop`, `.shutdown`, `.urb_enqueue`, `.urb_dequeue`, `.endpoint_disable`, `.endpoint_reset`, `.get_frame_number`, `.hub_status_data`, `.hub_control`, and TT buffer completion. Platform integration is through `fotg210_hcd_probe()`, `fotg210_hcd_remove()`, `fotg210_hcd_init()`, and `fotg210_hcd_cleanup()`. Core controller lifecycle helpers are `fotg210_setup()`, `hcd_fotg210_init()`, `fotg210_run()`, `fotg210_stop()`, `fotg210_shutdown()`, `fotg210_halt()`, `fotg210_reset()`, `fotg210_quiesce()`, and `fotg210_init()`.

Transfer scheduling centers on `struct fotg210_qh`, `struct fotg210_qtd`, `struct fotg210_itd`, `struct fotg210_iso_stream`, and the software periodic shadow table. Control and bulk URBs are transformed by `qh_urb_transaction()` and submitted through `submit_async()`. Interrupt URBs use the same QTD/QH construction but enter `intr_submit()` and `qh_schedule()`. Isochronous URBs use `itd_submit()`, `iso_stream_find()`, `itd_urb_transaction()`, `iso_stream_schedule()`, and `itd_link_urb()`. Completion scanning is split across `fotg210_work()`, `scan_async()`, `scan_intr()`, `scan_isoc()`, `qh_completions()`, and `itd_complete()`.

Root-hub behavior is implemented by `fotg210_hub_status_data()`, `fotg210_hub_descriptor()`, and `fotg210_hub_control()`, including port reset, suspend, resume, overcurrent, and test-mode requests. Diagnostic interfaces are built with `create_debug_files()`, `fill_async_buffer()`, `fill_periodic_buffer()`, `fill_registers_buffer()`, and the writable sysfs attribute `uframe_periodic_max`.

## Control Flow
Probe checks `usb_disabled()`, obtains the platform IRQ, creates a `usb_hcd`, points HCD registers at `fotg->base`, caches resources, runs `fotg210_setup()`, switches the shared OTG block toward host mode in `fotg210_init()`, then calls `usb_add_hcd()`. Setup computes operational-register base from capability length, caches HCS parameters, initializes DMA pools and the async ring head, halts and resets the controller, and leaves the hardware ready for `fotg210_run()`. Start programs `PERIODICLISTBASE` and `ASYNCLISTADDR`, sets `CMD_RUN`, marks the root hub running, enables IRQs, and creates debugfs/sysfs files.

The IRQ handler reads and acknowledges `USBSTS`, ignores shared IRQs, runs `fotg210_work()` for normal/error completions, completes async unlink cycles on `STS_IAA`, notifies usbcore of port-change events on `STS_PCD`, and marks the controller dead on `STS_FATAL` or all-ones MMIO reads. `fotg210_work()` serializes schedule scans with `scanning`/`need_rescan`, dispatches async, interrupt, and iso scanners, and arms the I/O watchdog when needed.

URB enqueue first builds software TDs. Control and bulk QTDs are appended to an endpoint QH and linked into the async schedule; interrupt QHs are bandwidth-checked against the periodic table before linking; isochronous packets are packed into ITDs and inserted into frame-list slots. Dequeue marks the URB unlinked through usbcore and starts the correct async or interrupt unlink path, while ISO dequeue waits for normal ITD completion. Endpoint disable waits for hardware unlink completion before freeing QHs or iso streams.

## State and Persistence Behavior
All persistent driver state is in memory and hardware registers. `struct fotg210_hcd` holds MMIO pointers, the cached command word, root-hub state, hrtimer state, async unlink queues, periodic frame list and shadow list, DMA pools, port-status bitmaps, transfer counters, and tuning fields. QHs and QTDs are DMA-pool objects shared with hardware; the periodic list is coherent DMA memory; the shadow list mirrors hardware links for safe software traversal. `urb->hcpriv` and endpoint `hcpriv` connect usbcore objects to QH or ISO stream state.

State transitions are protected by `fotg210->lock`, with deliberate lock drops around completion callbacks. Delayed cleanup is controlled by the high-resolution timer event bitmap and `event_handlers[]`: async/periodic schedule status polling, interrupt unlink grace periods, cached ITD free delays, IAA watchdog recovery, schedule-disable delays, and I/O watchdog scans. Debugfs output snapshots live state but does not persist it; sysfs `uframe_periodic_max` changes only the in-memory bandwidth cap for the running controller.

## Dependencies and Integration Points
The file integrates with usbcore HCD APIs, platform-device probing, Linux DMA pools and coherent DMA, debugfs, sysfs, hrtimers, spinlocks, and the EHCI debug-port helpers. It depends on register and descriptor definitions from `fotg210-hcd.h`, shared core data and `fotg210_vbus()` declarations from `fotg210.h`, and the outer FOTG210 core to provide MMIO resources, IRQ, clock/resource metadata, and role selection. It also relies on EHCI usbcore globals such as `ehci_cf_port_reset_rwsem`, TT clearing through `usb_hub_clear_tt_buffer()`, and root-hub polling through `usb_hcd_poll_rh_status()`.

## Risks
The highest-risk areas are the QH/QTD unlink races, lock dropping during URB giveback, DMA descriptor lifetime, and periodic bandwidth accounting. `qh_completions()` deliberately avoids refreshing active overlays unless the QH is idle, because writing live QH state can cause hardware to DMA from stale or inconsistent addresses. Lost IAA interrupts are mitigated by a watchdog, but late or missing hardware status still risks stuck async unlink queues. ISO scheduling assumes `URB_ISO_ASAP`, power-of-two intervals, bounded frame-list horizon, and limited future queueing; very long or sparse ISO streams can return `-EFBIG` or `-ENOSPC`.

Root-hub handling is single-port (`FOTG210_MAX_ROOT_PORTS` is 1) and has no active bus suspend/resume callbacks, so platform power-management behavior depends on the wrapper and generic usbcore handling. The HCD uses 32-bit DMA values in several descriptor/register paths despite high-address comments, so DMA mask assumptions should be validated on target SoCs. Debugfs creation does not retain per-bus dentries, so teardown relies on name lookup. The code is copied from older EHCI logic and includes comments about silicon quirks and unimplemented FSTN/rebalancing behavior.

## Test Signals
Build coverage should include `CONFIG_USB_FOTG210_HCD=y/m`, `CONFIG_USB_DEBUG`, `CONFIG_DEBUG_FS`, and module unload/reload. Runtime signals are clean `usb_add_hcd()` probe, `USB 2.0 started` logs, root hub enumeration, high-speed device enumeration, control/bulk traffic, interrupt endpoints, ISO endpoints if supported by hardware, successful port reset/resume/change notifications, and no DMA mapping or watchdog warnings. Stress tests should include URB dequeue during completion callbacks, endpoint disable with pending transfers, TT devices behind high-speed hubs, short reads with and without `URB_SHORT_NOT_OK`, scatter-gather bulk I/O, and shutdown/kexec paths. Diagnostics include `debugfs/usb/fotg210/<bus>/async`, `periodic`, `registers`, IRQ counters, and sysfs `uframe_periodic_max` rejection/acceptance behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-hcd.h -->
# sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-hcd.h

## Purpose
`fotg210-hcd.h` defines the EHCI-style host-side data structures, register layout, bit fields, byte-order helpers, and inline accessors used by `fotg210-hcd.c`. It is the hardware contract for the host controller side of the Faraday FOTG210 block.

## Important APIs, Types, and Functions
Key exported types are `struct fotg210_hcd`, `struct fotg210_caps`, `struct fotg210_regs`, `struct fotg210_qtd`, `struct fotg210_qh_hw`, `struct fotg210_qh`, `union fotg210_shadow`, `struct fotg210_iso_stream`, `struct fotg210_iso_sched`, `struct fotg210_itd`, and `struct fotg210_fstn`. The root-hub state machine is encoded in `enum fotg210_rh_state`; hrtimer work items are encoded in `enum fotg210_hrtimer_event`. Conversion helpers `hcd_to_fotg210()` and `fotg210_to_hcd()` bridge usbcore `struct usb_hcd` and the private HCD object.

Register definitions cover capability registers (`HC_LENGTH`, `HC_VERSION`, `HCS_N_PORTS`, `HCC_CANPARK`, `HCC_PGM_FRAMELISTLEN`), operational registers (`CMD_RUN`, `CMD_RESET`, `CMD_ASE`, `CMD_PSE`, `STS_*`, `PORT_*`), OTG registers (`OTGCSR_*`, `OTGISR_OVC`), and global interrupt mask bits. Descriptor helpers include `QTD_NEXT()`, `QH_NEXT()`, `FOTG210_LIST_END()`, QTD status bits, QH type tags, periodic link tags, and endian conversion helpers `cpu_to_hc32()`, `hc32_to_cpu()`, and `hc32_to_cpup()`.

## Control Flow
This header does not run independently, but its layout controls every host path. Probe maps MMIO into `fotg210_caps` and then computes `fotg210_regs`. Enqueue paths allocate `fotg210_qtd`, `fotg210_qh_hw`, and `fotg210_itd` objects whose first fields match the hardware descriptor formats. Completion paths interpret the bit fields here to translate hardware status into Linux URB status. Periodic scheduling updates both the hardware frame list and the parallel `union fotg210_shadow` table using the same link type tags.

## State and Persistence Behavior
`struct fotg210_hcd` is the central volatile state container. Its `lock` protects schedule lists, endpoint private pointers, hardware descriptor fields, and MMIO updates. The state includes root-hub lifecycle, hrtimer event masks/timeouts, async and interrupt unlink queues, periodic frame-list state, port suspend/resume/reset bitmaps, DMA pools, the cached command register, and statistics. No state persists across driver removal; the durable ABI is the MMIO/descriptor layout encoded by this header.

## Dependencies and Integration Points
The header depends on Linux USB HCD types, EHCI debug-port types, DMA address types, hrtimers, clocks, spinlocks, and the shared `struct fotg210` wrapper. It integrates with usbcore through `struct usb_hcd`, `struct usb_device`, `struct usb_host_endpoint`, URB endpoint private storage, and USB port status constants. It assumes little-endian MMIO and descriptors through fixed `readl()`/`writel()` and `cpu_to_le32()` helpers, while retaining EHCI-derived big-endian comments for non-FOTG variants.

## Risks
The descriptor structures are hardware-visible and alignment-sensitive. Changes to field order, packing, link tags, or endian helpers can corrupt DMA. The file has comments inherited from broader EHCI code about big-endian and companion-controller support, but this FOTG210 variant hardcodes little-endian behavior and a single root port. `FOTG210_MAX_ROOT_PORTS` limits bitmap use to one port; adding multi-port hardware would require coordinated changes in root-hub code. Timer enum order must remain synchronized with `event_delays_ns[]` and `event_handlers[]` in the C file.

## Test Signals
Compile testing with sparse/endian checks is useful because `__hc32` and hardware descriptors are central. Runtime validation should exercise all descriptor types: QTD/QH control and bulk, interrupt QH periodic entries, ITD ISO entries, and root-hub port status paths. Debugfs register and schedule dumps should show sane decoded status bits and link tags. Any change to this header should be paired with DMA alignment checks, USB enumeration, transfer stress, and unload/reload tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-hcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-udc.c

## Purpose
`fotg210-udc.c` implements the USB gadget/device-controller side of the Faraday FOTG210 OTG controller. The driver registers a `usb_gadget` with the gadget framework, exposes endpoint operations for EP0 and EP1-EP4, handles setup requests and endpoint FIFO interrupts, performs DMA transfers between system memory and controller FIFOs, and connects VBUS events to the shared FOTG210 core.

## Important APIs, Types, and Functions
Platform integration is through `fotg210_udc_probe()` and `fotg210_udc_remove()`. Gadget framework entry points are in `fotg210_gadget_ops`: `fotg210_udc_start()`, `fotg210_udc_stop()`, and `fotg210_vbus_session()`. Endpoint operations are in `fotg210_ep_ops`: enable, disable, allocate/free request, queue, dequeue, set halt, set wedge, and fifo flush. The IRQ handler is `fotg210_irq()`.

Endpoint setup uses `fotg210_config_ep()`, `fotg210_fifo_ep_mapping()`, `fotg210_set_fifo_dir()`, `fotg210_set_tfrtype()`, and `fotg210_set_mps()`. Transfer execution uses `fotg210_ep_queue()`, `fotg210_ep0_queue()`, `fotg210_start_dma()`, `fotg210_enable_dma()`, `fotg210_wait_dma_done()`, `fotg210_disable_dma()`, `fotg210_in_fifo_handler()`, and `fotg210_out_fifo_handler()`. Control request handling includes `fotg210_rdsetupp()`, `fotg210_setup_packet()`, `fotg210_get_status()`, `fotg210_set_address()`, `fotg210_set_feature()`, `fotg210_clear_feature()`, `fotg210_ep0in()`, and `fotg210_ep0out()`.

## Control Flow
Probe obtains the IRQ, allocates the UDC and endpoint structures, optionally initializes a USB PHY from the `usb-phy` phandle, points `fotg210->reg` at the shared MMIO base, initializes the `usb_gadget`, creates EP0 plus four bidirectional data endpoints, allocates an internal EP0 request, resets/masks controller interrupts in `fotg210_init()`, disables PHY unplug detection, requests the IRQ, registers a PHY notifier, and calls `usb_add_gadget_udc()`.

When a gadget function binds, `fotg210_udc_start()` stores the gadget driver, binds the PHY OTG peripheral if present, enables the chip, and enables device global interrupts. Endpoint enable programs FIFO direction/type/maxpacket and maps endpoint numbers to FIFO numbers. Queueing a request stores it on the endpoint list; EP0 may start DMA immediately for IN data or enable control OUT interrupts, while non-control endpoints enable FIFO interrupts when the queue transitions from empty to non-empty.

The IRQ handler reads the group interrupt register and masks. Group 2 handles USB reset, suspend, resume, ISO sequence errors, zero-length packet notifications, and DMA errors. Group 0 handles control endpoint setup, IN, OUT, command abort, command end, and command failure; standard requests are handled locally, while unrecognized/class/vendor requests are forwarded to `driver->setup()`. Group 1 scans FIFO interrupts for EP1-EP4 and invokes IN or OUT FIFO handlers to perform DMA and complete requests.

## State and Persistence Behavior
UDC state is volatile and rooted in `struct fotg210_udc`: a spinlock, MMIO base, device/core pointers, optional PHY, `usb_gadget`, bound gadget driver, endpoint array, internal EP0 request/data, EP0 direction, and re-enumeration flag. Each `struct fotg210_ep` tracks queue, stall/wedge state, DMA use flag, endpoint number, type, direction, maxpacket, descriptor, and backpointer. Requests are wrapped in `struct fotg210_request` with a list node. Request completion removes list entries, updates status, drops the lock while calling `usb_gadget_giveback_request()`, and disables FIFO interrupts when queues empty.

Hardware state is stored in device control, address, FIFO map/config, endpoint maxpacket/stall, DMA target/length/address, and interrupt mask/source registers. The driver does not persist state across remove; stop reinitializes the device block, clears the bound driver, and marks speed unknown. VBUS session changes are delegated to `fotg210_vbus()` in the shared core.

## Dependencies and Integration Points
The file depends on the Linux gadget framework, USB chapter 9 request definitions, DMA mapping API, platform IRQs, MMIO helpers, optional USB PHY/OTG APIs, and the shared FOTG210 wrapper in `fotg210.h`. It uses register definitions and local endpoint/request structures from `fotg210-udc.h`. It is selected through the broader FOTG210 core and gadget UDC Kconfig path, and it interoperates with composite/configfs or legacy gadget functions through standard `usb_gadget_driver` callbacks.

## Risks
The driver comments say bulk transfer support is the current focus, but endpoint capabilities advertise ISO, bulk, and interrupt for EP1-EP4. The DMA wait path busy-polls completion inside request handling, which can increase IRQ latency or deadlock if hardware fails to report completion; reset/error handling aborts DMA and resets FIFO, but the wait has no explicit timeout. `fotg210_start_dma()` unmaps every transfer with `DMA_TO_DEVICE` even when mapping OUT transfers with `DMA_FROM_DEVICE`, which is a suspicious direction mismatch. `fotg210_ep_release()` clears `ep->epnum` before calling `fotg210_reset_tseq()`, so reset sequencing for disabled nonzero endpoints should be reviewed. Several register updates OR new field values without clearing old field masks, risking stale FIFO/type/maxpacket configuration if endpoints are reconfigured.

Control request handling is minimal and forwards many requests to the gadget driver; error paths stall CX. Queue and completion callbacks intentionally drop locks, so concurrent dequeue/disable/setup paths need stress coverage. The remove error path calls `iounmap(fotg210->reg)` even though probe assigns it from the shared `fotg->base`, so ownership of MMIO mapping must match the outer core.

## Test Signals
Build with `CONFIG_USB_FOTG210_UDC` and common gadget functions such as configfs loopback, serial, Ethernet, and mass storage. Runtime signals include clean `usb_add_gadget_udc()`, successful gadget binding/unbinding, VBUS connect/disconnect handling through the PHY notifier, EP0 enumeration, standard GET_STATUS/SET_ADDRESS/SET_CONFIGURATION behavior, data endpoint IN/OUT transfer completion, halt/wedge/clear-halt behavior, and clean unload. Stress tests should cover short OUT packets, zero-length packets, USB reset during DMA, request dequeue during IRQ handling, endpoint disable with pending requests, DMA mapping failures, and hardware that never raises DMA completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-udc.h

## Purpose
`fotg210-udc.h` is the register and private-state header for the FOTG210 gadget/device-controller driver. It names device-side MMIO offsets and bit fields, defines endpoint/request/controller structures, and provides the `gadget_to_fotg210()` conversion helper used by the UDC implementation.

## Important APIs, Types, and Functions
The register constants cover global interrupt masking (`FOTG210_GMIR`), device main control (`FOTG210_DMCR`), address/test/PHY state, control endpoint FIFO/status (`FOTG210_DCFESR`, `FOTG210_CXPORT`), interrupt masks and sources (`FOTG210_DMIGR`, `DMISGR*`, `FOTG210_DIGR`, `DISGR*`), zero-length packet status, endpoint max-packet/stall registers, endpoint-to-FIFO maps, FIFO configuration/count/reset, and DMA registers (`FOTG210_DMATFNR`, `FOTG210_DMACPSR1`, `FOTG210_DMACPSR2`). The private types are `struct fotg210_request`, `struct fotg210_ep`, and `struct fotg210_udc`.

## Control Flow
The header does not execute code directly. `fotg210-udc.c` uses the constants to initialize the device block, mask/unmask interrupt sources, configure endpoints, map FIFOs, start/abort DMA, acknowledge setup/control/data events, and process USB reset/suspend/resume. The structure definitions determine how endpoint queues, stall state, descriptors, EP0 internal state, PHY references, and the bound gadget driver are stored during all UDC callbacks.

## State and Persistence Behavior
All state defined here is runtime-only. `struct fotg210_request` wraps a gadget request with queue linkage. `struct fotg210_ep` persists endpoint configuration and request queue while the gadget is active. `struct fotg210_udc` persists controller-wide lock, MMIO, IRQ trigger metadata, device/core/PHY pointers, gadget object, driver pointer, endpoint table, and EP0 bookkeeping. Hardware state corresponding to the register macros is reset or reprogrammed by probe/start/stop and endpoint enable/disable paths.

## Dependencies and Integration Points
The header depends on kernel USB gadget types, USB PHY types, Linux lists and spinlocks, and MMIO access in the C file. It integrates with the shared `struct fotg210` core through the UDC state backpointer, with gadget function drivers through `struct usb_gadget` and `struct usb_ep`, and with platform hardware through the register map. It is private to the FOTG210 UDC implementation rather than a public kernel API.

## Risks
Bitfield macros are hardware-facing and many compose shifted endpoint/FIFO numbers. Incorrect masking or endpoint numbering can silently program the wrong FIFO, direction, DMA target, or stall bit. `FOTG210_MAX_NUM_EP` and `FOTG210_MAX_FIFO_NUM` fix the implementation at EP0-EP4 and FIFO0-FIFO3/4 semantics; hardware variants with more endpoints need coordinated C changes. Some macros encode field values with shifts that depend on operator precedence, so changes should preserve parentheses carefully.

## Test Signals
Any change should be validated by endpoint configuration tests covering each EP1-EP4 direction and transfer type, FIFO map readback where possible, EP0 setup traffic, DMA target selection for control and data FIFOs, interrupt mask/unmask behavior, and stall/wedge/clear-halt behavior. Compile checks should include the UDC as built-in and module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210.h -->
# sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210.h

## Purpose
`fotg210.h` is the shared private header for the FOTG210 core, host, and gadget drivers. It defines the outer controller object shared by HCD and UDC code, role/port metadata, VBUS control entry point, and conditional host/device probe/remove declarations.

## Important APIs, Types, and Functions
`enum gemini_port` identifies the Gemini integration port as none, port 0, or port 1. `struct fotg210` holds the common device pointer, MMIO resource, mapped base address, peripheral clock, syscon regmap, and Gemini port selection. `fotg210_vbus()` is the shared VBUS control hook. Depending on `CONFIG_USB_FOTG210_HCD`, host functions `fotg210_hcd_probe()`, `fotg210_hcd_remove()`, `fotg210_hcd_init()`, and `fotg210_hcd_cleanup()` are declared or stubbed. Depending on `CONFIG_USB_FOTG210_UDC`, gadget functions `fotg210_udc_probe()` and `fotg210_udc_remove()` are declared or stubbed.

## Control Flow
The outer FOTG210 core includes this header and can call the host and/or gadget probe/remove functions without open-coded preprocessor branches. If a role driver is disabled, the inline stub returns success for probe/remove and does nothing for init/cleanup, allowing the core driver to compile across host-only, device-only, and dual-role configurations. Host and gadget implementations receive the same `struct fotg210 *` so they share resources and role-control behavior.

## State and Persistence Behavior
`struct fotg210` is the durable runtime container for the platform instance while the core driver is bound. It owns the common MMIO base and resource metadata consumed by both HCD and UDC implementations. It does not persist to disk. Role-specific state lives in `struct fotg210_hcd` or `struct fotg210_udc`, not in this header.

## Dependencies and Integration Points
This header integrates platform device code, clock framework, regmap/syscon integration, and USB host/device subdrivers. It is used by `fotg210-hcd.c` and `fotg210-udc.c`, and likely by the FOTG210 core file that matches Devicetree compatibles such as `faraday,fotg200`, `faraday,fotg210`, or `cortina,gemini-usb`. The VBUS hook connects gadget `vbus_session` behavior to board/SoC-specific power or role registers.

## Risks
The stub probes return success when a role is disabled, so the core must treat disabled roles as intentionally absent rather than as initialized hardware. Shared ownership of `base`, `res`, `pclk`, and `map` means host/device remove paths must not unmap or disable resources owned by the core. Role switching is sensitive because HCD and UDC share registers and IRQs on the same OTG block.

## Test Signals
Build matrix coverage should include host-only, gadget-only, both enabled, and both disabled if Kconfig allows it. Runtime testing should verify that the core probes successfully in each enabled role combination, disabled role stubs do not register devices, VBUS changes reach board control, and remove paths do not double-free shared resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/Kconfig

## Purpose
`drivers/usb/gadget/Kconfig` defines the top-level Linux USB gadget framework configuration menu. It enables peripheral-mode USB support, debugging options, gadget framework defaults, composite/configfs support, reusable function drivers, and legacy gadget drivers. It also sources the UDC-controller menu from `drivers/usb/gadget/udc/Kconfig`, where hardware drivers such as FOTG210 device mode are selected.

## Important APIs, Types, and Functions
The primary symbol is `USB_GADGET`, a tristate menuconfig that selects `USB_COMMON` and `NLS`. Debug options are `USB_GADGET_DEBUG`, `USB_GADGET_VERBOSE`, `USB_GADGET_DEBUG_FILES`, and `USB_GADGET_DEBUG_FS`. `USB_GADGET_VBUS_DRAW` provides a numeric default current draw. Framework and function symbols include `USB_LIBCOMPOSITE`, `USB_CONFIGFS`, `USB_U_SERIAL`, `USB_U_ETHER`, `USB_U_AUDIO`, and function pieces such as `USB_F_ACM`, `USB_F_SERIAL`, `USB_F_OBEX`, `USB_F_NCM`, `USB_F_ECM`, `USB_F_SUBSET`, `USB_F_RNDIS`, `USB_F_MASS_STORAGE`, `USB_F_FS`, `USB_F_UAC1`, `USB_F_UAC1_LEGACY`, `USB_F_UAC2`, `USB_F_UVC`, `USB_F_MIDI`, `USB_F_MIDI2`, `USB_F_HID`, `USB_F_PRINTER`, and `USB_F_TCM`.

Configfs user-facing selectors include serial, ACM, OBEX, NCM, ECM, ECM subset, RNDIS, EEM, Phonet, mass storage, loopback/sourcesink, FunctionFS, audio, MIDI, HID, UVC, printer, and target-fabric options. The file ends by sourcing `drivers/usb/gadget/legacy/Kconfig`.

## Control Flow
Kconfig evaluation starts at `USB_GADGET`; when enabled, the nested options become visible. The UDC-controller submenu is sourced early so hardware controller drivers can be selected before gadget functions. Selecting configfs or individual functions pulls in their implementation symbols and dependencies such as `TTY`, `NET`, `SND`, `BLOCK`, `VIDEO_DEV`, `TARGET_CORE`, `CONFIGFS_FS`, `DMA_SHARED_BUFFER`, `CRC32`, or UVC/video buffer helpers. The selected symbol set drives which objects `drivers/usb/gadget/Makefile` and subdirectory Makefiles compile.

## State and Persistence Behavior
The file has no runtime state. Persistent effects are kernel configuration symbols stored in `.config` and used by the build system and preprocessor. These symbols determine which framework code, gadget functions, debug features, and UDC drivers are compiled as built-in, modules, or omitted.

## Dependencies and Integration Points
The file integrates with the kernel Kconfig tree, USB common support, gadget UDC hardware drivers, composite/configfs framework, legacy gadget drivers, networking, storage, audio, MIDI, HID, UVC/video, target-core, TTY, and configfs subsystems. For FOTG210, the important integration is the `source "drivers/usb/gadget/udc/Kconfig"` line, because the FOTG210 UDC symbol is defined under the UDC submenu rather than in this top-level file.

## Risks
Kconfig dependency mistakes can expose function drivers without required subsystems, fail to select reusable helper modules, or hide valid UDC drivers. Because many configfs options are booleans depending on `USB_CONFIGFS`, built-in/module interactions must be checked carefully. Debug options can alter timing and memory behavior. Changes to common symbols such as `USB_LIBCOMPOSITE` or `USB_CONFIGFS` have broad blast radius across many gadget functions.

## Test Signals
Run Kconfig matrix checks with `allmodconfig`, `allyesconfig`, `randconfig`, and targeted configs for configfs composite functions and legacy gadgets. Build tests should confirm that selected functions pull required objects and that disabled dependencies hide options. Runtime signals include configfs gadget creation, binding to a UDC, enumeration on a host, function-specific smoke tests, and clean unbind/module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/Makefile

## Purpose
`drivers/usb/gadget/Makefile` builds the USB gadget framework top-level objects and descends into the UDC, function, and legacy gadget subdirectories. It is the build-system counterpart to the gadget Kconfig menu.

## Important APIs, Types, and Functions
The Makefile sets `subdir-ccflags-$(CONFIG_USB_GADGET_DEBUG) := -DDEBUG` and appends `-DVERBOSE_DEBUG` when `CONFIG_USB_GADGET_VERBOSE` is enabled. It builds `libcomposite.o` when `CONFIG_USB_LIBCOMPOSITE` is enabled, with component objects `usbstring.o`, `config.o`, `epautoconf.o`, `composite.o`, `functions.o`, `configfs.o`, and `u_f.o`. It descends into `udc/`, `function/`, and `legacy/` when `CONFIG_USB_GADGET` is enabled.

## Control Flow
Kbuild evaluates the conditional object lists from `.config`. If libcomposite is selected, the listed `libcomposite-y` members are linked into `libcomposite.o`. If gadget support is enabled, Kbuild recurses into the hardware-controller, reusable-function, and legacy-driver subdirectories, where lower-level Makefiles choose specific UDC and gadget function objects.

## State and Persistence Behavior
The Makefile has no runtime state. Its persistent effect is build output: which objects are compiled and how debug preprocessor symbols are applied. The debug flags affect all descendant compilation units through `subdir-ccflags`.

## Dependencies and Integration Points
The Makefile integrates with Kbuild, the top-level gadget Kconfig symbols, and subdirectory Makefiles. It is the path by which UDC drivers such as FOTG210 gadget mode and composite/configfs gadget code enter the kernel build.

## Risks
Changing `subdir-ccflags` affects every gadget subdirectory and can alter timing or log volume. Omitting a `libcomposite-y` member can break configfs or composite gadget linking. Removing `udc/`, `function/`, or `legacy/` from `obj-$(CONFIG_USB_GADGET)` can silently drop large families of gadget support.

## Test Signals
Build with `CONFIG_USB_GADGET`, `CONFIG_USB_LIBCOMPOSITE`, debug, verbose debug, selected UDC drivers, selected function drivers, and legacy gadgets as built-in and modules. Link failures in `libcomposite.o`, missing UDC modules, or absent configfs gadget functionality are direct signals of Makefile regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/Makefile -->
