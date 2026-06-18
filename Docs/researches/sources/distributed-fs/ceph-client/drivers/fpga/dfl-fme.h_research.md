## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme.h

Purpose: this header defines the main private state for the DFL FME compound driver and declares shared FME subfeature operation tables.

Important types and APIs: `struct dfl_fme` stores the FME manager platform device and linked lists of FME FPGA regions and bridges. External declarations expose PR management ops and IDs, global error ops/IDs/sysfs group, and performance ops/IDs to `dfl-fme-main.c`.

Control flow and integration: `dfl-fme-main.c` allocates `struct dfl_fme` and stores it in DFL feature private data. `dfl-fme-pr.c` fills `mgr`, `region_list`, and `bridge_list` during PR feature init. Error and perf feature files provide ops tables declared here so the main feature driver can register all FME subfeatures as one module.

State and persistence: this header defines state that persists for the FME device lifetime. The manager and child lists are initialized and destroyed with the PR management feature, while the containing private object is allocated and cleared by FME probe/remove.

Dependencies and risks: the header relies on consumers including platform and list definitions through surrounding includes. Cross-file external declarations mean mismatched object composition in the Makefile would cause link failures. Child-list access requires `fdata->lock` discipline established in PR management.

Test signals: compile FME compound objects, probe with and without PR/global-error/perf features, validate child list initialization before use, and remove with populated and empty child lists.
