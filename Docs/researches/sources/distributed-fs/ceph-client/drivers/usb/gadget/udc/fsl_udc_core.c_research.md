# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_udc_core.c

## Purpose

`fsl_udc_core.c` implements the Freescale high-speed USB device-controller driver for the USB DR block found on MPC8349E, MPC8313E, MPC5121E, and related SoCs. It exposes the controller through the Linux USB gadget UDC API, programs endpoint queue heads and device transfer descriptors, handles ep0 Chapter 9 control requests, dispatches interrupts for setup/completion/reset/suspend/port-change events, and binds as a platform driver for `fsl-usb2-udc` and compatible device-tree nodes.

## Important APIs, Types, and Functions

The public integration surface is through `fsl_ep_ops`, `fsl_gadget_ops`, and the `platform_driver` named `fsl-usb2-udc`. Endpoint operations include `fsl_ep_enable()`, `fsl_ep_disable()`, `fsl_alloc_request()`, `fsl_free_request()`, `fsl_ep_queue()`, `fsl_ep_dequeue()`, `fsl_ep_set_halt()`, `fsl_ep_fifo_status()`, and `fsl_ep_fifo_flush()`. Gadget operations include `fsl_get_frame()`, `fsl_wakeup()`, `fsl_vbus_session()`, `fsl_vbus_draw()`, `fsl_pullup()`, `fsl_udc_start()`, and `fsl_udc_stop()`.

Important internal routines are `dr_controller_setup()`, `dr_controller_run()`, `dr_controller_stop()`, `dr_ep_setup()`, `struct_ep_qh_setup()`, `ep0_setup()`, `fsl_build_dtd()`, `fsl_req_to_dtd()`, `fsl_queue_td()`, `fsl_prime_ep()`, `done()`, `nuke()`, `setup_received_irq()`, `tripwire_handler()`, `process_ep_req()`, `dtd_complete_irq()`, `reset_irq()`, and `fsl_udc_irq()`. Probe/remove and PM are handled by `fsl_udc_probe()`, `fsl_udc_remove()`, `fsl_udc_suspend()`, `fsl_udc_resume()`, `fsl_udc_otg_suspend()`, and `fsl_udc_otg_resume()`.

## Control Flow

Probe allocates the singleton `udc_controller`, records platform data, maps the controller registers, calls board/platform init, selects big- or little-endian accessors, validates `DCCPARAMS_DC`, reads the endpoint count, requests the shared IRQ, allocates the endpoint array and aligned coherent dQH table, creates the ep0 status request buffer, initializes hardware when not OTG-gated, initializes `usb_gadget`, configures ep0, creates non-control endpoint objects, creates the dTD DMA pool, and registers the gadget with `usb_add_gadget_udc_release()`.

When a gadget driver binds, `fsl_udc_start()` stores the driver and either registers with the OTG transceiver or starts the device controller by enabling interrupts and setting `USB_CMD_RUN_STOP`. Endpoint enable programs the dQH capability field and endpoint control register according to the descriptor type, direction, max packet size, high-bandwidth multiplier, and zero-length termination policy. Queueing maps the request for DMA, builds one or more dTDs up to `EP_MAX_LENGTH_TRANSFER`, links them, primes the endpoint, and adds the request to the endpoint queue. Completion interrupts walk `endptcomplete`, process dTD status and remaining lengths, and retire completed requests through `done()`.

Ep0 setup interrupts are read through the hardware setup tripwire to avoid racing a new setup packet. Standard `GET_STATUS`, `SET_ADDRESS`, endpoint halt feature, remote-wakeup/test-mode feature, and OTG feature cases are handled locally where possible; other requests are delegated to `driver->setup()`. The ep0 state machine moves through `WAIT_FOR_SETUP`, `DATA_STATE_XMIT`, `DATA_STATE_RECV`, and `WAIT_FOR_OUT_STATUS`, with `ep0_prime_status()` submitting status ZLPs as needed. Reset IRQs clear address and endpoint status, flush all endpoints, notify the gadget stack with either reset or disconnect semantics, restore ep0 setup, and restart the controller for controller resets.

## State and Persistence Behavior

All driver state is in-memory and hardware-register backed. The global `dr_regs`, optional `usb_sys_regs`, and singleton `udc_controller` point at the active device. `struct fsl_udc` stores gadget binding, platform data, endpoint array, IRQ, ep0 setup buffer, spinlock, optional USB PHY, soft-connect/VBUS/stopped flags, remote-wakeup and OTG suspend flags, coherent dQH memory, status request, dTD DMA pool, PHY mode, bus reset flag, current/resume USB states, ep0 state/direction, and pending device address. `struct fsl_ep` tracks the gadget endpoint, request queue, dQH pointer, stopped state, and endpoint name. `struct fsl_req` owns the gadget request plus its dTD chain.

No state is persisted to disk. Externally visible state is controller register state, USB gadget state, optional proc debug output under `driver/fsl_usb2_udc`, and callbacks to gadget drivers and OTG/PHY helpers. DMA descriptors and queue heads are coherent allocations whose lifetime is tied to active requests and the UDC lifetime.

## Dependencies and Integration Points

The driver depends on the Linux USB gadget framework, USB Chapter 9 definitions, platform-device resources, Freescale platform data in `linux/fsl_devices.h`, DMA mapping and DMA pools, optional USB PHY/OTG integration, optional proc debug files, IRQ handling, and SoC-specific system interface registers for PHY, IO, and snooping control. It uses runtime endian accessors on PPC32 because controller registers and descriptors can be big or little endian depending on SoC/platform data.

## Risks and Test Signals

Risk is concentrated in DMA descriptor ownership, endpoint queue manipulation under the spinlock, ep0 state transitions, endian conversion, reset races, OTG host/device role interaction, and timeout loops for controller reset and endpoint flush. `fsl_ep_disable()` clears `EPCTRL_RX_ENABLE | EPCTRL_TX_TYPE` on OUT endpoints, which is suspicious because RX type would be expected; this should be preserved unless separately audited against known behavior. Test signals include platform probe/remove, bind/unbind of several gadget drivers, ep0 enumeration and standard requests, SET_ADDRESS timing, endpoint halt/clear halt, multi-dTD transfers including ZLPs, DMA mapping failures, dequeue of active and queued requests, bus reset while requests are active, suspend/resume and remote wakeup, VBUS/pullup toggling, OTG transceiver paths, high/full/low speed detection, and big-endian descriptor/register platforms.
