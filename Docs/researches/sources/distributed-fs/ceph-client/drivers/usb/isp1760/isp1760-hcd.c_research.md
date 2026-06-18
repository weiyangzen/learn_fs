# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-hcd.c

## Purpose
`isp1760-hcd.c` implements the USB host-controller driver for ISP1760/1761/1763 chips. It presents an `hc_driver` to USB core, packetizes URBs into Philips PTDs/QTDs, manages the chip's on-controller payload memory, handles completion interrupts, provides root-hub control, and works around known interrupt errata.

## Important APIs, Types, And Functions
Key private types are `struct ptd`, `struct isp1760_qtd`, `struct isp1760_qh`, and `struct urb_listitem`. Public entry points are `isp1760_init_kmem_once()`, `isp1760_deinit_kmem_cache()`, `isp1760_hcd_register()`, and `isp1760_hcd_unregister()`. The `hc_driver` callbacks include `isp1760_hc_setup()`, `isp1760_run()`, `isp1760_stop()`, `isp1760_shutdown()`, `isp1760_urb_enqueue()`, `isp1760_urb_dequeue()`, `isp1760_endpoint_disable()`, `isp1760_get_frame()`, `isp1760_hub_status_data()`, `isp1760_hub_control()`, and `isp1760_clear_tt_buffer_complete()`.

Important internals include register helpers, `mem_read()/mem_write()` variant dispatch, `ptd_read()/ptd_write()`, `init_memory()/alloc_mem()/free_mem()`, `packetize_urb()`, `create_ptd_atl()`, `create_ptd_int()`, `schedule_ptds()`, `handle_done_ptds()`, and `isp1760_irq()`.

## Control Flow
Registration creates a USB HCD, links `struct isp1760_hcd` through `hcd_priv`, allocates ATL and interrupt slot arrays sized by variant memory layout, initializes memory chunks, and calls `usb_add_hcd()`. Setup validates scratch register access, clears buffer-fill and skip maps, performs EHCI reset, resets ATL/INT hardware, configures ISP1763-specific OTG/lock bits, enables ATL/INT interrupts, and initializes queue lists.

URB enqueue selects the endpoint queue by pipe type, rejects isochronous transfers, packetizes data into setup/data/status or bulk/interrupt QTDs, links the URB to USB core, creates or reuses a QH, appends QTDs, and calls `schedule_ptds()`. Scheduling first collects completed/retired QTDs and gives back URBs outside the lock, then starts queued control, interrupt, and bulk transfers when chip memory and PTD slots are available. Completion IRQs read/ack interrupt status, merge done maps, parse PTD status, reload NAK/error cases, retire failed URBs, update data toggle/ping, read IN payloads back to URB buffers, and reschedule. Root-hub operations translate hub requests to `PORTSC1` fields and EHCI state transitions.

## State And Persistence
Runtime state lives in `struct isp1760_hcd`: USB HCD pointer, regmap fields, variant flag, memory layout, spinlock, ATL/INT slot arrays, done maps, memory chunk free list, QH lists, periodic scheduling values, reset timing, and next-state timestamps. QH/QTD/URB-list objects use kmem caches. Hardware state includes PTD tables, payload memory, skip/done/last maps, buffer-fill bits, port status, interrupt masks, and command/config registers. There is no durable persistence.

## Dependencies And Integration Points
The file depends on USB HCD core, EHCI shared reset semaphore, hub/TT helpers, regmap fields from core, MMIO accessors, timers, kmem caches, unaligned access, and cache flushing for IN transfers. It integrates with `isp1760-core.c` through preinitialized regmaps and memory layout, and with Kconfig through HCD stubs.

## Risks
Isochronous transfers are explicitly unsupported. The PTD scheduler is lock-heavy and sensitive to ordering: payload writes must precede valid-bit writes, done-map bits must be masked against skip maps, and URB giveback can reenter the HCD. Memory allocation is first-fit by fixed chunk sizes; large URBs are split to the largest block size. The global errata timer stores a single `errata2_timer_hcd`, which is a risk for multiple controllers. `isp1760_stop()` unconditionally deletes that timer even for ISP1763 where it may not have been added. Root-hub resume/reset handling uses timing assumptions and direct `PORTSC1` read-modify-write special cases. TT buffer dirty handling must prevent scheduling behind failed low/full-speed split transfers.

## Test Signals
Run USB host enumeration and `usbtest` with control, bulk, and interrupt endpoints on high-speed plus full/low-speed devices behind a hub. Test short bulk packets with and without `URB_SHORT_NOT_OK`, zero-length packets, dequeue during active transfers, endpoint disable, disconnect during transfers, root-hub reset/suspend/resume/power requests, and ISP1760 versus ISP1763 memory access paths. Stress tests should look for stuck PTD slots, memory-pool leaks, timer behavior, and URB giveback races.
