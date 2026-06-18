<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/retimer.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/retimer.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/retimer.c` discovers USB4 retimers under ports, registers retimer devices, exposes retimer sysfs attributes, and supports on-board retimer NVM read/write/authentication through USB4 sideband transactions. The source was read as a complete 600-line file.

## Important APIs, Types, and Functions

Public APIs are `tb_retimer_nvm_read()`, `tb_retimer_scan()`, and `tb_retimer_remove_all()`. Device lifecycle helpers include `tb_retimer_add()`, `tb_retimer_remove()`, `tb_port_find_retimer()`, `retimer_match()`, and `tb_retimer_release()`. NVM helpers include `tb_retimer_nvm_add()`, `tb_retimer_nvm_validate_and_write()`, `tb_retimer_nvm_authenticate()`, `nvm_read()`, and `nvm_write()`. Sideband helpers include `tb_retimer_nvm_authenticate_status()`, `tb_retimer_set_inbound_sbtx()`, and `tb_retimer_unset_inbound_sbtx()`. Sysfs exposes `device`, `vendor`, `nvm_version`, and `nvm_authenticate`, with visibility gated by `retimer_is_visible()`.

## Control Flow

Scanning broadcasts retimer enumeration on the USB4 port, immediately samples NVM authentication status, enables inbound sideband transactions, queries each possible retimer index for last/cable status, and registers missing on-board retimers when requested. Cable retimers are skipped. Registration reads vendor/product sideband registers, allocates a `tb_retimer`, determines whether NVM upgrade is allowed by on-board status and sector-size support, registers the device under the USB4 port, adds NVM devices, enables runtime PM, and initializes debugfs.

NVM reads runtime-resume the retimer device, try-lock the domain, call USB4 retimer NVM read, and autosuspend. Writes stage data in `tb_nvm` under the domain lock. Writing `nvm_authenticate` can perform authenticate-only, write-only, or write-and-authenticate. Authentication may make the retimer inaccessible, so inbound sideband transactions are left enabled except on validation/write-only failure paths.

## State and Persistence Behavior

Retimer state lives in registered `struct tb_retimer` devices with vendor/device/index/auth status, `no_nvm_upgrade`, `nvm`, `port`, and domain pointers. NVM images are staged in memory until written/authenticated; firmware flash persists on the retimer after a successful update. Authentication status is captured before old devices disappear and stored in the new retimer object.

## Dependencies and Integration Points

The file depends on USB4 sideband helpers, `sb_regs.h`, `tb.h`, `tb_nvm_*`, runtime PM, device core, sysfs, and debugfs margining. It integrates with switch port lifecycle: `tb_retimer_scan()` runs for USB4 ports, and `tb_retimer_remove_all()` is called during switch removal.

## Risks and Edge Cases

The maximum scanned retimer index is larger when debugfs margining is enabled, otherwise scanning trims to on-board retimers up to `last_idx`. Sideband state must be set/unset according to online/offline port state; authentication deliberately disrupts access. Sysfs operations use `mutex_trylock()` and return `restart_syscall()` to avoid deadlocks. Only on-board retimers support upgrade. Failure to remove reverse child order can leave stale children under USB4 ports.

## Test Signals

Retimer enumeration with zero, on-board, cable, and multiple retimers; NVM sysfs visibility with and without sector-size support; authenticate-only/write-only/write-and-authenticate flows; runtime PM/autosuspend around nvmem reads; sideband transaction failures; hot-unplug removal; and debugfs margining configurations are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/retimer.c -->
