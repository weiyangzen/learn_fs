# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-buttress.h

## Purpose
This header declares buttress power, IPC, authentication, firmware mapping, interrupt, and TSC interfaces used across the IPU6 core and auxiliary drivers.

## Important APIs, types, and definitions
Frequency constants define allowed forced ISYS/PSYS frequency ranges. `struct ipu6_buttress_ctrl` describes subsystem frequency-control and power-status register fields. `struct ipu6_buttress_ipc` stores completion objects, CSE NACK handling, received data, and register offsets. `struct ipu6_buttress` groups mutexes, CSE IPC, constraints, watchdog cache, forced suspend flag, and reference clock. `struct ipu6_ipc_buttress_bulk_msg` describes CSE IPC commands. Public functions include IPC reset, firmware map/unmap, power control, secure-mode/authentication helpers, TSC helpers, buttress ISR functions, init/exit, CSI port config, and restore.

## Control flow and integration points
The bus PM domain calls `ipu6_buttress_power()`, the PCI driver calls init/exit and ISR entry points, CPD/firmware boot paths call map/authenticate helpers, and ISYS code uses TSC conversion for timestamps. Exported symbols form the cross-module API between `intel_ipu6` and `intel_ipu6_isys`.

## State, persistence, and dependencies
The structs are embedded in `struct ipu6_device` and persist for the PCI device lifetime. The header depends on completions, IRQ types, lists, mutexes, firmware/scatterlist forward declarations, and IPU6 bus/device types.

## Risks and test signals
Risks are struct/API changes that break module boundaries, incomplete mutex initialization, incorrect power control descriptors, and mismatched IPC register offsets. Test signals include modpost namespace checks, secure and non-secure probe paths, runtime PM transitions, firmware authentication, IRQ dispatch, and TSC timestamp consistency.
