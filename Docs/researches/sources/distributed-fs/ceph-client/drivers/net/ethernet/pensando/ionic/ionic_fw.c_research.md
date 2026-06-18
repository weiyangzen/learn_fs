# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_fw.c

Purpose: Implements devlink-triggered Ionic firmware update: segmented firmware download, asynchronous install, slot activation, long status waits, and user-visible progress/error reporting.

Important APIs and flow: `ionic_firmware_update()` validates devcmd registers, copies the firmware image into the devcmd data window in chunks, issues `IONIC_CMD_FW_DOWNLOAD` for each offset, starts `IONIC_FW_INSTALL_ASYNC`, reads the returned slot, waits for `IONIC_FW_INSTALL_STATUS`, starts `IONIC_FW_ACTIVATE_ASYNC`, waits for `IONIC_FW_ACTIVATE_STATUS`, and reports final devlink flash status. `ionic_fw_status_long_wait()` polls firmware control status commands under `dev_cmd_lock`, allowing `-EAGAIN` or `-ETIMEDOUT` until the long timeout expires. Helper command builders wrap download/install/activate firmware devcmds.

State and persistence: Mutates firmware image storage on the device and selected firmware slot. In driver memory it uses only transient offsets, status, and devcmd completion data.

Dependencies and integration: Called from `ionic_dl_flash_update()` and depends on devlink notifications, firmware loader objects, netlink extack, LIF/netdev state, and serialized devcmd access from `ionic_dev.c`.

Risks and test signals: Install timeout is intentionally long for rare CPLD updates. Failures must surface useful extack messages and final flash status. The code assumes the device remains present and firmware command registers valid during the whole update. Test segmented download boundary sizes, devcmd timeout/error at each phase, invalid/null devcmd registers, device removal/reset during flash, progress notifications, and successful activation followed by reboot/reset requirements from firmware policy.
