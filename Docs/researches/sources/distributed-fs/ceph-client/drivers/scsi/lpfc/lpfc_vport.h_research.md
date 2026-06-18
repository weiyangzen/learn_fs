# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vport.h

## Purpose
`lpfc_vport.h` declares the LPFC virtual-port management interface and legacy vport information structures. It defines API version bits, vport information and creation payloads, vport return codes, command tags, and the exported functions implemented by `lpfc_vport.c`.

## Important APIs, Types, And Functions
`struct vport_info` is a reporting structure with API version bits, physical/virtual link type, active/offline/failed state, failure reason and previous reason, WWNN/WWPN, SCSI host pointer, and physical-link capacity counters for vports and RPIs. `struct vport_data` describes creation input: API version, options such as `VPORT_OPT_AUTORETRY`, WWNN/WWPN, and the resulting `vport_shost`.

Return codes are `VPORT_OK`, `VPORT_ERROR`, `VPORT_INVAL`, `VPORT_NOMEM`, and `VPORT_NORESOURCES`. Function declarations include `lpfc_vport_create()`, `lpfc_vport_delete()`, `lpfc_vport_getinfo()`, `lpfc_vport_tgt_remove()`, `lpfc_create_vport_work_array()`, `lpfc_destroy_vport_work_array()`, `lpfc_alloc_vpi()`, and `lpfc_vport_set_state()`. `DID_VPORT_ERROR` defines a host-byte result code for virtual-link failures. `struct vport_cmd_tag` packages a vport operation command and payload.

## Control Flow
The header has no executable control flow. It defines the call surface used by FC transport and LPFC internals. Create/delete/disable flows in `lpfc_vport.c` consume these prototypes and return codes. Work-array helpers let callers snapshot active vports with SCSI host references and later release them.

## State And Persistence
The structures describe runtime state only. `vport_info` is a snapshot-style payload; `vport_data` and `vport_cmd_tag` are command/control payloads. No persistent storage is defined.

## Dependencies And Integration Points
The header depends on declarations for `struct Scsi_Host`, `struct fc_vport`, `struct lpfc_hba`, `struct lpfc_vport`, and `enum fc_vport_state` from SCSI/FC transport and LPFC headers included by users. It integrates LPFC vport code with the FC transport, SCSI host layer, and any legacy management path still using `vport_cmd_tag`.

## Risks And Edge Cases
Several APIs are declared here but not implemented in the paired source file section, so users must include the broader LPFC tree when tracing them. The information structures expose raw `Scsi_Host *` pointers and fixed-size WWN arrays, which are kernel-internal contracts rather than stable UAPI. Return codes are negative integers that are distinct from standard Linux `-errno` values, so callers must not blindly mix them.

## Test Signals
Validation signals include compile checks for all declarations, FC transport create/delete/disable callbacks returning documented `VPORT_*` values, `DID_VPORT_ERROR` result propagation for failed virtual links, work-array reference balancing, and any management path using `vport_info` correctly reporting physical versus virtual capacity counters.
