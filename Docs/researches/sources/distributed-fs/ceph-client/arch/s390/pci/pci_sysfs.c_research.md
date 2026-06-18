<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_sysfs.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_sysfs.c

Purpose: This file defines zPCI sysfs attributes for PCI function identity, firmware metadata, MIO state, recovery control, util string, error reporting, UID uniqueness, PFIP segments, slot UID, and firmware-wide CLP UID checking.

Important APIs/types/functions: Generated read-only attributes expose `function_id`, `function_handle`, `pchid`, `pfgid`, `vfn`, `pft`, `port`, `fidparm`, `uid`, and PFIP segments. Other handlers include `mio_enabled_show`, `recover_store`, `util_string_read`, `report_error_write`, `uid_is_unique_show`, `uid_checking_show`, `index_show`, and `zpci_uid_slot_show`. Exported attribute groups include `zpci_attr_group`, `pfip_attr_group`, `zpci_slot_attr_group`, `zpci_ident_attr_group`, and `__zpci_fw_sysfs_init`.

Control flow: Attribute reads format zdev fields directly. The `recover` write breaks sysfs active protection, serializes on `state_lock` and PCI rescan/remove lock, removes the sysfs file to coalesce concurrent calls, removes the PCI core device, disables the zPCI function if needed, reenables it, and rescans the bus. `report_error` forwards a user-provided report header to SCLP for the current FH/FID. Firmware sysfs initialization creates a `clp` group under `firmware_kobj`.

State and persistence: Sysfs reflects persistent zdev CLP metadata and UID-checking state. Recovery mutates the PCI device tree and zPCI enabled state. The `index` attribute is visible only when firmware guarantees unique UIDs.

Dependencies and integration points: It depends on generic PCI sysfs internals, zPCI state locks and reenable/disable helpers, SCLP PCI report support, `zpci_unique_uid` from CLP code, firmware kobjects, and PCI slot attributes.

Risks and test signals: Recovery has delicate lock ordering because sysfs active protection can deadlock with PCI remove/rescan if not broken. `report_error` trusts the binary attribute size and should reject offsets/short writes. Attribute visibility must update correctly with UID-checking state. Tests include reading all attributes after discovery, writing `recover` during normal and error states, concurrent recover writes, bus rescan after recovery, report-error writes with invalid sizes/offsets, and firmware `clp/uid_checking` visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_sysfs.c -->
