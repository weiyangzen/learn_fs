# sources/distributed-fs/ceph-client/drivers/usb/host/oxu210hp-hcd.c

## Purpose
This file implements the platform HCD for Oxford Semiconductor OXU210HP, a quasi-EHCI USB 2.0 host controller exposing two logical host controllers, OTG and SPH, behind shared top-level chip registers. It embeds EHCI register definitions, queue-head and qTD structures, an on-chip memory allocator, async and periodic schedules, root-hub emulation, interrupt handling, and platform-driver probe/remove glue.

## Important APIs, Types, and Functions
Key local hardware types are `struct ehci_caps`, `struct ehci_regs`, `struct ehci_qtd`, `struct ehci_qh`, `union ehci_shadow`, `struct oxu_onchip_mem`, `struct oxu_murb`, and `struct oxu_hcd`. `struct oxu_hcd` is the controller-private state: MMIO register pointers, on-chip memory bitmap pools, async QH, reclaim queue, periodic schedule, root-hub port state, timers, and split-URB resource tracking.

The exported integration surface is the `oxu_hc_driver` method table: `.reset = oxu_reset`, `.start = oxu_run`, `.stop = oxu_stop`, `.shutdown = oxu_shutdown`, `.urb_enqueue = oxu_urb_enqueue`, `.urb_dequeue = oxu_urb_dequeue`, `.endpoint_disable = oxu_endpoint_disable`, `.get_frame_number = oxu_get_frame`, `.hub_status_data = oxu_hub_status_data`, `.hub_control = oxu_hub_control`, and PM bus callbacks. The platform entry points are `oxu_drv_probe`, `oxu_drv_remove`, and `oxu_drv_shutdown`, registered by `module_platform_driver(oxu_driver)`.

Memory management is centered on `ehci_mem_init`, `ehci_mem_cleanup`, `ehci_qtd_alloc`, `oxu_qtd_free`, `oxu_qh_alloc`, `oxu_qh_free`, `oxu_buf_alloc`, `oxu_buf_free`, `oxu_murb_alloc`, and `oxu_murb_free`. Queue construction and scheduling are handled by `qh_urb_transaction`, `qh_make`, `qh_append_tds`, `submit_async`, `intr_submit`, `qh_link_async`, `start_unlink_async`, `end_unlink_async`, `scan_async`, `qh_schedule`, `qh_link_periodic`, `qh_unlink_periodic`, and `scan_periodic`.

## Control Flow
Probe maps the platform MMIO resource, sets the IRQ trigger, allocates `struct oxu_info`, runs `oxu_configuration`, verifies the chip ID in `oxu_verify_id`, then calls `oxu_create` twice to create OTG and SPH HCDs sharing the same base mapping and IRQ. Each HCD reset (`oxu_reset`) selects either OTG or SPH capability/operational register windows and the opposite on-chip memory region, initializes locks and resource queues, then calls `oxu_hcd_init`.

Startup (`oxu_run`) resets the EHCI core, installs the periodic frame list and async head DMA addresses, configures segment addressing, sets RUN and CONFIGFLAG, and enables EHCI interrupt bits. Shutdown/stop halt or reset the core, turn off ports, clean schedules, delete timers, and free software allocations while leaving the chip in a state suitable for reboot or handoff.

URB submission first builds qTD chains with `qh_urb_transaction`, including OXU-local data buffers for every transfer. Control, bulk, and interrupt transfers share QH/qTD machinery. Bulk URBs larger than 4096 bytes are split by `oxu_urb_enqueue` into `struct oxu_murb` micro URBs whose `complete == NULL` marks them as internal fragments; completion of the last fragment gives back the original URB. Interrupt URBs additionally run through periodic bandwidth placement before qTDs are linked.

Interrupt flow starts at the top-level `oxu_irq`, which masks chip-level interrupts, dispatches to `oxu210_hcd_irq` for the active logical controller, then restores the top-level mask. The EHCI IRQ handler clears status, handles INT/ERR completions, async advance, port-change wakeups, and fatal errors, then calls `ehci_work`. `ehci_work` drains async reclaim, scans async QHs, scans periodic entries if enabled, and arms the watchdog when work remains.

## State and Persistence Behavior
All persistent runtime state is in `struct oxu_hcd` and the USB core's endpoint/URB fields. Endpoint state persists through `urb->ep->hcpriv` QH pointers, URBs reference QHs through `urb->hcpriv`, and the async/periodic hardware-visible lists live in OXU on-chip memory. `qh_used`, `qtd_used`, `db_used`, and `murb_used` are bitmap-like allocation ledgers protected by `mem_lock`; schedule state is protected by `lock`.

The driver does not persist data outside kernel memory or device registers. Across suspend/resume it saves command/schedule intent in `oxu->command`, `bus_suspended`, `reset_done`, and the existing software schedule lists, then rewrites operational registers on resume. Across remove, all HCD state is destroyed through USB core removal and local cleanup.

## Dependencies and Integration Points
This file depends on the Linux USB HCD core, platform-device resources, IRQ APIs, MMIO helpers, DMA address assumptions, timers, spinlocks, and USB hub-control semantics. It is heavily derived from EHCI concepts but is self-contained rather than using the generic EHCI HCD implementation. It integrates with root hub polling through `usb_hcd_poll_rh_status`, remote wake through `usb_hcd_resume_root_hub`, HCD death through `usb_hc_died`, and URB completion through `usb_hcd_giveback_urb`.

The hardware-specific integration points are OXU top registers such as `OXU_HOSTIFCONFIG`, `OXU_SOFTRESET`, `OXU_CHIPIRQSTATUS`, `OXU_CHIPIRQEN_SET/CLR`, `OXU_CLKCTRL_SET`, `OXU_ASO`, and per-core `OXU_USBMODE`. Module parameters `log2_irq_thresh`, `park`, and `ignore_oc` affect interrupt latency, async park behavior, and root-hub overcurrent reporting.

## Risks
The largest risk is resource exhaustion in tiny fixed pools: 16 QHs, 32 qTDs, 8 data buffers, and 8 micro URBs. Submission paths sometimes busy-wait with `schedule()` until resources become available, which can hide pressure and risks latency or livelock if completions stop. Bulk URB splitting relies on `complete == NULL` to distinguish internal fragments, so unusual URB initialization or future USB core assumptions could break fragment completion.

The on-chip buffer allocator does manual power-of-two block allocation and computes physical addresses with `virt_to_phys` on MMIO-backed memory. That is hardware-specific and fragile if memory attributes or DMA addressing assumptions change. Isochronous support returns `-ENOSYS`, so callers expecting full EHCI feature parity will fail for iso endpoints. Endpoint disable intentionally leaks a QH rather than freeing it when the core did not unlink URBs first, which protects correctness but is a recoverability risk.

Concurrency is complex: completion callbacks drop and reacquire `oxu->lock`, scans can modify schedules during callbacks, async reclaim is watchdog-backed, and the top-level IRQ temporarily masks shared chip interrupts. Regressions around QH state transitions (`LINKED`, `UNLINK`, `IDLE`, `COMPLETING`, `UNLINK_WAIT`) can lead to use-after-free, leaked references, or wedged schedules. Root-hub control manually manages reset/resume timing and port R/WC bits; incorrect writes can lose change notifications or leave ports in reset/resume.

## Test Signals
Compile coverage should include `CONFIG_USB`, platform bus support, and this driver enabled, with warnings checked around pointer arithmetic on `void *`, `__iomem`, and DMA addresses. Runtime signals include successful probe showing OXU device ID and both OTG/SPH HCDs added, USB 2.0 devices enumerating on both logical controllers, bulk transfers above and below 4096 bytes completing with correct byte counts, interrupt devices maintaining periodic schedule bandwidth, and iso submissions returning the expected `-ENOSYS`.

Stress tests should force QH/qTD/buffer exhaustion with concurrent bulk and interrupt endpoints, test unlink while transfers are active, repeatedly disable endpoints, suspend/resume with remote wake enabled, and verify watchdog recovery when async-advance IRQs are delayed. Hub tests should cover reset completion, suspend/resume change bits, overcurrent behavior with and without `ignore_oc`, and remove/shutdown paths leaving no active IRQ or timer.
