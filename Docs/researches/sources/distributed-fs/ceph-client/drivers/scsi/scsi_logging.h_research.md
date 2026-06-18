# sources/distributed-fs/ceph-client/drivers/scsi/scsi_logging.h

## Purpose

`scsi_logging.h` defines the SCSI mid-layer's compile-time gated diagnostic logging macros. It divides the global `scsi_logging_level` word into ten 3-bit fields covering error recovery, timeout handling, scanning, mid-layer queue/complete, low-level queue/complete, high-level queue/complete, and ioctl paths. Call sites use category-specific macros so debug output can be turned on by category and level without sprinkling bit arithmetic through the SCSI code.

## Important APIs, types, and functions

The important public surface is macro-based. `SCSI_LOG_*_SHIFT` and `SCSI_LOG_*_BITS` define each category's bitfield. `SCSI_LOG_LEVEL(SHIFT, BITS)` extracts the active level from `scsi_logging_level` when `CONFIG_SCSI_LOGGING` is enabled and returns zero otherwise. `SCSI_CHECK_LOGGING(SHIFT, BITS, LEVEL, CMD)` conditionally executes an arbitrary logging command if the configured category level is greater than the requested level. The call-site macros, such as `SCSI_LOG_SCAN_BUS()`, `SCSI_LOG_TIMEOUT()`, and `SCSI_LOG_HLCOMPLETE()`, bind those generic helpers to a category.

## Control flow

There is no runtime function body in this header. Control flow is injected at macro expansion sites throughout the SCSI core and upper-level drivers. With logging enabled, each macro performs a cheap level extraction and an `unlikely()` branch around the caller-supplied logging statement. With logging disabled, the macros collapse to no-ops and the supplied logging command is not emitted into the object code.

## State and persistence behavior

The only state dependency is the externally defined `unsigned int scsi_logging_level`, implemented in `scsi.c` and exposed through the `scsi_logging_level` module parameter and the `dev/scsi/logging_level` sysctl. The header itself persists nothing. Logging settings persist only as kernel memory/module/sysctl state until changed or until module/kernel teardown.

## Dependencies and integration points

This header is included by SCSI core files such as scanning, procfs, queueing, completion, and upper-level drivers. It depends on common kernel branch prediction and printk-style logging infrastructure through its call sites. `scsi_sysctl.c` is the administrative integration point for the sysctl path, while `scsi.c` provides the global variable and module parameter.

## Risks and edge cases

The ten 3-bit fields consume 30 bits of the word, so adding categories requires changing the packing scheme. The macro condition uses configured level `>` requested level rather than `>=`, which matters for call-site expectations. Because `CMD` is arbitrary code, it must be side-effect-free except for logging; otherwise behavior would differ between `CONFIG_SCSI_LOGGING` builds and non-logging builds. Since the global value is read locklessly, callers should treat it as best-effort diagnostic state.

## Test signals

Compile coverage should verify both `CONFIG_SCSI_LOGGING=y` and `n` builds. Runtime checks can set the module parameter or sysctl and confirm category-specific logs appear only at expected levels, especially scan logs from `scsi_scan.c`, timeout logs from `sg.c`, and queue/complete logs from `scsi_lib.c` and `sd.c`. Static checks should confirm each shift/width pair stays within the integer width and that new logging categories have sysctl/module parameter reachability through the shared global.
