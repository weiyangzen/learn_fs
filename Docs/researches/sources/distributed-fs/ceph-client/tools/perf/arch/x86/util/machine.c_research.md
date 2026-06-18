# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/machine.c

Purpose: adds x86_64-specific extra kernel maps for entry trampoline symbols so perf can resolve trampoline addresses that live outside normal kernel text mappings.

Important APIs/types/functions: `struct extra_kernel_map_info` accumulates candidate maps and `_entry_trampoline`. `add_extra_kernel_map()` grows the map array. `find_extra_kernel_maps()` is a kallsyms parser callback that records `_entry_trampoline` and `is_entry_trampoline()` symbols. `machine__create_extra_kernel_maps()` is the integration entry point.

Control flow: the machine chooses a kallsyms filename, skips restricted `/proc/kallsyms`, parses symbols, requires `_entry_trampoline`, patches every collected trampoline map's `pgoff` to the entry trampoline base, and calls `machine__create_extra_kernel_map()` for each.

State and persistence: temporary symbol-derived map data is heap-allocated and freed before return. The durable effect is mutation of the perf `machine` object: extra maps are installed and `machine->trampolines_mapped` records the count.

Dependencies and integration: compiled only for `__x86_64__`. Depends on perf machine/map/symbol APIs, kallsyms parser, ELF binding translation, page size, and `is_entry_trampoline()`.

Risks: if kallsyms is restricted or `_entry_trampoline` is absent, the function silently does nothing. Map end is assumed to be one page after symbol start. Allocation or map creation failure aborts the pass.

Test signals: symbol resolution tests on x86_64 kernels with KPTI trampolines, restricted kallsyms behavior, and perf report annotation of entry trampoline samples.
