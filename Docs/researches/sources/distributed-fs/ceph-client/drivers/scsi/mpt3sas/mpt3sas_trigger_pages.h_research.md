# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_pages.h

Purpose: defines MPI extended configuration pages used to store MPT3SAS diagnostic trigger settings persistently in firmware/controller NVRAM. The pages mirror the runtime master, event, SCSI sense, and IOCStatus/loginfo trigger structures.

Important APIs/types/functions: `MPI2_CONFIG_EXTPAGETYPE_DRIVER_PERSISTENT_TRIGGER` selects the extended page type. Page 0 (`Mpi26DriverTriggerPage0_t`) contains validity flags for the following pages. Page 1 stores one master trigger entry, Page 2 stores up to 20 MPI event triggers, Page 3 stores up to 20 SCSI sense triggers, and Page 4 stores up to 20 IOCStatus/loginfo triggers. Version macros are all `0x01`.

Control flow: no runtime flow exists in this header. Configuration helper code reads/writes these page layouts, checks Page 0 validity flags, then maps page entries to the in-memory structures from `mpt3sas_trigger_diag.h`.

State and persistence: unlike `mpt3sas_trigger_diag.c`, these types represent persistent firmware-backed state. Counts (`NumMasterTrigger`, `NumMPIEventTrigger`, `NumSCSISenseTrigger`, `NumIOCStatusLogInfoTrigger`) determine how many fixed-array entries are meaningful.

Dependencies and integration points: includes `mpi/mpi2_cnfg.h` for `MPI2_CONFIG_EXTENDED_PAGE_HEADER` and integer typedefs. It integrates with MPT3SAS config-page accessors and the diagnostic-trigger sysfs/control path.

Risks and test signals: firmware layout compatibility is the main risk; any structure-size or endian mismatch can corrupt persistent trigger settings. Tests should cover reading missing/invalid pages, writing each trigger family, maximum count boundaries, Page 0 flag handling, and cross-boot persistence on controllers that implement the vendor page type.
