# sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/Makefile

Purpose: this Makefile wires the ARECA ARCMSR PCI-X/PCIe SATA RAID SCSI driver into the kernel build.

Important APIs/types/functions: it declares the composite object list `arcmsr-objs := arcmsr_attr.o arcmsr_hba.o` and the Kconfig-controlled build target `obj-$(CONFIG_SCSI_ARCMSR) := arcmsr.o`.

Control flow and state: no runtime flow. During kbuild, enabling `CONFIG_SCSI_ARCMSR` links `arcmsr_attr.o` and `arcmsr_hba.o` into `arcmsr.o`, which is then built as built-in or module according to the config value.

Persistence behavior: none. It only affects build artifacts.

Dependencies and integration points: depends on the surrounding kernel SCSI Makefile descending into `drivers/scsi/arcmsr` and on `CONFIG_SCSI_ARCMSR` being defined by Kconfig. It assumes `arcmsr_attr.c` and `arcmsr_hba.c` exist in the same directory.

Risks: small but build-breaking if object names diverge from source files or Kconfig symbol changes. No conditional per-feature object selection is present, so both objects are always required when the driver is enabled.

Test signals: `make M=drivers/scsi/arcmsr` or an equivalent tree build with `CONFIG_SCSI_ARCMSR=m/y`, plus a disabled-config build verifying the object is omitted.
