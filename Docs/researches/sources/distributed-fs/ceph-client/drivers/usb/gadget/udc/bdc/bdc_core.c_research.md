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
