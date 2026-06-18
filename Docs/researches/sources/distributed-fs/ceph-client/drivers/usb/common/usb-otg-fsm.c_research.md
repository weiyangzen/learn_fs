# Research: sources/distributed-fs/ceph-client/drivers/usb/common/usb-otg-fsm.c

Purpose: implements the USB 2.0 OTG finite state machine used by controller drivers that provide an `otg_fsm`. It transitions between A-device and B-device OTG states, starts/stops host or gadget protocols, manages OTG timers, drives VBUS/connect/SOF callbacks, and supports HNP polling.

Important functions: `otg_statemachine` is exported and performs transition decisions under `fsm->lock`. `otg_set_state` executes entry actions for each new state. `otg_leave_state` cleans up timers and flags from the old state. `otg_set_protocol` stops the old host/gadget role and starts the new one. `otg_hnp_polling_work` polls the connected device's OTG status selector and triggers HNP by clearing bus request flags.

Control flow: callers update inputs in `struct otg_fsm` and call `otg_statemachine`. The state machine tests current state plus inputs such as `id`, session valid, bus requests, VBUS valid, connect/suspend/resume flags, ADP/SRP flags, and timer timeout flags. Entry actions call controller-provided OTG helpers such as `otg_drv_vbus`, `otg_chrg_vbus`, `otg_loc_conn`, `otg_loc_sof`, `otg_start_host`, `otg_start_gadget`, `otg_add_timer`, and `otg_del_timer`.

State and persistence: all state is in `struct otg_fsm` and `fsm->otg->state`; no persistence. HNP polling uses delayed work and an optional controller-allocated `host_req_flag` buffer. `fsm->state_changed` reports whether a transition occurred.

Dependencies and integration points: depends on usbcore host/gadget/OTG APIs, hub child lookup, control messages to read/set OTG feature flags, workqueues, timers implemented by controller drivers, and `usb_otg_state_string` from common code.

Risks: transition correctness is highly stateful and tied to OTG spec timing. Missing timer cleanup can cause stale timeout flags. HNP polling assumes port 1 child on root hub and a valid `host_req_flag` buffer. Protocol start/stop failures abort state entry before `fsm->otg->state` is updated. Controllers must serialize input updates with `fsm->lock` discipline.

Test signals: controller or simulated FSM tests for every transition, timeout handling, ID changes, SRP/ADP paths, A/B host/peripheral handoff, HNP polling success/failure, protocol start/stop errors, and suspend/resume interactions.
