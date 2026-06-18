# sources/distributed-fs/ceph-client/drivers/usb/core/hcd.c

## Purpose

`hcd.c` is the common USB Host Controller Driver framework. It provides virtual root-hub descriptors and request handling, bus-number registration, root-hub registration, URB queue/link/unlink/giveback lifecycle, DMA mapping and local-memory bounce buffering, endpoint shutdown/bandwidth/streams helpers, root-hub and bus PM, IRQ dispatch, HCD death handling, HCD allocation/refcounting, add/remove lifecycle, local memory setup, and usbmon registration.

## Important APIs, Types, and Functions

- Global state and locks: `usb_bus_idr`, `usb_bus_idr_lock`, `hcd_root_hub_lock`, `hcd_urb_list_lock`, `hcd_urb_unlink_lock`, and `usb_kill_urb_queue`.
- Root hub descriptors and control: static root-hub device/config descriptors, `ascii2desc()`, `rh_string()`, `rh_call_control()`, `usb_hcd_poll_rh_status()`, `rh_queue_status()`, `rh_urb_enqueue()`, and `usb_rh_urb_dequeue()`.
- Bus/root hub lifecycle: `usb_bus_init()`, `usb_register_bus()`, `usb_deregister_bus()`, `register_root_hub()`, `usb_hcd_start_port_resume()`, and `usb_hcd_end_port_resume()`.
- URB lifecycle: `usb_hcd_link_urb_to_ep()`, `usb_hcd_check_unlink_urb()`, `usb_hcd_unlink_urb_from_ep()`, `usb_hcd_submit_urb()`, `usb_hcd_unlink_urb()`, `usb_hcd_giveback_urb()`, `__usb_hcd_giveback_urb()`, and `usb_giveback_urb_bh()`.
- DMA/local memory: `hcd_alloc_coherent()`, `hcd_free_coherent()`, `usb_hcd_map_urb_for_dma()`, `usb_hcd_unmap_urb_setup_for_dma()`, `usb_hcd_unmap_urb_for_dma()`, `map_urb_for_dma()`, and `unmap_urb_for_dma()`.
- Endpoint/bandwidth/stream helpers: `usb_hcd_flush_endpoint()`, `usb_hcd_alloc_bandwidth()`, `usb_hcd_disable_endpoint()`, `usb_hcd_reset_endpoint()`, `usb_alloc_streams()`, `usb_free_streams()`, `usb_hcd_synchronize_unlinks()`, and `usb_hcd_get_frame_number()`.
- PM and wake: `hcd_bus_suspend()`, `hcd_bus_resume()`, `usb_hcd_resume_root_hub()`, `hcd_resume_work()`, and OTG-only `usb_bus_start_enum()`.
- HCD infrastructure: `usb_hcd_irq()`, `usb_hc_died()`, `__usb_create_hcd()`, `usb_create_hcd()`, `usb_create_shared_hcd()`, `usb_get_hcd()`, `usb_put_hcd()`, `usb_hcd_is_primary_hcd()`, `usb_hcd_find_raw_port_number()`, `usb_hcd_request_irqs()`, `usb_add_hcd()`, `usb_remove_hcd()`, `usb_hcd_platform_shutdown()`, `usb_hcd_setup_local_mem()`, `usb_mon_register()`, and `usb_mon_deregister()`.

## Control Flow

`usb_add_hcd()` is the main bring-up path. It allocates/init/powers PHY roothub resources unless skipped, records device authorization policy from the module parameter, marks hardware accessible and interfaces authorized, creates HCD buffer pools, registers a USB bus number, allocates a root-hub `usb_device`, sets root-hub speed/lane fields from `hcd->speed`, enables root-hub wakeup capability, sets `HCD_FLAG_RH_RUNNING`, calls optional `driver->reset()`, calibrates PHYs, initializes high- and low-priority giveback workqueues, requests the primary IRQ, starts the hardware with `driver->start()`, and registers the root hub unless registration is deferred. Error labels unwind in reverse: stop, free IRQ, drop root hub, deregister bus, destroy buffers, power off/exit PHY.

Root-hub control URBs are handled synchronously in `rh_call_control()`. The function links the URB under root-hub lock, decodes the setup packet, responds directly to standard device/config/string/interface/endpoint requests where possible, delegates hub-class and BOS requests to `hcd->driver->hub_control()`, patches descriptors for wakeup and integrated transaction translator capability, copies response bytes, unlinks the URB, and completes it through `usb_hcd_giveback_urb()`. Root-hub interrupt URBs are stored as `hcd->status_urb` by `rh_queue_status()` and completed by `usb_hcd_poll_rh_status()` when `hub_status_data()` reports changes, with timer polling used when the HCD does not use new polling.

Normal URB submission in `usb_hcd_submit_urb()` increments URB/device refs, notifies usbmon, routes root-hub URBs to `rh_urb_enqueue()`, maps DMA for non-root URBs, and calls `hcd->driver->urb_enqueue()`. On submission error it reports usbmon submit error, clears state, decrements `use_count` and `urbnum`, wakes kill waiters when rejected, and drops the URB ref. Unlinking uses `usb_hcd_unlink_urb()` to safely hold the device while `unlink1()` calls either root-hub dequeue or HCD `urb_dequeue()`.

Completion flows through `usb_hcd_giveback_urb()`. The final status is stored in `urb->unlinked`; interrupt/isoc URBs and all root-hub URBs are normally queued to high-priority or low-priority BH work, while other URBs can complete immediately when `HCD_BH` is not set. `__usb_hcd_giveback_urb()` clears `hcpriv`, enforces `URB_SHORT_NOT_OK`, unmaps DMA, notifies usbmon, suspends anchor wakeups, unanchors, reports LED activity, invokes the completion callback under KCOV softirq coverage, resumes anchor wakeups, decrements use count with memory ordering, wakes kill waiters, and drops the URB ref.

Endpoint shutdown uses `usb_hcd_flush_endpoint()` to repeatedly unlink queued URBs and then wait until the endpoint queue drains. `usb_hcd_alloc_bandwidth()` reprograms HCD endpoint scheduling when configurations or alternate settings change, using `add_endpoint`, `drop_endpoint`, `check_bandwidth`, and `reset_bandwidth` driver hooks. Streams APIs validate SuperSpeed bulk endpoints and delegate stream allocation/free to the HCD.

PM root-hub bus suspend clears `HCD_FLAG_RH_RUNNING`, moves state to quiescing, calls `driver->bus_suspend()`, sets the root hub suspended, optionally suspends PHYs, and checks for wakeup races through `hub_status_data()`. Resume powers/calibrates PHYs, calls `driver->bus_resume()`, clears wakeup pending, restores root-hub device state and `HCD_FLAG_RH_RUNNING`, and delays for global resume when child ports need it. `usb_hcd_resume_root_hub()` records wakeup pending and queues freezable work to call `usb_remote_wakeup()`.

Removal in `usb_remove_hcd()` clears root-hub running, marks state quiescing, marks the root hub unregistered under lock, cancels wakeup/death work, disconnects the root hub, stops polling and hardware, frees the primary IRQ, deregisters the bus, destroys buffers, powers off/exits PHYs, invalidates the root-hub pointer under peer lock, and clears HCD flags.

## State and Persistence Behavior

State is entirely live kernel state. Bus numbers are allocated from `usb_bus_idr`; root-hub device state lives in `hcd->self.root_hub`; URB queue membership lives on endpoint `urb_list`; HCD state uses flags such as `HCD_FLAG_RH_RUNNING`, `HCD_FLAG_POLL_RH`, `HCD_FLAG_POLL_PENDING`, `HCD_FLAG_DEAD`, `HCD_FLAG_HW_ACCESSIBLE`, and state values such as `HC_STATE_RUNNING`, `QUIESCING`, `SUSPENDED`, and `HALT`. DMA mapping state is tracked in URB transfer flags and DMA handles. Shared HCDs share address0 and bandwidth mutexes and cross-reference each other until final release. No on-disk persistence exists.

## Dependencies and Integration Points

`hcd.c` is central to the USB stack. It integrates with HCD driver callbacks in `struct hc_driver`, hub core (`usb_new_device`, `usb_disconnect`, `usb_kick_hub_wq`, `usb_hub_for_each_child`), PM runtime/system paths, USB PHY roothub helpers, DMA mapping APIs, genalloc local memory pools, workqueues/timers, IRQ core, usbmon, KCOV, LED activity, OTG, root-hub descriptor emulation, and platform/PCI glue.

## Risks and Edge Cases

- URB lifecycle races are high risk: list membership, `urb->unlinked`, `use_count`, `reject`, and device references must stay ordered across submit, unlink, giveback, kill, and disconnect.
- DMA mapping flags must be idempotently cleared; setup and transfer mappings can be single, page, SG, sgtable sync, or local-memory bounce buffers.
- Root-hub control handling mixes generic emulation with HCD-specific `hub_control()`; incorrect descriptor length or patching can break enumeration.
- Root-hub polling must not complete a stale `status_urb` after removal or HCD death.
- Shared HCD release must not free shared mutexes while a peer remains.
- `usb_hc_died()` must handle both primary and shared HCDs and wake hub cleanup exactly once.
- `usb_hcd_alloc_bandwidth()` must roll back HCD schedule state on add/drop/check failures or later transfers may use invalid endpoint schedules.
- Suspend/resume wakeup races are explicitly checked; missing a pending wake can leave devices inaccessible.
- Local-memory bounce buffering stores original virtual addresses at the end of the bounce buffer, making size and alignment correctness important.

## Test Signals

Signals include HCD add/remove under success and failure injection, root-hub descriptor reads across USB1.1/2/3/3.1/3.2 speeds, root-hub status URB polling and dequeue, normal URB submit/unlink/kill/giveback, DMA mapping error paths including stack-buffer warnings, SG and sgtable sync paths, endpoint flush on disconnect/suspend, configuration and altsetting bandwidth checks, SuperSpeed stream allocation/free, root-hub bus suspend/resume with wakeup races, HCD death handling, shared HCD creation/release, local-memory pool setup, usbmon registration, and leak/race detection with lockdep/KASAN/KCSAN.
