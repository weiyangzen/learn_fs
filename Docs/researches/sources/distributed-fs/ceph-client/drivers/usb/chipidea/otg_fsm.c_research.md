# sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg_fsm.c

Purpose: implements ChipIdea support for the Linux USB OTG finite state machine, including HNP/SRP sysfs controls, OTG timers, VBUS driving, local connection/SOF controls, SRP pulsing, role start/stop operations, IRQ event translation, and FSM initialization/removal.

Important APIs/types/functions: public functions are `ci_hdrc_otg_fsm_init`, `ci_hdrc_otg_fsm_start`, `ci_otg_fsm_work`, `ci_otg_fsm_irq`, and `ci_hdrc_otg_fsm_remove`. Key internals include sysfs stores for `a_bus_req`, `a_bus_drop`, `b_bus_req`, `a_clr_err`, timer management, `ci_otg_drv_vbus`, `ci_otg_loc_conn`, `ci_otg_loc_sof`, `ci_otg_start_pulse`, `ci_otg_start_host`, and `ci_otg_start_gadget`.

Control flow: sysfs inputs update FSM fields under `fsm.lock` and queue OTG work. Hrtimer callbacks mark timeout fields and queue work. `ci_otg_fsm_irq` reads OTGSC/intr status, updates FSM variables for ID, BSV, AVV, data pulse, suspend/resume, and port connection events, then queues the state machine. `ci_otg_fsm_work` runs `otg_statemachine` under runtime PM and handles follow-up transitions.

State and persistence: persistent FSM state lives in `ci->fsm`, `ci->otg`, timer arrays, enabled timer bitmask, next timer, gadget HNP flags, runtime PM refs, and regulator/port-power state.

Dependencies and integration: depends on Linux OTG FSM core, gadget and HCD APIs, regulators, runtime PM, ChipIdea role start/stop, OTGSC helpers, and sysfs.

Risks: timer ordering in `ci_otg_del_timer` appears to compare `next_timer` and `cur_timer` in a way that may not select the earliest timeout as intended. Role start/stop in FSM operations assumes both host and gadget roles exist. Runtime PM refs around SRP data pulse must balance.

Test signals: OTG compliance HNP/SRP scenarios, sysfs input toggles, SRP timeout behavior, A/B role swaps, port connect/disconnect IRQs, VBUS regulator transitions, and suspend/resume wake by SRP.
