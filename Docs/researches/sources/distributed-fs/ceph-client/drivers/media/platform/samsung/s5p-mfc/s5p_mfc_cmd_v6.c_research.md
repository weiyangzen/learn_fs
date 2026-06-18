# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v6.c

## Purpose
This file implements the command table for MFC v6 and newer hardware. Unlike v5, command parameters are programmed into dedicated registers by operation code or command-specific helpers, then a host command and interrupt bit are written.

## Important APIs, Types, and Functions
Key functions are `s5p_mfc_cmd_host2risc_v6()`, `s5p_mfc_sys_init_cmd_v6()`, `s5p_mfc_sleep_cmd_v6()`, `s5p_mfc_wakeup_cmd_v6()`, `s5p_mfc_open_inst_cmd_v6()`, `s5p_mfc_close_inst_cmd_v6()`, the compatibility wrapper `s5p_mfc_cmd_host2risc_v6_args()`, and exported `s5p_mfc_init_hw_cmds_v6()`.

## Control Flow and State
The generic helper clears `RISC2HOST_CMD_V6`, writes `HOST2RISC_CMD_V6`, and raises `HOST2RISC_INT_V6`. SYS_INIT allocates a device context buffer, writes its DMA address and size, and posts the sys-init command. Open-instance maps `ctx->codec_mode` to v6/v7/v10 codec ids, sets `dev->curr_ctx`, writes codec type, context DMA address, context size, and CRC control, then posts OPEN_INSTANCE. Close-instance writes `INSTANCE_ID_V6` when the context is not free and posts CLOSE_INSTANCE.

## Dependencies and Integration Points
It uses common macros, interrupt definitions, operation helpers for context allocation, and codec constants from v6+ register headers. `s5p_mfc_ctrl.c` handles waits and resource cleanup around the command calls.

## Risks
The command helper does not poll for an empty command register like v5; correctness depends on higher-level `hw_lock` serialization. Unsupported codec modes map to `S5P_FIMV_CODEC_NONE_V6`, so format/control validation must prevent invalid firmware opens. HEVC and VP9 mappings depend on v10+ constants being included through the common header.

## Test Signals
Signals include v6+ SYS_INIT context allocation, open/close for all advertised decode and encode codecs, sleep/wakeup across suspend/resume, and command serialization under concurrent contexts.
