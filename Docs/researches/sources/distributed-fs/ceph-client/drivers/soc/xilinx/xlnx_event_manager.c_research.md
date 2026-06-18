# sources/distributed-fs/ceph-client/drivers/soc/xilinx/xlnx_event_manager.c

## Purpose
This file implements the Xilinx firmware event management driver. It lets client drivers register callbacks for firmware notify events or suspend-init callbacks, receives firmware callbacks through an SGI, dispatches callbacks from an in-kernel hash table, and re-registers one-shot notifications with firmware.

## Important APIs, Types, And Functions
Exported APIs are `xlnx_register_event` and `xlnx_unregister_event`. Main internal types are `struct registered_event_data` and `struct agent_cb`. Important helpers include `xlnx_is_error_event`, add/remove callback helpers, `xlnx_call_notify_cb_handler`, `xlnx_call_suspend_cb_handler`, `xlnx_event_handler`, SGI init/cleanup helpers, CPU hotplug callbacks, and probe/remove.

## Control Flow
Probe checks `PM_REGISTER_NOTIFIER` firmware feature/version, maps SGI 15 or module-param `sgi_num` through the GIC IRQ domain, requests a percpu IRQ, registers CPU hotplug enable/disable callbacks, registers the SGI with firmware, and sets availability to 0. Registration validates callback type/function, adds callback data to `reg_driver_map`, splits error-event bitmasks into single-event keys for Versal/Versal Net error nodes, and calls `zynqmp_pm_register_notifier`. The IRQ handler fetches callback payload via `GET_CALLBACK_DATA`, dispatches notify or suspend callbacks, splits error masks if needed, and re-registers notify events for future delivery. Remove frees all hash/list entries, unregisters SGI, removes hotplug state, frees percpu IRQ, and marks unavailable.

## State And Persistence
Global state includes `virq_sgi`, `event_manager_availability`, `sgi_num`, `is_need_to_unregister`, and hash table `reg_driver_map`. Each event stores key, callback type, wake flag, and callback list. Firmware notifier registrations persist until unregistered or driver removal.

## Dependencies And Integration Points
It depends on ZynqMP/Versal firmware APIs, GIC IRQ domain SGI mapping, percpu IRQs, CPU hotplug, Linux hashtable/list helpers, and public `linux/firmware/xlnx-event-manager.h`. Kconfig requires `ZYNQMP_FIRMWARE`.

## Risks And Test Signals
Risks include limited locking around hash/list mutation versus IRQ dispatch, global `is_need_to_unregister` semantics across multi-bit unregisters, SGI mapping assumptions, one-shot firmware notifier re-registration failures, and availability returning `-EACCES` before probe. Test signals include probe logs for SGI registration, successful callback registration/unregistration, callbacks firing for normal and error events, CPU hotplug enable/disable coverage, and clean remove freeing notifier state.
