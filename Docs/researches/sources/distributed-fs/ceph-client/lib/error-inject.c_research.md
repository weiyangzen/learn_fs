# sources/distributed-fs/ceph-client/lib/error-inject.c

## Purpose
Maintains the kernel's whitelist of functions that are safe targets for function-level error injection, such as BPF error injection. It discovers whitelist entries from built-in and module sections, answers address/type queries, and exposes a debugfs listing.

## Important APIs, Types, and Functions
Key public functions are `within_error_injection_list(unsigned long addr)` and `get_injectable_error_type(unsigned long addr)`. Internal state is represented by `struct ei_entry`, which records a function start/end range, error type, and owner pointer. `populate_error_injection_list()`, `populate_kernel_ei_list()`, `module_load_ei_list()`, and `module_unload_ei_list()` manage entries. Seq-file callbacks behind `DEFINE_SEQ_ATTRIBUTE(ei)` implement debugfs `error_injection/list`.

## Control Flow
Late init calls `populate_kernel_ei_list()` to scan the built-in `_error_inject_whitelist` section. With modules enabled, a module notifier adds entries on `MODULE_STATE_COMING` and removes entries belonging to that module on `MODULE_STATE_GOING`. Population resolves symbol descriptors, validates that the target is kernel text, looks up function size through kallsyms, allocates an `ei_entry`, and appends it to the global list.

## State and Persistence
Mutable state is the global `error_injection_list`, protected by `ei_mutex`. Built-in entries live until shutdown; module entries are tagged with `priv = mod` and removed on unload. Debugfs only reflects this live in-memory list.

## Dependencies and Integration Points
Uses `linux/error-injection.h`, kallsyms, kprobes symbol descriptor handling, module notifiers, debugfs, seq_file, and section markers `__start_error_injection_whitelist`/`__stop_error_injection_whitelist`. Consumers such as BPF/kprobe error injection call the query APIs to enforce the whitelist and allowed return type.

## Risks
If kallsyms lookup fails or allocation stops, entries are skipped, reducing injection coverage. Address-range matching depends on accurate function sizes and symbol descriptor dereferencing. The list is linear, which is simple but can become costly if many whitelist entries exist. `init_error_injection()` ignores debugfs init failure when module notifier registration succeeds, so debugfs observability is best-effort.

## Test Signals
Check that built-in whitelist entries appear in debugfs, module load/unload adds and removes entries, address queries match inside but not outside function ranges, and each `EI_ETYPE_*` maps to the expected string. Negative tests should cover invalid section entries and allocation/kallsyms failures.
