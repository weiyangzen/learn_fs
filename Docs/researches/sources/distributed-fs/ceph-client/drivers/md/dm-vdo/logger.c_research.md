# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logger.c

## Purpose
`logger.c` implements VDO logging on top of kernel `printk` APIs. It applies the module log level, formats context-aware prefixes for interrupt, VDO device, VDO kernel thread, and generic process contexts, and provides error-string and assertion support.

## Important APIs, Types, and Functions
Public functions are `vdo_get_log_level()`, `vdo_log_embedded_message()`, `vdo_vlog_strerror()`, `__vdo_log_strerror()`, `vdo_log_backtrace()`, `__vdo_log_message()`, and `vdo_pause_for_logger()`. Internals include `get_current_interrupt_type()`, `emit_log_message_to_kernel()`, and `emit_log_message()`.

## Control Flow
`vdo_get_log_level()` clamps an invalid global level back to default. Logging calls build `va_format` values, choose output priority, and emit through `pr_crit`, `pr_err`, `pr_warn`, `pr_info`, `pr_debug`, or generic `printk`. Prefix selection first handles interrupt context, then registered device IDs, then own kernel threads, then generic process/module names. Error logging resolves VDO/UDS error strings and appends numeric codes.

## State and Persistence Behavior
`vdo_log_level` is global runtime state read with `READ_ONCE()` and corrected with `WRITE_ONCE()`. No log state is persistent. `vdo_pause_for_logger()` sleeps briefly to reduce message loss after heavy logging.

## Dependencies and Integration Points
The file depends on Linux current task, interrupt context, printk, module, scheduler, VDO error string conversion, thread-device IDs, and thread-utils naming. It is used across nearly all VDO/UDS modules and by `permassert.c`.

## Risks and Edge Cases
Logging can be called from interrupt contexts, so context detection and formatting avoid blocking work except for explicit pause. Invalid priorities fall back to default `printk`. `va_list` handling uses `va_copy()` because ABI representation can vary. High-volume logging still risks kernel log loss, hence rate-limited macros in the header and pause helper.

## Test Signals
Test log level clamping, each priority path, error-string formatting, interrupt-context prefixing where feasible, device-thread prefixing, assertion backtrace logging, and rate-limited macro behavior from callers.
