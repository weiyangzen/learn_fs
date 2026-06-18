# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_defs.h

Purpose: central constants header for mvsas hardware and protocol definitions shared by all Marvell chip variants. It defines chip flavor IDs, queue/ring sizing, hardware limits, register bit masks, port/phy event bits, command-table fields, status/error record bits, PCI config fields, and SAS/STP/SMP protocol encodings.

Important APIs/types/functions: key enums include `chip_flavors`, `driver_configuration`, `hardware_details`, `peripheral_registers`, `hw_register_bits`, `sas_sata_config_port_regs`, `sas_cmd_port_registers`, `mvs_info_flags`, `mvs_event_flags`, `mvs_port_type`, `ct_format`, `status_buffer`, `error_info_rec`, `error_info_rec_2`, `pci_cfg_register_bits`, `open_frame_protocol`, and `datapres_field`. Device IDs for Areca 1300/1320 are also defined.

Control flow: no direct execution. The values are used throughout `mv_init.c`, `mv_sas.c`, `mv_chips.h`, and per-chip files to size DMA memory, parse completion/error state, program hardware, and translate link/device events into libsas notifications.

State and persistence: no state. The constants define the layout and meaning of runtime hardware state.

Dependencies and integration points: included by `mv_sas.h`, making it part of nearly every mvsas source file. It bridges chip-specific register headers with generic libsas/SCSI code.

Risks and test signals: incorrect bit masks can break command issue, completion parsing, or error handling across both chip families. Queue constants interact with allocation sizes and hardware limits. Test signals include compile-time coverage, max queue/scatterlist I/O, error-injection paths for each error bit family, SATA/SAS port detection, and static analysis for shifts and mask widths.
