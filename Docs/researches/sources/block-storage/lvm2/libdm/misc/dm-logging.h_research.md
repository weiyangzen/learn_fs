# File Research: sources/block-storage/lvm2/libdm/misc/dm-logging.h

## Summary
Provides libdm logging macro glue that routes source-file and line-number-aware messages through the exported `dm_log_with_errno` callback and then includes the broader LVM logging interface.

## Main Contents
- Declares `extern dm_log_with_errno_fn dm_log_with_errno`.
- Defines `LOG_MESG()`, `LOG_LINE()`, `LOG_LINE_WITH_ERRNO()`, and `LOG_LINE_WITH_CLASS()`.
- Includes `lib/log/log.h` after macro setup.

## Important Behavior
Logging macros capture `__FILE__` and `__LINE__` and pass either errno-like values or debug classes through the same callback signature.

## State and Lifetime
The actual logging function pointer is defined elsewhere. This header establishes the macro contract used by libdm source files.

## Risks
Every log call depends on `dm_log_with_errno` being initialized consistently by the library/application. Macro varargs are compiler-extension style.
