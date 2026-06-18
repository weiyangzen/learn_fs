# sources/distributed-fs/ceph-client/drivers/usb/dwc2/gadget.c

## Purpose

`gadget.c` is the DWC2 USB device-side controller driver. It adapts Synopsys DWC_otg/DWC2 device-mode hardware to the Linux USB gadget framework by exposing `usb_gadget_ops` and `usb_ep_ops`, managing endpoint allocation/configuration, programming endpoint/FIFO/DMA registers, handling EP0 control transfers, dispatching device-mode interrupts, and preserving device register state across suspend, hibernation, partial power down, and clock gating.

The file is not Ceph-specific despite living in this source snapshot under `sources/distributed-fs/ceph-client`; it is a kernel USB controller driver and integrates with the common DWC2 core through `core.h` and `hw.h`.

## Important APIs, Types, and Functions

- `struct dwc2_hsotg` is the shared controller state. This file uses its gadget fields: `driver`, `gadget`, `eps_in`, `eps_out`, `ctrl_req`, `ctrl_buff`, `ep0_buff`, `ep0_state`, `delayed_status`, `test_mode`, `remote_wakeup_allowed`, `enabled`, `connected`, `fifo_mem`, `fifo_map`, `dedicated_fifos`, descriptor-DMA EP0 chains, `dr_backup`, `lx_state`, `hibernated`, `in_ppd`, and `bus_suspended`.
- `struct dwc2_hsotg_ep` wraps `struct usb_ep` and carries endpoint-local state: request queue, current request, direction, max-packet/multicount, FIFO assignment/load accounting, periodic/isochronous flags, halt/wedge status, DDMA descriptor chain state, and isochronous target-frame scheduling.
- `struct dwc2_hsotg_req` wraps `struct usb_request` with a queue node and `saved_req_buf` for DMA bounce buffering of unaligned requests.
- EP0 state is tracked by `enum dwc2_ep0_state`: `DWC2_EP0_SETUP`, `DATA_IN`, `DATA_OUT`, `STATUS_IN`, and `STATUS_OUT`.
- `dwc2_gadget_init()` initializes gadget-facing state, endpoint objects, EP0 control buffers, optional descriptor-DMA control chains, IRQ registration, and gadget metadata.
- `dwc2_hsotg_udc_start()` and `dwc2_hsotg_udc_stop()` bind/unbind the current gadget driver, toggle low-level hardware in peripheral mode, wire the legacy OTG PHY peripheral pointer, and initialize or disconnect the hardware.
- `dwc2_hsotg_ep_enable()`, `dwc2_hsotg_ep_disable()`, `dwc2_hsotg_ep_queue()`, `dwc2_hsotg_ep_dequeue()`, and `dwc2_hsotg_ep_sethalt()` implement the endpoint operations exposed through `dwc2_hsotg_ep_ops`.
- `dwc2_hsotg_irq()` is the device-mode interrupt top half. It handles USB reset, enumeration, endpoint interrupts, FIFO-empty and RX-FIFO events, suspend-related signals, incomplete isochronous events, global NAK effects, and wakeup-alert handling.
- `dwc2_hsotg_core_init_disconnected()`, `dwc2_hsotg_core_connect()`, and `dwc2_hsotg_core_disconnect()` reset/configure the core and control the soft-disconnect bit.
- `dwc2_backup_device_registers()`, `dwc2_restore_device_registers()`, `dwc2_gadget_enter_hibernation()`, `dwc2_gadget_exit_hibernation()`, `dwc2_gadget_enter_partial_power_down()`, `dwc2_gadget_exit_partial_power_down()`, `dwc2_gadget_enter_clock_gating()`, and `dwc2_gadget_exit_clock_gating()` implement persistence and low-power transitions.

## Control Flow

Probe/platform integration calls `dwc2_gadget_init()` when the controller supports peripheral or dual-role mode. That routine reads hardware endpoint direction capabilities from `hsotg->hw_params`, allocates endpoint structures, sets `gadget.ops`, configures max speed, allocates EP0 control buffers, registers `dwc2_hsotg_irq()`, initializes `gadget.ep_list`, allocates `ctrl_req`, and initializes each endpoint with `dwc2_hsotg_initep()`.

When a gadget function driver binds, the gadget core invokes `udc_start`. `dwc2_hsotg_udc_start()` records the driver, enables low-level hardware when operating as a fixed peripheral, optionally attaches to the USB PHY OTG object, and if the core is already in device mode runs `dwc2_hsotg_init()` followed by `dwc2_hsotg_core_init_disconnected()`. Pullup or VBUS activation later calls `dwc2_hsotg_pullup()` or `dwc2_hsotg_vbus_session()`, which reinitialize disconnected hardware and clear `DCTL_SFTDISCON` only when the role/session is valid.

Core initialization resets EP0 state and hardware programming. `dwc2_hsotg_core_init_disconnected()` kills existing EP0 requests, optionally soft-resets the core, initializes PHY and FIFOs, programs `DCFG`, masks/unmasks global and endpoint interrupts, configures DMA or PIO mode in `GAHBCFG`, enables descriptor-DMA and service-interval features when requested, configures EP0 OUT and IN control registers, initializes LPM/ref-clock registers, sets `lx_state` to `DWC2_L0`, and queues the initial 8-byte setup request.

Request flow starts in `dwc2_hsotg_ep_queue()`. It rejects requests unless the controller is active, validates isochronous length limits, creates a bounce buffer for unaligned DMA buffers, maps DMA when enabled, selects EP0 descriptor chains in DDMA mode, appends the request to the endpoint queue, and either starts it immediately or waits for isochronous synchronization. `dwc2_hsotg_start_req()` computes transfer length/payload splitting, packet count, zero-length-packet needs, DDMA descriptors or DxEPTSIZ/DxEPDMA programming, isochronous frame selection, EP enable/CNAK bits, PIO FIFO priming, and endpoint interrupt masking.

Completion flow is split by transfer direction and mode. PIO OUT data arrives through RX-FIFO events handled by `dwc2_hsotg_handle_rx()` and `dwc2_hsotg_rx_data()`. OUT completion is handled by `dwc2_hsotg_handle_outdone()`, while IN completion is handled by `dwc2_hsotg_complete_in()`. DDMA isochronous completions use `dwc2_gadget_complete_isoc_request_ddma()`. All normal paths converge on `dwc2_hsotg_complete_request()`, which finalizes status, unmaps DMA, restores bounce buffers, removes the request from the endpoint queue, calls `usb_gadget_giveback_request()` with the controller lock dropped, and starts the next queued request when appropriate.

EP0 control flow uses the driver-owned `ctrl_req`. `dwc2_hsotg_enqueue_setup()` queues an 8-byte setup read and sets EP0 to `DWC2_EP0_SETUP`. `dwc2_hsotg_complete_setup()` either requeues setup on a zero-length completion or calls `dwc2_hsotg_process_control()`. Standard `SET_ADDRESS`, `GET_STATUS`, `SET_FEATURE`, and `CLEAR_FEATURE` requests are handled locally where possible; other requests are passed to `driver->setup()`. Failed setup handling stalls EP0, while data/status stages are transitioned with `dwc2_hsotg_ep0_zlp()` and `dwc2_hsotg_program_zlp()`. Delayed-status requests are tracked with `hsotg->delayed_status`.

Interrupt handling is register-driven. `dwc2_hsotg_irq()` first verifies device mode, then loops with a bounded retry for FIFO-sensitive interrupts. Reset paths disconnect the gadget, reset the device address, and reinitialize hardware when VBUS/session remains valid. Enumeration updates gadget speed and endpoint max-packet limits. Endpoint interrupts are decoded with `DAINT/DAINTMSK` and delegated to `dwc2_hsotg_epint()`, which handles transfer complete, endpoint disabled, OUT-token-on-disabled-EP, NAK, setup, status-phase-received, BNA, and FIFO-empty conditions. Global FIFO-empty interrupts invoke `dwc2_hsotg_irq_fifoempty()`, which tries to push more PIO IN data.

Isochronous control is frame-sensitive. The driver tracks `target_frame`, `interval`, and `frame_overrun`, synchronizes initial ISOC-IN on NAK and ISOC-OUT on OUTTKNEPDIS, drops expired requests with `-ENODATA`, handles incomplete SOF interrupts by disabling stale endpoints, and has a descriptor-DMA path that fills ring-like descriptor chains and completes descriptors by comparing software indices against DMA status.

## State and Persistence Behavior

Most mutable runtime state is in memory under `dwc2_hsotg` and `dwc2_hsotg_ep`; it is protected by `hsotg->lock` for IRQ, queue, endpoint, and connection state. Completion callbacks deliberately run with that lock released to avoid deadlocks when gadget drivers queue follow-up work.

Persistent hardware state is MMIO register state rather than filesystem data. `dwc2_backup_device_registers()` snapshots device registers including `DCFG`, `DCTL`, endpoint masks, endpoint control/size/DMA registers, and TX FIFO size registers into `hsotg->dr_backup` and marks it valid. `dwc2_restore_device_registers()` restores that snapshot and clears the valid flag. In descriptor-DMA mode it repairs saved DIEPDMA/DOEPDMA values for enabled endpoints to avoid BNA interrupts from stale hibernation-time DMA pointers.

Low-power transitions update both registers and state flags. Hibernation backs up global and device registers, sequences `GPWRDN` and `PCGCTL`, sets `hibernated` and `lx_state = DWC2_L2`, and saves `GPWRDN`. Exit hibernation uses `dwc2_hib_restore_common()`, restores selected DCFG/DCTL/global/device registers, handles remote wakeup signaling, clears pending interrupts, and returns to `DWC2_L0`. Partial power down backs up registers, clamps/resets/stops the module clock through `PCGCTL`, sets `in_ppd`, and optionally restores on exit. Clock gating only gates clocks and records `bus_suspended`, then invokes the gadget driver's `resume` callback on exit.

There is no on-disk persistence and no user-visible configuration written by this file. Configuration comes from `hsotg->params`, `hsotg->hw_params`, platform/DT-derived parameters in surrounding DWC2 code, and the active gadget driver.

## Dependencies

- Linux USB gadget core: `struct usb_gadget`, `struct usb_ep`, `struct usb_request`, `usb_add_gadget_udc()` through surrounding integration, `usb_del_gadget_udc()`, `usb_gadget_map_request()`, `usb_gadget_unmap_request()`, `usb_gadget_giveback_request()`, endpoint descriptor helpers, USB Chapter 9 request constants, and gadget state helpers.
- DWC2 local core: `core.h` provides `dwc2_hsotg`, endpoint/request structures, core parameters, low-power prototypes, global register backup helpers, PHY/core helpers, and mode checks. `hw.h` provides DWC2 register offsets and bit fields.
- Linux kernel infrastructure: spinlocks, IRQ handling, devm/dmam allocation, DMA mapping, scatterlists, list management, debug logging, delays, clocks/resets/regulators indirectly through `dwc2_hsotg`, and optional debugfs support.
- Hardware assumptions: DWC2 device-mode register semantics, FIFO RAM layout, optional dedicated TX FIFOs, DMA/DDMA capability, LPM/service-interval support, UTMI/ULPI hibernation sequencing, and VBUS/session validity via `GOTGCTL_BSESVLD`.

## Integration Points

- `platform.c` calls `dwc2_gadget_init()` during probe for device-capable configurations and calls `dwc2_hsotg_remove()`, `dwc2_hsotg_suspend()`, and `dwc2_hsotg_resume()` during lifecycle transitions.
- `core.c` delegates device-mode hibernation and partial-power-down transitions to this file through `dwc2_gadget_enter_hibernation()`, `dwc2_gadget_exit_hibernation()`, `dwc2_gadget_enter_partial_power_down()`, and `dwc2_gadget_exit_partial_power_down()`.
- `core_intr.c`, `drd.c`, and host-side code may call gadget clock-gating exit/init helpers when role switching, wakeups, or shared interrupts require device-mode state recovery.
- The USB gadget framework interacts through `dwc2_hsotg_gadget_ops` and `dwc2_hsotg_ep_ops`. Function drivers bind via `udc_start`, submit transfer work through endpoint `queue`, receive completions through request callbacks, handle setup requests through `driver->setup`, and receive disconnect/resume callbacks via `call_gadget()`.
- External PHY integration occurs through `otg_set_peripheral()` and `usb_phy_set_power()` when a legacy `usb_phy` is present.

## Risks and Edge Cases

- DMA alignment is a recurring risk. The file globally selects DMA through `params.g_dma`, but comments note DWC2 DMA alignment limitations. The implementation uses temporary bounce buffers for unaligned request buffers, and completion must restore/copy correctly, especially for OUT transfers.
- Descriptor-DMA paths are complex and mode-specific. EP0 uses distinct setup/control IN/control OUT descriptor chains; non-control endpoints allocate chains on enable; isochronous endpoints use circular descriptor indices. Stale or wrong descriptor DMA addresses can produce BNA interrupts, which is why restore paths patch enabled endpoint DMA pointers.
- EP0 direction and state are fragile because `eps_out[0]` is used for both directions. Several paths temporarily change `dir_in`, select descriptor chains from `ep0_state`, and requeue setup after status phases or stalls.
- Isochronous scheduling depends on current frame, wrap handling, service interval mode, and first-token synchronization. Expired transfers complete with `-ENODATA`; missed interrupt or wrong frame arithmetic can cause dropped audio/video packets or endless resynchronization.
- Interrupt storms are possible if endpoint or FIFO-empty masks are left enabled without queued work. The driver explicitly disables some FIFO interrupts and endpoint interrupts when idle, but regressions in queue/completion paths can reintroduce floods.
- Endpoint halt handling differs for IN and OUT. OUT halt uses global OUT NAK and final STALL programming in the GOUTNAKEFF path; busy endpoints may return `-EAGAIN` unless halting immediately for protocol handling.
- Power-management restore has narrow ordering requirements. Hibernation, partial power down, and clock gating manipulate clock/reset/power registers with delays and pending-interrupt clears. Missing backup validity, wrong restore flags, or remote-wakeup/reset confusion can leave the controller disconnected or with a stale address.
- The IRQ handler is shared and returns `IRQ_NONE` outside device mode. Dual-role transitions must keep mode/op-state synchronized so host-mode interrupts are not misprocessed by the gadget handler.

## Test Signals

- Build coverage should include `CONFIG_USB_DWC2_PERIPHERAL` and `CONFIG_USB_DWC2_DUAL_ROLE`, with DMA disabled, DMA enabled, and descriptor-DMA enabled configurations.
- Enumeration smoke tests should show reset, `EnumDone`, correct `usb_speed_string()` logging, device address assignment, EP0 setup requeueing, and successful Chapter 9 `GET_STATUS`, `SET_ADDRESS`, feature clear/set, and gadget-driver setup fallback.
- Transfer tests should exercise bulk, interrupt, and isochronous IN/OUT endpoints; short packets; ZLP generation; request dequeue; halt/wedge and CLEAR_FEATURE recovery; scatter-gather in descriptor-DMA mode; and unaligned DMA buffers that trigger bounce-buffer handling.
- PIO-specific signals include RX-FIFO packet reads, `GINTSTS_RXFLVL` retry behavior, non-periodic and periodic FIFO-empty interrupts, and no idle interrupt storm.
- Descriptor-DMA-specific signals include correct EP0 setup/data/status descriptor selection, BNA handling, descriptor completion accounting, ISOC frame numbers, and SG request handling where supported.
- Power tests should cover suspend/resume, remote wakeup, USB reset while in partial power down, hibernation entry/exit with and without reset, and clock-gating exit paths. Expected observations include valid register backup/restore, `lx_state` transitions between L0/L2/L3, `bus_suspended` clearing on resume, and no stale endpoint DMA pointer BNA after restore.
- Integration tests with composite gadgets such as mass storage, ECM/RNDIS, HID, and UAC/UVC-style isochronous functions would provide broad endpoint-type and control-flow coverage.
