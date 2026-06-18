<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_pci.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_pci.c

**Purpose:** This file implements SCLP PCI I/O adapter configure/deconfigure helpers and PCI error notification reporting.

**Important APIs and functions:** Exported functions are `sclp_pci_configure()`, `sclp_pci_deconfigure()`, and `sclp_pci_report()`. `do_pci_configure()` sends configure command words with adapter type PCI and adapter ID. `sclp_pci_check_report()` validates report version, action, and length. `sclp_pci_report()` wraps a zPCI report in an `EVTYP_ERRNOTIFY` event.

**Control flow, state, and persistence:** Configure/deconfigure are synchronous one-shot commands gated by `SCLP_HAS_PCI_RECONFIG`. Error reporting is serialized by `sclp_pci_mutex`, dynamically registers for error notification send capability, allocates an SCCB page, submits a Write Event Data request, waits for completion, checks request status and response code, then unregisters.

**Dependencies and integration:** It depends on zPCI report structures, SCLP event masks, completion API, mutexes, and SCLP core. PCI hotplug/error-recovery paths call into these helpers.

**Risks and test signals:** Risks include report length validation not matching future structures, repeated register/unregister overhead, mutex contention during error storms, unsupported event mask handling, and response-code assumptions. Tests should cover configure responses, invalid report versions/actions/lengths, successful error notification, unsupported send mask, request failure, and concurrent reports serialized by the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_pci.c -->
