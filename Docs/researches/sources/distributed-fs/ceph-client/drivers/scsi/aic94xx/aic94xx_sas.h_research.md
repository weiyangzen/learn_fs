# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sas.h

Purpose: this header defines the aic94xx hardware ABI for SAS/SATA domain state, scatter/gather elements, 128-byte SCBs, done-list entries, and per-phy driver state. It is the bridge between libsas concepts (`sas_task`, `domain_device`, SSP/SMP/STP frames) and what the Adaptec sequencers consume in DMA-visible memory.

Important APIs/types/functions: key packed types include DDB formats (`asd_ddb_ssp_smp_target_port`, `asd_ddb_stp_sata_target_port`, `asd_ddb_init_port`, SATA tag/PM tables, `asd_ddb_seq_shared`), hardware SG elements (`sg_el`), `scb_header`, protocol SCB payloads (`initiate_ssp_task`, `initiate_ata_task`, `initiate_smp_task`, `control_phy`, `abort_task`, `clear_nexus`, `initiate_ssp_tmf`, `send_prim`), the `scb` union, `done_list_struct`, and `asd_phy`. Constants define SCB opcodes, done-list completion opcodes, nexus selectors, data directions, SG flags, timer defaults, and notify/spinup policy.

Control flow and state: no executable flow lives here, but its layouts drive all SCB construction and completion decoding. `aic94xx_task.c` fills SSP/SMP/ATA SCB payloads and SG elements; `aic94xx_tmf.c` fills abort, TMF, and clear-nexus payloads; `aic94xx_scb.c` decodes `done_list_struct` and empty-buffer events; `aic94xx_seq.c` initializes DDB 0 and SCB/DDB sites using structure offsets. `asd_phy` stores libsas phy state plus hardware profile and received frame buffers.

Persistence behavior: SCBs and SG lists are transient DMA descriptors. DDBs are hardware context memory entries that persist across commands until cleared/reset. Done-list entries are hardware completion records. Per-phy frame buffers and `asd_port` association are driver memory state updated during hotplug and link reset.

Dependencies and integration points: includes `<scsi/libsas.h>` and relies on SAS frame structs, task status enums, and libsas phy/port notifications. It is tightly coupled to sequencer firmware expectations and register scratch offsets in `aic94xx_reg_def.h`.

Risks: packed layout drift is catastrophic because firmware reads exact byte offsets. Endianness annotations are mixed big/little endian according to SAS frame and hardware fields. SG list chaining is limited by the three embedded elements and external list convention, so DMA mapping changes need careful cleanup and EOL/EOS validation.

Test signals: build-time struct-field users, sparse/endian checks, successful SSP/SMP/STP I/O, task-management operations, wide-port formation, hotplug, and completion status mapping. Hardware tests should cover no-data, single-buffer, multi-SG, SMP response, ATA NCQ, and error-completion paths.
