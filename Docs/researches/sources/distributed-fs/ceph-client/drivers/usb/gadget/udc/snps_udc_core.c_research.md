# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_core.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_core.c` is the core implementation for a Synopsys USB device controller derived from the AMD Geode 5536 UDC driver and reused by PCI or SoC-integrated instances. It exposes the Linux USB gadget UDC surface, programs endpoint and device registers, manages FIFO or DMA transfers, handles EP0 control traffic, and dispatches endpoint/device interrupts. The source was read as a complete 3192-line file for this report.

## Important APIs, Types, and Functions

The exported integration functions are `udc_probe`, `udc_remove`, `udc_irq`, `udc_basic_init`, `udc_mask_unused_interrupts`, `udc_enable_dev_setup_interrupts`, `empty_req_queue`, `init_dma_pools`, `free_dma_pools`, and `gadget_release`. Gadget endpoint operations are implemented through `udc_ep_ops`: `udc_ep_enable`, `udc_ep_disable`, `udc_alloc_request`, `udc_free_request`, `udc_queue`, `udc_dequeue`, and `udc_set_halt`. Gadget device operations are `udc_wakeup`, `udc_get_frame`, `amd5536_udc_start`, and `amd5536_udc_stop`.

Important internal flows include DMA descriptor construction in `udc_create_dma_chain` and `prep_dma`, request completion in `complete_req`, FIFO helpers `udc_txfifo_write` and `udc_rxfifo_read`, control endpoint setup in `activate_control_endpoints` and `setup_ep0`, timer callbacks `udc_timer_function` and `udc_pollstall_timer_function`, and ISR handlers `udc_data_out_isr`, `udc_data_in_isr`, `udc_control_out_isr`, `udc_control_in_isr`, and `udc_dev_isr`. The file depends heavily on types and register macros from `amd5536udc.h`, including `struct udc`, `struct udc_ep`, `struct udc_request`, `struct udc_data_dma`, and `union udc_setup_data`.

## Control Flow

Platform or PCI glue allocates and maps a `struct udc`, then calls `udc_probe`. `udc_probe` installs `udc_ops`, names the gadget, calls `startup_registers`, registers with `usb_add_gadget_udc_release`, initializes timers, sets soft-disconnect, and prints register mode state. `startup_registers` soft-resets the controller, masks interrupts, initializes the gadget context, wires endpoint structures, and chooses high-speed or full-speed operation.

When a gadget function binds, `amd5536_udc_start` stores the gadget driver, shares EP0 driver data between EP0 IN and OUT, activates EP0, clears soft-disconnect, and connects the device. Endpoint enable programs hardware type, max-packet, FIFO sizing, CSR endpoint fields, interrupt masks, and NAK state. Request queueing maps DMA when enabled, initializes request status, prepares FIFO or DMA descriptors, writes descriptor pointers, opens RX DMA when safe, and appends requests to the endpoint queue.

Interrupt flow is split between endpoint and device status registers. `udc_irq` holds `dev->lock`, dispatches EP0 OUT/IN interrupts first, iterates data endpoints, clears per-endpoint interrupt status, then clears and dispatches global device interrupts. Data IN handles FIFO pushes or DMA TDC completions; data OUT handles FIFO reads, DMA completion accounting, BNA recovery, and RX DMA rearming. EP0 OUT decodes SETUP versus data packets, reads the setup packet from DMA setup memory or FIFO, selects the active EP0 direction, calls `driver->setup`, then ACKs, stalls, or waits for a ZLP. Device interrupts synthesize `USB_REQ_SET_CONFIGURATION` and `USB_REQ_SET_INTERFACE` for requests partly handled by hardware, reset and reinitialize on USB reset and enumeration, call gadget suspend/resume hooks, and disconnect on session-valid loss.

## State and Persistence Behavior

State is volatile kernel and hardware state only. A file-global `udc` pointer is used by timers and some helper paths; global spinlocks protect reset and stall polling; global variables track pending CNAK bits, RX FIFO pending data, soft-reset workarounds, timer stop flags, and shared RX DMA enable state. Per-device state tracks gadget binding, current configuration/interface/alternate setting, EP queues, EP0 handshakes, speed, connection state, DMA pools, and mapped register bases.

No file-backed persistence exists. Persistent effects are hardware register programming, DMA descriptors allocated from DMA pools, and gadget core state exposed through `usb_gadget_set_state` or gadget callbacks. Timers are stopped and deleted in `udc_remove`; DMA pools are created and destroyed by the platform glue through exported helpers.

## Dependencies and Integration Points

The file integrates with the Linux USB gadget core (`usb_add_gadget_udc_release`, `usb_gadget_giveback_request`, `usb_gadget_udc_reset`, request map/unmap helpers), Linux DMA pool APIs, timers, spinlocks, interrupts, and MMIO accessors. Its primary local contract is `amd5536udc.h`, which defines register layouts, endpoint indexes, descriptor formats, module parameters such as `use_dma`, and SoC revision constants. `snps_udc_plat.c` supplies platform resource mapping, PHY/extcon handling, IRQ registration, and calls into these exported core routines.

## Risks and Edge Cases

The controller has a single global RX DMA enable bit for all OUT endpoints; the `set_rde` timer and BNA dummy descriptors are workarounds to avoid blocking control traffic while data OUT descriptors are absent. This is race-sensitive and depends on lock, timer, and FIFO-empty ordering. DMA modes have multiple variants (`PPB`, `PPBDU`, buffer-fill) with different byte accounting and descriptor-chain behavior; off-by-one ring or chain errors can corrupt transfer completion. EP0 control flow mixes hardware-handled requests, synthesized setup callbacks, ZLP ACK tracking, and stall handling, so descriptor/state drift can break enumeration. Some paths use global `udc` rather than the local `dev`, making multi-controller assumptions fragile. Remove and suspend paths must stop timers before memory disappears. Error paths around BNA, host errors, pending CNAK, and `udc_dequeue` cancellation are especially hardware-dependent.

## Test Signals

Useful test signals include successful build with `CONFIG_USB_GADGET` and the Synopsys/AMD UDC options, probe/remove on Broadcom-compatible platform glue, enumeration at full and high speed, EP0 standard request coverage, gadget function bind/unbind with queue draining, bulk IN/OUT transfer tests in FIFO and DMA modes, mass-storage reset and halt/clear-halt behavior, disconnect/session-valid transitions, suspend/resume callbacks, interrupt storm/regression checks, and DMA sanitizers or IOMMU faults during chained large requests and short-packet completion.
