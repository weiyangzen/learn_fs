# Research: subset-b-005505

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/r8a66597-udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/r8a66597-udc.c

## Purpose

This file implements the Linux USB gadget UDC driver for the Renesas R8A66597 controller. It adapts the controller's endpoint pipes, FIFO windows, VBUS detection, optional SUDMAC DMA channel, and USB control-transfer state into the `usb_gadget` and `usb_ep` APIs used by gadget function/composite drivers. It is a high/full-speed peripheral controller driver, registered as platform driver `r8a66597_udc`.

## Important APIs, Types, and Functions

- `r8a66597_ep_ops` implements endpoint operations: `enable`, `disable`, `alloc_request`, `free_request`, `queue`, `dequeue`, `set_halt`, `set_wedge`, and `fifo_flush`.
- `r8a66597_gadget_ops` implements gadget operations: `udc_start`, `udc_stop`, `pullup`, `get_frame`, and `set_selfpowered`.
- `r8a66597_probe()` maps MMIO, requests IRQ, enables the optional on-chip clock, maps optional SUDMAC registers, initializes endpoint objects, allocates the internal EP0 request, and registers with `usb_add_gadget_udc()`.
- `r8a66597_irq()` is the top-level interrupt handler. It dispatches VBUS, device-state, BRDY, BEMP, control-stage, and optional SUDMAC completion handling while preserving the selected CFIFO pipe.
- Pipe setup is owned by `alloc_pipe_config()`, `pipe_buffer_setting()`, `r8a66597_ep_setting()`, `pipe_initialize()`, and `free_pipe_config()`.
- Transfer setup and completion are split across `start_packet_write()`, `start_packet_read()`, `start_ep0()`, `irq_packet_write()`, `irq_packet_read()`, `irq_ep0_write()`, `irq_pipe_ready()`, `irq_pipe_empty()`, `transfer_complete()`, and the SUDMAC helpers.
- Standard control requests partly handled in hardware/driver are implemented by `setup_packet()`, `get_status()`, `clear_feature()`, `set_feature()`, `irq_control_stage()`, and `control_end()`.

## Control Flow

Probe constructs a `struct r8a66597` instance and endpoint table, but the controller is held disabled until a gadget driver binds through `r8a66597_start()`. Start validates the gadget driver, stores it in `r8a66597->driver`, initializes the controller registers, enables VBUS interrupting, and if VBUS is already present starts the sampling timer. VBUS changes are debounced by `r8a66597_timer()` for `R8A66597_MAX_SAMPLING` samples before calling `r8a66597_usb_connect()` or `r8a66597_usb_disconnect()`.

Endpoint enable allocates one hardware pipe according to endpoint type. Bulk endpoints consume bulk pipes first and may fall back to isochronous pipe numbers; interrupt and isochronous endpoints use their dedicated ranges. `pipe_buffer_setting()` programs `PIPECFG`, `PIPEBUF`, `PIPEMAXP`, and `PIPEPERI`, and `r8a66597_ep_setting()` binds the logical endpoint to a pipe number plus FIFO/control register addresses.

Requests are queued by `r8a66597_queue()`. The first request on an idle queue starts immediately: EP0 dispatches through `start_ep0()` based on control-transfer stage bits, while non-control endpoints use `start_packet()` and endpoint direction to select IN/OUT. Transfers are mostly interrupt-driven by BRDY/BEMP. PIO IN writes packets into FIFO and uses BEMP to detect final emptying; PIO OUT reads received bytes from FIFO and completes on short packet, zero packet, or requested length. When SUDMAC is available and a bulk pipe can claim the single shared channel, `sudmac_start()` programs channel 0, and `r8a66597_sudmac_irq()`/`sudmac_finish()` update `req.actual` before completion or BEMP follow-up.

Control requests are split between local standard handling and gadget-driver delegation. GET_STATUS uses an internal EP0 request and `ep0_data`; CLEAR_FEATURE and SET_FEATURE manipulate endpoint stall/toggle state and test mode; unknown or class/vendor requests are passed to `driver->setup()`. Completion paths drop the spinlock before `usb_gadget_giveback_request()` or gadget callbacks, then reacquire it.

## State and Persistence Behavior

All runtime state is in memory in `struct r8a66597`. Persistent hardware state consists only of controller registers while the device is bound and powered. Key state fields include the endpoint queue lists, `pipenum2ep[]`, `epaddr2ep[]`, pipe resource counters (`bulk`, `interrupt`, `isochronous`, `num_dma`), optional shared `dma`, VBUS debounce fields (`old_vbus`, `scount`), `old_dvsq`, `device_status`, `ep0_req`, and `ep0_data`.

The driver uses a single spinlock for queue and register sequencing. Some functions intentionally release the lock around gadget-driver callbacks and request giveback. Endpoint halt state is tracked with `busy` and `wedge`, and data toggle is read/restored when BFRE mode changes. DMA state is short-lived: `sudmac_alloc_channel()` maps the request and switches the endpoint FIFO to D0FIFO; `sudmac_free_channel()` unmaps and restores CFIFO.

## Dependencies and Integration Points

The driver depends on the USB gadget core, Linux platform device resources, IRQs, MMIO helpers, optional clocks, DMA mapping, and Renesas R8A66597 register definitions from `linux/usb/r8a66597.h` plus the local header. Platform data is required for important controller differences such as on-chip vs external bus width, endian mode, crystal frequency, bus wait, SUDMAC availability, and WR0/WR1 wiring.

Integration points are `usb_add_gadget_udc()`/`usb_del_gadget_udc()`, gadget-driver callbacks (`setup`, `disconnect`), `usb_gadget_udc_reset()`, `usb_ep_clear_halt()`, request DMA mapping helpers, and platform driver binding under alias `platform:r8a66597_udc`.

## Risks and Edge Cases

- `get_request_from_ep()` assumes the endpoint queue is non-empty; interrupt/status paths rely on enable bits and queue discipline to make that true.
- EP0 uses a single internal request/data buffer for GET_STATUS. The source comment notes the risk if the path is reentered before the internal transfer completes.
- Several waits are busy loops around FIFO readiness or pipe selection. Timeouts log errors but not every caller can fully recover the hardware state.
- SUDMAC support is limited to one shared channel and bulk pipes. Concurrent bulk endpoints fall back or race through the `used` flag under the driver lock.
- `r8a66597_disable()` drains queued requests by repeatedly completing the queue head while reacquiring the lock; request completion callbacks that queue new work are a concurrency-sensitive path.
- Platform-data correctness is critical. Wrong bus width, endian, clock, or SUDMAC settings will cause FIFO corruption, timeout, or failed enumeration.

## Test Signals

Useful validation includes probe/remove with and without on-chip clock and SUDMAC resources, binding common gadget functions through configfs, USB high/full-speed enumeration, SET_ADDRESS/GET_STATUS/CLEAR_FEATURE/SET_FEATURE control requests, endpoint stall/wedge/clear behavior, short packet and zero-length packet transfers, bulk IN/OUT under PIO and DMA fallback, disconnect/reconnect debounce, suspend/reset paths, and forced error testing for FIFO timeout or DMA map failure. Kernel logs should be checked for pipe allocation errors, FIFO readiness errors, "USB speed unknown", and SUDMAC completion anomalies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/r8a66597-udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/r8a66597-udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/r8a66597-udc.h

## Purpose

This header defines the private data model and low-level register/FIFO helpers for the R8A66597 USB gadget driver. It is the bridge between the controller-specific register map from `linux/usb/r8a66597.h` and the implementation in `r8a66597-udc.c`.

## Important APIs, Types, and Macros

- Pipe capacity and numbering constants define the controller layout: `R8A66597_MAX_NUM_PIPE`, bulk/isoc/interrupt counts, base pipe numbers, and buffer-number limits.
- `is_bulk_pipe()`, `is_interrupt_pipe()`, and `is_isoc_pipe()` classify hardware pipe numbers and are used by allocation/release logic.
- `struct r8a66597_pipe_info` is a temporary pipe-programming descriptor carrying pipe number, endpoint number, maxpacket, transfer type, interval, and direction.
- `struct r8a66597_request` wraps `struct usb_request` with a queue node.
- `struct r8a66597_ep` wraps `struct usb_ep` with controller backpointer, FIFO/control register offsets, pipe number, transfer type, queue, DMA pointer, and flags for busy, wedge, internal EP0 completion, and DMA use.
- `struct r8a66597_dma` represents the single SUDMAC channel state with `used` and direction.
- `struct r8a66597` is the controller object: MMIO bases, clock, platform data, gadget and driver pointers, endpoint arrays/maps, timer, EP0 internal request storage, pipe resource counters, device status, VBUS sampling state, and IRQ polarity.
- Register helper APIs include `r8a66597_read()`, `r8a66597_write()`, `r8a66597_mdfy()`, `r8a66597_bclr()`, `r8a66597_bset()`, `r8a66597_read_fifo()`, `r8a66597_write_fifo()`, and SUDMAC 32-bit accessors.

## Control Flow Support

The inline helpers are designed so the C file can express state transitions as pipe/FIFO operations rather than raw bus accesses. `r8a66597_read_fifo()` and `r8a66597_write_fifo()` select 32-bit accesses for on-chip controllers and 16-bit accesses for external controllers when alignment allows, then handle residual bytes manually. `get_xtal_from_pdata()` translates platform-data crystal settings into controller bitfields for initialization. `get_pipectr_addr()`, `get_pipetre_addr()`, and `get_pipetrn_addr()` compute per-pipe register addresses. IRQ convenience macros map pipe numbers to BRDY/BEMP/NRDY enable-bit operations implemented in the C file.

## State and Persistence Behavior

The header does not create global state but defines all driver-owned in-memory state. Queue lifetime is per endpoint and request. Hardware register state is accessed directly through the MMIO base in `struct r8a66597`, so callers must hold the implementation lock where concurrent interrupt/process-context access is possible. FIFO helpers update no software counters themselves; actual transfer progress is tracked by `usb_request.actual` in the C file.

## Dependencies and Integration Points

The header depends on Linux clock support, USB gadget types, platform data from `linux/usb/r8a66597.h`, and I/O accessors. It is tightly coupled to the Renesas register definitions and to the implementation's `enable_pipe_irq()`/`disable_pipe_irq()` functions via macros at the end of the file.

## Risks and Edge Cases

- FIFO residual byte handling depends on controller endian and bus-width behavior. Incorrect `pdata->on_chip`, `endian`, or `wr0_shorted_to_wr1` values can corrupt transfers.
- `r8a66597_write_fifo()` toggles MBW behavior for the `wr0_shorted_to_wr1` quirk; any future changes must preserve the hardware requirement around byte writes.
- The pipe classification macros encode fixed resource ranges; adding a controller variant with different pipe layout would require coordinated changes in allocation logic.
- The SUDMAC accessor helpers assume `sudmac_reg` is valid when called; the C file gates usage with platform data.

## Test Signals

Header-level behavior is validated indirectly by transfer tests across aligned and unaligned buffers, on-chip and external controller configurations, little/big-endian FIFO behavior, SUDMAC-enabled and disabled paths, endpoint type allocation, and pipe IRQ enable/disable behavior. Static build coverage should catch structure/member coupling with `r8a66597-udc.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/r8a66597-udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/renesas_usb3.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/renesas_usb3.c

## Purpose

This file implements the Renesas USB3.0 peripheral controller gadget driver. It supports SuperSpeed/HighSpeed/FullSpeed gadget operation, EP0 standard request handling, non-control pipe FIFO and PRD-based DMA transfers, extcon notifications, USB role switching, debugfs controls, runtime PM, and R-Car/RZ SoC variations including RZ/V2M dual-role reset integration.

## Important APIs, Types, and Functions

- `struct renesas_usb3` is the controller state: MMIO bases, optional separate DRD registers, reset/PHY handles, gadget/driver pointers, extcon and role-switch objects, host companion device, endpoint array, DMA setting areas, lock, EP0 buffer/request, connection role state, VBUS workaround flags, and SoC feature flags.
- `struct renesas_usb3_ep` wraps `usb_ep` with pipe number, endpoint name, queue, RAM map value, direction, halt/wedge, started flag, and active DMA setting.
- `struct renesas_usb3_request` wraps `usb_request`; `struct renesas_usb3_dma` and `struct renesas_usb3_prd` model hardware PRD DMA resources.
- `renesas_usb3_ep_ops` and `renesas_usb3_gadget_ops` expose the endpoint and gadget API to the USB gadget core.
- Controller lifecycle is handled by `renesas_usb3_probe()`, `renesas_usb3_remove()`, `renesas_usb3_start()`, `renesas_usb3_stop()`, suspend/resume PM ops, and SoC match data in `usb3_of_match`.
- EP0 and standard requests are handled by `usb3_irq_epc_pipe0_setup()`, `usb3_handle_standard_request()`, `usb3_std_req_*()`, `usb3_pipe0_internal_xfer()`, `usb3_start_pipe0()`, and `usb3_p0_xfer()`.
- Pipe-N data flow is handled by `usb3_enable_pipe_n()`, `usb3_start_pipen()`, `usb3_irq_epc_pipen_*()`, `usb3_request_done_pipen()`, and FIFO helpers `usb3_write_pipe()`/`usb3_read_pipe()`.
- DMA flow is handled by `usb3_dma_get_setting_area()`, `usb3_dma_fill_prd()`, `usb3_dma_kick_prd()`, `usb3_dma_try_start()`, `usb3_dma_try_stop()`, and `usb3_irq_dma_int()`.
- Role and cable state are handled by `usb3_check_id()`, `usb3_check_vbus()`, `usb3_mode_config()`, `renesas_usb3_role_switch_set()`, `handle_role_switch_states()`, and `handle_ext_role_switch_states()`.

## Control Flow

Probe allocates the controller, maps registers, initializes endpoint objects from SoC RAM sizing, requests the main IRQ, optionally requests the RZ/V2M DRD IRQ, registers extcon, allocates an internal EP0 request and PRD tables, obtains optional PHY/reset resources, registers the gadget UDC, creates a `role` sysfs attribute, optionally registers a USB role switch, and creates debugfs state.

When a gadget driver binds, `renesas_usb3_start()` rejects incompatible drivers and RZ/V2M A-device conflicts, initializes the PHY and runtime PM, performs an RZ/V2M peripheral reset when needed, and calls `renesas_usb3_init_controller()`. Initialization enables AXI/EPC interrupts, configures pipe data interface behavior, enables OTG ID interrupts, checks ID and VBUS, then starts connection if role/VBUS permit. Stop reverses softconnect, speed, reset, controller, PHY, and runtime-PM state.

The main IRQ first reads AXI interrupt status. DMA interrupts are dispatched to `usb3_irq_dma()`, while EPC interrupts are dispatched to `usb3_irq_epc()`. EPC interrupt group 1 handles link events, USB2 resume/suspend/reset, USB3 hot/warm reset, speed detection, and VBUS. Interrupt group 2 dispatches individual pipe interrupts: pipe 0 for setup/data/status and pipe N for FIFO transfer readiness or last-transfer events. Non-RZ/V2M OTG ID interrupts are polled through the same EPC path; RZ/V2M uses a separate DRD IRQ.

EP0 setup reads two setup data registers, updates direction, lets local standard handlers process address/status/feature/set-sel/configuration where supported, and delegates unhandled requests to `driver->setup()`. Pipe 0 data movement uses P0 register response fields to drive control read/write/no-data/status phases. Status-end interrupt gives back the EP0 request and applies pending USB2 test mode.

Pipe-N queueing adds the request and starts only the queue head if the endpoint is not halted or already active. IN PIO writes maxpacket chunks and waits for BFRDY/LSTTR; OUT PIO reads received length and completes on full request or short/zero condition. If module parameter `use_dma` is true and the request is suitable, the driver claims one of four setting areas, maps the request, fills PRDs capped at 32768 bytes per entry, enables DMA, and completes through DMA interrupt status.

Role switching is layered over direct DRD mode bits or `usb_role_switch`. ID/VBUS changes update extcon state and schedule work. Connector-managed role switching tracks `connection_state` and attaches/releases the host companion device while disconnecting gadget state as needed. RZ/V2M uses parent `rzv2m_usb3drd_reset()` for host/peripheral reset sequencing.

## State and Persistence Behavior

The driver stores all persistent runtime state in `struct renesas_usb3`, protected by `usb3->lock` for endpoint queues and hardware sequencing. Endpoint state includes `halt`, `wedge`, `started`, direction, RAM mapping, and active DMA setting. Controller state includes `softconnect`, `forced_b_device`, `start_to_connect`, `connection_state`, extcon booleans, role switch target, `disabled_count` used for USB3-to-USB2 fallback, and current test mode.

Hardware state is reinitialized on controller start, disconnect, reset, suspend/resume, hot reset, warm reset, and bus reset. PRD tables are coherent DMA allocations kept for the device lifetime. EP0 uses one internal request and an 8-byte buffer for local standard replies.

## Dependencies and Integration Points

The file integrates with the USB gadget core, USB role-switch framework, extcon, debugfs, runtime PM, PHY framework, reset controls, Open Firmware match data, DMA coherent allocation/mapping, and optional host companion device attachment. It also imports `rzv2m_usb3drd_reset()` from the RZ/V2M DRD glue driver. User-visible controls include the `role` sysfs attribute and debugfs `b_device`.

## Risks and Edge Cases

- DMA PRD traversal contains bounded entry logic and request size limits; large or unsupported maxpacket requests fall back, but errors in PRD end conditions could truncate or overrun transfers.
- `usb3_irq_dma_int()` dereferences `usb3_ep->dma`; it relies on DMA interrupts only being enabled for endpoints with an active DMA setting.
- Role switching can sleep through host `device_attach()`/`device_release_driver()` and is split across locks/workqueues; ordering with gadget disconnect and RZ/V2M resets is delicate.
- The VBUS workaround path intentionally skips normal VBUS checks and uses debugfs/forced B-device flags, so testing must cover SoC variants separately.
- EP0 local standard handling only covers selected requests; request delegation and stall behavior must match USB chapter 9 expectations.
- `renesas_usb3_pullup()` only updates `softconnect`; actual connection is gated by later VBUS/role/controller paths.

## Test Signals

Validation should cover UDC probe/remove for each compatible string, PRD allocation failure, configfs gadget enumeration at SuperSpeed/HighSpeed/FullSpeed, EP0 standard requests including SET_ADDRESS, GET_STATUS, U1/U2 feature toggles, SET_SEL, SET_CONFIGURATION, stalls and clear-halt on endpoints, PIO and DMA bulk/interrupt traffic, module parameter `use_dma=0/1`, suspend/resume, hot/warm/bus reset, role switch host/device/none, extcon state updates, RZ/V2M parent reset interactions, debugfs `b_device`, and sysfs `role`. Useful failure signals include link fallback via `disabled_count`, unexpected `-EBUSY` waits, DMA error PRD bits, and host attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/renesas_usb3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/renesas_usbf.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/renesas_usbf.c

## Purpose

This file implements the Renesas USBF USB Function gadget UDC driver, targeting the `renesas,rzn1-usbf` compatible. It exposes up to 16 function endpoints, handles EP0 chapter-9 control transfers with a software state machine, supports PIO and endpoint DMA transfers, processes separate EPC and AHB/EPC bridge interrupts, and registers with the Linux USB gadget core as `usbf_renesas`.

## Important APIs, Types, and Functions

- `struct usbf_udc` is the controller object: gadget, driver pointer, device, MMIO base, spinlock, remote-wakeup/suspend flags, endpoint array, EP0 state, canned setup reply request, and EP0 buffer.
- `struct usbf_ep` wraps `usb_ep` with endpoint id, queue, direction, disabled/wedged/delayed-status flags, per-endpoint register bases, optional DMA register base, last status, processing guard, and bridge-DMA completion callback.
- `struct usbf_req` wraps `usb_request` with queue node, zero-packet state, DMA mapping state, transfer state (`xfer_step`), and DMA transfer size.
- `usbf_ep_info[]` encodes the fixed endpoint capabilities, internal RAM base addresses, buffer type, and maxpacket limits expected from the SoC datasheet.
- `usbf_ep_ops` implements endpoint methods; `usbf_gadget_ops` implements gadget methods including pullup and remote wakeup.
- EP0 flow is driven by `usbf_ep0_interrupt()`, `usbf_handle_ep0_setup()`, `usbf_handle_ep0_data_status()`, status-start helpers, local standard request handlers, and `usbf_ep0_pio_in()`/`usbf_ep0_pio_out()`.
- Endpoint-N data flow is driven by `usbf_epn_start_queue()`, `usbf_ep_process_queue()`, `usbf_epn_process_queue()`, PIO helpers, DMA helpers, and `usbf_epn_interrupt()`.
- Interrupt top halves are `usbf_epc_irq()` for USB/EPC events and `usbf_ahb_epc_irq()` for VBUS and bridge DMA completion.

## Control Flow

Probe maps registers, enables runtime PM, releases EPC reset, initializes gadget metadata, endpoint descriptors, endpoint register bases, optional DMA bases, and the setup reply request. It validates hardware endpoint type/buffer mode against `usbf_ep_info[]` via `usbf_epn_check()`, requests two IRQs, configures AHB burst and USB interrupt selection, and registers the gadget UDC.

`usbf_udc_start()` stores the gadget driver and enables VBUS bridge interrupts. Pullup is the actual attach/detach control: `usbf_attach()` enables D+ pullup and reset/speed/resume/suspend interrupts while leaving EP0 to be enabled by USB reset; `usbf_detach()` disables interrupts, resets active endpoints, and disconnects the function PHY. VBUS changes are reported from the AHB/EPC IRQ through `usb_udc_vbus_handler()` and gadget state changes.

On USB reset, `usbf_reset()` nukes active endpoints, updates full/high-speed state, clears remote wakeup, enables EP0, and calls `usb_gadget_udc_reset()`. EP0 interrupts run a state machine with states for idle, IN/OUT data phases, IN/OUT status start, status transfer, and status end. SETUP packets are read from two setup registers; standard GET_STATUS, CLEAR_FEATURE, SET_FEATURE, SET_ADDRESS, and SET_CONFIGURATION are handled locally when valid, while other requests delegate to the gadget driver. Delayed status is supported through `USB_GADGET_DELAYED_STATUS`.

Endpoint queueing is locked by `udc->lock`. EP0 queueing is constrained by the current control state and direction. Non-control endpoints reset request transfer state and, if the queue was empty, arm the hardware immediately. IN endpoints push PIO or DMA data right away; OUT endpoints clear NAK and enable OUT/OUT_NULL interrupts when a request is available.

PIO transfer functions process one maxpacket at a time and complete on requested length, short packet, zero packet, overflow, or explicit zero-length packet handling. DMA IN and DMA OUT are multi-step state machines in `req->xfer_step`. DMA IN maps aligned buffers, programs packet counts and last-packet size, waits for bridge-level completion before enabling USBF IN_END, then handles residues or optional ZLP. DMA OUT handles short packets separately, tracks bridge completion ordering, handles null packets, adjusts `actual` based on remaining DMA count, and may chain a final short DMA or residue read.

## State and Persistence Behavior

Software state is in memory only. Endpoint queue state is held in `usbf_ep.queue`, request transfer progress in `usb_request.actual`, and DMA substate in `usbf_req.xfer_step`, `dma_size`, and `is_mapped`. EP0 protocol state is explicit in `udc->ep0state`; remote wakeup and suspend state are tracked by booleans.

The hardware maintains FIFO contents, endpoint control/status, endpoint RAM mapping, DMA counters, USB address, and interrupt masks. The driver resets or flushes hardware state on detach, bus reset, endpoint disable, dequeue of active requests, stall clear, and transfer error. DMA mapping is carefully unwound in `usbf_ep_req_done()` through `usbf_epn_dma_abort()` if a request completes while still mapped.

## Dependencies and Integration Points

The driver depends on platform MMIO/IRQ resources, runtime PM, USB gadget/composite core, USB role header types, DMA mapping, atomic polling helpers, and Linux list/spinlock primitives. It uses `usb_add_gadget_udc()`, `usb_del_gadget_udc()`, `usb_udc_vbus_handler()`, `usb_gadget_udc_reset()`, `usb_gadget_set_state()`, request giveback, and gadget-driver callbacks for setup/suspend/resume. Its OF binding is `renesas,rzn1-usbf`.

## Risks and Edge Cases

- DMA requires 32-bit aligned request buffers; unaligned buffers intentionally fall back to PIO, but mixed aligned/residue paths need coverage.
- DMA OUT completion has subtle ordering between USBF endpoint interrupts and AHB bridge interrupts. The `bridge_on_dma_end` callback is central to avoiding premature completion.
- `usbf_ep_free_request()` unconditionally removes the request from its list under lock; callers must not free active requests outside normal gadget discipline.
- EP0 dequeue forces stall and nukes pending control requests because partial EP0 transactions cannot remain coherent.
- The driver intentionally avoids setting the USB suspend bit due to shared clock side effects; this is a hardware-integration tradeoff that may matter for power tests.
- Endpoint capabilities are fixed by `usbf_ep_info[]` and checked against hardware registers. Any new variant with different endpoint layout needs a new table or match data.

## Test Signals

Tests should include probe with endpoint availability/DMA availability variations, attach/detach through pullup, VBUS transitions, bus reset and speed changes, EP0 standard request matrix, delayed status from gadget functions, SET_CONFIGURATION state transitions, remote wakeup enable/disable and wakeup attempts, endpoint halt/wedge/clear behavior, EP0 and EPN dequeue paths, PIO transfer with short/ZLP/overflow cases, DMA IN/OUT aligned buffers, unaligned DMA fallback, bridge DMA interrupt ordering, suspend/resume callbacks, and remove/runtime-PM cleanup. Kernel logs should be checked for endpoint capability mismatches, bridge timeouts, flush timeouts, request queue while disabled, and "no request available" warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/renesas_usbf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/rzv2m_usb3drd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/rzv2m_usb3drd.c

## Purpose

This file is a small Renesas RZ/V2M USB3 dual-role glue driver. It owns the parent DRD register block and reset control, populates child platform devices, and exports `rzv2m_usb3drd_reset()` so child host/peripheral drivers can switch reset state and peripheral/host mode consistently.

## Important APIs, Types, and Functions

- `rzv2m_usb3drd_reset(struct device *dev, bool host)` is exported GPL-only and is the main integration API. It looks up the parent `struct rzv2m_usb3drd` from driver data and manipulates `USB_PERI_DRD_CON`.
- `rzv2m_usb3drd_set_bit()` and `rzv2m_usb3drd_clear_bit()` are read-modify-write helpers for the DRD register block.
- `rzv2m_usb3drd_probe()` allocates state, records the DRD IRQ named `"drd"`, maps the register resource, obtains/deasserts the reset control, enables runtime PM, and calls `of_platform_populate()` for child devices.
- `rzv2m_usb3drd_remove()` depopulates children, drops runtime PM, disables PM, and asserts reset.
- OF match data binds `renesas,rzv2m-usb3drd`; the platform driver name is `rzv2m-usb3drd`.

## Control Flow

Probe is parent-first. It maps the shared DRD registers and stores them in driver data before child nodes are populated, which lets children retrieve the parent state. The reset line is deasserted and runtime PM is resumed before `of_platform_populate()` creates host/peripheral children.

The exported reset helper switches between host and peripheral. In host mode it clears `PERI_CON`, clears host reset, and asserts peripheral reset. In peripheral mode it sets `PERI_CON`, asserts host reset, and clears peripheral reset. Remove reverses the probe sequence by depopulating children, dropping PM, disabling PM, and asserting the DRD reset.

## State and Persistence Behavior

The driver's state is the parent `struct rzv2m_usb3drd`, defined in the public RZ/V2M USB3DRD header. This file uses its `dev`, `reg`, `drd_irq`, and `drd_rstc` fields. There is no persistent storage. Hardware state persists in the DRD control register and reset line until changed by this driver or a child invoking `rzv2m_usb3drd_reset()`.

## Dependencies and Integration Points

The file depends on platform resources, OF child population, reset controls, runtime PM, MMIO helpers, and `linux/usb/rzv2m_usb3drd.h`. It is directly integrated by `renesas_usb3.c` for RZ/V2M peripheral reset and DRD IRQ/register sharing. Host-side child drivers can use the same parent device and exported reset helper.

## Risks and Edge Cases

- The helper assumes `dev_get_drvdata(dev)` returns a valid parent DRD object; callers must pass the parent device, not an arbitrary child.
- Register updates are unlocked read-modify-write operations. If host and peripheral children call the exported helper concurrently, mode bits could race unless higher-level role switching serializes them.
- Probe obtains the `"drd"` IRQ but does not request it itself; children are expected to consume it from parent state.
- Error paths must keep reset and runtime PM balanced; `err_pm` and `err_rst` do this, but future changes around child population need the same ordering.

## Test Signals

Validation should cover successful parent probe with child population, missing IRQ/resource/reset error paths, runtime PM resume failure, child probe access to parent `reg` and `drd_irq`, host-to-peripheral and peripheral-to-host reset calls, remove cleanup order, and integration with RZ/V2M `renesas_usb3` role switching. Hardware-level tests should verify `PERI_CON`, `HOST_RST`, and `PERI_RST` bit transitions for both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/rzv2m_usb3drd.c -->
