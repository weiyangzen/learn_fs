# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/flash.h

## Purpose
This header declares the low-level flash-mode and flash-write APIs for ZL3073x firmware update.

## Important APIs
It declares entry/exit with `zl3073x_flash_mode_enter()` and `zl3073x_flash_mode_leave()`, plus page, page-copy, and sector flashing functions. Each API accepts `struct zl3073x_dev` and a netlink extack for devlink error reporting.

## Integration, state, risks, and tests
`fw.c` uses page/sector helpers according to component metadata; `devlink.c` uses mode enter/leave around the entire update. The header owns no state. Compile tests and devlink firmware update paths validate prototype consistency.
