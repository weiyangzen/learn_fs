# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_ctrl.c

## Purpose
This file manages firmware memory, firmware loading, hardware reset/init/deinit, sleep/wakeup, and firmware instance open/close. It is the main lifecycle control layer between the platform driver and the version-specific command/operation tables.

## Important APIs, Types, and Functions
Exports include `s5p_mfc_alloc_firmware()`, `s5p_mfc_load_firmware()`, `s5p_mfc_release_firmware()`, `s5p_mfc_reset()`, `s5p_mfc_init_hw()`, `s5p_mfc_deinit_hw()`, `s5p_mfc_sleep()`, `s5p_mfc_wakeup()`, `s5p_mfc_open_mfc_inst()`, and `s5p_mfc_close_mfc_inst()`. Internal helpers include `s5p_mfc_bus_reset()`, `s5p_mfc_init_memctrl()`, `s5p_mfc_clear_cmds()`, `s5p_mfc_v8_wait_wakeup()`, and `s5p_mfc_wait_wakeup()`.

## Control Flow
Firmware allocation reserves an internal private buffer sized by the hardware variant. Firmware load tries newer firmware slots first, copies into firmware memory, and caches success except v12 reloads for each run. Init resets hardware, programs memory base addresses, clears command state, releases RISC reset, waits for firmware transfer, posts SYS_INIT, waits for SYS_INIT return, checks interrupt error/type, reads firmware version, and clocks off. Sleep/wakeup post PM commands and wait for returns. Open-instance allocates instance and decoder temp buffers, sets the work bit, runs hardware, waits for OPEN_INSTANCE return, and cleans resources on failure. Close-instance posts close, waits, releases codec/instance/decoder buffers, and marks the context free.

## State and Persistence Behavior
State changes affect firmware buffer fields, `dev->fw_get_done`, `dev->fw_ver`, `dev->risc_on`, device/context private buffers, `ctx->state`, `ctx->inst_no`, and command wait conditions. Firmware bytes are copied from `/lib/firmware` or built-in firmware into DMA memory.

## Dependencies and Integration Points
It depends on firmware loader APIs, jiffies/timeouts, MFC PM clock helpers, interrupt wait helpers, private buffer allocation in the operation layer, command tables, and register constants. It is called from probe/open/release/watchdog/suspend/resume.

## Risks
Reset/init sequencing is hardware-sensitive. Missing clock-off paths on error can leak PM refs. v12's forced firmware reload is an important special case; removing it can break second initialization. Open-instance cleanup must release decoder temp buffers and instance buffers in the right order. Wait timeouts can leave hardware locked unless callers clear work bits.

## Test Signals
Signals include firmware missing/oversized errors, init timeout paths, successful firmware version read, repeated v12 open/close, suspend/resume sleep/wakeup, watchdog deinit/reinit, and allocation failure injection for firmware, device context, instance, and decoder temp buffers.
