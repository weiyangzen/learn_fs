# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/tegra-xudc.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/tegra-xudc.c` implements NVIDIA Tegra XUSB device-mode controller support for the Linux USB gadget framework. It programs Tegra XUSB device registers, endpoint contexts, transfer rings, event rings, PHY role state, SoC-specific link tuning, power domains, runtime PM, and EP0 standard request handling. The source was read as a complete 4095-line file for this report.

## Important APIs, Types, and Functions

Major hardware data structures are `struct tegra_xudc`, `struct tegra_xudc_ep`, `struct tegra_xudc_request`, `struct tegra_xudc_trb`, `struct tegra_xudc_ep_context`, `struct tegra_xudc_soc`, `struct tegra_xudc_setup_packet`, and `struct tegra_xudc_save_regs`. Register and TRB access is wrapped by generated inline readers/writers from `BUILD_EP_CONTEXT_RW` and `BUILD_TRB_RW`, plus helpers like `trb_read_data_ptr`, `trb_write_data_ptr`, `ep_ctx_read_deq_ptr`, and `ep_ctx_write_deq_ptr`.

Gadget endpoint operations are `tegra_xudc_ep_enable`, `tegra_xudc_ep_disable`, `tegra_xudc_ep_alloc_request`, `tegra_xudc_ep_free_request`, `tegra_xudc_ep_queue`, `tegra_xudc_ep_dequeue`, and `tegra_xudc_ep_set_halt`, with special EP0 enable/disable stubs. Gadget device operations are `tegra_xudc_gadget_get_frame`, `tegra_xudc_gadget_wakeup`, `tegra_xudc_gadget_pullup`, `tegra_xudc_gadget_start`, `tegra_xudc_gadget_stop`, `tegra_xudc_gadget_vbus_draw`, and `tegra_xudc_set_selfpowered`.

Important internal subsystems include TRB queueing (`tegra_xudc_queue_one_trb`, `tegra_xudc_queue_trbs`, `tegra_xudc_ep_ring_doorbell`, `tegra_xudc_ep_kick_queue`), dequeue/ring repair (`squeeze_transfer_ring`, `trb_in_request`, `trb_before_request`, `__tegra_xudc_ep_dequeue`), EP0 requests (`tegra_xudc_ep0_standard_req` and its set/get helpers), event dispatch (`tegra_xudc_handle_event`, `tegra_xudc_process_event_ring`, `tegra_xudc_irq`), port state (`tegra_xudc_port_connect`, `tegra_xudc_port_disconnect`, `tegra_xudc_port_reset`, suspend/resume handlers), resource allocation (`tegra_xudc_alloc_eps`, `tegra_xudc_alloc_event_ring`), SoC tuning (`tegra_xudc_device_params_init`), PHY/role handling (`tegra_xudc_phy_get`, `tegra_xudc_update_data_role`), and PM (`tegra_xudc_powergate`, `tegra_xudc_unpowergate`).

## Control Flow

Probe matches SoC data, maps `base`, `fpci`, and optional `ipfs` resources, requests the IRQ, gets clocks/regulators, obtains padctl and PHYs, attaches power domains, initializes PHYs, allocates event rings and endpoint rings, initializes work items and runtime PM, then registers `tegra-xudc` with the gadget core. USB PHY notifiers update `device_mode`; role work powers PHYs on/off and switches UTMI mode between device and none.

When a gadget driver starts, EP0 is enabled, controller interrupts and link-state events are enabled, pullup state is honored, and OTG peripherals are attached. Pullup toggles `CTRL_ENABLE`. Endpoint enable configures an endpoint context from descriptors, resets the transfer ring and link TRB, transitions to configured state when the first non-control endpoint is enabled, reloads/unhalts/unpauses hardware, and temporarily pauses bulk endpoints when enabling isochronous endpoints for bandwidth allocation. Queueing maps the request, computes required TRBs including ZLP handling, fills TRBs up to ring availability, and rings a doorbell. Completion events find the request by TRB range, calculate residual bytes, complete the request, advance EP0 state, and kick later queued work.

EP0 setup events are handled in `tegra_xudc_handle_ep0_event`. If another setup is in progress, the latest setup is queued until a sequence-number error allows it to replace the old transaction. Standard requests for status, address, feature, set-sel, and isoch delay are handled locally; other standard and class/vendor requests are delegated to the gadget driver. EP0 status/data stages are queued through a reserved `ep0_req` and advance `setup_state` in `tegra_xudc_ep0_req_done`.

The IRQ handler checks `ST_IP`, acknowledges it, and drains event-ring TRBs while cycle bits match. Event types dispatch to port-status, transfer, or setup handling. Port status changes drive connect, disconnect, reset, suspend, resume, link-state quirks, VBUS toggles, and completion notification for disconnect. Runtime/system PM saves `CTRL` and `PORTPM`, disables controller/clocks/regulators, and on resume reinitializes FPCI/IPFS, tuning registers, event rings, endpoint context base, and saved registers.

## State and Persistence Behavior

State is volatile controller, DMA, and gadget state. `struct tegra_xudc` owns the active gadget driver, endpoint contexts, event-ring pointers, transfer rings, setup state, device address, self-powered flag, pullup state, enabled endpoint counters, current PHYs, power flags, saved registers, delayed work flags, and disconnect completion. DMA-coherent event rings and endpoint contexts persist across normal operation but are reinitialized after powergate. No disk persistence exists.

## Dependencies and Integration Points

The driver integrates with the Linux USB gadget core, platform bus, OF matching, DMA coherent allocation and DMA pools, IRQ handling, runtime PM, generic power domains, reset/clock/regulator frameworks, Tegra XUSB padctl, generic PHY and USB PHY/OTG notifier APIs, USB role semantics, and kernel workqueues. SoC data selects supplies, clocks, number of PHYs, U1/U2/LPM support, invalid-sequence workaround, port link-state quirks, port reset workaround, SuperSpeed port-speed workaround, and IPFS availability.

## Risks and Edge Cases

TRB ring accounting is high-risk: enqueue/dequeue pointers, cycle state, link TRBs, short packets, ring-full repair, and request cancellation all must stay synchronized with hardware endpoint context. EP0 sequencing is complex because setup packets can arrive while a previous control transfer is active; invalid Tegra210 sequence numbers are explicitly halted. Runtime PM must not powergate while interrupts, role work, or disconnect handling still needs registers. PHY pairing logic relies on padctl companion mapping and optional PHYs. Port-change workarounds toggle VBUS or force link-state transitions and are SoC-specific. Error completions halt endpoints and can leave gadget functions dependent on clear-halt/reset recovery.

## Test Signals

Build with Tegra XUDC, USB gadget, PHY, PM, and OF support; probe on Tegra210/186/194/234 device-tree compatibles; enumerate at high-speed and SuperSpeed; exercise EP0 standard requests including set-address, get-status, U1/U2, remote wake, set-sel, isoch delay, and class/vendor delegation; run bulk, interrupt, isochronous, stream, short-packet, ZLP, dequeue, halt/clear-halt, and disconnect tests; validate runtime suspend/resume and system sleep while disconnected and connected; check VBUS role-switch notifications; and monitor event-ring, endpoint halt, DMA mapping, and power-domain errors under stress.
