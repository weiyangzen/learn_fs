# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/deb_defs.h

## Purpose
Provides debug category flags and logging macros for the Libertas thinfirm driver.

## Important APIs And Constants
Defines `DRV_NAME` defaulting to `libertas_tf`, maps `CONFIG_LIBERTAS_THINFIRM_DEBUG` to `DEBUG`, declares `extern unsigned int lbtf_debug`, and defines `LBTF_DEB_*` bitmasks for main, net, mesh, scan, association, command, RX/TX, USB, firmware, thread, SDIO, MAC ops, and hex dump categories. Macros such as `lbtf_deb_enter()`, `lbtf_deb_leave()`, `lbtf_deb_cmd()`, `lbtf_deb_usb()`, and `lbtf_deb_usbd()` compile to conditional `printk()` when debugging is enabled and no-ops otherwise. `lbtf_deb_hex()` conditionally dumps buffers.

## Control Flow And State
Runtime logging is controlled by the global `lbtf_debug` mask. When debugging is disabled, most macros compile out, leaving no runtime logging state.

## Dependencies And Integration
Included by thinfirm headers and source files. Depends on kernel logging, spinlock include, and `print_hex_dump_bytes()` in debug builds.

## Risks And Test Signals
Risks include format-string mismatches hidden in disabled builds, category names that do not match code paths, and excessive logging in debug builds. Test signals include debug module parameter behavior, category-filtered logs, and clean non-debug compilation.
