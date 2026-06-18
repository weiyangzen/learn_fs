# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dev.c

Purpose: manages hardware Device Descriptor Blocks (DDBs) for libsas domain devices discovered behind an AIC94xx adapter.

Important APIs/types/functions: `asd_dev_found()` and `asd_dev_gone()` are libsas callbacks. `asd_get_ddb()` allocates and clears a DDB bitmap entry. `asd_free_ddb()` marks a DDB unused. `asd_init_target_ddb()`, `asd_init_sata_pm_ddb()`, `asd_init_sata_pm_port_ddb()`, `asd_init_sata_tag_ddb()`, and `asd_init_sata_pm_table_ddb()` write target, SATA, NCQ tag, and port-multiplier context fields. `asd_set_dmamode()` configures SATA NCQ tag masks/depth.

Control flow: on discovery, `asd_dev_found()` takes `ddb_lock`, selects initialization by `dev_type`/protocol, writes DDB site fields through register helpers, and stores the DDB number in `dev->lldd_dev`. SATA/STP devices get SATA status and NCQ state; port multipliers get companion table/port DDBs. On removal, sister DDBs are freed before the primary context and `lldd_dev` is cleared.

State and persistence: DDB allocation state lives in `hw_prof.ddb_bitmap` and hardware DDB context memory. The software pointer `domain_device->lldd_dev` persists until device removal. No disk persistence exists.

Dependencies and integration: depends on libsas domain devices, libata NCQ helpers, SMP report-phy-SATA data, DDB structure offsets from `aic94xx_sas.h`, and register helpers from `aic94xx_reg.h`.

Risks and test signals: DDB allocation/freeing must stay balanced, especially for SATA tag and PM sister DDBs. `asd_set_dmamode()` disables NCQ if tag-DDB allocation fails, making low-memory behavior visible. Tests should cover SAS targets, STP/SATA, SATA PM and PM ports, NCQ capable/incapable devices, device removal, and DDB exhaustion.
