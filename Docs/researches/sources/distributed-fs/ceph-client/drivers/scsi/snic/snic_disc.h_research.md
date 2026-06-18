# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_disc.h

Purpose: this header defines SNIC discovery state, target objects, target states, and discovery-related APIs shared across the SNIC driver.

Important APIs, types, and functions: `enum snic_disc_state`, `struct snic_disc`, `enum snic_tgt_state`, `struct snic_tgt_priv`, and `struct snic_tgt` describe discovery and targets. Inline helpers map devices and SCSI targets to SNIC targets, test whether a `struct device` belongs to SNIC, convert targets to `Scsi_Host`, and check target readiness. Function declarations cover discovery init/start/term, report-target and target-info completions, discovery work, target release/deletion, and target I/O abort.

Control flow: `snic_main.c` initializes `snic->disc` and work items, `snic_disc.c` fills the target list, and `snic_scsi.c` uses `starget_to_tgt()` and `snic_tgt_chkready()` before queueing commands or selecting task-management behavior.

State and persistence: the header defines runtime-only structures. `disc.tgt_list`, `disc.state`, `disc.req_cnt`, `disc.rtgt_info`, and `snic_tgt.state/flags` drive target availability. `snic_tgt.dev.release` is used to verify SNIC target devices.

Dependencies and integration: includes `snic_fwint.h` for target wire types. It integrates Linux device model, SCSI target structures, workqueues, and SNIC firmware discovery responses.

Risks: `name` in `struct snic_tgt_priv` is declared as `char *name[SNIC_TGT_NAM_LEN]`, an array of pointers, not a character buffer; it is unused here but easy to misuse. `snic_tgt_chkready()` assumes non-null target pointers in callers unless checked earlier.

Test signals: build and runtime tests should exercise `starget_to_tgt()` for SNIC and non-SNIC parent devices, target readiness transitions, and target deletion while SCSI mid-layer still holds references.
