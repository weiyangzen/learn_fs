# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_phy.c

## Purpose
`sas_phy.c` implements libsas phy event workers and registration of local phys with the SCSI SAS transport class. It translates hardware/link events into port deformation, hard reset, spinup-hold release, resume-timeout cleanup, or phy shutdown.

## Important APIs, types, and functions
- `sas_phye_loss_of_signal` clears the phy error counter and deforms the port as gone.
- `sas_phye_oob_done` clears OOB error state after successful out-of-band negotiation.
- `sas_phye_oob_error` deforms the current port, then for enabled standalone phys attempts two hard resets and disables the phy on the third error if LLDD phy control is available.
- `sas_phye_spinup_hold` releases spinup hold via `PHY_FUNC_RELEASE_SPINUP_HOLD`.
- `sas_phye_resume_timeout` cancels itself if the LLDD already cleared suspension; otherwise it clears `suspended` and deforms the port.
- `sas_phye_shutdown` disables an enabled phy through `PHY_FUNC_DISABLE`, logs LLDD failures, and clears `in_shutdown`.
- `sas_register_phys` initializes every `asd_sas_phy`, allocates a transport `sas_phy`, populates identify and link-rate fields, and adds it to the transport class.
- `sas_unregister_phys` deletes and frees each transport phy.
- `sas_phy_event_fns` maps `PHYE_*` enum values to the corresponding work functions.

## Control flow and state
Phy event workers receive `struct asd_sas_event` through `to_asd_sas_event(work)` and operate on `event->phy`. Port membership changes are delegated to `sas_deform_port`. Error escalation is local to `asd_sas_phy.error`: OOB errors increment the counter only when no port is formed, the phy is enabled, and LLDD control exists; the third error disables the phy and resets the counter.

Registration loops over `sas_ha->num_phys`. Each `asd_sas_phy` is linked to its HA, event counter, frame locks, primitive lock, port list node, and transport object. If allocation or `sas_phy_add` fails, the function rolls back previously added phys by deleting and freeing their transport objects.

## State and persistence behavior
Phy state is transient kernel state: `error`, `event_nr`, `in_shutdown`, `enabled`, `suspended`, frame data, `port`, and `phy->phy` transport pointer. Link-rate fields are initialized to `SAS_LINK_RATE_UNKNOWN` and later updated by LLDD/discovery paths. No durable persistence is performed.

## Dependencies and integration points
This file integrates with `sas_port.c` through `sas_deform_port`, with `sas_init.c` event allocation and thresholding, with the SCSI SAS transport through `sas_phy_alloc/add/delete/free`, and with LLDD callbacks through `lldd_control_phy`.

## Risks and edge cases
- `sas_phye_oob_error` assumes repeated OOB errors on a standalone enabled phy indicate a bad link and can disable it; overly aggressive LLDD event reporting can take a phy offline.
- Resume timeout has an intentional race with late resume completion; it rechecks `phy->suspended` before deformation.
- Registration rollback must stay in sync with initialization order to avoid transport object leaks.
- `sas_unregister_phys` assumes all phys were registered; partial-registration error paths must not call it on uninitialized entries.

## Test signals
- Inject `PHYE_OOB_ERROR` repeatedly and verify hard reset, hard reset, disable ordering.
- Exercise `PHYE_RESUME_TIMEOUT` both before and after LLDD clears `suspended`.
- Fail `sas_phy_alloc` or `sas_phy_add` mid-registration and check rollback.
- Confirm transport class shows expected local phy identity and unknown initial link rates.
