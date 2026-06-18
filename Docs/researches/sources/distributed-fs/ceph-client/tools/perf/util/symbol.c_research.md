<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/symbol.c

## Purpose

`symbol.c` is the generic symbol-management and symbol-loading orchestrator for perf. It owns symbol allocation, rb-tree insertion and lookup, duplicate and end-address fixups, name sorting, kallsyms parsing and splitting, module parsing, kcore map loading, DSO symbol-source search policy, vmlinux/kallsyms fallback policy, symbol filters, global symbol configuration, and demangling.

## Important APIs, Types, and Functions

Major public functions include `symbol__new()`, `symbol__delete()`, `symbols__delete()`, `symbols__insert()`, `__symbols__insert()`, `symbols__fixup_duplicate()`, `symbols__fixup_end()`, `dso__insert_symbol()`, `dso__delete_symbol()`, `dso__find_symbol()`, `dso__find_symbol_nocache()`, `dso__find_symbol_by_name()`, `dso__sort_by_name()`, `modules__parse()`, `compare_proc_modules()`, `dso__load()`, `dso__load_vmlinux()`, `dso__load_vmlinux_path()`, `__dso__load_kallsyms()`, `dso__load_kallsyms()`, `symbol__init()`, `symbol__exit()`, `symbol__config_symfs()`, `symbol__validate_sym_arguments()`, and `dso__demangle_sym()`.

The central global is `struct symbol_conf symbol_conf`, initialized with defaults for demangling, modules, vmlinux search, callchain behavior, field display, symfs layout, and addr2line timeout. The file also owns `vmlinux_path` and `vmlinux_path__nr_entries`.

## Control Flow and Data Flow

Symbol allocation reserves optional private space before `struct symbol`, initializes annotation state when configured, and stores a flexible-array name. Symbols are inserted into address-ordered rb-trees. Lookups use address ranges and a DSO last-find cache; name lookups require a sorted symbol-name array. Duplicate fixup chooses the best symbol at a shared start address using length, type, binding, underscore count, name length, and architecture hooks. End fixup fills zero-sized symbols using the next symbol, with special kallsyms behavior to avoid giant gaps between kernel, module, and BPF regions.

Kernel loading first honors explicit `kallsyms` or `vmlinux` paths, then build-id cache vmlinux, configured vmlinux paths, and finally kallsyms from `/proc` or build-id cache. Kallsyms symbols are loaded into a temporary kernel DSO tree, fixed up, and split into kernel/module maps or into kcore-derived maps. User and module DSO loading searches candidate binary types in priority order, checking compatibility, namespace/chroot paths, optional BFD loading, `symsrc__init()`, and then `dso__load_sym()` plus PLT synthesis. Perf JIT maps are handled through `/tmp/perf-<pid>.map`, including mount namespace lookup.

Initialization aligns private symbol storage, initializes the ELF backend, builds vmlinux search paths, validates field separators and parallelism filters, builds DSO/comm/pid/tid/symbol/backtrace-stop filters, normalizes symfs, and reads kernel pointer restrictions. Exit frees configured lists and vmlinux paths. Demangling tries Rust v0, C++/BFD, OCaml, then Java according to kernel/user demangle flags.

## State and Persistence Behavior

This file mutates long-lived perf model state: DSO loaded flags, binary types, build IDs, symbol rb-trees, sorted name arrays, last lookup caches, map boundaries, module maps, kcore maps, and global `symbol_conf`. It reads persistent system state from `/proc/modules`, `/proc/kallsyms`, `/proc/sys/kernel/kptr_restrict`, `/proc/kcore`, uname-derived vmlinux paths, build-id caches, and `/tmp/perf-<pid>.map`. It may persist a changed build-id cache directory when `symbol__config_symfs()` is used.

## Dependencies and Integration Points

The code depends on perf `dso`, `map`, `maps`, `machine`, namespace, build-id, kallsyms, annotation, demangler, cpumap, strlist, intlist, and header utilities. It integrates with `symbol-elf.c` or `symbol-minimal.c` through `symsrc__init()` and `dso__load_sym()`, with reporting and annotation through `symbol_conf.priv_size`, and with machine/kernel map creation through `maps__insert()`, `maps__merge_in()`, and trampoline mapping.

## Risks and Edge Cases

Symbol loading races against changing `/proc/modules`, `/proc/kallsyms`, `/proc/kcore`, exiting processes, and namespace changes. Kptr restrictions and perf paranoid settings can silently restrict kernel symbol access. Duplicate selection changes can alter reported call stacks. Map splitting must preserve BPF maps and handle relocated kernels, entry trampolines, guest kernels, modules without matching maps, and kcore maps whose PT_LOAD ranges overlap. `dso__load()` marks DSOs loaded even after some failures, so retry semantics are limited. Global `symbol_conf` must be initialized before code that needs annotation private space.

## Test Signals

Tests should cover symbol rb-tree insertion/lookup boundaries, zero-sized end fixups, duplicate resolution, name sorting with versioned symbols, module file parsing, perf-map loading, explicit bad vmlinux/kallsyms validation, symfs hierarchy and flat layouts, kptr restrictions, DSO candidate search order, deleted DSOs, guest kernel fallback, and demangling for Rust/C++/OCaml/Java. Integration tests should verify kernel symbolization from vmlinux, `/proc/kallsyms`, build-id cache, and kcore, plus user DSO symbolization from debuglink/debugdata/build-id paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol.c -->
