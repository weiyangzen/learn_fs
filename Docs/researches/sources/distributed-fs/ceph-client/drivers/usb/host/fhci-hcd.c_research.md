# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-hcd.c

## Purpose
`fhci-hcd.c` is the Linux USB HCD platform driver for the Freescale QUICC Engine USB Host Controller Interface. It wires the FHCI implementation into `struct hc_driver`, allocates FHCI software state, maps QE USB registers and multi-user RAM parameter RAM, requests QE pins/GPIOs/timer IRQs, and starts/stops the controller.

## Important APIs, Types, and Functions
- HCD lifecycle: `fhci_start()`, `fhci_stop()`, `fhci_urb_enqueue()`, `fhci_urb_dequeue()`, `fhci_endpoint_disable()`, and `fhci_get_frame_number()` populate `fhci_driver`.
- Controller setup: `of_fhci_probe()` validates device-tree mode, creates the HCD, maps registers, allocates FHCI PRAM with `cpm_muram_alloc()`, requests GPIO descriptors, QE pins, GTM timer, clock sources, and USB IRQ, then calls `usb_add_hcd()`.
- Low-level helpers: `fhci_start_sof_timer()`, `fhci_stop_sof_timer()`, `fhci_get_sof_timer_count()`, `fhci_usb_enable_interrupt()`, `fhci_usb_disable_interrupt()`, and `fhci_ioports_check_bus_state()`.
- Memory/lifetime helpers: `fhci_mem_init()`, `fhci_mem_free()`, `fhci_create_lld()`, `fhci_usb_init()`, and `fhci_usb_free()`.

## Control Flow
Probe exits early when USB is disabled or device-tree `mode` is not `host`. After HCD allocation, probe maps the USB register resource, allocates and assigns QE parameter RAM, gathers GPIOs/pins, obtains a 16-bit GTM timer and IRQ, maps the USB IRQ, resolves optional full-/low-speed clock names, programs initial transceiver speed, clears interrupt state, and registers the HCD. `fhci_start()` then allocates controller lists/root hub/TD and ED pools, creates the low-level `fhci_usb`, initializes PRAM/registers and endpoint zero, initializes the virtual root hub, marks the HCD running, and enables the controller. URB enqueue computes TD count by pipe type, allocates `urb_priv`, links the URB to the USB core endpoint, initializes URB state, and delegates transfer construction to `fhci_queue_urb()`. Stop disables interrupts/controller, frees endpoint zero and low-level state, and recycles software memory.

## State and Persistence Behavior
Runtime state is entirely in kernel memory and device registers: `fhci_hcd`, `fhci_usb`, virtual root hub fields, ED/TD free lists, QE PRAM, and hardware registers. Interrupt nesting is tracked with `intr_nesting_cnt`; `saved_msk` persists the desired USB interrupt mask across disable/enable windows. No disk persistence exists. The source assumes the HCD spinlock protects URB, endpoint, and root-hub mutable state.

## Dependencies and Integration Points
The file depends on Linux USB HCD APIs, OF/platform-device APIs, QE/CPM MURAM helpers, GTM timer helpers, GPIO descriptors, and FHCI sibling files for hub, scheduler, queue, memory, and TD-ring behavior. Device-tree properties include `mode`, `hub-power-budget`, `reg`, GPIO indices, QE pin indices, `fsl,fullspeed-clock`, and `fsl,lowspeed-clock`.

## Risks and Test Signals
Risks include fragile interrupt nesting balance, error-path resource unwinding across PRAM/pins/timer/IRQ/HCD, assumptions about GPIO ordering and optional speed/power GPIOs, and TD-count sizing for zero-length or zero-packet URBs. Useful test signals are probe/remove on real QE hardware or DT emulation, enumeration at full and low speed, control/bulk/interrupt/iso URB enqueue/dequeue, disconnect during active URBs, endpoint disable while TDs are queued, and injected failures for MURAM, timer IRQ, GPIO, pin, and clock acquisition.
