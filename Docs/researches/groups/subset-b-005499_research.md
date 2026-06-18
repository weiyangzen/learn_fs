# Research: subset-b-005499

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bcm63xx_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bcm63xx_udc.c

## Purpose
This file implements the Broadcom BCM63xx high/full-speed USB device controller driver. It registers a `usb_gadget` backed by the BCM63xx USBD block plus an internal IUDMA engine, exposes one control endpoint and fixed bulk/interrupt endpoints, and bridges gadget driver requests to hardware descriptor rings. It is platform-data driven and depends on BCM63xx SoC register helpers, clocks, IRQ resources, and USB USBD/IUDMA register definitions.

## Important APIs, Types, And Functions
The main state containers are `struct bcm63xx_udc`, `struct bcm63xx_ep`, `struct bcm63xx_req`, and `struct iudma_ch`. Static `iudma_defaults[]` defines the hardware endpoint/channel mapping, FIFO sizing, packet sizes, and descriptor ring depths. Gadget endpoint operations are implemented by `bcm63xx_ep_enable()`, `bcm63xx_ep_disable()`, `bcm63xx_udc_queue()`, `bcm63xx_udc_dequeue()`, `bcm63xx_udc_set_halt()`, and `bcm63xx_udc_set_wedge()`. Gadget controller operations are `bcm63xx_udc_get_frame()`, `bcm63xx_udc_pullup()`, `bcm63xx_udc_start()`, and `bcm63xx_udc_stop()`. Hardware setup is split across `bcm63xx_init_udc_hw()`, `iudma_init()`, `bcm63xx_fifo_setup()`, `bcm63xx_ep_setup()`, and PHY/pullup helpers. Interrupt entry points are `bcm63xx_udc_ctrl_isr()` for USBD events and `bcm63xx_udc_data_isr()` for per-channel IUDMA completion. Debugfs views are provided through `bcm63xx_usbd_dbg_show()` and `bcm63xx_iudma_dbg_show()`.

## Control Flow
Probe allocates the UDC, maps USBD and IUDMA resources, initializes endpoint objects, clocks, DMA rings, IRQs, debugfs, and registers the gadget. `udc_start` switches the shared USB PHY to device mode, configures FIFOs/endpoints, and records the gadget driver. Pullup transitions EP0 from shutdown to a requeue state, enables control IRQs, and asserts D+. Non-EP0 requests are DMA-mapped, appended to an endpoint queue, and the head request is submitted to `iudma_write()`. IUDMA completion interrupts call `iudma_read()`, update `actual`, either queue the next fragment/request or complete the request outside the spinlock.

EP0 is workqueue-driven. Hardware delivers ordinary setup packets through EP0 RX IUDMA, but it auto-acks SET_CONFIGURATION and SET_INTERFACE. The control ISR therefore records pending synthetic events, and `bcm63xx_ep0_process()` runs a state machine covering setup receive, IN data, OUT data, OUT status, fake IN status, reset, and shutdown. Standard requests consumed by hardware are replayed to the gadget driver using synthesized `usb_ctrlrequest` objects.

## State And Persistence
State is in RAM and hardware registers only. Persistent driver state includes gadget speed, current config/interface/alternate interface, endpoint queues, IUDMA ring pointers, EP0 pending flags, EP0 reply/request pointers, and the wedged endpoint bitmap. DMA descriptors are coherent allocations owned by the device while the owner bit is set. Debugfs is observational and does not persist configuration. Module parameters `use_fullspeed` and `irq_coalesce` affect runtime mode and transfer interrupt behavior.

## Dependencies And Integration Points
The driver integrates with the Linux USB gadget core via `usb_add_gadget_udc()`, endpoint ops, and gadget ops; with platform device resources for two MMIO regions and seven IRQs; with BCM63xx board platform data for `port_no`; with BCM63xx clock and PHY/USBH private register helpers; with DMA mapping APIs; and with debugfs under `usb_debug_root`.

## Risks
The file explicitly documents that RX IRQ coalescing is less robust and does not reliably pass `testusb`; cancellation of partially complete RX transfers is a hardware limitation. EP0 is complex because hardware auto-acks some requests, so bad SET_CONFIGURATION/SET_INTERFACE cannot be stalled after the fact. `bcm63xx_udc_dequeue()` completes the request after releasing the lock even if the request was not found, so callers rely on valid queued requests. Shutdown waits by polling `ep0state` with sleeps, which is sensitive to worker progress and memory barriers. Several paths use SoC-specific global register writes, making port-number and clock ordering mistakes high impact.

## Test Signals
Useful validation signals are successful enumeration at full and high speed, `testusb` transfer and cancellation tests with `irq_coalesce=0`, explicit regression checks with `irq_coalesce=1`, SET_CONFIGURATION/SET_INTERFACE gadget callbacks, EP0 IN/OUT control transfers, stall/wedge persistence across CLEAR_FEATURE and reset, link down/reset callbacks, debugfs descriptor state, and suspend/resume or pullup cycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bcm63xx_udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Kconfig

## Purpose
This Kconfig entry exposes the Broadcom USB3.0 Device Controller IP driver as `USB_BDC_UDC`. It gates compilation of the BDC UDC code under the USB gadget subsystem.

## Important APIs, Types, And Functions
The only symbol is `config USB_BDC_UDC`, a tristate option named "Broadcom USB3.0 device controller IP driver(BDC)". It depends on `USB_GADGET` and `HAS_DMA`, defaults to enabled on `ARCH_BRCMSTB`, and describes the module name as `bdc`.

## Control Flow
Kconfig selection decides whether the BDC object list in the adjacent Makefile is built into the kernel or as a module. There is no runtime control flow in this file.

## State And Persistence
The configuration choice persists in the kernel build configuration. At runtime, BDC state is managed by the C files in the same directory.

## Dependencies And Integration Points
This entry integrates with kernel configuration, the USB gadget menu, Broadcom STB architecture defaults, and DMA-capable platform constraints. It is consumed by `obj-$(CONFIG_USB_BDC_UDC)` in the Makefile.

## Risks
The dependency does not express platform bus or device-tree requirements, so selecting it outside a matching Broadcom BDC platform only builds the driver; probe still depends on compatible hardware and resources. The default for `ARCH_BRCMSTB` can increase build coverage and warning exposure for that architecture.

## Test Signals
Build tests should confirm `CONFIG_USB_BDC_UDC=y` links the BDC objects, `=m` produces `bdc.ko`, and unset excludes the objects. Runtime test requires a `brcm,bdc` or `brcm,bdc-udc-v2` platform device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Makefile

## Purpose
This Makefile defines how the Broadcom BDC USB device controller driver is compiled.

## Important APIs, Types, And Functions
`obj-$(CONFIG_USB_BDC_UDC) += bdc.o` creates the driver object when enabled. `bdc-y` always includes `bdc_core.o`, `bdc_cmd.o`, `bdc_ep.o`, and `bdc_udc.o`. If `CONFIG_USB_GADGET_VERBOSE` is non-empty, `bdc_dbg.o` is added for verbose debug dumping.

## Control Flow
The build combines core platform probing, command submission, endpoint transfer management, gadget glue, and optional debug helpers into one module or built-in object.

## State And Persistence
There is no runtime state. The build composition is persistent in kernel build artifacts.

## Dependencies And Integration Points
The file is controlled by the Kconfig symbol in this directory and by the generic `CONFIG_USB_GADGET_VERBOSE` debug option.

## Risks
Verbose debug functions are compiled out unless `CONFIG_USB_GADGET_VERBOSE` is set, so code that expects `bdc_dbg_*()` side effects must not rely on them. Object ordering is conventional but all listed source files share internal headers and must remain consistent.

## Test Signals
Build with `CONFIG_USB_BDC_UDC=y/m` and with `CONFIG_USB_GADGET_VERBOSE` both enabled and disabled to catch missing declarations or stale debug references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc.h

## Purpose
This is the central private header for the Broadcom BDC USB3 device controller driver. It defines register offsets, bit fields, descriptor formats, endpoint/request/controller state structures, inline MMIO helpers, and cross-file prototypes.

## Important APIs, Types, And Functions
Important data types are `struct bdc_bd` for buffer descriptors, `struct bdc_sr` for status reports, `struct bd_table` and `struct bd_list` for chained descriptor tables, `struct bd_transfer`, `struct bdc_req`, `struct bdc_ep`, `struct srr`, and `struct bdc`. EP0 state is encoded by `enum bdc_ep0_state`, and USB link states by `enum bdc_link_state`. Constants describe command opcodes/status values, USPC/USPPMS/BDCSC fields, BD flags, status report types, transfer statuses, maximum transfer sizes, U1 timing, interrupt coalescing, and remote wake bookkeeping. Cross-file APIs include controller lifecycle (`bdc_run()`, `bdc_stop()`, `bdc_reset()`, `bdc_reinit()`), gadget lifecycle (`bdc_udc_init()`, `bdc_udc_exit()`), connection control, transfer notification, status report handlers, and EP0 report handlers.

## Control Flow
The header encodes hardware conventions used by all BDC source files: endpoint array index 1 is EP0, endpoint indexes map as OUT even and IN odd for nonzero endpoints, status reports dispatch by `sr_handler[]`, and EP0 transfer status reports dispatch through `sr_xsf_ep0[]`. `bdc_readl()` and `bdc_writel()` are the shared MMIO accessors.

## State And Persistence
`struct bdc` owns all persistent in-memory driver state: gadget object, gadget driver pointer, spinlock, PHYs, endpoint array, registers, scratchpad DMA buffer, status report ring, setup packet, EP0 requests and state, delayed status/ZLP flags, pullup state, device status bits, DMA pool, remote wake delayed work, and optional clock. Endpoint and request state persists until disabled, completed, or freed.

## Dependencies And Integration Points
The header depends on Linux USB gadget/ch9 types, DMA mapping, lists, spinlocks, debugfs, unaligned access helpers, and BDC hardware definitions local to the file. It is included by core, command, endpoint, gadget, and debug implementation files.

## Risks
Most hardware programming constants are open-coded here; mistakes in bit shifts or endpoint index conventions affect every implementation file. `BDC_PSP` is defined twice with the same expression, which is harmless but easy to notice during maintenance. Maximum transfer and descriptor ring sizing are fixed by macros and can reject large gadget requests or stress isochronous buffering.

## Test Signals
Compile coverage is the main header test. Runtime signals include correct endpoint naming/indexing, successful EP0 configuration after connect, status report dispatch to the expected handler, correct DMA address programming on 32-bit and 64-bit capable devices, and remote wake status bit transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.c

## Purpose
This file implements synchronous command submission to the BDC hardware command processor. It is used by endpoint configuration, address assignment, stall/reset/stop operations, dequeue pointer changes, and USB3 function wake notifications.

## Important APIs, Types, And Functions
`bdc_issue_cmd()` writes command parameters, uses a write memory barrier, sets `BDC_CMD_CWS | BDC_CMD_SRD`, and polls command status until not busy or timeout. `bdc_submit_cmd()` validates the command processor is idle, converts BDC completion codes into Linux errors, and logs failures. Exported internal helpers are `bdc_config_ep()`, `bdc_dconfig_ep()`, `bdc_ep_bla()`, `bdc_address_device()`, `bdc_function_wake_fh()`, `bdc_function_wake()`, `bdc_ep_set_stall()`, `bdc_ep_clear_stall()`, and `bdc_stop_ep()`.

## Control Flow
Endpoint enable calls `bdc_config_ep()` after a descriptor list exists. This builds command parameters from descriptor max packet size, endpoint type, interval, burst/mult fields, and gadget speed, then reinitializes the BD list on success. Deconfigure drops the endpoint from hardware. Dequeue and some cancellation paths use `bdc_stop_ep()` followed by `bdc_ep_bla()` to redirect the hardware dequeue pointer. Standard SET_ADDRESS uses `bdc_address_device()`. Clear-stall may first force a stall, issues reset endpoint, optionally resets sequence numbers, and notifies transfer fetching.

## State And Persistence
The file mutates hardware command registers and endpoint flags. `ep_bd_list_reinit()` resets enqueue/dequeue indexes and marks the first BD with stop-buffer-fetch so software can safely requeue. `bdc_stop_ep()` sets `BDC_EP_STOP` after a successful stop command. Address and wake commands update hardware state indirectly; `bdc->dev_addr` is set by callers.

## Dependencies And Integration Points
The command layer depends on `bdc.h` register definitions, endpoint descriptors from the USB core, speed state maintained by `bdc_udc.c`, and debug helpers. It is called from endpoint, EP0, gadget, link-state, and remote wake paths.

## Risks
Commands are serialized only by callers holding the controller lock; calling without that lock could race command register programming. Timeouts are short busy-poll loops in atomic context, so hardware latency changes can surface as `-ECONNRESET`. Endpoint configuration is sensitive to interval conversion for full-speed interrupt/isochronous endpoints and to optional superspeed companion descriptors. Clear-stall behavior intentionally stalls an unstalled non-EP0 endpoint before resetting it, which must match hardware sequence-number requirements.

## Test Signals
Exercise SET_ADDRESS, endpoint enable/disable for bulk/interrupt/isochronous descriptors at each speed, halt/clear-halt, dequeue of in-flight requests, and USB3 remote/function wake. Command timeout and parameter error logs are key diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.h

## Purpose
This private header declares the BDC command helpers implemented in `bdc_cmd.c`.

## Important APIs, Types, And Functions
It declares device command helpers (`bdc_address_device()`), endpoint configuration commands (`bdc_config_ep()`, `bdc_dconfig_ep()`), endpoint operation commands (`bdc_stop_ep()`, `bdc_ep_set_stall()`, `bdc_ep_clear_stall()`, `bdc_ep_bla()`), and remote/function wake commands (`bdc_function_wake()`, `bdc_function_wake_fh()`).

## Control Flow
The declarations let endpoint and gadget code issue hardware commands without exposing the lower-level command register polling functions.

## State And Persistence
This header has no state. The declared functions mutate BDC registers, endpoint flags, hardware endpoint configuration, and device address or wake state.

## Dependencies And Integration Points
It depends on `struct bdc`, `struct bdc_ep`, `u32`, and `dma_addr_t` definitions made available before inclusion, normally through `bdc.h`.

## Risks
The comment says "header for the BDC debug functions", which is stale and can mislead readers. The header intentionally exposes only command-level operations, so new code should not duplicate command register programming elsewhere.

## Test Signals
Compile tests catch declaration drift. Runtime validation comes from call sites in endpoint enable/disable, EP0 SET_ADDRESS, halt/clear-halt, dequeue, and remote wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_core.c

## Purpose
This file owns BDC platform-driver probing, hardware reset/run/stop operations, memory allocation for controller-owned rings and scratchpad buffers, PHY and clock setup, suspend/resume, and module registration.

## Important APIs, Types, And Functions
Hardware state transitions are implemented by `bdc_stop()`, `bdc_reset()`, `bdc_run()`, and `poll_oip()`. Connection helpers are `bdc_softconn()` and `bdc_softdisconn()`. Memory setup uses `scratchpad_setup()`, `setup_srr()`, `bdc_mem_alloc()`, `bdc_mem_init()`, and `bdc_mem_free()`. Runtime recovery uses `bdc_reinit()`. Probe/remove and PM are handled by `bdc_probe()`, `bdc_remove()`, `bdc_suspend()`, and `bdc_resume()`.

## Control Flow
Probe maps MMIO, obtains IRQ, optional PHYs, optional clock, initializes PHYs, chooses a 64-bit or 32-bit coherent DMA mask based on capability, resets hardware, allocates DMA pools/status ring/scratchpad, initializes status report handlers, and calls `bdc_udc_init()` to register the gadget. `bdc_mem_init()` programs the status report ring address and size, enables SRR interrupts, configures interrupt coalescing, enables USB2 LPM, masks unwanted microframe wrap reports, and either initializes handlers once or refreshes memory and flags during reinit. Resume reenables the clock and calls `bdc_reinit()`.

## State And Persistence
The core allocates persistent coherent memory for the status report ring and optional scratchpad, creates a DMA pool for endpoint BD tables, allocates the endpoint pointer array based on hardware endpoint counts, and stores PHY/clock pointers. `bdc_reinit()` resets hardware registers while preserving already allocated memory and reinitializing software-visible controller state.

## Dependencies And Integration Points
It integrates with the platform bus and device tree (`brcm,bdc-udc-v2`, `brcm,bdc`), generic PHY framework, optional `sw_usbd` clock, DMA mask APIs, Linux PM sleep callbacks, and the BDC gadget layer in `bdc_udc.c`.

## Risks
Endpoint count is read from hardware extended capability registers; bad register values can size the endpoint array incorrectly. Reinit clears endpoint flags only when gadget speed is unknown, so suspend/resume and disconnect paths depend on subtle speed state. Scratchpad address programming writes the low register from `bdc->scratchpad.sp_dma` directly in one path and split low/high values in another, making 64-bit DMA behavior worth testing. Probe cleanup must keep clock, PHY, UDC, and coherent allocations balanced.

## Test Signals
Probe/remove on matching device tree nodes, DMA mask fallback, suspend/resume, disconnect-triggered reinit, status ring interrupt delivery, scratchpad-required hardware, and `bdc_run()`/`bdc_stop()` timeout logs are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.c

## Purpose
This optional verbose-debug file dumps BDC controller registers, endpoint status registers, the status report ring, and endpoint buffer descriptor lists.

## Important APIs, Types, And Functions
`bdc_dbg_regs()` prints BDC configuration, capability, port, and device context registers. `bdc_dump_epsts()` prints EP status registers 0 through 7. `bdc_dbg_srr()` iterates all status report ring entries and prints their DMA address and four descriptor words. `bdc_dbg_bd_list()` walks each BD table for an endpoint and prints global/local indexes, virtual and DMA addresses, and descriptor words.

## Control Flow
These functions are called from core initialization, endpoint queuing/dequeue paths, and command stop paths when verbose gadget debugging is built. They do not influence transfer flow except for MMIO reads and logging.

## State And Persistence
No state is owned here. The functions observe `struct bdc`, `struct srr`, and `struct bd_list` state plus hardware registers.

## Dependencies And Integration Points
This file depends on `CONFIG_USB_GADGET_VERBOSE` being selected by the Makefile. The fallback inline no-op implementations live in `bdc_dbg.h`, letting the rest of the driver call debug helpers unconditionally.

## Risks
Full descriptor-ring dumps can be noisy and expensive under verbose logging. The functions assume descriptor arrays are allocated and valid at call time; calling after endpoint memory has been freed would be unsafe. One format string for `dvcsb` appears malformed (`0x%x08`), which affects readability but not behavior.

## Test Signals
Build with verbose gadget logging, then inspect logs during probe, endpoint queue/dequeue, stop endpoint, and status report processing. Confirm no debug helper is linked when verbose logging is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.h

## Purpose
This header declares BDC verbose debug helpers and supplies no-op inline replacements when verbose gadget debugging is not built.

## Important APIs, Types, And Functions
With `CONFIG_USB_GADGET_VERBOSE`, it declares `bdc_dbg_bd_list()`, `bdc_dbg_srr()`, `bdc_dbg_regs()`, and `bdc_dump_epsts()`. Otherwise each helper is an empty static inline function.

## Control Flow
The header lets production code call debug helpers without wrapping every call site in preprocessor conditionals. The build either links `bdc_dbg.o` or compiles calls away.

## State And Persistence
No state is stored in this header. Debug implementations only observe controller, endpoint, and ring state.

## Dependencies And Integration Points
It includes `bdc.h` for `struct bdc` and `struct bdc_ep`. It is used by core, command, and endpoint implementation files.

## Risks
Because no-op functions erase calls entirely, debug-only timing or read side effects must not be required for correctness. The header comment describes debug functions correctly here, unlike the command header.

## Test Signals
Compile both with and without `CONFIG_USB_GADGET_VERBOSE`; endpoint/core code should require no additional `#ifdef`s.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.c

## Purpose
This file implements BDC endpoint allocation, buffer descriptor list management, request queueing and completion, EP0 control-transfer handling, transfer status report processing, and USB endpoint operations.

## Important APIs, Types, And Functions
BD list helpers include `ep_bd_list_alloc()`, `ep_bd_list_free()`, `chain_table()`, `bd_needed_req()`, `bd_available_ep()`, `bdi_to_bd()`, `bd_add_to_bdi()`, and `ep_bdlist_eqp_adv()`. Transfer setup is handled by `setup_bd_list_xfr()`, `bdc_queue_xfr()`, `bdc_notify_xfr()`, and `bdc_req_complete()`. Endpoint lifecycle uses `bdc_ep_enable()`, `bdc_ep_disable()`, `bdc_free_ep()`, and `bdc_init_ep()`. EP0 control logic includes `ep0_queue_status_stage()`, `ep0_queue_data_stage()`, `handle_control_request()`, `ep0_handle_status()`, `ep0_handle_feature()`, `bdc_xsf_ep0_setup_recv()`, `bdc_xsf_ep0_data_start()`, `bdc_xsf_ep0_status_start()`, and `ep0_xsf_complete()`. Gadget endpoint ops are implemented by `bdc_gadget_ep_enable()`, `bdc_gadget_ep_disable()`, `bdc_gadget_ep_queue()`, `bdc_gadget_ep_dequeue()`, `bdc_gadget_ep_set_halt()`, and request alloc/free helpers.

## Control Flow
Endpoint enable allocates chained BD tables, configures the hardware endpoint, and marks it enabled. Queuing maps the request, verifies transfer length, calculates needed BDs, writes one or more descriptors, clears stop-buffer-fetch on the first descriptor after a memory barrier, appends the request to the queue, and notifies the controller. Status reports enter `bdc_sr_xsf()`, dispatch by XSF status, complete normal or short transfers through `handle_xsr_succ_status()`, or drive EP0 setup/data/status state transitions. Dequeue stops the endpoint, compares request BD range with the hardware dequeue pointer, and either converts the request start to a chain descriptor or issues a BLA command to skip to the next transfer.

## State And Persistence
Each endpoint owns a BD ring-like list of tables, enqueue/dequeue indexes, endpoint flags (`BDC_EP_ENABLED`, `BDC_EP_STALL`, `BDC_EP_STOP`), an outstanding request list, and an `ignore_next_sr` flag for multi-BD short transfers. EP0 state persists in `bdc->ep0_state`, `setup_pkt`, delayed status flag, ZLP flag, standard-request response buffer, test mode, and device status bits.

## Dependencies And Integration Points
The file depends on command helpers, USB gadget mapping/giveback APIs, USB composite/ch9 request semantics, status reports from `bdc_udc.c`, and register/descriptor definitions in `bdc.h`.

## Risks
BD ring accounting is subtle because chain descriptors are excluded from availability and wrap behavior. Short multi-BD transfers require ignoring an extra status report. EP0 delayed status and ZLP handling interact with control request direction and host `wLength`; mistakes can stall enumeration. `bdc_gadget_ep_queue()` requires non-NULL complete callbacks and buffers, so zero-length non-EP0 requests still need a valid buffer. Dequeue behavior depends on accurate hardware dequeue reads and correct chain descriptor rewriting.

## Test Signals
Run enumeration, GET_STATUS/SET_FEATURE/CLEAR_FEATURE, SET_SEL, test mode, delayed-status gadget functions, zero-length packet cases, short transfers with `short_not_ok`, multi-BD requests above 64 KiB, dequeue of head and non-head requests, endpoint stall/wedge, and isochronous endpoint enable if hardware exposes it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.h

## Purpose
This private header declares endpoint lifecycle functions for the BDC driver.

## Important APIs, Types, And Functions
It declares `bdc_init_ep()` to create software endpoint objects, `bdc_ep_enable()` and `bdc_ep_disable()` to configure or tear down an endpoint, and `bdc_free_ep()` to free all endpoint structures.

## Control Flow
The declarations connect core/gadget initialization in `bdc_udc.c` with the endpoint implementation in `bdc_ep.c`.

## State And Persistence
The header has no state. The declared functions allocate/free endpoint objects, descriptor lists, queue state, and endpoint flags.

## Dependencies And Integration Points
It depends on `struct bdc` and `struct bdc_ep` from `bdc.h`, and on the USB gadget core through the implementation.

## Risks
The file comment incorrectly says it is a debug header. The interface is intentionally narrow; callers should not allocate BD lists or endpoint objects directly.

## Test Signals
Compile tests catch signature drift. Runtime validation comes from UDC init/exit, EP0 enable on startup/connect, and non-EP0 enable/disable through gadget function binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_udc.c

## Purpose
This file provides the BDC USB gadget registration layer, status report ring interrupt handler, upstream port status handling, remote wake behavior, and gadget-level operations.

## Important APIs, Types, And Functions
Status ring flow uses `srr_dqp_index_advc()` and `bdc_udc_interrupt()`. Port events are handled by `bdc_sr_uspc()`, `bdc_uspc_connected()`, `bdc_uspc_disconnected()`, and `handle_link_state_change()`. Remote wake retry logic is in `bdc_func_wake_timer()`. Gadget ops are `bdc_udc_start()`, `bdc_udc_stop()`, `bdc_udc_pullup()`, `bdc_udc_set_selfpowered()`, and `bdc_udc_wakeup()`. UDC lifecycle is `bdc_udc_init()` and `bdc_udc_exit()`.

## Control Flow
`bdc_udc_init()` requests the shared IRQ, initializes endpoints, registers the gadget, preallocates/enables EP0 BD resources, initializes delayed work, and enables global interrupts. The IRQ handler verifies global and SRR pending bits, consumes status report entries until the software dequeue index reaches hardware enqueue, dispatches XSF or USPC reports, writes the updated SRR dequeue pointer, and runs reinit if requested by disconnect/reset handling. USPC reports detect connect, VBUS, reset/disconnect, and link-state changes. On connect, speed is decoded, EP0 maxpacket is set, EP0 is configured in hardware, and gadget state becomes default. On disconnect, EP0 is disabled, gadget driver disconnect is called, speed/state/status flags are reset, and optional reinit is requested.

## State And Persistence
This file maintains gadget speed/state, pullup state, device status bits for suspend/remote wake/function wake, EP0 descriptor state, delayed remote wake work, and SRR dequeue index. It also sets `bdc->gadget_driver` and `gadget.dev.driver` on UDC start/stop.

## Dependencies And Integration Points
It integrates BDC core operations, command functions, endpoint functions, Linux USB gadget registration, IRQ handling, delayed work, and USB device state management. It consumes status reports produced by the BDC hardware and endpoint handlers from `bdc_ep.c`.

## Risks
The interrupt handler holds `bdc->lock` while dispatching reports; handlers must carefully drop/reacquire around gadget callbacks. Remote wake for superspeed relies on repeated Function Wake notifications until a transfer clears `FUNC_WAKE_ISSUED`. `bdc_udc_set_selfpowered()` appears to set the self-powered status bit when `is_self` is false and clear it when true, which is counterintuitive and should be reviewed against hardware/gadget expectations. Disconnect-triggered reinit is deferred until after SRR processing, so failure leaves the controller logged but not recovered.

## Test Signals
Validate connect/disconnect at low/full/high/superspeed as supported, EP0 maxpacket changes, VBUS-only pullup behavior, bus reset, suspend/resume callbacks, remote wake from U3, delayed Function Wake retry cancellation after host traffic, SRR wraparound, and UDC bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Kconfig

## Purpose
This Kconfig entry exposes the Cadence USBHS Device Controller gadget driver as `USB_CDNS2_UDC`.

## Important APIs, Types, And Functions
The symbol is a tristate named "Cadence USBHS Device Controller". It depends on `USB_PCI`, `ACPI`, and `HAS_DMA`. Help text identifies a PCI-based USB peripheral controller supporting full-speed and high-speed USB 2.0 transfers and names the module `cdns2-udc-pci.ko`.

## Control Flow
Selecting this option allows the Makefile to build the PCI/gadget/EP0 pieces and optional trace support. There is no runtime logic in Kconfig itself.

## State And Persistence
The selected value persists in the kernel build configuration.

## Dependencies And Integration Points
This config integrates with the USB PCI and ACPI stacks and requires DMA. It feeds `obj-$(CONFIG_USB_CDNS2_UDC)` in the Makefile.

## Risks
The dependencies limit this driver to PCI/ACPI builds even though the gadget logic is separated from PCI glue. Systems using non-PCI Cadence USBHS integrations would need additional glue and Kconfig changes.

## Test Signals
Build with the option disabled, built-in, and modular; verify `cdns2-udc-pci.ko` is produced for modular builds and that gadget drivers can bind on matching PCI/ACPI hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Makefile

## Purpose
This Makefile defines the build composition for the Cadence USBHS Device Controller PCI gadget driver.

## Important APIs, Types, And Functions
It adds an include path for `cdns2-trace.o` through `CFLAGS_cdns2-trace.o := -I$(src)`. `obj-$(CONFIG_USB_CDNS2_UDC)` builds `cdns2-udc-pci.o`. The main object includes `cdns2-pci.o`, `cdns2-gadget.o`, and `cdns2-ep0.o` when the UDC config is enabled, and adds `cdns2-trace.o` when `CONFIG_TRACING` is enabled.

## Control Flow
The build links PCI probe/runtime glue, generic gadget transfer logic, EP0 handling, and optional tracepoints into one driver object.

## State And Persistence
No runtime state is represented. The file controls build artifacts and tracing availability.

## Dependencies And Integration Points
It depends on the Kconfig symbol in this directory and on the kernel tracing configuration. Trace include path handling is required because `define_trace.h` must locate the local trace header.

## Risks
If trace include paths or object membership drift, trace builds can fail while non-tracing builds pass. The main module name is tied to the PCI glue, so non-PCI reuse would require build restructuring.

## Test Signals
Compile with `CONFIG_USB_CDNS2_UDC=y/m`, with and without `CONFIG_TRACING`, and verify that `cdns2-trace.o` can include its generated trace definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-debug.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-debug.h

## Purpose
This header provides inline string decoders for CDNS2 USB/DMA interrupt state, endpoint transfer rings, and TRBs. It supports trace/debug output without owning runtime behavior.

## Important APIs, Types, And Functions
`cdns2_decode_usb_irq()` decodes USB and external IRQ bits. `cdns2_decode_dma_irq()`, `cdns2_decode_epx_irq()`, and `cdns2_decode_ep0_irq()` decode DMA endpoint interrupt/status bits. `cdns2_raw_ring()` formats a transfer ring including dequeue/enqueue indexes, free TRB count, cycle states, and raw TRB words. `cdns2_trb_type_string()` and `cdns2_decode_trb()` format normal and link TRBs.

## Control Flow
These functions are pure formatting helpers used by trace/debug code. They append into caller-provided buffers with `scnprintf()` and warn if the buffer fills exactly to `size - 1`.

## State And Persistence
No state is stored here. The helpers inspect `struct cdns2_endpoint`, `struct cdns2_ring`, and `struct cdns2_trb` state supplied by callers.

## Dependencies And Integration Points
The header depends on register bit definitions, TRB macros, and `cdns2_trb_virt_to_dma()` from the CDNS2 gadget code/header. It is indirectly tied to `cdns2-trace.h` formatting.

## Risks
The helpers assume `TRBS_PER_SEGMENT <= 40` before dumping every TRB; with the current larger ring size they report that the ring is too big rather than dumping all entries. Buffer truncation detection is approximate. Because this is inline debug code, macro/type changes in `cdns2-gadget.h` can break trace builds.

## Test Signals
Enable tracing/debug formatting and check decoded USB reset/setup/suspend/LPM, endpoint IOC/ISP/TRBERR/DESCMIS/ISOERR, and TRB text for normal and link descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-ep0.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-ep0.c

## Purpose
This file implements endpoint zero for the Cadence USBHS gadget driver: setup packet handling, standard control requests, EP0 DMA/TRB submission, status stages, stalls, delayed status completion, and EP0 endpoint operations.

## Important APIs, Types, And Functions
The EP0 descriptor is `cdns2_gadget_ep0_desc`. Helpers include `cdns2_w_index_to_ep_index()`, `cdns2_check_new_setup()`, `cdns2_ep0_enqueue()`, `cdns2_ep0_delegate_req()`, `cdns2_ep0_stall()`, and `cdns2_status_stage()`. Standard request handlers include `cdns2_req_ep0_set_configuration()`, `cdns2_req_ep0_set_address()`, `cdns2_req_ep0_handle_status()`, and feature helpers for device/interface/endpoint recipients. Public internal entry points are `cdns2_handle_setup_packet()`, `cdns2_handle_ep0_interrupt()`, `cdns2_pending_setup_status_handler()`, `cdns2_ep0_config()`, and `cdns2_init_ep0()`. EP0 ops are queue/dequeue through `cdns2_gadget_ep0_ops`.

## Control Flow
On SUDAV, `cdns2_handle_setup_packet()` acknowledges setup-change state, reads eight setup bytes, drops stale reads if the setup buffer changed mid-read, clears EP0 stall state, cancels any pending EP0 request, chooses data or status stage, sets transfer direction, reconciles auto-applied SET_ADDRESS from the function-address register, handles standard requests locally when possible, delegates other requests to the gadget driver, then either stalls or sends status. EP0 queued data requests are DMA-mapped, put on the pending list, optionally expanded with a ZLP TRB, and started by `cdns2_ep0_enqueue()`. EP0 DMA interrupts call `cdns2_transfer_completed()` and then status stage.

## State And Persistence
EP0 state is shared through `pdev->setup`, `pdev->ep0_stage`, `pdev->dev_address`, `pdev->may_wakeup`, `pdev->pending_status_request`, `status_completion_no_call`, `ep0_preq`, and `eps[0].pending_list`. The EP0 transfer ring uses the first two TRBs for data and optional ZLP.

## Dependencies And Integration Points
The file integrates with the generic CDNS2 gadget helpers (`cdns2_select_ep()`, request allocation/free, giveback, halt), USB composite/ch9 semantics, DMA mapping by device, tracepoints, and controller registers defined in `cdns2-gadget.h`.

## Risks
SET_ADDRESS is acknowledged automatically by hardware, so the driver must infer missed address changes from `fnaddr`. Status-stage completion has no interrupt and is completed asynchronously via `system_freezable_wq`, which is a race-sensitive integration point. Only one EP0 data request is allowed at a time; a new setup cancels pending work. The endpoint feature handler maps `wIndex` directly into `pdev->eps[]`, so invalid endpoint indexes rely on upstream request validity.

## Test Signals
Test enumeration, SET_ADDRESS, SET_CONFIGURATION with delayed status, GET_STATUS for device/interface/endpoint, remote wake enable/disable, endpoint halt/clear-halt with wedge, test mode requests, ZLP on EP0 IN, new setup overriding pending data, and EP0 stall recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-ep0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-gadget.c

## Purpose
This file implements the main Cadence USBHS gadget controller logic for non-control endpoints, transfer rings, DMA interrupts, gadget operations, endpoint matching/configuration, suspend/resume, and gadget initialization/removal.

## Important APIs, Types, And Functions
Core helpers include register bit setters, `cdns2_select_ep()`, `cdns2_trb_virt_to_dma()`, `cdns2_next_preq()`, TR segment allocation/free, and ring index advancement. Transfer preparation is handled by `cdns2_prepare_ring()`, `cdns2_count_trbs()`, `cdns2_count_sg_trbs()`, `cdsn2_isoc_burst_opt()`, `cdns2_ep_tx_isoc()`, `cdns2_ep_tx_bulk()`, `cdns2_ep_run_transfer()`, and `cdns2_start_all_request()`. Completion uses `cdns2_trb_handled()`, `cdns2_transfer_completed()`, `cdns2_gadget_giveback()`, and isochronous skip handling. Endpoint ops are enable/disable/queue/dequeue/set_halt/set_wedge and request alloc/free. Gadget ops include get_frame, wakeup, set_selfpowered, pullup, UDC start/stop, and match_ep. Public lifecycle functions are `cdns2_gadget_init()`, `cdns2_gadget_remove()`, `cdns2_gadget_suspend()`, and `cdns2_gadget_resume()`.

## Control Flow
`cdns2_gadget_init()` sets a 32-bit DMA mask, resumes the device, precomputes isochronous burst optimization, initializes the gadget, allocates endpoint DMA pools and EP0 setup/ZLP buffers, registers the gadget, and requests a shared threaded IRQ. Queueing maps a request, places it on the deferred list, starts all possible requests if the endpoint is not stalled, writes TRBs, uses a memory barrier before toggling the first TRB cycle bit, and rings the DMA doorbell. Interrupt handling has a hard IRQ that masks sources and wakes a thread, then the thread handles USB reset/suspend/LPM/setup and DMA endpoint bits. Completion advances ring dequeue state, updates request actual bytes, gives back completed requests, and starts deferred work.

## State And Persistence
Persistent state lives in `struct cdns2_device` and per-endpoint objects: transfer rings, pending/deferred request lists, endpoint state bits, buffering allocation, isochronous skip flag, and WA1 stale-address workaround state. The driver also stores on-chip TX/RX buffer sizes, available endpoint bitmap, selected endpoint, speed, wake/self-powered flags, DMA pool, ZLP buffer, and EP0 setup buffer.

## Dependencies And Integration Points
The file depends on CDNS2 register definitions and structs from `cdns2-gadget.h`, EP0 helpers from `cdns2-ep0.c`, tracepoints, Linux DMA pools/mapping, runtime PM, device properties, IRQ threading, and the USB gadget core.

## Risks
The documented WA1 stale-TRB-address workaround is central; incorrect cycle-bit restoration or doorbell timing can DMA from stale buffers. Ring wrap and link TRB handling are complex, especially for small rings, IN bulk extra link TRBs, and isochronous reserved TRBs. Isochronous transfer code has several hardware-specific workarounds for 4 KiB boundaries, packet loss, and first-packet corruption. `cdns2_gadget_set_selfpowered()` writes `pdev->is_selfpowered`, while EP0 GET_STATUS reads `pdev->gadget.is_selfpowered`; that mismatch should be reviewed. Interrupt masking/unmasking is shared-IRQ sensitive and intentionally avoids `IRQF_ONESHOT`.

## Test Signals
Validate full/high-speed enumeration, bulk/interrupt IN and OUT, scatter-gather, request ZLP insertion, dequeue of pending/deferred requests, halt/clear-halt/wedge, ring wrap, TRBERR/DESCMIS recovery, isochronous IN/OUT including missed packets, suspend/resume/LPM/wakeup, runtime PM remove paths, and tracing of DMA endpoint status and TRB completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-gadget.c -->
