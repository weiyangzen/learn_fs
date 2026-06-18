# File Research: sources/block-storage/kvdo/vdo/logger.c

Kernel logging implementation for UDS/VDO.

Key responsibilities:
- Maps string names to UDS log priorities and priorities to printable names.
- Stores a global log level, defaulting to `UDS_LOG_INFO`.
- Maps UDS priorities to kernel `KERN_*` prefixes.
- Formats log messages differently for interrupt context, VDO/UDS kernel threads, device-associated threads, and other processes.
- Supports packed two-part varargs log messages.
- Logs error messages with decoded UDS/system error text.
- Emits stack traces and provides a short pause to let kernel logs flush.

Important behavior:
- Messages with priority numerically greater than current log level are dropped.
- Interrupt context logs include interrupt type (`NMI`, `HI`, `SI`, or `INTR`) and omit process context.
- Device-associated logs include module, device instance, and task name.
- Uses `va_copy()` for both varargs sections to handle implementation-specific `va_list`.

Dependencies:
- Linux printk, hardirq context helpers, module/current task state, stack dump, delay, thread-device ID, UDS thread/string error helpers.

Notable risks:
- `log_level` is a plain global int without locking.
- Logging from interrupt context intentionally avoids device/thread lookup.
