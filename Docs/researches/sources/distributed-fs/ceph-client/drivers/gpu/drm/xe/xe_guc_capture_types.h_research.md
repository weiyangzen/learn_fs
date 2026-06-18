# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture_types.h

## Purpose

`xe_guc_capture_types.h` defines register descriptor types used by GuC capture list generation and reporting.

## Important APIs, Types, and Functions

- `enum capture_register_data_type` distinguishes 32-bit registers, low dword of a 64-bit register, and high dword of a 64-bit register.
- `struct __guc_mmio_reg_descr` describes one register: offset, data type, GuC flags, mask, cached DSS id for steered registers, and printable name.
- `struct __guc_mmio_reg_descr_group` groups descriptor arrays by owner, capture type, and engine class.

## Control Flow

Static descriptor tables and dynamic steered lists use these types to build GuC ADS capture lists. Runtime printing uses the descriptors to format captured values in descriptor order and combine adjacent 64-bit low/high pairs.

## State and Persistence Behavior

Descriptors are mostly static const tables; dynamic extension descriptors are DRM-managed allocations built after topology is known. Captured runtime values are stored separately in GuC ABI `struct guc_mmio_reg` arrays.

## Dependencies and Integration Points

The header depends on `regs/xe_reg_defs.h` and Linux types. It is used by capture implementation, ADS capture-list registration, and snapshot printing.

## Risks and Edge Cases

64-bit registers require correct consecutive low/high descriptor ordering; print code warns on invalid order. Steered descriptors need accurate flags, group, instance, and DSS id or dumps will be misleading. Names can be NULL for low halves and must be handled by printers.

## Test Signals

Descriptor validation should check 64-bit pair ordering, non-null names where printed, class/type owner consistency, and steered flag/group/instance encoding.
