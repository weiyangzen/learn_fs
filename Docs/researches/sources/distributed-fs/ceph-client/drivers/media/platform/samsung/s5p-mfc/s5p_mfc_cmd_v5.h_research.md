# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v5.h

## Purpose
This header exposes the v5 command vtable initializer to the command dispatcher.

## Important APIs, Types, and Functions
It declares `const struct s5p_mfc_hw_cmds *s5p_mfc_init_hw_cmds_v5(void);` and includes `s5p_mfc_common.h` for the command table type.

## Control Flow and State
There is no local control flow or stored state. Calling the initializer returns the static command table implemented in `s5p_mfc_cmd_v5.c`.

## Dependencies and Integration Points
It is included by `s5p_mfc_cmd.c`, which chooses v5 commands for non-v6-plus devices. The returned table is stored in `dev->mfc_cmds`.

## Risks
The include guard comment names `S5P_MFC_CMD_H_` rather than its own guard, which is harmless but mildly confusing. Prototype drift between this header and the implementation would break builds.

## Test Signals
Compile coverage with v5 support enabled validates the declaration. Runtime v5 probe and SYS_INIT validates that the dispatcher can call the returned table.
