# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/qlogic_stub.c

Purpose: PCMCIA wrapper for Qlogic FAS SCSI cards using the shared `qlogicfas408` core.

Important APIs/functions: `qlogicfas_driver_template` delegates SCSI methods to `qlogicfas408_*`. `qlogic_detect()` probes chip type, sets up the chip, allocates host/private state, requests IRQ, adds/scans host. `qlogic_probe()`, `qlogic_config_check()`, `qlogic_config()`, `qlogic_release()`, and `qlogic_resume()` implement card lifecycle.

Control flow/state: config loops resources, enables the card, applies selected manufacturer quirks, adjusts base for 32-byte windows, and creates the host. `scsi_info_t` stores PCMCIA device, host, and manufacturer ID; shared core private state holds base, IRQ, initiator ID, and info string.

Dependencies/integration: PCMCIA, SCSI midlayer, `qlogicfas408.h`, and PCMCIA active-low open-drain interrupt mode through `INT_TYPE 0`.

Risks/test signals: `info->manf_id` is never assigned, so quirk paths likely do not run. Resume calls `qlogicfas408_host_reset(NULL)`. Test product IDs, IRQ handling, base+16 behavior, command completion, removal, and resume reset.
