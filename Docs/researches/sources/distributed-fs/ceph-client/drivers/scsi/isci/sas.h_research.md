# sources/distributed-fs/ceph-client/drivers/scsi/isci/sas.h

Purpose: provides local SAS/SATA protocol constants and packed wire-format structures used by the ISCI request path where equivalent libsas definitions were absent or insufficient in this codebase.

Important APIs/types: SATA FIS type constants define register H2D/D2H, set-device-bits, DMA activate/setup, BIST activate, PIO setup, and data FIS values. `SSP_RESP_IU_MAX_SIZE` fixes the maximum response IU copy size at 280 bytes. `struct ssp_cmd_iu` models an SSP command IU with LUN, task attributes, and 16-byte CDB. `struct ssp_task_iu` models an SSP task-management IU with LUN, task function, and task tag. SMP request payload structs cover phy-id requests, configure route info, phy control, and generic `struct smp_req` with flexible data. `struct sci_sas_address` represents a SAS address as high/low u32 words.

Control flow: `request.c` fills `ssp_cmd_iu` for normal SSP I/O, `ssp_task_iu` for task management, inspects and byte-swaps `smp_req` for SMP construction, and compares FIS constants while processing unsolicited SATA/STP frames. Response-size constants bound SSP response copying and byte-swapping.

State and persistence behavior: these are packed on-wire or hardware-DMA layouts, not persistent driver state. Their field layout and endianness handling are part of the request/task-context ABI between driver, libsas buffers, and SCU hardware.

Dependencies/integration: includes only `<linux/kernel.h>` but is included by `request.c` alongside libsas/libata headers. Several comments note these definitions ideally belong in common SCSI/SAS headers, so this file is compatibility glue.

Risks: packed bitfields and protocol layouts must match SAS/SATA specifications. CDB length is fixed at 16 bytes here, so extended CDB support would require changes. SMP request default-length fixups in `request.c` assume `struct smp_req` header layout. Test signals include byte-for-byte SSP command/task IU contents, FIS type dispatch for every STP substate, SMP request length defaults, and response IU copy bounds.
