<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_hp_sw.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_hp_sw.c

Purpose: implements a minimal HP/Compaq MSA 1000 active/passive SCSI device handler for firmware that requires START STOP UNIT to activate a passive path. It detects active versus passive paths using TEST UNIT READY sense data and blocks I/O on passive paths until activation succeeds.

Important APIs/types/functions: `struct hp_sw_dh_data` stores path state, retry settings, and the SCSI device pointer. Core helpers are `hp_sw_tur()`, `tur_done()`, `hp_sw_start_stop()`, `hp_sw_prep_fn()`, `hp_sw_activate()`, `hp_sw_bus_attach()`, and `hp_sw_bus_detach()`. The registered handler `hp_sw_dh` provides attach/detach/activate/prep_fn callbacks.

Control flow: attach allocates handler data, sends TEST UNIT READY, marks the path active on success or passive on NOT READY `04/02`, and rejects unknown states. `prep_fn` fails requests quietly unless `path_state` is active. Activation repeats TEST UNIT READY and, when the path is passive, sends START STOP UNIT with retries for switch-over-in-progress sense `04/03`; it then calls the multipath completion callback.

State and persistence: per-device in-memory state records only current path state and retry values. START STOP UNIT changes array path ownership externally, but no local persistence exists. `retry_cnt` is present in the struct but not actively used by the implementation.

Dependencies and integration: depends on SCSI command execution, TEST UNIT READY, START STOP UNIT, sense parsing, failure-definition retry handling, request `RQF_QUIET`, and the SCSI device-handler core. It is intended for dm-multipath active/passive path activation on old MSA firmware.

Risks: support is intentionally narrow and keyed to specific sense codes. No explicit `check_sense` callback means runtime path-state changes are learned only through activation/attach, not arbitrary I/O sense. The driver stores retry fields with limited use, and activation is synchronous around command execution. Unsupported firmware may be misdetected or fail I/O until multipath retries another path.

Test signals: TEST UNIT READY success and NOT READY `04/02` paths, START STOP UNIT activation with retry on `04/03`, `prep_fn` blocking passive paths, attach rejection for unknown TUR failures, callback result propagation, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_hp_sw.c -->
