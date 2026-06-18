# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_scsi.h

Purpose: this header defines SCSI-side parameter structures consumed by the qedi firmware task builders.

Important types: `struct scsi_sgl_task_params` carries an SGL pointer, physical SGL address, total buffer size, SGE count, and `small_mid_sge` slow-path hint. `struct scsi_dif_task_params` describes DIF/protection information, including reference/application tags, block size, host/network DIF placement, guard/protection type, validation/forwarding controls, CRC seed, and error behavior. `struct scsi_initiator_cmd_params` carries an extended CDB SGE and sense data buffer physical address.

Control flow and state: the header is declarative. Its fields are populated by `qedi_fw.c` and interpreted by `qedi_fw_api.c` to fill firmware storm contexts and SQE flags.

Dependencies and integration points: it includes Linux types, byteorder support, `qedi_hsi.h`, and QED interfaces. The structs mirror firmware HSI expectations for SGL and DIF programming.

Risks: DIF flags are numerous and easy to combine incorrectly. `small_mid_sge` must reflect SGL alignment constraints or the firmware may use the wrong SGL path. Sense buffer and extended CDB addresses must be DMA-safe and endian-correct when transferred into firmware context.

Test signals: I/O with no DIF and with supported DIF modes, reads/writes with sense data, extended CDB commands, slow-path SGL alignment cases, and firmware context validation against expected SGL/DIF fields.
