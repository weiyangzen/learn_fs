# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/displayport.c

Purpose: Provides DisplayPort alternate-mode support for UCSI ports, bridging Type-C altmode operations to UCSI current/new CAM commands and emulating DisplayPort VDM responses for the Type-C altmode framework.

Important APIs/types/functions: `struct ucsi_dp` stores DP altmode state, connector pointer, CAM offset, override support, VDM header/data, and work item. Main functions are `ucsi_register_displayport`, `ucsi_displayport_enter`, `ucsi_displayport_exit`, `ucsi_displayport_vdm`, `ucsi_displayport_configure`, `ucsi_displayport_status_update`, `ucsi_displayport_work`, and `ucsi_displayport_remove_partner`.

Control flow and state: registration forces conservative DP capabilities and all common pin assignments, registers a port altmode, attaches ops, and stores the CAM offset. Enter checks the active CAM and, when possible, prepares an ACK for Enter Mode while letting later Configure send `SET_NEW_CAM`. VDM handling responds to Status Update and Configure; Configure may issue UCSI `SET_NEW_CAM` with selected pins and marks the mode initialized. Work asynchronously calls `typec_altmode_vdm`.

Persistence behavior: per-altmode state is device-managed and lives for the altmode lifetime. `initialized`, DP status/config, and pending VDM fields are reset on partner removal.

Dependencies/integration points: depends on UCSI core connector locking, Type-C DP altmode APIs, USB PD VDO helpers, `typec_altmode_vdm`, and UCSI optional altmode override capability.

Risks: without firmware override support, user-initiated changes are rejected after initialization. Status Update is partly guessed because UCSI does not expose the DP Status VDO. Incorrect pin selection can misconfigure mux policy downstream. Work must be canceled on partner removal to avoid use-after-disconnect.

Test signals: DP altmode registration, enter/exit behavior with and without override, `SET_NEW_CAM` command success, generated VDM ACK/NAK behavior, active altmode updates after configure, partner removal cancellation, and DP monitor/mux behavior across reconnects.
