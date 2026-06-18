# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_qe_udc.c

## Purpose

`fsl_qe_udc.c` is the Freescale QE/CPM USB peripheral controller driver for SoCs such as MPC8360, MPC8323, and MPC8272. It implements a four-endpoint USB gadget UDC using QE/CPM parameter RAM, buffer descriptor rings, controller registers, tasklets, and interrupts. It registers with the generic UDC core and exposes standard gadget endpoint and controller operations.

## Important APIs, Types, And Functions

The implementation uses `struct qe_udc`, `struct qe_ep`, `struct qe_req`, and `struct qe_frame`. Endpoint ops are enable/disable, request allocation/free, queue/dequeue, and halt. Gadget ops are frame number, `fsl_qe_start()`, and `fsl_qe_stop()`.

Low-level helpers control RX/TX stall, NACK, stop/restart TX, FIFO flush/fill, BD reset, endpoint reset, BD allocation, RX BD setup, and endpoint register initialization. Transfer helpers handle EP0 RX, RX frame copying, RX tasklet processing, TX BD creation, TX completion, ZLP/status phases, active TX request advancement, and request receive/send. Chapter 9 helpers handle SET_ADDRESS, GET_STATUS, feature set/clear, and delegation to gadget `setup()`. `qe_udc_irq()` dispatches idle, TX, RX, reset, busy, and TX error events.

## Control Flow

Probe requires device-tree `mode = "peripheral"`. It allocates controller state, maps USB parameter RAM, allocates endpoint parameter blocks in MURAM, maps controller registers, initializes registers, configures gadget fields, initializes four endpoints, initializes EP0, allocates ZLP and GET_STATUS buffers, sets up the RX tasklet, maps and requests IRQ, and registers the gadget with UDC core.

When a gadget driver binds, `fsl_qe_start()` stores the driver, sets speed, enables the controller, clears event bits, enables default interrupts, and moves EP0 to wait-for-setup. Stop disables the controller, resets state, nukes queues, and clears the driver pointer.

Endpoint enable validates descriptor type, transfer type, speed/maxpacket constraints, direction, and naming. It allocates RX/TX BD rings in MURAM, RX resources for OUT/control endpoints, TX frame state for IN/control endpoints, initializes endpoint registers, and leaves hardware NAKing until requests are queued.

Requests are queued under `udc->lock`. The driver maps or syncs DMA, marks requests in progress, appends them to endpoint queues, and starts immediate send or receive handling. IN endpoints keep one active `tx_req` and send up to maxpacket per frame. OUT endpoints un-NACK or drain existing RX BDs. EP0 uses explicit setup, data, and status states.

## State And Persistence

The driver maintains USB state, resume state, EP0 state/direction, pending device address, MURAM parameter pointers, endpoint objects, RX tasklet, IRQ, and DMA buffers. Endpoint state includes BD ring bases/current pointers, RX/TX frames, RX data buffers, active TX request, data toggle, queue, NACK/stall state, local NACK, and queued RX data count. State is volatile and reconstructed on probe or endpoint enable.

## Dependencies And Integration Points

This driver depends on UDC core, Linux DMA mapping, device tree, platform drivers, IRQ APIs, QE/CPM command APIs, MURAM allocation, and big-endian register/BD accessors. It matches `fsl,mpc8323-qe-usb`, `fsl,mpc8360-qe-usb`, and `fsl,mpc8272-cpm-usb`, with match data selecting QE or CPM command paths.

## Risks

The code is hardware-specific and subtle. It uses `virt_to_phys()` first and falls back to DMA mapping only on a sentinel result. RX buffers are manually aligned for BD addresses. Request queueing may hide transfer-start errors. EP0 control flow drops and reacquires `udc->lock` around gadget callbacks. Some paths allocate with `GFP_ATOMIC` under lock. Suspend/resume return `-ENOTSUPP`. Cleanup must free MURAM, DMA mappings, frames, IRQs, tasklets, and gadget references in order.

## Test Signals

Key tests are probe with each compatible string, UDC registration, EP0 enumeration through SET_ADDRESS and GET_STATUS, endpoint enable/disable for valid and invalid descriptors, IN transfers including ZLP, OUT transfers under RX BD pressure and local NACK recovery, endpoint halt/clear-halt, bus reset recovery, suspend/resume IRQ callbacks, TX retry behavior, and remove/probe-failure cleanup.
