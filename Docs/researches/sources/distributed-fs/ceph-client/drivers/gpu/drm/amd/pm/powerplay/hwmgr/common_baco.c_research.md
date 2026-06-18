# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/common_baco.c

## Purpose
`common_baco.c` is the shared BACO command interpreter. It executes compact command tables used by ASIC-specific BACO files to program MMIO registers, poll fields, and delay between power sequencing steps.

## Important APIs And Control Flow
`baco_wait_register()` polls a register every millisecond up to 5000 iterations until `(data & mask) == value`. `baco_cmd_handler()` implements `CMD_WRITE`, `CMD_READMODIFYWRITE`, `CMD_WAITFOR`, `CMD_DELAY_MS`, and `CMD_DELAY_US`, warning on invalid commands. `baco_program_registers()` walks legacy command entries, tracks the active register across commands, and aborts on the first failed command. `soc15_baco_program_registers()` performs the same logic but computes the register base through `adev->reg_offset[hwip][inst][seg]`.

## State, Dependencies, And Integration
The file mutates hardware registers only; it has no persistent software state. It depends on `common_baco.h`, `hwmgr.h`, `amdgpu_device` MMIO access macros, `msleep()`, and `udelay()`. It is used by CI, Fiji, Polaris, Vega, and other BACO implementation files to keep state-machine tables declarative.

## Risks And Test Signals
Risks include the fixed 5-second poll timeout being too long for failing paths, no locking around MMIO sequences, RMW on registers with side effects, and table encoding mistakes where delay entries reuse the previous register implicitly. Test signals are BACO enter/exit success across supported ASICs, no invalid-command warnings, expected wait completion, and clean recovery when a table wait intentionally fails.
