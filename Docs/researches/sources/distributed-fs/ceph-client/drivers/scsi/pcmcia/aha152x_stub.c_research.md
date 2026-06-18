# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/aha152x_stub.c

Purpose: PCMCIA binding layer for AHA152X-compatible SCSI cards. It configures PCMCIA resources and passes card settings to the shared AHA152X core.

Important APIs/functions: module parameters `host_id`, `reconnect`, `parity`, `synchronous`, `reset_delay`, and `ext_trans` populate `struct aha152x_setup`. `aha152x_probe()` allocates private state and starts config. `aha152x_config_check()` chooses the I/O resource. `aha152x_config_cs()` enables the card and calls `aha152x_probe_one()`. `aha152x_release_cs()` and `aha152x_resume()` handle teardown and reset.

Control flow/state: probe allocates `scsi_info_t`; config loops resources, enables the device, creates the SCSI host via shared core, and stores it in `info->host`. Remove releases and frees private data. Module parameters persist for module lifetime.

Dependencies/integration: PCMCIA Card Services, SCSI midlayer, and AHA152X core built via `aha152x_core.c`.

Risks/test signals: release lacks a local NULL guard for partial probe failures. Test product-ID matching, resource failure cleanup, SCSI scan, resume reset, and remove.
