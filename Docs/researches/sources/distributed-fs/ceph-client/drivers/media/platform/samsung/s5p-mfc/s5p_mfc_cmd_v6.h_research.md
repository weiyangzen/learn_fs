# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v6.h

## Purpose
This header exposes the v6+ command vtable initializer to the command dispatcher.

## Important APIs, Types, and Functions
It declares `const struct s5p_mfc_hw_cmds *s5p_mfc_init_hw_cmds_v6(void);` and includes `s5p_mfc_common.h`.

## Control Flow and State
There is no executable flow. The initializer returns the static table implemented in `s5p_mfc_cmd_v6.c`, which is stored in `dev->mfc_cmds` for v6 and later variants.

## Dependencies and Integration Points
It is included by `s5p_mfc_cmd.c`. Downstream calls are made from firmware control, PM, and instance lifecycle paths.

## Risks
The header covers all v6+ hardware, so any future command ABI split must not be hidden behind this single initializer. The include guard closing comment references `S5P_MFC_CMD_H_`, which is harmless but imprecise.

## Test Signals
Compile coverage and runtime SYS_INIT/OPEN_INSTANCE on v6+ variants validate this declaration and dispatch path.
