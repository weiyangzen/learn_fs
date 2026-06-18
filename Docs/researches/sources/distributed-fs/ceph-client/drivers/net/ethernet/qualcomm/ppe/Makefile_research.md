<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/Makefile

## Purpose
The PPE Makefile connects the Qualcomm Packet Process Engine driver to Kbuild.

## Important APIs, Types, and Data
- `obj-$(CONFIG_QCOM_PPE) += qcom-ppe.o` builds the module/object when the Kconfig symbol is enabled.
- `qcom-ppe-objs := ppe.o ppe_config.o ppe_debugfs.o` composes the driver from platform probe, hardware configuration, and debugfs counter files.

## Control Flow
Kbuild evaluates the object rules; no runtime flow exists in this file.

## State and Persistence
The file affects build graph state only. It has no runtime state.

## Dependencies and Integration Points
It depends on `CONFIG_QCOM_PPE` being defined elsewhere in the Qualcomm Ethernet Kconfig hierarchy and integrates the PPE subdirectory with the kernel build system.

## Risks and Edge Cases
Object list drift can omit required symbols or include unused objects. Renaming files or symbols requires matching Makefile updates.

## Test Signals
`CONFIG_QCOM_PPE=m` should produce a `qcom-ppe` module with all three objects linked; built-in configs should link the same objects into vmlinux.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/Makefile -->
