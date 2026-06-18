## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-error.c

Purpose: this file implements global error reporting, masking, clearing, injection, and IRQ ioctls for the Intel DFL FPGA Management Engine.

Important APIs and functions: sysfs attributes under `errors/` expose PCIe0/PCIe1 errors, nonfatal and catastrophic RAS errors, error injection bits, FME errors, first error, and next error. Store handlers for PCIe and FME errors mask the relevant group, require the written value to match current hardware error bits, clear by writeback, then unmask. `fme_err_mask()` masks or unmasks all error groups and applies a revision-zero workaround that keeps `MBP_ERROR` masked. `fme_global_error_ioctl()` handles FME error IRQ num/set ioctls.

Control flow: feature init unmasks global errors, feature uninit masks them. Sysfs visibility depends on `FME_FEATURE_ID_GLOBAL_ERR` being enumerated. Injection writes update only `INJECT_ERROR_MASK` bits in `RAS_ERROR_INJECT`.

State and persistence: all error state lives in FME hardware registers. The only software state is lock-protected access through `fdata->lock`; masking state is programmed into hardware and persists until changed or device reset.

Dependencies and integration: it depends on DFL feature lookup, DFL IRQ helpers, `dfl-fme.h` declarations, and FME feature revision checks. The attribute group is registered by `dfl-fme-main.c`.

Risks: exact-match clearing can race with new hardware errors. Nonfatal and catastrophic RAS attributes are read-only here, so clearing may require other mechanisms or reset. Error injection is writable through sysfs and must be permission-controlled by sysfs mode and device ownership. The revision-zero MBP workaround changes mask semantics and should be preserved in future refactors.

Test signals: verify sysfs group visibility, clear success and mismatch failure for PCIe/FME groups, MBP mask behavior for revision zero versus later revisions, injection mask validation, IRQ ioctl dispatch, and masking on init/uninit.
