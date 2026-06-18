# sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg.h

Purpose: declares ChipIdea OTG helper APIs and provides the shared queued-work helper used by IRQ and FSM paths.

Important APIs/types/functions: prototypes `hw_read_otgsc`, `hw_write_otgsc`, `ci_hdrc_otg_init`, `ci_hdrc_otg_destroy`, `ci_otg_role`, `ci_handle_vbus_change`, and `ci_handle_id_switch`; defines inline `ci_otg_queue_work`.

Control flow: `ci_otg_queue_work` disables the controller IRQ without synchronization, queues `ci->work`, and immediately re-enables the IRQ if the work was already pending.

State and persistence: no state of its own, but the helper operates on `ci->irq`, `ci->wq`, and `ci->work`.

Dependencies and integration: included by core, debug, OTG, and OTG FSM code. It bridges hard IRQ handling to process-context role switching.

Risks: callers must ensure the workqueue has been created before queuing and that IRQ disable/enable balance is preserved if queueing fails due to already-pending work.

Test signals: repeated OTG events while work is pending, destroy/unbind after queued work, and FSM timer callbacks queuing work.
