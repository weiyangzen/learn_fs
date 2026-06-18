# sources/distributed-fs/ceph-client/include/drm/drm_print.h

## Purpose
`drm_print.h` centralizes DRM logging and printable output streams. It provides `drm_printer` abstractions for debugfs, devcoredump, device logs, debug logs, error logs, line-numbered dumps, and DRM-specific printk/dev_printk wrappers.

## Important APIs, types, and functions
Important types are `enum drm_debug_category`, `struct drm_printer`, and `struct drm_print_iterator`. Categories map to `drm.debug` bits such as CORE, DRIVER, KMS, PRIME, ATOMIC, VBL, STATE, LEASE, DP, and DRMRES. Printer constructors include `drm_coredump_printer`, `drm_seq_file_printer`, `drm_info_printer`, `drm_dbg_printer`, `drm_err_printer`, and `drm_line_printer`. Output APIs include `drm_printf`, `drm_puts`, `drm_vprintf`, `drm_print_regset32`, `drm_print_bits`, and `drm_print_hex_dump`. Logging macros cover `drm_info`, `drm_warn`, `drm_err`, category-specific `drm_dbg_*`, ratelimited debug/error variants, deprecated `DRM_*` and `DRM_DEV_*` macros, and device-aware `drm_WARN*`.

## Control flow
Callers construct a printer for the target sink, then pass it to shared dump functions. Debug logging first checks either `__drm_debug` bits or dynamic-debug class callsites depending on configuration. Coredump printing uses an iterator offset/remain model for read callbacks or two-pass buffered generation.

## State and persistence
Global debug state is `__drm_debug`, typically controlled by the `drm.debug` module parameter/sysfs. Printer state is stack/local and records sink callback pointers, argument, origin, prefix, line counter, and category. Static ratelimit and once flags persist for each callsite.

## Dependencies and integration points
The header depends on printk, dev_printk, dynamic debug, debugfs regsets, seq_file, devcoredump-style iterators, DRM device metadata, and WARN infrastructure. It is used throughout DRM diagnostics.

## Risks and test signals
Risks include using deprecated printk-style macros in new code, expensive formatting when debug is disabled, missing device context in logs, coredump O(N^2) generation for large dumps, incorrect format attributes, and ratelimit hiding important errors. Test signals include dynamic debug on/off builds, `drm.debug` runtime toggling, debugfs printer output, devcoredump reads at offsets, line printer numbering, ratelimited logs, and compile-time format checking.
