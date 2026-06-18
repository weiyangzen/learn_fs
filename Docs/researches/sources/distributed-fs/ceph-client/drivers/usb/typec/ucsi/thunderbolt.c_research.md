# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/thunderbolt.c

Purpose: Adds Thunderbolt alternate-mode control for UCSI ports that support altmode override, mapping Type-C altmode enter/exit/VDM calls to UCSI `SET_NEW_CAM` and generated Thunderbolt VDM acknowledgements.

Important APIs/types/functions: `struct ucsi_tbt` stores the connector, altmode, work item, CAM offset, and pending VDM header. Main functions are `ucsi_register_thunderbolt`, `ucsi_thunderbolt_enter`, `ucsi_thunderbolt_exit`, `ucsi_thunderbolt_vdm`, `ucsi_thunderbolt_set_altmode`, `ucsi_thunderbolt_work`, and `ucsi_thunderbolt_remove_partner`.

Control flow and state: registration always registers the port altmode, but only installs ops/private state if override is supported. Enter locks the connector, checks current CAM, sends `SET_NEW_CAM` with the requested VDO if no CAM is active, updates active altmode state, and schedules VDM ACK work. Exit sends `SET_NEW_CAM` with enter cleared. Generic incoming VDM init commands are ACKed asynchronously.

Persistence behavior: per-altmode device-managed state exists for the altmode lifetime. Pending VDM header is cleared after work runs; work is canceled on partner removal.

Dependencies/integration points: depends on Type-C Thunderbolt altmode definitions, USB PD VDO helpers, UCSI connector locking, UCSI command encoding, and Type-C altmode VDM delivery.

Risks: if override is not supported, the file registers a passive altmode without active control callbacks. Current CAM index validation must stay aligned with UCSI core altmode arrays. Generated ACKs assume firmware accepted the CAM command and do not carry additional data VDOs.

Test signals: Thunderbolt altmode registration, enter/exit with valid/invalid current CAM, `SET_NEW_CAM` command success/failure, VDM ACK emission, active altmode update, disconnect cancellation, and behavior with override disabled.
