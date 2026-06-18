# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_accel_devices.h

## Purpose
This central header defines QAT device identity, hardware capability enums, BAR/MSI-X/PCI/device structures, callback tables, and the main `struct adf_accel_dev` and `struct adf_hw_device_data` used by all QAT PF/VF drivers and common framework code.

## Important APIs, Types, And Functions
Important types include `struct adf_bar`, `struct adf_accel_pci`, `struct adf_hw_device_class`, `struct adf_hw_csr_ops`, `struct adf_pfvf_ops`, `struct adf_dc_ops`, `struct adf_ras_ops`, `struct qat_migdev_ops`, `struct adf_hw_device_data`, `struct adf_accel_vf_info`, `struct adf_dc_data`, `struct adf_pm`, `struct adf_sysfs`, and `struct adf_accel_dev`. It also defines PCI IDs, device names, capability bits, fuse indexes, state enums, CSR read/write macros, and accessor macros such as `GET_HW_DATA()`, `GET_CSR_OPS()`, and `GET_DC_OPS()`.

## Control Flow
The header has only inline data classification such as `get_sku_info()` and CSR accessor macros. Runtime control is indirect: each hardware-data file fills callback fields in `adf_hw_device_data`, and common lifecycle code invokes those callbacks for probe, init, firmware load, transport, reset, PM, RAS, PF/VF messaging, compression context build, and migration.

## State And Persistence Behavior
The defined structs are volatile kernel state. `adf_accel_dev` persists for one bound PF/VF device and anchors transport, config, firmware loader, admin, telemetry, PM, PF/VF state, status bits, reference counts, debugfs, PCI info, timers, heartbeat, rate limiting, sysfs, and RAS counters.

## Dependencies And Integration Points
It includes Linux interrupt/module/list/io/pci/rate-limit/types headers plus QAT migration, anti-rollback, config, compression, telemetry, PF/VF, and hardware firmware definitions. Nearly every QAT source file depends on it.

## Risks
This is a high-blast-radius contract. Layout and callback changes affect all generations. CSR macros perform raw MMIO and require correct BAR/offset selection. Status bits and refcount/module ownership must stay synchronized with lifecycle paths.

## Test Signals
Build coverage across all QAT modules, probe/start/stop for PF and VF generations, SR-IOV, AER reset, firmware load, transport operations, debugfs/sysfs, compression/crypto algorithms, PM/RAS/anti-rollback, and migration paths validate this header.
