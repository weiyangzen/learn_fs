# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_debug.h

## Purpose
This header provides local logging macros for the MFC driver. It centralizes debug, error, rate-limited error, and info logging with function and line metadata.

## Important APIs, Types, and Constants
`mfc_debug_level` is an external integer controlled by the module parameter in `s5p_mfc.c`. `mfc_debug(level, fmt, ...)` prints `KERN_DEBUG` messages when the configured level is high enough. `mfc_debug_enter()` and `mfc_debug_leave()` are shorthand for level-5 tracing. `mfc_err()`, `mfc_err_limited()`, and `mfc_info()` print error or info messages.

## Control Flow and State
The only state dependency is `mfc_debug_level`. The file defines `DEBUG`, so debug macro code is always compiled in for this driver, with runtime filtering by level.

## Dependencies and Integration Points
It relies on kernel `printk` and `printk_ratelimited` symbols through normal kernel headers included by users. Nearly every MFC source file includes this header for diagnostics.

## Risks
Always compiling debug logging can add code size and make excessive logs possible if the debug module parameter is raised. `mfc_err()` is not rate-limited, so repeated hardware errors can flood logs; callers should use `mfc_err_limited()` in noisy paths, as decode DQBUF does.

## Test Signals
Signals include module parameter behavior, debug-level filtering, function/line metadata in logs, and rate limiting during repeated error calls.
