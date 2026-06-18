# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/Makefile

## Purpose
The Makefile defines how the qla2xxx driver objects are assembled. It maps Kconfig symbols to the main qla2xxx initiator module and the optional TCM target module.

## Important Build Rules
- `qla2xxx-y` aggregates the built-in object list for the main driver: OS glue, initialization, mailbox, IOCB, ISR, generic services, debug, support, attributes, NPIV/midlayer, debugfs, BSG, newer ASIC support, target code, template, NVMe, and EDIF components.
- `obj-$(CONFIG_SCSI_QLA_FC) += qla2xxx.o` builds the main module when the initiator driver is enabled.
- `obj-$(CONFIG_TCM_QLA2XXX) += tcm_qla2xxx.o` builds the target fabric module when target-mode support is enabled.

## Control Flow and Integration
There is no runtime control flow, but object membership affects which runtime code is linked:
- `qla_attr.o` supplies sysfs and FC transport hooks.
- `qla_bsg.o` supplies BSG passthrough and vendor command handling.
- `qla_target.o` is included in the main qla2xxx object, while `tcm_qla2xxx.o` is built as the target-core fabric module when configured.
- `qla_nvme.o` and `qla_edif.o` are compiled into the main driver, with runtime and Kconfig guards deciding active behavior.

## State and Persistence
- Build state is persisted through Kbuild outputs and module artifacts. The Makefile does not create runtime state.
- Object ordering can matter for link-time symbol resolution and init/exit section layout.

## Dependencies
- Depends on symbols selected by `Kconfig`, kernel Kbuild conventions, and the source files listed in `qla2xxx-y`.
- The included objects depend on SCSI, FC transport, PCI, firmware loader, optional NVMe FC, target core hooks, debugfs, and EDIF support.

## Risks and Edge Cases
- Removing an object can silently drop a runtime interface; for example, without `qla_bsg.o`, `qla24xx_bsg_request` and timeout hooks referenced by the FC transport template would be unresolved.
- Adding code to the tree without updating this list leaves it unbuilt.
- Including target support in the main object while also building `tcm_qla2xxx.o` requires clear symbol ownership to avoid duplicate or missing exports.

## Test Signals
- `make M=drivers/scsi/qla2xxx` with `CONFIG_SCSI_QLA_FC=m` should produce `qla2xxx.ko`.
- Enabling `CONFIG_TCM_QLA2XXX=m` should also produce `tcm_qla2xxx.ko`.
- Link tests should catch missing symbols from `qla_attr.o`, `qla_bsg.o`, target, NVMe, or EDIF components.
