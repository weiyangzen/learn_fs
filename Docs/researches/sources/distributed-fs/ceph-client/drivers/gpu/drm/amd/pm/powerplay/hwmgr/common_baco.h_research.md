# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/common_baco.h

## Purpose
`common_baco.h` defines the table format and public helpers for BACO register sequencing. It lets ASIC-specific files describe power-off and power-on flows as arrays rather than open-coded MMIO sequences.

## Important APIs And Types
`enum baco_cmd_type` defines write, read-modify-write, wait, millisecond delay, and microsecond delay commands. `struct baco_cmd_entry` stores command, register offset, mask, shift, timeout, and value for pre-SOC15 register spaces. `struct soc15_baco_cmd_entry` adds `hwip`, `inst`, and `seg` fields so SOC15 code can resolve per-block register bases from `adev->reg_offset`. The exported helpers are `baco_program_registers()` and `soc15_baco_program_registers()`.

## State, Dependencies, And Integration
The header includes `hwmgr.h` for `struct pp_hwmgr` and integer types. It is included by common and ASIC BACO implementations. The command arrays it defines become an implicit hardware state machine for BACO transitions.

## Risks And Test Signals
The main risks are command table misencoding, mask/shift mismatches, and the typo-like include guard name `__COMMON_BOCO_H__`, which is harmless locally but worth preserving carefully. Test signals are successful compilation for all BACO users, static command arrays matching the expected struct type, and runtime BACO transitions succeeding through the shared executor.
