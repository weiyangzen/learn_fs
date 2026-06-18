# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amdgpu_reg_state.h

## Purpose
This header defines the binary/sysfs format used to expose selected AMDGPU register state snapshots for XGMI, WAFL, PCIe, and user-defined state groups.

## Important APIs, Types, And Constants
`enum amdgpu_reg_state` defines state types: invalid, XGMI, WAFL, PCIe, USR, and USR_1. `enum amdgpu_sysfs_reg_offset` assigns sysfs read offsets in 0x1000-sized windows from XGMI through USR_1, ending at `0x5000`.

`struct amdgpu_reg_state_header` is the common file/record header with structure size, format revision, content revision, state type, number of instances, and padding. `enum amdgpu_reg_inst_state` reports per-instance status: OK, disabled, or access error.

`struct amdgpu_smn_reg_data` stores an SMN address/value pair. `struct amdgpu_reg_inst_header` stores instance number, state, and register count. Flexible-array structures model XGMI, WAFL, PCIe, and user state payloads. PCIe instances additionally store PCI config/status fields such as device status, link status, sub-bus/latency, and correctable/uncorrectable error statuses.

`amdgpu_reginst_size()` computes the combined size for repeated instance records. Macros `amdgpu_asic_get_reg_state_supported()` and `amdgpu_asic_get_reg_state()` dispatch through `adev->asic_funcs->get_reg_state`. `amdgpu_reg_state_sysfs_init()` and `amdgpu_reg_state_sysfs_fini()` declare sysfs lifecycle hooks.

## Control Flow
The header does not implement sysfs reads, but it defines the flow: sysfs init registers a binary attribute, users read an offset range corresponding to a state type, the implementation calls the ASIC `get_reg_state` hook if present, and the hook fills a buffer using the header and flexible-array layouts.

## State And Persistence
The structures represent transient snapshots of hardware and SMN state. They are exposed through sysfs offsets but are not persistent storage. The only durable contract is the binary layout and offset partitioning, which user-space tools may depend on.

## Dependencies And Integration Points
The header is included by `amdgpu.h`, `soc15.h`, and ASIC-specific code such as `aqua_vanjaram.c`. It depends on `struct amdgpu_device` and `adev->asic_funcs->get_reg_state` being defined by broader AMDGPU headers. It integrates with sysfs and hardware-specific register dump providers.

## Risks
Flexible arrays require careful size calculation and bounds checking. A mismatch between `num_instances`, `num_smn_regs`, and buffer length can corrupt output or truncate records. The sysfs offset constants are a user-visible ABI; changing them can break tools that read specific windows.

The dispatch macro returns 0 if no hook exists, which can be ambiguous if callers treat 0 as success with zero bytes. Callers should separately check support with `amdgpu_asic_get_reg_state_supported()`.

## Test Signals
Tests should validate exact structure sizes, `amdgpu_reginst_size()` arithmetic, sysfs offset routing, unsupported-ASIC behavior, and buffer-bound handling. Integration signals include successful sysfs reads for XGMI/WAFL/PCIe/user snapshots and correct disabled/access-error reporting per instance.
