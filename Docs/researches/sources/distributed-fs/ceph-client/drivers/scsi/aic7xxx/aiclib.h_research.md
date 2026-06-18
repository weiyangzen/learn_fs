# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aiclib.h

Purpose: compatibility helper header for aic7xxx/aic79xx code, carrying SCSI sense structures/constants, endian byte conversion, disk geometry division, and PCI ID table generation macros.

Important APIs/types/functions: `struct scsi_sense` and `struct scsi_sense_data` define legacy SCSI REQUEST SENSE layouts and sense-key flags. `aic_sector_div()` wraps Linux `sector_div()` for capacity geometry math. `scsi_4btoul()` converts four big-endian bytes to a host `uint32_t`. `GETID`, `ID_C`, `ID2C`, `IDIROC`, and `ID16` help generate compressed PCI ID table entries for related Adaptec devices.

Control flow: only inline helpers and macros execute. `aic_sector_div()` destructively divides a local sector count and returns the quotient. `scsi_4btoul()` is used by SCSI IU helpers for lengths and packet-failure codes.

State and persistence: no mutable state or persistence. The header defines constants compiled into the driver.

Dependencies and integration: expects Linux kernel types such as `sector_t`, `uint8_t`, PCI class constants, and the aic driver’s `ID()`/mask macros to be available from including files.

Risks and test signals: `scsi_4btoul()` assumes byte pointers contain at least four bytes and shifts `uint8_t` values through integer promotion. PCI ID macros are dense and easy to misuse if bit packing changes. Build coverage of aic7xxx/aic79xx PCI tables, sense-data consumers, and large-disk geometry paths are the useful signals.
