# sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg.c

Purpose: implements ChipIdea OTGSC access abstraction, ID/VBUS role selection, VBUS connect/disconnect handling, ID-based role switching, and OTG workqueue lifecycle.

Important APIs/types/functions: provides `hw_read_otgsc`, `hw_write_otgsc`, `ci_otg_role`, `ci_handle_vbus_change`, `ci_handle_id_switch`, `ci_hdrc_otg_init`, and `ci_hdrc_otg_destroy`; internal worker is `ci_otg_work`.

Control flow: OTGSC reads merge hardware state with extcon or USB role-switch synthetic ID/VBUS state. OTGSC writes clear cable change flags and suppress hardware interrupt enables when external notifiers are used. ID switch locks the role mutex, stops the old role, optionally waits for VBUS to fall before gadget start, starts the new role, and processes VBUS. The workqueue handles ID and B-session-valid events under runtime PM, or delegates to OTG FSM first.

State and persistence: uses `ci->id_event`, `ci->b_sess_valid_event`, `ci->vbus_active`, cable `connected/changed/enabled` fields, current role, workqueue, and OTG FSM state when enabled.

Dependencies and integration: depends on extcon, USB role-switch, gadget VBUS APIs, runtime PM, workqueues, `bits.h` OTGSC masks, and role callbacks from host/gadget modules.

Risks: external connector state deliberately overrides hardware OTGSC bits; incorrect extcon or role-switch updates can force wrong roles. IRQ is disabled while work is queued and must be re-enabled on all paths.

Test signals: ID/VBUS extcon events, role-switch user requests, hardware OTGSC interrupts, VBUS fall wait timeout, gadget VBUS connect/disconnect, and OTG FSM mode delegation.
