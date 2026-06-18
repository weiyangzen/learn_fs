# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_print.c

Purpose: provides DRM printing infrastructure, debug category control, `drm_printer` backends for coredumps and seq_file, device-aware printk wrappers, bit/register/hex dump helpers, and dynamic-debug integration.

Important APIs/types/functions: global `__drm_debug` is the DRM debug category bitmask. Dynamic debug builds define `drm_debug_classes` and a `ddebug_class_param`. `__drm_puts_coredump()` and `__drm_printfn_coredump()` implement offset/range copying into `drm_print_iterator`. `__drm_puts_seq_file()` and `__drm_printfn_seq_file()` write to seq_file. `__drm_printfn_info()`, `__drm_printfn_dbg()`, `__drm_printfn_err()`, `__drm_printfn_line()`, `drm_puts()`, `drm_printf()`, `drm_dev_printk()`, `__drm_dev_dbg()`, and `__drm_err()` are printer and log entry points. `drm_print_bits()`, `drm_print_regset32()`, and `drm_print_hex_dump()` format common diagnostics.

Control flow: module parameter `debug` either directly controls `__drm_debug` or maps bit classes to dynamic debug. Printer callbacks receive a `drm_printer` whose `arg`, `prefix`, `origin`, and category determine the output target. Coredump printing either skips until the requested offset, copies directly when the formatted string fits, or formats into a temporary buffer and feeds the generic puts path. Debug printing first checks `__drm_debug_enabled()` before emitting.

State and persistence behavior: persistent state is the global debug bitmask and dynamic-debug class map. Coredump state is caller-supplied iterator offset/start/remain/data. Line printers mutate an embedded counter in the `drm_printer`.

Dependencies and integration points: used across DRM core and drivers through `drm_print.h` macros. Integrates with kernel printk, device logging, seq_file/debugfs, coredump capture, dynamic debug, and MMIO register dumps.

Risks: coredump formatting intentionally uses `GFP_KERNEL | __GFP_NOWARN | __GFP_NORETRY`; allocation failure silently drops that formatted fragment. `drm_print_regset32()` performs raw MMIO reads and depends on valid register mappings. Debug gating must stay aligned with enum category ordering and dynamic-debug class names.

Test signals: module parameter and dynamic-debug category toggling, coredump offset/length boundary tests, seq_file/debugfs output checks, prefix/origin formatting, bit list formatting for empty and unknown names, register dump smoke tests with safe mock mappings, and hex dump line splitting.
