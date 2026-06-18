# sources/distributed-fs/ceph-client/tools/perf/tests/vmlinux-kallsyms.c

## Purpose
This test compares symbols loaded from a matching `vmlinux` image against symbols parsed from `/proc/kallsyms`, validating perf's kernel symbol loading, relocation, map splitting, symbol lookup, and tolerance for known architecture/linker artifacts.

## Important APIs, Types, And Functions
Important functions are `is_ignored_symbol()`, three verbose map comparison callbacks, and `test__vmlinux_matches_kallsyms()`. It uses `struct machine`, `struct maps`, `struct map`, `struct dso`, `struct symbol`, rb-tree symbol iteration, `machine__create_kernel_maps()`, `machine__load_kallsyms()`, `machine__load_vmlinux_path()`, `machine__find_kernel_symbol()`, `machine__find_kernel_symbol_by_name()`, `map__unmap_ip()`, `map__for_each_symbol()`, `maps__for_each_map()`, and `arch__compare_symbol_names()`.

## Control Flow
The test initializes separate `machine` instances for kallsyms and vmlinux. It creates kernel maps for kallsyms, loads `/proc/kallsyms` without kcore, captures the kallsyms kernel map, creates vmlinux maps, auto-locates a matching vmlinux, and then iterates every non-empty vmlinux symbol. For each symbol, it maps vmlinux IPs to runtime addresses, finds a kallsyms symbol at that address, accepts exact or architecture-normalized name matches, tolerates end-address skew below one page, ignores aliases to `_etext`, and filters known synthetic/local/debug/absolute symbols. Any remaining missing symbol marks failure. Verbose mode prints map-only and renamed-map diagnostics.

## State, Dependencies, And Integration
The test reads live host kernel state from `/proc/kallsyms`, `/proc/modules`, module files, and vmlinux search paths. It registers as `DEFINE_SUITE("vmlinux symtab matches kallsyms", vmlinux_matches_kallsyms)`. It owns `machine` lifetimes and releases both via `machine__exit()`.

## Risks And Test Signals
It is host-sensitive: missing permissions, unavailable matching vmlinux, module churn, restricted kallsyms, or unusual linker symbols can skip or fail the test. `TEST_SKIP` is expected when kernel maps, kallsyms, or vmlinux cannot be loaded. True failures signal symbol relocation, filtering, or lookup regressions.
