# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd.c

## Purpose
This file selects the hardware command vtable for an MFC device. It is the bridge between version detection in `s5p_mfc_common.h` and the concrete v5 or v6+ host-to-RISC command implementations.

## Important APIs, Types, and Functions
The only function is `s5p_mfc_init_hw_cmds(struct s5p_mfc_dev *dev)`. It assigns `dev->mfc_cmds` to `s5p_mfc_init_hw_cmds_v6()` when `IS_MFCV6_PLUS(dev)` is true, otherwise to `s5p_mfc_init_hw_cmds_v5()`.

## Control Flow and State
The function is called from `s5p_mfc_probe()` after operation setup and before devices are registered. It mutates one field in `struct s5p_mfc_dev`; later control code calls through `dev->mfc_cmds` for sys-init, sleep, wakeup, open instance, close instance, and generic host-to-RISC commands.

## Dependencies and Integration Points
It includes common, debug, and both command-version headers. It integrates with `s5p_mfc_ctrl.c` and operation code through `struct s5p_mfc_hw_cmds`.

## Risks
The selection assumes all v6 and newer hardware uses the v6 command ABI. That is true for the included v7/v8/v10/v12 paths, but any future hardware with a changed command interface needs this dispatcher updated. A missing `dev->variant` before this call would make `IS_MFCV6_PLUS()` unsafe, but probe obtains variant data first.

## Test Signals
A simple probe test should verify `dev->mfc_cmds` is non-null for v5 and v6+ compatibles. Functional confirmation comes from successful SYS_INIT and OPEN_INSTANCE commands on both v5 and v6+ hardware.
