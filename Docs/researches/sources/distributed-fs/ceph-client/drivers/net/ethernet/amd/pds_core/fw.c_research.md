# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/fw.c

## Purpose
`fw.c` implements devlink-triggered firmware update for AMD/Pensando core devices. It downloads the firmware image to the device in command-data-sized segments, starts an asynchronous install, waits for install completion, activates/selects the installed slot, waits for activation completion, and reports progress through devlink flash notifications.

## Important APIs, Types, And Functions
The public function is `pdsc_firmware_update`. Helpers are `pdsc_devcmd_fw_download_locked`, `pdsc_devcmd_fw_install`, `pdsc_devcmd_fw_activate`, and `pdsc_fw_status_long_wait`. Constants define a long install timeout of 25 minutes, a select timeout of 30 seconds, and progress notification interval fraction of 32.

## Control Flow
The update starts by checking `cmd_regs`, notifying "Preparing to flash", and setting chunk size to the firmware command data window size. It loops over the firmware image; each iteration notifies download progress at coarse intervals, locks `devcmd_lock`, copies a chunk into `cmd_regs->data`, sends `PDS_CORE_CMD_FW_DOWNLOAD` with the data-window offset, image offset, and length, unlocks, and advances. After all chunks download, it notifies completion of download and a long install timeout, sends `PDS_CORE_FW_INSTALL_ASYNC`, and treats the completion slot as the target firmware slot.

Install and activation are asynchronous. `pdsc_fw_status_long_wait` repeatedly sends a firmware-control status command, sleeping 20 ms between polls, while the command returns `-EAGAIN` or `-ETIMEDOUT` and the operation timeout has not expired. After install succeeds, the code notifies selecting timeout, starts `PDS_CORE_FW_ACTIVATE_ASYNC` for the returned slot, waits for activation status, and finally sends "Flash done" or "Flash failed".

## State And Persistence
The function uses transient stack state for offsets, slot, and progress intervals. Firmware bytes are temporarily copied into the MMIO command data window. Persistent device-side effects are the installed/activated firmware image in hardware-managed storage; the driver itself writes no files.

## Dependencies And Integration Points
It is called from devlink flash update in `devlink.c`, relies on the Linux firmware loader's `struct firmware`, uses devlink flash status/timeout notifications, uses netlink extack error messages, and serializes MMIO command data access with `devcmd_lock` and `pdsc_devcmd*` helpers.

## Risks
Firmware update is long-running and command-timeout behavior is deliberately tolerated while polling async status; distinguishing real transport failure from in-progress status is critical. Progress interval calculation uses `fw->size / 32`; for very small firmware images this can be zero, making progress notification occur every loop iteration but still advancing by chunk size. Update cannot proceed if command registers are unavailable. A failure after install but before activation may leave device firmware staged but not selected, depending on firmware semantics.

## Test Signals
Use `devlink dev flash` with valid firmware, invalid firmware, truncated firmware, and forced device-command failures. Observe devlink status notifications for preparing/downloading/installing/selecting/done/failed, extack messages for segment download/install/select failures, and firmware slot/version changes through `devlink dev info`.
