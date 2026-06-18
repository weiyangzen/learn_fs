# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/Kconfig

## Purpose
This Kconfig file declares build-time feature switches for the QLogic/Broadcom qla2xxx Fibre Channel driver and its optional target-mode fabric module. It controls whether the initiator driver, target driver, and target debug support are available in a kernel build.

## Important Symbols
- `SCSI_QLA_FC` is a tristate option named "QLogic QLA2XXX Fibre Channel Support". It builds the main `qla2xxx` Fibre Channel HBA driver.
- `TCM_QLA2XXX` is a tristate target fabric module for QLogic 24xx+ target-mode HBAs.
- `TCM_QLA2XXX_DEBUG` is a bool nested under `if TCM_QLA2XXX`; it includes target-mode debug support and the SCSI command jammer.

## Dependencies and Selected Facilities
- `SCSI_QLA_FC` depends on `PCI`, `HAS_IOPORT`, `SCSI`, and `SCSI_FC_ATTRS`.
- `SCSI_QLA_FC` also has `depends on NVME_FC || !NVME_FC`, a common Kconfig pattern that permits build ordering whether NVMe FC is enabled or absent.
- `SCSI_QLA_FC` selects `FW_LOADER` because firmware images are loaded through the kernel firmware loader and selects `BTREE` for driver data structures.
- `TCM_QLA2XXX` depends on `SCSI_QLA_FC`, `TARGET_CORE`, and `LIBFC`, and selects `BTREE`.

## Control Flow and Build Integration
Kconfig has no runtime control flow, but it shapes compilation:
- Enabling `SCSI_QLA_FC` causes the Makefile to link `qla2xxx.o` from the driver object list.
- Enabling `TCM_QLA2XXX` builds `tcm_qla2xxx.o`.
- Enabling `TCM_QLA2XXX_DEBUG` changes compiled target-mode debug behavior.

## State and Persistence
- The selected values persist in the kernel `.config` and determine whether driver code is built in, modular, or absent.
- The help text documents firmware filenames (`ql2100_fw.bin`, `ql2200_fw.bin`, `ql2300_fw.bin`, `ql2322_fw.bin`, `ql2400_fw.bin`, `ql2500_fw.bin`) expected from linux-firmware. Runtime firmware caching is described as driver behavior on request, not Kconfig state.

## Integration Points
- Integrates with the SCSI core, FC transport class (`SCSI_FC_ATTRS`), PCI, firmware loader, optional NVMe FC code, target core, and libfc.
- The target option requires the initiator/base qla2xxx driver, so target mode is layered on top of the main adapter support.

## Risks and Edge Cases
- Changing dependencies can break allmodconfig or randconfig builds, especially around optional `NVME_FC`.
- Selecting `FW_LOADER` is required for firmware-backed adapters; removing it would produce runtime probe failures.
- Target mode is limited to 24xx+ hardware in the prompt text; code paths must still guard unsupported adapters at runtime.

## Test Signals
- `make olddefconfig`, `allmodconfig`, and `randconfig` coverage with `SCSI_QLA_FC=m/y/n`, `NVME_FC=m/y/n`, and `TCM_QLA2XXX=m/y/n`.
- Build logs showing `qla2xxx.o` only when `CONFIG_SCSI_QLA_FC` is enabled and `tcm_qla2xxx.o` only when `CONFIG_TCM_QLA2XXX` is enabled.
- Module load/probe tests verifying firmware loader requests match the documented firmware filenames.
