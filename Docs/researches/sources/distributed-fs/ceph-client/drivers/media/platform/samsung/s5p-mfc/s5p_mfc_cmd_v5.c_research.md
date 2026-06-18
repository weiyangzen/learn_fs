# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v5.c

## Purpose
This file implements the host-to-RISC command table for MFC v5 hardware. v5 commands are sent by waiting for the command register to become empty, writing up to four argument registers, then writing the command id.

## Important APIs, Types, and Functions
The core helper is `s5p_mfc_cmd_host2risc_v5()`. Version-specific commands include `s5p_mfc_sys_init_cmd_v5()`, `s5p_mfc_sleep_cmd_v5()`, `s5p_mfc_wakeup_cmd_v5()`, `s5p_mfc_open_inst_cmd_v5()`, and `s5p_mfc_close_inst_cmd_v5()`. The exported initializer `s5p_mfc_init_hw_cmds_v5()` returns a static `struct s5p_mfc_hw_cmds`.

## Control Flow and State
The command helper busy-waits up to `MFC_BW_TIMEOUT` for `S5P_FIMV_HOST2RISC_CMD` to equal `S5P_FIMV_H2R_CMD_EMPTY`, writes `HOST2RISC_ARG1..4`, and posts the command. Open-instance maps `ctx->codec_mode` to v5 firmware codec ids, sets `dev->curr_ctx`, passes context offset/size, and marks `ctx->state = MFCINST_ERROR` if command posting fails. Close-instance validates the instance is not already free and posts the instance number.

## Dependencies and Integration Points
It uses v5 register constants from `regs-mfc.h`, common read/write macros, debug logging, and the command header. `s5p_mfc_ctrl.c` waits for the corresponding interrupt returns after this layer posts commands.

## Risks
The busy-wait can fail if firmware or hardware leaves the command register non-empty. Codec mapping defaults to `S5P_FIMV_CODEC_NONE`, so unsupported codec requests may reach firmware unless earlier format validation prevents them. Context offsets and sizes must be v5 bank-relative, not v6 DMA addresses.

## Test Signals
Signals include command timeout handling, SYS_INIT after firmware load, sleep/wakeup, open/close for every v5-supported codec, and proper error state if open/close command posting fails.
