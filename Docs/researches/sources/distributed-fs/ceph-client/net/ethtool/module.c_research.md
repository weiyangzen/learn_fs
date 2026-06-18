# sources/distributed-fs/ceph-client/net/ethtool/module.c

## Purpose
This file implements netlink module power-mode GET/SET and the asynchronous module firmware flash action with progress notifications for CMIS-capable optical modules.

## Important APIs, Types, And Functions
Power-mode handling uses `struct module_reply_data`, `module_get_power_mode()`, `module_prepare_data()`, `module_fill_reply()`, `ethnl_set_module_validate()`, `ethnl_set_module()`, and `ethnl_module_request_ops`. Firmware flashing uses `ethnl_module_fw_flash_act_policy`, `module_flash_fw_work_list_add()`, `module_flash_fw_work()`, `module_flash_fw_work_init()`, `ethnl_module_fw_flash_sock_destroy()`, `module_flash_fw_schedule()`, `ethnl_module_fw_flash_validate()`, `ethnl_act_module_fw_flash()`, and notification helpers `ethnl_module_fw_flash_ntf_*()`.

## Control Flow
GET enters ethtool ops and reads module power mode unless firmware flashing is in progress. SET validates a supplied power-mode policy, checks flashing state and driver support, fetches current policy, and calls `set_module_power_mode()` only when changed.

Firmware flashing parses a header, file name, and optional password; takes RTNL and netdev ops lock; validates EEPROM page ops, reset support, device-down state, non-split devlink port, and no existing flash. It requests firmware, reads the module physical identifier from EEPROM page 0 address `0x50`, accepts CMIS-capable IDs, records socket-private state, adds the work item to a global list, and schedules work. The worker calls `ethtool_cmis_fw_update()`, removes itself from the list, clears `module_fw_flash_in_progress`, drops the netdev reference, releases firmware, and frees memory.

## State And Persistence
Power-mode values persist in device/module state through driver callbacks. Firmware flash state is held in `dev->ethtool->module_fw_flash_in_progress`, a global protected work list, a held netdev reference/tracker, firmware memory, notification port/sequence, and a closed-socket flag.

## Dependencies And Integration Points
The file depends on firmware loading, SFP identifiers, devlink port metadata, netdev locks, `ethtool_ops` module EEPROM and reset methods, `ethnl_sock_priv_set()`/socket destruction from `netlink.c`, and CMIS implementation supplied by `ethtool_cmis_fw_update()`.

## Risks And Edge Cases
There is a subtle failure-path risk in `module_flash_fw_schedule()`: after setting `module_fw_flash_in_progress` and taking a netdev reference, later errors jump to firmware release/free paths without visibly clearing the flag or dropping the netdev reference. Duplicate work is rejected by portid/device pair, and socket close only suppresses notifications rather than cancelling work. Flashing is blocked while the netdevice is up and also blocks module reads/resets elsewhere.

## Test Signals
Tests should exercise unsupported module IDs, missing driver callbacks, device-up rejection, split-port rejection, duplicate request rejection, socket-close notification suppression, failure unwinds after `ethnl_sock_priv_set()`, and complete/error/in-progress notification payloads.
