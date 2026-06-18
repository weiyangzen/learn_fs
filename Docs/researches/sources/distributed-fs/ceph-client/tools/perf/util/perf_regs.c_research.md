# sources/distributed-fs/ceph-client/tools/perf/util/perf_regs.c

## Purpose
This file is the architecture-neutral dispatcher for perf register metadata. It maps ELF machine IDs to architecture-specific register masks, register names, IP and SP register identifiers, and SDT argument parsing hooks.

## Important APIs, Types, and Functions
Exports include `perf_sdt_arg_parse_op`, `perf_intr_reg_mask`, `perf_user_reg_mask`, `perf_reg_name`, `perf_reg_value`, `perf_arch_reg_ip`, and `perf_arch_reg_sp`. It works with `struct regs_dump` from sample decoding and the architecture helpers declared in `perf_regs.h`.

## Control Flow
Most functions switch on `e_machine` and call the matching `__perf_reg_*_<arch>` helper. Unknown machines log debug messages and return empty masks, `"unknown"`, or zero IP/SP IDs. `perf_reg_value` checks the requested ID against `PERF_SAMPLE_REGS_CACHE_SIZE`, validates that the sampled register mask contains it, computes the dense index in the sample register array, and caches the value by register ID.

## State and Persistence
There is no global state. Per-call caching is stored in the caller-owned `regs_dump` through `cache_mask` and `cache_regs`.

## Dependencies and Integration Points
The file depends on ELF machine constants, architecture-specific perf register modules, DWARF register naming, and sampled register storage. It feeds perf script/report paths that display sampled register values or resolve probe SDT arguments.

## Risks
Unsupported `e_machine` values silently lose register masks, which can degrade decoding without failing the whole command. `perf_reg_value` assumes `regs->regs` is ordered by ascending bits in `regs->mask`; mismatch with sample parsing corrupts displayed values.

## Test Signals
Tests should cover each supported ELF machine, unknown-machine fallbacks, dense-index register extraction, cache reuse, and invalid IDs. Architecture build coverage is important because missing helper definitions surface only on some configs.
