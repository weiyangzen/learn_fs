<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/Kconfig

Purpose: declares the Emulex/Broadcom `SCSI_EFCT` Fibre Channel target-mode driver configuration symbol.

Important APIs/types/functions: the sole symbol is `SCSI_EFCT`, a tristate named "Emulex Fibre Channel Target". It depends on `PCI`, `SCSI`, `TARGET_CORE`, and `SCSI_FC_ATTRS`, and selects `CRC_T10DIF`.

Control flow: no runtime flow exists. At configuration time, enabling the symbol includes the efct target driver and its supporting libraries in the build.

State and persistence: persistent state is the selected `.config` value. The symbol controls whether the PCI target-mode driver can register at runtime.

Dependencies and integration: ties efct to PCI hardware discovery, the SCSI stack, LIO target core, Fibre Channel transport attributes, and DIF CRC support.

Risks: dependency drift can produce build failures in `efct_driver.c`, target integration, or FC transport code. Selecting `CRC_T10DIF` is required for protection-information support used elsewhere in the efct stack.

Test signals: Kconfig builds with dependencies enabled/disabled, `CONFIG_SCSI_EFCT=m/y`, and link checks for target-core and FC transport symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/Kconfig -->
