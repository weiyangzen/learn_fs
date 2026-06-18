# sources/distributed-fs/ceph-client/net/bluetooth/lib.c

## Purpose
Provides small exported utility routines shared across the Bluetooth kernel subsystem: Bluetooth address byte-order conversion, conversion between HCI/Bluetooth status codes and Linux errno values, and standardized Bluetooth logging helpers.

## APIs, Types, and Functions
`baswap()` reverses the six bytes of a `bdaddr_t` and is exported for modules that need Bluetooth address order conversion. `bt_to_errno()` maps Bluetooth controller status/error codes to positive Linux errno numbers. `bt_status()` maps negative Linux errno values back to Bluetooth status codes, returning nonnegative input unchanged and using `0x1f` for unspecified errors.

Logging helpers `bt_info()`, `bt_warn()`, `bt_err()`, `bt_warn_ratelimited()`, and `bt_err_ratelimited()` wrap `pr_info`, `pr_warn`, `pr_err`, and ratelimited variants with the `Bluetooth: ` prefix established by `pr_fmt`. Under `CONFIG_BT_FEATURE_DEBUG`, `bt_dbg_set()`, `bt_dbg_get()`, and `bt_dbg()` maintain and use a runtime debug-enable flag; `bt_dbg()` emits `KERN_DEBUG` output only when enabled. Exported symbols make these helpers available to other Bluetooth components and modules.

## Control Flow, State, and Persistence
`baswap()` is a fixed six-iteration byte reversal. `bt_to_errno()` and `bt_status()` are switch-table conversions with explicit fallbacks. Logging helpers build `struct va_format` around their variadic arguments and call the appropriate printk helper.

The only mutable state is the file-local `debug_enable` boolean compiled under `CONFIG_BT_FEATURE_DEBUG`. It is toggled by `bt_dbg_set()` and observed by `bt_dbg_get()` and `bt_dbg()`. There is no locking around this flag; it is a simple runtime subsystem knob used for best-effort debug logging. No state is persisted beyond process/kernel memory.

## Dependencies and Integration
Depends on `linux/export.h`, printk infrastructure, variadic formatting, errno constants, and Bluetooth base types from `net/bluetooth/bluetooth.h`. Address conversion is used by higher-level Bluetooth networking code such as 6LoWPAN and BNEP. Error conversion is used by connection teardown and command paths in L2CAP, SCO, ISO, and HCI sync code. Debug toggling integrates with Bluetooth management commands that expose runtime debug state.

## Risks and Test Signals
Risks include incomplete mappings as Bluetooth status codes evolve, asymmetry between `bt_to_errno()` and `bt_status()` where multiple status codes collapse to one errno, callers confusing positive errno returns from `bt_to_errno()` with normal kernel negative-error conventions, and unsynchronized debug flag reads/writes. `baswap()` also assumes `bdaddr_t` is exactly six address bytes, as expected by Bluetooth core types.

Useful test signals include table-driven checks for known status-code mappings in both directions, fallback behavior for unknown codes, preservation of nonnegative input in `bt_status()`, byte-exact address reversal, logging prefix verification, ratelimit behavior under repeated warnings/errors, and management-path debug toggling under `CONFIG_BT_FEATURE_DEBUG`.
