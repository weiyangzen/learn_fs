# subset-b-005474 Research

Grouped research for the USB c67x00 scheduler/header and Cadence CDNS3 gadget/glue sources. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-sched.c -->
# sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-sched.c

Purpose: Implements the Cypress C67x00 host-controller transfer scheduler. It accepts Linux USB core URBs, keeps per-endpoint queues, builds hardware transfer descriptors in the chip's HPI memory window, arms one frame at a time, parses completed TDs, advances data toggles, and gives URBs back to the HCD core.

Important APIs, types, and functions: `struct c67x00_ep_data` stores the endpoint queue, endpoint pointer, held `usb_device`, and next periodic frame. `struct c67x00_td` mirrors the 12-byte hardware TD and adds software links, URB pointer, stage/private data, endpoint state, and pipe. `struct c67x00_urb_priv` is stored in `urb->hcpriv` and tracks port, isochronous packet index, status, and endpoint data. Public HCD hooks are `c67x00_urb_enqueue`, `c67x00_urb_dequeue`, `c67x00_endpoint_disable`, `c67x00_sched_kick`, `c67x00_sched_start_scheduler`, and `c67x00_sched_stop_scheduler`. Core internal paths are `c67x00_fill_frame`, `c67x00_create_td`, `c67x00_send_frame`, `c67x00_check_td_list`, and `c67x00_do_work`.

Control flow: enqueue allocates URB private data, links the URB to the USB core endpoint list, creates or reuses endpoint scheduler data, initializes control or isochronous scheduling state, appends to the endpoint queue, enables SOF/EOP interrupts when the first URB appears, and queues high-priority work. The worker holds `c67x00->lock`, waits for hardware current-TD to clear, parses all completed TDs, completes endpoint-disable waiters, skips duplicate scheduling within the same frame, disables SOF/EOP if no URBs remain, otherwise fills a new frame in priority order: isochronous, interrupt, control, then bulk. TD creation checks frame bandwidth, periodic bandwidth, TD memory, and data buffer space before appending descriptors. Completed TD handling maps hardware status to URB completion: control transfers move through setup/data/status stages in `urb->interval`, bulk/interrupt complete on short packet or full transfer, and isochronous frames update per-packet descriptors.

State and persistence behavior: State is entirely in kernel memory and hardware registers/memory; nothing persists across driver unload. Endpoint scheduler data is attached to `usb_host_endpoint->hcpriv` and keeps a `usb_get_dev` reference so toggle repair can be done even while URBs are dequeued. `urb_count`, `urb_iso_count`, `max_frame_bw`, `current_frame`, `last_frame`, `next_td_addr`, `next_buf_addr`, and bandwidth counters define scheduler state. TDs live only for a frame and are freed after parsing. Data toggle state is synchronized back through `usb_settoggle` only when ACK/sequence status is valid.

Dependencies and integration points: The file depends on `c67x00.h` and `c67x00-hcd.h`, low-level HPI helpers such as `c67x00_ll_read_mem_le16`, `c67x00_ll_write_mem_le16`, `c67x00_ll_husb_set_current_td`, and Linux USB HCD APIs including `usb_hcd_link_urb_to_ep`, `usb_hcd_giveback_urb`, toggle helpers, and endpoint queues. It is driven by SOF/EOP/DONE interrupts that call `c67x00_sched_kick`, but heavy work runs in `system_highpri_wq`.

Risks: Frame arithmetic is wraparound-sensitive and off-by-one errors can stall periodic traffic. `urb->interval` is reused as a private control-stage field, which is compact but fragile. `c67x00_ep_data_alloc` attempts ordered endpoint insertion, yet the list-empty check occurs immediately after initialization, so endpoint ordering should be reviewed if fairness matters. `c67x00_endpoint_disable` waits with a one-second timeout loop and can delay teardown if hardware never drains. Short packets call `c67x00_clear_pipe`, so list mutation during TD iteration is a key correctness risk. Isochronous support assumes `URB_ISO_ASAP`, explicitly marked FIXME.

Test signals: Useful tests include control enumeration, bulk IN/OUT with short packets and `URB_ZERO_PACKET`, interrupt polling interval behavior, low-speed device behind full-speed root port preamble behavior, isochronous multi-packet URBs across frame wrap, dequeue while TDs are active, endpoint disable under load, and HPI memory-bound conditions that return `-EMSGSIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00.h -->
# sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00.h

Purpose: Provides shared register definitions, memory layout constants, device/SIE/HPI data structures, and low-level function declarations for the Cypress C67x00 USB controller driver.

Important APIs, types, and functions: The header defines USB control/status, host, device, HPI, SIE message, BIOS vector, TD buffer, and UDC memory offsets. `struct c67x00_sie` is the per-serial-interface-engine object with a spinlock, subdriver private data, IRQ callback, owning device pointer, SIE number, and mode. `struct c67x00_lcp` stores mailbox/LCP synchronization. `struct c67x00_hpi` stores MMIO base, register stride, lock, and LCP state. `struct c67x00_device` owns the HPI block, two SIEs, the platform device, and platform data. Declarations expose HPI status/init, SOF/EOP routing, USB status accessors, LE16 memory transfers, host frame/current-TD operations, reset/init/release, and IRQ dispatch.

Control flow: This file does not implement runtime control flow, but it defines the contract used by the platform, low-level HPI, host, and scheduler files. Register macros choose SIE-specific addresses by SIE index, while memory macros partition the on-chip RAM into host TD/data areas and peripheral request/header areas.

State and persistence behavior: The structs describe runtime state only. Locks protect chip registers and common state; completions/mutexes serialize LCP message exchange. Hardware register state persists only as long as the device is powered and initialized by the low-level driver.

Dependencies and integration points: Includes Linux spinlock, platform-device, completion, and mutex APIs. It is consumed by c67x00 low-level HPI, host controller, scheduler, and any peripheral-side code. The declarations bridge the host scheduler to HPI memory and host-port operations.

Risks: Register offsets and bit masks are hardware ABI; mistakes cause silent device malfunction. Many macros take an SIE or port index and encode different addresses, so callers must pass consistent zero/one values. Shared HPI/SIE register locking must be observed by implementation files. The header exposes low-level memory write/read APIs accepting raw addresses and lengths, so buffer bounds are enforced by callers, not the type system.

Test signals: Compile coverage across host and low-level driver files, probe/reset tests, register smoke tests on both SIEs, host frame/current-TD reads, interrupt routing verification, and memory read/write tests against known on-chip RAM offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/Kconfig

Purpose: Defines kernel configuration switches for Cadence USBSS/CDNS3 and CDNSP dual-role, gadget, host, PCI, and SoC glue support.

Important APIs, types, and functions: The main symbols are `USB_CDNS_SUPPORT`, `USB_CDNS_HOST`, `USB_CDNS3`, `USB_CDNS3_GADGET`, `USB_CDNS3_HOST`, `USB_CDNS3_PCI_WRAP`, `USB_CDNS3_TI`, `USB_CDNS3_IMX`, `USB_CDNS3_STARFIVE`, `USB_CDNSP_PCI`, `USB_CDNSP_GADGET`, and `USB_CDNSP_HOST`. The file selects `USB_XHCI_PLATFORM` when host support is relevant and selects `USB_ROLE_SWITCH` from common support.

Control flow: Kconfig nesting gates feature visibility: common support first, CDNS3-specific gadget/host/wrapper choices only under `USB_CDNS3`, and CDNSP gadget/host choices only under `USB_CDNSP_PCI`.

State and persistence behavior: Configuration symbols persist in the kernel build configuration and drive object inclusion at build time. They do not create runtime state directly.

Dependencies and integration points: Integrates with the Linux USB, USB gadget, USB PCI, ACPI, HAS_DMA, ARCH_K3, ARCH_MXC, ARCH_STARFIVE, and COMPILE_TEST configuration ecosystem. The Makefile consumes these symbols to choose object files.

Risks: Mismatched dependency expressions can build impossible host/gadget combinations. Defaults tying glue drivers to `USB_CDNS3` can pull wrappers into builds unexpectedly. Gadget dependency expressions require either built-in gadget support or gadget support matching the CDNS3 module mode.

Test signals: `allyesconfig`, `allmodconfig`, architecture defconfigs for TI/NXP/StarFive, compile-test builds, module/built-in combinations for `USB=m` and `USB=y`, and menuconfig visibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/Makefile

Purpose: Maps Cadence USB Kconfig symbols to kernel objects and module composition for common CDNS USB, CDNS3, CDNSP, platform glue, gadget, host, and trace support.

Important APIs, types, and functions: Builds `cdns-usb-common-y` from `core.o drd.o`, `cdns3-y` from `cdns3-plat.o`, adds `host.o` under `CONFIG_USB_CDNS_HOST`, adds `cdns3-gadget.o cdns3-ep0.o` under `CONFIG_USB_CDNS3_GADGET`, adds trace objects under `CONFIG_TRACING`, and emits glue objects for PCI, TI, i.MX, and StarFive. CDNSP PCI builds `cdnsp-udc-pci.o` with gadget ring/memory/ep0 pieces when configured.

Control flow: The Makefile handles the special `CONFIG_USB=m` case by forcing common and cdns3 objects into `obj-m`; otherwise it uses normal `obj-$(CONFIG_...)` inclusion. Trace object CFLAGS include `-I$(src)` so generated trace headers can resolve local includes.

State and persistence behavior: Build-only behavior; no runtime state.

Dependencies and integration points: Consumes the Kconfig symbols in this folder and relies on kbuild composite object syntax. It coordinates with trace headers requiring include-path adjustment.

Risks: Module composition is sensitive to built-in versus module USB core mode. Missing trace include paths break generated trace compilation. Adding new source files requires updating the correct composite object rather than only `obj-y`.

Test signals: Build with tracing enabled/disabled, gadget-only, host-only, dual-role, `CONFIG_USB=m`, `CONFIG_USB=y`, and CDNSP PCI configurations. `modinfo` should show expected modules such as `cdns3`, `cdns3-pci`, and platform glue modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-debug.h -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-debug.h

Purpose: Provides inline debug formatting helpers for CDNS3 USB and endpoint interrupts and for dumping endpoint TRB rings.

Important APIs, types, and functions: `cdns3_decode_usb_irq` appends human-readable USB interrupt names and speed. `cdns3_decode_ep_irq`, `cdns3_decode_epx_irq`, and `cdns3_decode_ep0_irq` decode endpoint status bits. `cdns3_dbg_ring` formats dequeue/enqueue indexes, DMA/virtual addresses, free TRB counts, cycle states, and each TRB's buffer/length/control values.

Control flow: Each helper writes formatted text into a caller-provided buffer using `sprintf` and returns the same buffer. `cdns3_dbg_ring` derives ring length from endpoint type through `GET_TRBS_PER_SEGMENT`, stops with a warning if the derived count exceeds `TRBS_PER_SEGMENT`, then walks the ring linearly.

State and persistence behavior: No persistent state; it reads endpoint fields and TRB memory for diagnostics.

Dependencies and integration points: Includes `core.h` and uses CDNS3 register/status macros, `usb_speed_string`, TRB helpers, and `struct cdns3_endpoint`. Intended for debugfs, trace, or dev_dbg-style consumers.

Risks: The functions assume the destination buffer is large enough; there is no bounds checking. Because they read live ring state without taking locks themselves, callers must ensure stable endpoint state if exact dumps matter. `sprintf(str + ret, ...)` patterns can overrun if used with small stack buffers.

Test signals: Compile with debug/trace users, exercise endpoint interrupt formatting for each bit, dump rings for bulk/control/isoc endpoints, and run with lockdep/KASAN to catch misuse around buffer sizing or stale endpoint pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-ep0.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-ep0.c

Purpose: Implements CDNS3 gadget endpoint zero control-transfer handling: setup packet arming, standard request handling, delegation to composite gadget drivers, status/data stage completion, ep0 queuing, and ep0 initialization.

Important APIs, types, and functions: Internal transfer primitive `cdns3_ep0_run_transfer` writes up to two TRBs for data/ZLP and rings DRDY/ERDY. Standard request handlers cover set address, set configuration, get status, set/clear feature, set SEL, and set isoch delay. `cdns3_ep0_setup_phase`, `cdns3_transfer_completed`, and `cdns3_check_ep0_interrupt_proceed` form the ep0 interrupt state machine. Exported functions are `cdns3_pending_setup_status_handler`, `cdns3_ep0_config`, and `cdns3_init_ep0`. The ep0 `usb_ep_ops` provide queue/dequeue through CDNS3 implementations and reject explicit enable/disable.

Control flow: Connection or reset configures ep0 and arms an OUT setup transfer. On setup/IOC, `cdns3_ep0_setup_phase` records direction, cancels any old ep0 request, sets DATA or STATUS stage based on `wLength`, handles standard requests locally when possible, delegates class/vendor requests to `gadget_driver->setup`, and either stalls, waits for delayed status, or completes status. `cdns3_gadget_ep0_queue` handles function-driver data-stage requests, maps DMA, enforces only one pending request, handles status-stage `SET_CONFIGURATION` by configuring all claimed endpoints and scheduling a software completion work item because the controller does not interrupt for that status stage.

State and persistence behavior: Runtime state lives in `struct cdns3_device`: `ep0_stage`, `ep0_data_dir`, `wait_for_setup`, `setup_pending`, `pending_status_request`, `status_completion_no_call`, `u1_allowed`, `u2_allowed`, `wake_up_flag`, and gadget state. The setup buffer is coherent DMA allocated by gadget initialization. No filesystem persistence exists.

Dependencies and integration points: Uses the Linux gadget/composite setup callback, USB chapter 9 request constants, DMA mapping helpers, CDNS3 register/TRB definitions, `cdns3_gadget_giveback`, endpoint halt helpers, `cdns3_set_hw_configuration`, and tracepoints from `cdns3-trace.h`.

Risks: ep0 is highly stateful and races with new SETUP packets; `cdns3_check_new_setup` is used to reject stale queues. The deferred status path relies on workqueue completion because hardware lacks an interrupt. `cdns3_gadget_ep0_set_halt` is a TODO returning success, so ep0 halt behavior is mostly through internal setup completion. SET_CONFIGURATION configures claimed endpoints that class drivers have not enabled yet, reflecting a Cadence hardware limitation that endpoint type/maxpacket must be known before hardware configuration.

Test signals: USB enumeration at full/high/super speed, standard requests including address/configuration/status/features, delayed-status gadget functions, ep0 ZLP requests, class/vendor setup delegation, disconnect/reset during pending ep0 transfer, SET_CONFIGURATION endpoint preconfiguration, and control-transfer stall/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-ep0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-gadget.c

Purpose: Implements the CDNS3 USBSS device-controller gadget driver: endpoint discovery/configuration, TRB ring allocation and DMA programming, request queue/dequeue/completion, interrupt handling, hardware workarounds, UDC registration, role-driver integration, and suspend/resume handling.

Important APIs, types, and functions: Public helpers exported to ep0 and other CDNS code include `cdns3_set_register_bit`, `cdns3_ep_addr_to_index`, `cdns3_next_request`, `cdns3_select_ep`, `cdns3_allocate_trb_pool`, `cdns3_hw_reset_eps_config`, `cdns3_allow_enable_l1`, `cdns3_get_speed`, `cdns3_gadget_giveback`, `cdns3_set_hw_configuration`, `cdns3_rearm_transfer`, `cdns3_ep_config`, halt helpers, `cdns3_gadget_ep_dequeue`, and `cdns3_gadget_init`. Internal control centers on `cdns3_ep_run_transfer`, `cdns3_ep_run_stream_transfer`, `cdns3_transfer_completed`, `cdns3_check_ep_interrupt_proceed`, `cdns3_check_usb_interrupt_proceed`, `cdns3_gadget_ep_enable/disable/queue`, `cdns3_init_eps`, and `cdns3_gadget_start/exit`.

Control flow: Gadget role startup sets a 32-bit DMA mask, powers the DRD gadget role, allocates `struct cdns3_device`, initializes endpoint objects from capability registers, creates a DMA pool for TRB rings, allocates setup/ZLP buffers, registers the USB gadget, and requests a shared threaded IRQ. UDC start records the function driver, limits speed, configures ep0/global interrupts, and enables controller settings. Endpoint matching claims hardware endpoints during autoconfig; endpoint enable configures endpoint registers, allocates/reset rings, enables endpoint interrupts, initializes producer/consumer cycle state, and arms workaround detection. Queue maps or prepares aligned DMA buffers, appends to deferred requests, and starts transfers if hardware is configured and not stalled. Completion interrupts inspect DMA position and cycle bits, accumulate actual lengths, advance dequeue indexes, give requests back, and start more deferred requests. USB interrupts handle connection, disconnection, suspend/resume, reset, and speed/state transitions.

State and persistence behavior: Persistent runtime state lives in `struct cdns3_device` and per-endpoint fields declared in `cdns3-gadget.h`: endpoint flags, TRB pools and DMA addresses, enqueue/dequeue indexes, cycle states, pending/deferred/internal descriptor-missing request lists, on-chip memory accounting, stream state, selected endpoint cache, and gadget-driver pointer. State is protected mainly by `priv_dev->lock`; callbacks intentionally drop the lock around gadget driver calls. No disk persistence exists. Hardware state is reset through `USB_CONF_CFGRST`, endpoint reset commands, and role suspend/resume paths.

Dependencies and integration points: Integrates with Linux USB gadget UDC APIs, `usb_add_gadget`, endpoint ops, composite gadget callbacks, DMA pool/coherent/noncoherent APIs, runtime PM, Cadence DRD role framework (`struct cdns_role_driver`), core `struct cdns` resources, tracepoints, and CDNS3 register definitions. It expects the platform driver to provide `cdns->dev_regs`, `dev_irq`, runtime PM, and role switching.

Risks: Hardware workaround 1 for pre-V3 silicon deliberately withholds/restores the first TRB cycle bit to avoid stale DMA addresses; ordering barriers and DMA-position checks are critical. Workaround 2 for pre-V2 OUT endpoints allocates internal requests on descriptor-missing interrupts to drain shared on-chip FIFO data, which risks memory pressure and subtle data-copy interactions. TRB ring wrap, link-TRB updates, stream PRIME/ERDY races, TDL programming, isochronous scheduling, and endpoint dequeue all mutate ring state under interrupt pressure. `cdns3_gadget_ep_queue` allocates a ZLP request without checking allocation failure. `cdns3_gadget_ep_disable` declares `ret` but does not assign poll results to it in two places, limiting error reporting. Buffer alignment handling uses noncoherent DMA and delayed freeing, so synchronization must remain exact.

Test signals: Gadget enumeration, bulk/interrupt/isoc IN and OUT traffic, SG and non-SG transfers, stream-capable bulk endpoints, ZLP requests, unaligned buffers, endpoint stall/clear/wedge, request dequeue while pending on hardware, disconnect/reset/suspend/resume, runtime PM role switching, pre-V2 descriptor-missing scenarios, pre-V3 WA1 stress, on-chip buffer exhaustion, and tracepoint validation of TRB rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-gadget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-gadget.h -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-gadget.h

Purpose: Defines the CDNS3 device-controller register map, bit fields, TRB format, endpoint/request/device data structures, constants, and cross-file gadget function prototypes.

Important APIs, types, and functions: `struct cdns3_usb_regs` maps the device register block. Macros define global USB config/status/command/interrupt bits, endpoint select/config/command/status bits, TRB fields, capability parsing, DMA AXI settings, versions, ring sizes, endpoint limits, and workaround buffer sizes. `struct cdns3_trb` is the hardware transfer descriptor. `struct cdns3_endpoint` stores Linux endpoint object, request lists, TRB ring, endpoint flags, direction/type/interval, ring producer-consumer state, workaround state, stream state, and TDL tracking. `struct cdns3_request` wraps `usb_request` with TRB indexes and flags. `struct cdns3_device` is the gadget controller state. Prototypes expose the gadget/ep0 shared functions.

Control flow: The header does not run control flow, but its constants encode how implementation files select endpoints, program TRBs, determine speeds, configure endpoint buffering, handle interrupts, and track endpoint lifecycle.

State and persistence behavior: The defined structs describe in-memory state only. `cdns3_device` owns DMA pools, setup/ZLP buffers, endpoint array, selected endpoint cache, status work, and feature flags. `cdns3_endpoint` tracks pending/deferred/internal request lists and ring indexes. No persistent storage is involved.

Dependencies and integration points: Includes Linux gadget and DMA direction headers. Used by `cdns3-gadget.c`, `cdns3-ep0.c`, debug helpers, and trace definitions. It is tightly coupled to Cadence USBSS hardware ABI and Linux gadget core types.

Risks: Register bit macros are hardware-critical. Some macros appear parameterized but reference `p` in bodies for link-state helpers, so callers must use only valid macros and compile coverage matters. Ring-size constants affect memory use and isochronous behavior. Endpoint flags are a dense bitfield contract across multiple files; adding flags or changing semantics requires auditing queue, completion, halt, and reset paths.

Test signals: Compile all CDNS3 gadget configurations, run sparse/clang warnings over macro usage, validate register field programming on hardware or emulation, exercise all endpoint types and stream modes, and inspect trace/debug dumps for ring index/cycle consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-gadget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-imx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-imx.c

Purpose: Provides the NXP i.MX glue layer around the Cadence USB3 controller, handling non-core registers, clocks, child `cdns,usb3` population, wakeup configuration, and platform-specific low-power transitions.

Important APIs, types, and functions: `struct cdns_imx` stores the device, non-core MMIO base, clock bulk array, and child platform device pointer. `cdns_imx_noncore_init` validates PHY clock, asserts/deasserts reset bits, straps OTG mode, disables overcurrent, and enables host/device interrupts. `cdns_imx_probe/remove` manage resources, clocks, child population, and runtime PM. `cdns_imx_platform_suspend` is exported through `cdns3_platform_data` and handles host-mode D1/D0 transitions. PM callbacks handle runtime clock gating and system power-loss recovery.

Control flow: Probe maps non-core registers, duplicates and obtains required clocks (`lpm`, `bus`, `aclk`, `ipg`, `core`), enables them, initializes wrapper registers, populates children with platform data, and enables runtime PM. During host suspend, it writes xHCI PMCSR to D1, selects mdctrl clock, polls wrapper/clock/PHY request bits, and enables wakeups. Resume reverses wakeups, returns xHCI to D0, clears RXDET P3, restores clocks, and waits for OTG readiness.

State and persistence behavior: Runtime state is only `struct cdns_imx`, clock enable state, PM state, and wrapper registers. System resume checks reset bits to detect power loss and reinitializes non-core registers when needed.

Dependencies and integration points: Uses OF platform population, Linux clock bulk APIs, runtime/system PM, MMIO polling, Cadence `core.h`, and `cdns3_platform_data.platform_suspend`. Compatible string is `fsl,imx8qm-usb3`; it creates a child compatible with `cdns,usb3`.

Risks: Suspend/resume touches xHCI and OTG registers through child `struct cdns`, so ordering with core role/PM state is important. Poll timeouts are warnings in several low-power paths, which may leave marginal hardware states. The constant `DEVU3_WAEKUP_EN` appears misspelled but is used as a bit name. Power-loss recovery depends on reset-mask values in wrapper registers.

Test signals: i.MX probe/remove, child creation, runtime suspend/resume clock toggling, host-mode system suspend with wake enabled/disabled, resume after power loss, OTG role transitions, and timeout injection for PHY clock valid and mdctrl/lpm/otg-ready polls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-pci-wrap.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-pci-wrap.c

Purpose: Wraps a Cadence PCI USBSS device exposing separate PCI functions/BARs into a single `cdns-usb3` platform device with named host, peripheral, and OTG resources.

Important APIs, types, and functions: `struct cdns3_wrap` stores the synthesized platform device, six resources, and the devfn that registered the platform child. `cdns3_get_second_fun` finds the peer PCI function. `cdns3_pci_probe` enables PCI, fills resources from BARs and IRQs, and registers the platform device when both functions are available. `cdns3_pci_remove` unregisters the platform child and frees shared wrapper memory.

Control flow: The wrapper accepts only devfn 0 (host/device) and devfn 1 (OTG). Each function probe records its piece of the resource array. When the peer function is already enabled, the second probe creates `PLAT_DRIVER_NAME` (`cdns-usb3`) with resources named `host`, `peripheral`, `otg`, `xhci`, `dev`, and `otg` memory as appropriate.

State and persistence behavior: Shared state is `struct cdns3_wrap` referenced from PCI drvdata of both functions. It persists only while the PCI functions are bound. The platform child owns no permanent storage.

Dependencies and integration points: Uses Linux PCI, platform-device registration, DMA mask propagation, and Cadence PCI IDs. The generated platform device is consumed by `cdns3-plat.c`.

Risks: Peer-function discovery with `pci_get_device` is delicate and may mishandle multiple identical devices if not constrained by bus/device context. Lifetime depends on `pci_is_enabled(func)` and shared `wrap` ownership. Both device and host IRQ resources may use the same IRQ for function 0, so downstream IRQ sharing must work.

Test signals: Probe order with function 0 first and function 1 first, remove order in both directions, multiple identical PCI cards, platform resource names/ranges, shared IRQ operation, and module unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-pci-wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-plat.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-plat.c

Purpose: Implements the generic Cadence CDNS3 platform core driver that binds named resources, powers PHYs, initializes the common DRD core, wires gadget initialization, and handles runtime/system PM.

Important APIs, types, and functions: `cdns3_plat_probe` allocates `struct cdns`, collects `host`, `peripheral`, and `otg` IRQ/memory resources, obtains optional wakeup IRQ and USB2/USB3 PHYs, powers PHYs, assigns `cdns->gadget_init = cdns3_gadget_init`, and calls `cdns_init`. `cdns3_plat_remove` tears this down. PM helpers `cdns3_controller_suspend/resume`, runtime callbacks, and system sleep callbacks coordinate PHY power, platform suspend hooks, core suspend/resume, wakeup IRQs, and low-power flags.

Control flow: Probe initializes resources and PHYs before entering common core initialization. Runtime suspend calls optional platform glue suspend, powers off PHYs, and marks `cdns->in_lpm`. Resume reinitializes PHYs if power was lost, powers PHYs back on, calls optional platform resume hook, resumes core state under lock, and re-enables wakeup IRQ if one was consumed.

State and persistence behavior: Runtime state is `struct cdns`, PHY states, runtime PM state, `in_lpm`, and wakeup flags. No persistent storage exists. PM state survives only across suspend cycles in memory and hardware registers.

Dependencies and integration points: Consumes platform resources from DT or PCI wrapper, optional `cdns3_platform_data` from SoC glue, Linux PHY APIs, runtime PM, `core.h`, `drd.h`, and `gadget-export.h`. Compatible is `cdns,usb3`.

Risks: Error paths must unwind PHY init/power in the right order. Runtime PM is forbidden unless platform quirks allow default runtime PM, which can surprise platforms expecting autosuspend. Resume after power loss depends on `cdns_power_is_lost` and PHY reinit correctness. Locking spans `cdns_resume` and wakeup flag updates.

Test signals: Probe error injection for missing named resources/IRQs/PHYs, host-only/gadget-only/dual-role operation, runtime autosuspend/resume, system suspend with wakeup IRQ, power-loss resume, PCI wrapper resources, and DT resource naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-starfive.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-starfive.c

Purpose: Provides the StarFive JH7110 glue layer for Cadence USB, configuring syscon strap bits, clocks, resets, child platform devices, wakeup capability, and PM clock/reset handling.

Important APIs, types, and functions: `struct cdns_starfive` stores device, syscon regmap, reset array, clocks, and syscon offset. `cdns_mode_init` sets PLL/refclk/suspend bypass bits and straps host or peripheral mode from `usb_get_dr_mode`. `cdns_clk_rst_init/deinit` enable clocks and deassert/assert resets. Probe/remove create and destroy child platform devices and PM state. Runtime and system PM callbacks toggle clocks/resets.

Control flow: Probe reads `starfive,stg-syscon` phandle argument as the USB mode register offset, gets all clocks and reset controls, writes mode strap bits, enables clocks/resets, populates children, marks wake capable, and enables runtime PM. Remove gets runtime PM, unregisters children, disables PM, and asserts resets/clocks off.

State and persistence behavior: State is in `struct cdns_starfive`, PM clock/reset state, and syscon strap register bits. No disk persistence.

Dependencies and integration points: Uses syscon/regmap, reset controller, bulk clock APIs, OF platform population, `usb_get_dr_mode`, runtime/system PM, and Cadence child nodes. Compatible string is `starfive,jh7110-usb`.

Risks: Mode strap programming only handles explicit host/peripheral and leaves other modes unchanged. `devm_clk_bulk_get_all` can return zero clocks; behavior depends on platform data. System resume calls full reset init, so child/core state must tolerate wrapper reset ordering.

Test signals: Host and peripheral DT modes, syscon phandle parsing, all clock/reset probe failures, runtime suspend/resume, system suspend/resume, child population failure, and remove while runtime suspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-starfive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-ti.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-ti.c

Purpose: Provides the TI K3/AM64/J721E wrapper for Cadence USB3, configuring wrapper reset, reference clock rate encoding, optional USB2-only and VBUS divider properties, child device population, runtime PM, and a DRD suspend residency quirk.

Important APIs, types, and functions: `struct cdns_ti` stores wrapper MMIO, property flags, `ref` and `lpm` clocks, and encoded reference clock rate. `cdns_ti_rate_table` maps supported kHz rates to hardware codes. `cdns_ti_reset_and_init_hw` asserts reset, programs static config, USB2-only mode, and modestrap, then deasserts reset. Probe obtains resources/clocks/properties, validates refclk rate, initializes hardware, enables runtime PM, and populates `cdns,usb3` children with platform data. Runtime resume reinitializes hardware if reset bits indicate uninitialized state.

Control flow: Probe performs a manual reset before the first `pm_runtime_get_sync` so runtime resume observes initialized hardware. Child devices are unregistered on remove before runtime PM is released. Runtime resume is idempotent by checking `USBSS_W1_PWRUP_RST | USBSS_W1_MODESTRAP_SEL`.

State and persistence behavior: State is in `struct cdns_ti`, wrapper registers, clock state, and runtime PM reference. No persistent storage. Wrapper state may be lost across runtime/system suspend and is repaired on resume.

Dependencies and integration points: Uses platform MMIO, clock APIs, OF platform population, device properties `ti,vbus-divider` and `ti,usb2-only`, runtime PM, and `cdns3_platform_data` quirks. Compatible strings are `ti,j721e-usb` and `ti,am64-usb`.

Risks: Unsupported refclk rates fail probe. The rate table order is hardware ABI; changing it changes register programming. Error path after child population failure must balance runtime PM. Runtime resume only checks two wrapper bits, so partially corrupted static config may not be repaired. `lpm_clk` is obtained but not explicitly enabled in this file, relying on runtime/core behavior.

Test signals: Supported and unsupported reference clocks, `ti,vbus-divider`, `ti,usb2-only`, child populate failure, runtime resume after wrapper reset, system sleep through `pm_runtime_force_suspend/resume`, and host/gadget operation on J721E/AM64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-ti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-trace.c

Purpose: Instantiates CDNS3 tracepoints by defining `CREATE_TRACE_POINTS` and including `cdns3-trace.h`.

Important APIs, types, and functions: No functions are defined directly. The file causes tracepoint definitions declared in `cdns3-trace.h` to be emitted into `cdns3-trace.o` when tracing and gadget support are enabled by the Makefile.

Control flow: Build-time tracepoint instantiation only; runtime behavior is provided by the generated tracepoint code and call sites in `cdns3-gadget.c` and `cdns3-ep0.c`.

State and persistence behavior: No local state. Runtime trace buffers are managed by the kernel tracing subsystem.

Dependencies and integration points: Depends on `cdns3-trace.h`, kbuild `CFLAGS_cdns3-trace.o := -I$(src)`, `CONFIG_TRACING`, and CDNS3 trace call sites.

Risks: Exactly one compilation unit should define `CREATE_TRACE_POINTS` for this trace header. Include-path or conditional-build mistakes cause missing trace symbols or duplicate definitions.

Test signals: Build with `CONFIG_TRACING=y`, boot/load the module, enable CDNS3 trace events under tracefs, exercise endpoint and USB interrupts, and verify events are emitted without duplicate symbol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-trace.c -->
