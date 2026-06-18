# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/Makefile

## Purpose
This Makefile builds the Broadcom/Emulex `lpfc` Fibre Channel HBA driver as a kernel object when `CONFIG_SCSI_LPFC` is enabled. It also supports optional GCOV instrumentation and treating warnings as errors.

## Important APIs, types, and functions
- `ccflags-$(GCOV)` adds `-fprofile-arcs -ftest-coverage` and disables optimization with `-O0` for coverage builds.
- `ifdef WARNINGS_BECOME_ERRORS` adds `-Werror` to `ccflags-y`.
- `obj-$(CONFIG_SCSI_LPFC) := lpfc.o` ties the driver object to kernel configuration.
- `lpfc-objs` composes the module from `lpfc_mem.o`, `lpfc_sli.o`, `lpfc_ct.o`, `lpfc_els.o`, `lpfc_hbadisc.o`, `lpfc_init.o`, `lpfc_mbox.o`, `lpfc_nportdisc.o`, `lpfc_scsi.o`, `lpfc_attr.o`, `lpfc_vport.o`, `lpfc_debugfs.o`, `lpfc_bsg.o`, `lpfc_nvme.o`, `lpfc_nvmet.o`, and `lpfc_vmid.o`.

## Control flow and state
There is no runtime control flow. Build-time configuration decides whether the module is compiled, whether GCOV flags are applied, and whether warnings fail the build.

## State and persistence behavior
No runtime state or persistence. Build artifacts are produced by the kernel build system.

## Dependencies and integration points
The Makefile depends on Kbuild variables (`obj-*`, `<module>-objs`, `ccflags-*`) and the `CONFIG_SCSI_LPFC` kernel config option. The object list corresponds to lpfc subsystems: memory, SLI, CT/ELS discovery, mailbox, SCSI, sysfs attributes, vports, debugfs, BSG, NVMe initiator/target, and VMID.

## Risks and edge cases
- Adding source files without updating `lpfc-objs` leaves code unbuilt.
- `WARNINGS_BECOME_ERRORS` can expose compiler-version-dependent warnings.
- GCOV builds use `-O0`, which can change timing and code generation compared with production builds.

## Test signals
- `CONFIG_SCSI_LPFC=m` should produce `lpfc.ko` with all listed objects linked.
- GCOV-enabled builds should include coverage flags.
- Warning-as-error CI should be run across supported compiler versions.
