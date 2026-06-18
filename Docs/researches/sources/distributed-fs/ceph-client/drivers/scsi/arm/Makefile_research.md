# sources/distributed-fs/ceph-client/drivers/scsi/arm/Makefile

## Purpose
This Makefile maps the ARM/Acorn SCSI Kconfig symbols to the object files built into the kernel or loadable modules.

## Important build rules
- `acornscsi_mod-objs := acornscsi.o acornscsi-io.o` builds the Acorn SCSI driver from its C implementation and ARM assembly I/O helper.
- `obj-$(CONFIG_SCSI_ACORNSCSI_3) += acornscsi_mod.o queue.o msgqueue.o`
- `obj-$(CONFIG_SCSI_ARXESCSI) += arxescsi.o fas216.o queue.o msgqueue.o`
- `obj-$(CONFIG_SCSI_CUMANA_1) += cumana_1.o`
- `obj-$(CONFIG_SCSI_CUMANA_2) += cumana_2.o fas216.o queue.o msgqueue.o`
- `obj-$(CONFIG_SCSI_OAK1) += oak.o`
- `obj-$(CONFIG_SCSI_POWERTECSCSI) += powertec.o fas216.o queue.o msgqueue.o`
- `obj-$(CONFIG_SCSI_EESOXSCSI) += eesox.o fas216.o queue.o msgqueue.o`

## Control flow and state behavior
The file has no runtime control flow. Kbuild expands each `obj-$()` assignment according to `.config` and links common helper objects (`fas216.o`, `queue.o`, `msgqueue.o`) into each selected module or built-in target as required.

## Persistence behavior
There is no runtime persistence. Build output depends on the persistent kernel configuration and Kbuild's generated artifacts.

## Dependencies and integration points
This Makefile integrates with the Kconfig symbols in the same directory and with the kernel SCSI build. Several drivers share `fas216`, queue, and message-queue helper modules, while the Acorn SCSI card additionally uses the assembly file researched in this work item.

## Risks and edge cases
- Shared objects listed under multiple `obj-$()` lines can be linked into multiple modules depending on Kbuild composition; changes to helper names or module grouping must preserve Kbuild semantics.
- `acornscsi-io.o` is architecture assembly and must only be built in compatible ARM/Acorn configurations.
- Misaligning object lists with Kconfig options can cause unresolved symbols or missing low-level transfer helpers.

## Test signals
- Build each configured driver as module and built-in where supported.
- Confirm `acornscsi_mod.o` includes both `acornscsi.o` and `acornscsi-io.o`.
- Verify helper object dependencies remain satisfied for ARXE, Cumana II, PowerTec, and EESOX builds.
