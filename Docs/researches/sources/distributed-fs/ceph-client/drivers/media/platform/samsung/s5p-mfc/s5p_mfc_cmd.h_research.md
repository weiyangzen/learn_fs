# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd.h

## Purpose
This header declares the MFC command abstraction used by control and operation code. It normalizes v5 argument-register commands and v6+ register-programmed commands behind one function-pointer table.

## Important APIs, Types, and Constants
`MAX_H2R_ARG` fixes the generic argument count at four. `struct s5p_mfc_cmd_args` carries those arguments for v5 and for generic compatibility. `struct s5p_mfc_hw_cmds` contains function pointers for `cmd_host2risc`, `sys_init_cmd`, `sleep_cmd`, `wakeup_cmd`, `open_inst_cmd`, and `close_inst_cmd`. `s5p_mfc_init_hw_cmds()` initializes the table in the device.

## Control Flow and State
There is no implementation flow, but the table defines how state transitions are requested: system init, PM sleep/wakeup, firmware instance open, and firmware instance close. Device state stores a pointer to this table in `dev->mfc_cmds`.

## Dependencies and Integration Points
It includes `s5p_mfc_common.h` for `struct s5p_mfc_dev` and `struct s5p_mfc_ctx`. The API is consumed by `s5p_mfc_ctrl.c`, `s5p_mfc_cmd.c`, and version-specific command files.

## Risks
The generic `cmd_host2risc` signature accepts argument data, but v6 ignores it because v6+ commands use specific registers. Callers must not assume the generic arguments are honored on all hardware. Missing function pointers are guarded by `s5p_mfc_hw_call()` in common code, but failures then surface as `-ENODEV`.

## Test Signals
Build tests should catch prototype drift across command implementations. Runtime tests should exercise every function pointer through init, suspend/resume, open, and close on v5 and v6+ variants.
