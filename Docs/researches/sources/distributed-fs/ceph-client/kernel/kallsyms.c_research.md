# sources/distributed-fs/ceph-client/kernel/kallsyms.c

## Purpose
Provides in-kernel symbol lookup, symbol formatting for stack traces/oopses, `/proc/kallsyms`, and BPF iterator exposure. It decodes the generated compressed kallsyms tables and combines vmlinux, module, ftrace, BPF, and kprobe symbol sources.

## Important APIs, Types, and Functions
Core lookup APIs are `kallsyms_lookup_name`, `kallsyms_on_each_symbol`, `kallsyms_on_each_match_symbol`, `kallsyms_lookup_size_offset`, `kallsyms_lookup`, `lookup_symbol_name`, and sprint helpers (`sprint_symbol`, `sprint_symbol_build_id`, `sprint_symbol_no_offset`, `sprint_backtrace`, `sprint_backtrace_build_id`). `struct kallsym_iter` drives `/proc/kallsyms` and BPF iteration. Compression helpers include `kallsyms_expand_symbol`, `kallsyms_get_symbol_type`, `get_symbol_offset`, `kallsyms_sym_address`, and `kallsyms_lookup_names`.

## Control Flow
Name lookup binary-searches `kallsyms_seqs_of_names`, expands candidate names from `kallsyms_names`, then scans adjacent duplicates. Address lookup binary-searches sorted addresses, backs up to the first alias, calculates symbol end from the next non-aliased symbol or section boundaries, and then expands the symbol name. `/proc/kallsyms` uses seq-file callbacks to walk core symbols first, then modules, ftrace module pages, BPF symbols, and kprobe symbols.

## State and Persistence
The main state is generated read-only arrays declared in `kallsyms_internal.h`: offsets, compressed names, token tables, markers, and name-order sequences. Iterator instances keep transient position and section-end caches. The proc entry is created at `device_initcall`.

## Dependencies and Integration Points
Integrates with modules, BPF JIT symbol lookup and BPF iterators, ftrace, kprobes, `/proc`, seq_file, KDB, build IDs, and address visibility policy through `kallsyms_show_value`. Many other kernel diagnostics rely on the sprint and lookup APIs.

## Risks
Compressed-name decoding and marker seeking must remain synchronized with `scripts/kallsyms.c` output. Symbol value visibility must not leak addresses when policy hides them. Iteration may reschedule, so module and name lifetime guarantees rely on RCU or caller discipline. Duplicate symbol names and aliases require careful ordering.

## Test Signals
`kallsyms_selftest.c` exercises lookup correctness, duplicate handling, compression ratio, and lookup performance. Runtime failures appear as missing `/proc/kallsyms` entries, incorrect stack traces, unresolved module/BPF symbols, or warnings around missing module build IDs.
