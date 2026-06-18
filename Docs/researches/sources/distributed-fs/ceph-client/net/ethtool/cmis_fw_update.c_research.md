# sources/distributed-fs/ceph-client/net/ethtool/cmis_fw_update.c

## Purpose
This file implements the CMIS module firmware update sequence over the CDB transport. It queries firmware management capabilities, starts a download, writes firmware blocks by LPL or EPL mechanism, completes the download, runs the new image, reinitializes CDB state, commits the image, resets the module, and emits progress/error/completion notifications.

## Important APIs, Types, And Functions
The exported entry point is `ethtool_cmis_fw_update()`. Internal types include `cmis_fw_update_fw_mng_features`, `cmis_cdb_fw_mng_features_rpl`, `cmis_cdb_fw_write_mechanism`, `cmis_cdb_start_fw_download_pl`, `cmis_cdb_write_fw_block_lpl_pl`, `cmis_cdb_write_fw_block_epl_pl`, and `cmis_cdb_run_fw_image_pl`. Important helpers include feature query, start, LPL write, EPL write, complete, run, commit, module-state wait, and reset functions.

## Control Flow
The top-level flow initializes CDB, sends a start notification, queries firmware-management features, downloads the image, runs the image, frees and reinitializes CDB because the module reset may change settings, commits the image, performs an ethtool PHY reset, and sends completion. Download starts with firmware size and vendor bytes from the beginning of the firmware payload. LPL writes chunk firmware into command payloads sized by read/write extension. EPL writes use a small LPL block address plus an extended payload up to 2048 bytes. Progress notifications are sent before each block.

## State, Persistence, And Dependencies
The operation persistently changes module firmware. It also uses `dev->ethtool->module_fw_flash_in_progress` indirectly through surrounding module-flash orchestration and notifiers. Dependencies include CMIS CDB helpers, kernel firmware blobs, netdev ops locking for reset, `ethtool_ops->reset`, and module firmware notification helpers.

## Integration Points
The module firmware flashing netlink path in `module.c` invokes `ethtool_cmis_fw_update()`. CDB command execution is delegated to `cmis_cdb.c`. Userspace receives `start`, `in_progress`, `complete`, or `err` notifications through the ethtool module firmware notification path.

## Risks
Firmware update is high impact: interrupted writes, wrong write mechanism selection, bad block addressing, or incorrect start payload size can leave modules unusable. The code treats `BOTH` as EPL, so module behavior for dual support must match that preference. Reinitializing after run-image is required; failures there must still emit final errors. Reset calls depend on driver support and lock correctness.

## Test Signals
Test with simulated modules supporting no write mechanism, LPL only, EPL only, and both. Cover firmware sizes smaller than vendor-data start size, exact block boundaries, large EPL multi-block images, command failure at each phase, module-state timeout after run, CDB reinit failure, reset failure, and notification ordering.
