<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.c

## Purpose

`esas2r_log.c` implements the ESAS2R driver's small logging subsystem. It gates events by a module parameter, formats messages with optional device identity, translates ESAS2R log levels to kernel log priorities, and emits messages or hexdumps to the kernel log.

## Important APIs, Types, and Functions

The externally visible functions are `esas2r_log()`, `esas2r_log_dev()`, and `esas2r_log_hexdump()`. `esas2r_log_master()` is the shared formatter, declared with `__printf` checking and passed a `va_list`. `translate_esas2r_event_level_to_kernel()` maps `ESAS2R_LOG_CRIT`, `WARN`, `INFO`, `DEBG`, and `TRCE` to `KERN_CRIT`, `KERN_WARNING`, `KERN_INFO`, and `KERN_DEBUG`.

The module parameter `event_log_level` defaults to `ESAS2R_LOG_DFLT` from `esas2r_log.h`; normal builds log critical and warning events, while trace builds default to trace verbosity. A single `event_buffer[1024]` and `event_buffer_lock` are used to serialize formatted messages.

## Control Flow

Callers invoke `esas2r_log()` for plain driver messages or `esas2r_log_dev()` for messages that include device driver, bus, and device name fields. Both wrappers start a varargs list and call `esas2r_log_master()`. The master helper first checks `level <= event_log_level`; skipped messages do no formatting. For emitted messages it takes `event_buffer_lock` with IRQ save, zeroes the shared buffer, writes either `"<level>esas2r: "` or `"<level>esas2r [driver, bus, dev]"`, advances to the remaining buffer area, appends the caller's formatted message with `vsnprintf()`, calls `printk("%s\n", event_buffer)`, and releases the spinlock.

`esas2r_log_hexdump()` performs the same level check, then calls `print_hex_dump()` with offset prefixes, 16-byte rows, one-byte groups, and ASCII output enabled.

## State and Persistence Behavior

The file has no persistent storage. State is module-global: current log level, one formatting buffer, and one spinlock. The log level is readable through module-parameter permissions and affects all adapters in the module. Because formatting is centralized through one shared buffer, messages from multiple CPUs are serialized.

## Dependencies and Integration Points

The file depends on kernel logging, module parameters, `struct device`, spinlocks, and hex dump helpers through `esas2r.h`. The macros in `esas2r_log.h` compile debug and trace calls either to these functions or to no-ops depending on `ESAS2R_DEBUG` and `ESAS2R_TRACE`.

## Risks and Edge Cases

The formatter holds a spinlock while calling `printk()`, which is simple but can lengthen interrupt-disabled critical sections when logging heavily. Messages longer than the remaining fixed 1024-byte buffer are truncated by `vsnprintf()` but still emitted. `esas2r_log_hexdump()` returns `1` when it logs or skips, unlike `esas2r_log()` returning `0` on success; callers should not treat it as a conventional errno-style helper. Device formatting omits a separator after the device tuple before the caller message, so log readability depends on caller text.

## Test Signals

Validation signals include module loading with `event_log_level` values 0 through 5, critical/warning default output, debug/trace builds honoring macro expansion, device and non-device log prefixes, long-message truncation without overflow, hexdump formatting, and concurrent logging under interrupt and process contexts without interleaved shared-buffer output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.c -->
