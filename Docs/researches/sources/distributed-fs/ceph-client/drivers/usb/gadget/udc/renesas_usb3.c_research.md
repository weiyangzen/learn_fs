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
