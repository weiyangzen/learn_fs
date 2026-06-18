# sources/distributed-fs/ceph-client/drivers/usb/host/xen-hcd.c

## Purpose
`xen-hcd.c` implements a Xen paravirtual USB host controller frontend. It presents USB 1.1 or USB 2.0 HCDs to Linux, but forwards URB work to a Xen backend through shared rings and grant references. It also emulates a virtual root hub whose port events arrive over a Xen connection ring.

## Important APIs, Types, And Functions
`struct xenhcd_info` is the HCD-private state: pending/in-progress/giveback lists, lock, watchdog timer, virtual port/device arrays, xenbus device, URB and connection rings, event channel/IRQ, request shadows, freelist, and error flag. `struct urb_priv` tracks one URB's request IDs, unlink status, and giveback status. Hub helpers manage port connection, power, suspend, resume, reset, descriptor/status/control. Grant/ring helpers include `xenhcd_map_urb_for_request()`, `xenhcd_gnttab_map()`, `xenhcd_gnttab_done()`, `xenhcd_do_request()`, `xenhcd_urb_request_done()`, and `xenhcd_conn_notify()`. HCD callbacks are `xenhcd_setup()`, `xenhcd_run()`, `xenhcd_stop()`, `xenhcd_urb_enqueue()`, `xenhcd_urb_dequeue()`, and `xenhcd_get_frame()`. Xenbus lifecycle is handled by probe, backend-state changes, connect, disconnect, ring setup/destruction, and module init/exit.

## Control Flow
Probe creates an HCD after reading backend `num-ports` and `usb-ver`, initializes shadow freelist, stores driver data, and calls `usb_add_hcd()`. Backend transition to connected sets up URB/connection rings, allocates an event channel, publishes ring refs and event channel in xenstore, primes connection requests, and switches frontend state. URB enqueue allocates `urb_priv`, then either sends a ring request immediately or queues it if the ring is full or earlier requests are pending. Mapping grants backend access to transfer buffers and ISO descriptors. IRQ handling drains URB responses and connection responses until no more work, ending grant access and polling root-hub status when ports change. Dequeue sends an unlink request or moves not-yet-submitted URBs to giveback waiting.

## State And Persistence Behavior
State is runtime-only and shared between frontend memory, Xen rings, and backend-visible grant references. `shadow[]` tracks outstanding ring slots and their URBs. `pending_submit_list`, `pending_unlink_list`, `in_progress_list`, and `giveback_waiting_list` define the URB lifecycle. Virtual root-hub state is synthesized in `ports[]` and `devices[]`. The watchdog timer retries pending work and gives back already-unlinked URBs. Protocol errors set `info->error`, after which IRQs are treated as handled but no new work should proceed.

## Dependencies And Integration Points
The driver depends on Xen domain detection, xenbus, event channels, grant table APIs, Xen USB interface definitions, Linux USB HCD core, timers, slabs, and root-hub polling. The backend must implement the `vusb` protocol, publish valid xenstore keys, consume grants, and return well-formed ring responses.

## Risks And Edge Cases
Grant lifetime is critical: failure to release grants marks protocol error, while overlarge segment counts return `-E2BIG`. Ring overflow is handled with pending lists and watchdog timers, but ordering between submit and unlink queues is subtle. `xenhcd_pipe_urb_to_xenusb()` uses a static local variable, but callers hold `info->lock`; future lockless use would be unsafe. Root-hub resume/reset completion is timer-driven through `GetPortStatus`. On backend close, `usb_remove_hcd()` precedes ring destruction in remove/disconnect paths, so lifecycle ordering must remain balanced.

## Test Signals
Test xenbus probe with invalid and valid `num-ports`/`usb-ver`, backend connection and close, URB submit/completion for all transfer types, ISO descriptor grant mapping, ring-full queuing, URB unlink before submit and after submit, backend protocol errors, hotplug connection ring events, root-port reset/resume/power, suspend/resume, and module unload with pending grants.
