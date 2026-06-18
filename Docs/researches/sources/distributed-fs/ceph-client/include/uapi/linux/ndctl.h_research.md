# sources/distributed-fs/ceph-client/include/uapi/linux/ndctl.h

## Purpose
Defines NVDIMM/ndctl ioctl ABI for DIMM flags, label/config data, vendor calls, address range scrub, error clearing, device type flags, and generic firmware command packages.

## Important APIs, Types, And Functions
Exports command structs for DIMM flags/config/vendor/ARS/clear-error, command IDs `ND_CMD_*`, helper inline command-name functions, `ND_IOCTL_*`, device type constants, `nd_driver_flags`, ARS masks, `nd_cmd_pkg`, and NVDIMM family IDs.

## Control Flow
Userspace issues ioctls on nvdimm bus/dimm/region devices. Some commands read/write label storage, some start/status ARS scans, some clear errors, and `ND_IOCTL_CALL` passes firmware-specific packages with input/output size negotiation.

## State, Persistence, And Dependencies
State persists in NVDIMM label/config areas, firmware state, ARS scan state, and persistent memory error metadata. Depends on `linux/types.h`.

## Integration Points
Used by ndctl/libndctl, persistent memory management tools, and ACPI NFIT/vendor firmware interfaces.

## Risks
Packed flexible-array structs require exact allocation sizing. Firmware package commands have reserved fields that must be zero. ARS status uses variable records and status masks.

## Test Signals
Validate ioctl numbers, config get/set bounds, vendor command size negotiation, ARS cap/start/status records, clear-error accounting, command-name helpers, and reserved-field rejection.
