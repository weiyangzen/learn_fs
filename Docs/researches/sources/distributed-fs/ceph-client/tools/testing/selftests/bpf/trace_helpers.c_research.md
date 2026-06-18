<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.c

## Purpose
`trace_helpers.c` provides tracing-related utilities for BPF selftests: loading and searching kallsyms, resolving uprobe offsets and relative offsets, reading ELF build IDs, reading trace_pipe, and enumerating ftrace-attachable symbols or addresses.

## Important APIs, Types, And Functions
- Kallsyms support: `load_kallsyms_local_common()`, `load_kallsyms_local()`, `load_kallsyms_custom_local()`, `load_kallsyms()`, `ksym_search_local()`, `search_kallsyms_custom_local()`, `ksym_search()`, `ksym_get_addr_local()`, `ksym_get_addr()`, and `kallsyms_find()`.
- Uprobe helpers: `get_uprobe_offset()` and `get_rel_offset()` parse `/proc/self/maps` or use optional `PROCMAP_QUERY`.
- Build ID helpers: `parse_build_id_buf()` and `read_build_id()` parse ELF PT_NOTE GNU build-id notes.
- Trace pipe helpers: `read_trace_pipe_iter()` and `read_trace_pipe()`.
- Attachable symbol enumeration: `bpf_get_ksyms()` returns filtered names, while `bpf_get_addrs()` returns filtered addresses.
- Filtering helpers skip invalid kernel/module entries and known risky symbols such as idle, RCU, migration, preempt count, and BPF dispatcher functions.

## Control Flow
Kallsyms loaders read `/proc/kallsyms`, allocate symbol arrays with `libbpf_ensure_mem()`, add names, and sort by address or custom comparator. Search functions use binary search. Uprobe offset resolution first tries `PROCMAP_QUERY` and falls back to scanning `/proc/self/maps`; PPC64 ABIv2 adjusts for global entry-point stubs. Build-ID reading opens an ELF file, scans program headers for PT_NOTE, and extracts GNU notes. `bpf_get_ksyms()` cross-references `available_filter_functions` with kallsyms, deduplicates names through libbpf hashmap, and stores filtered symbols in the returned `struct ksyms`.

## State And Persistence
Global `ksyms` caches process-wide kallsyms behind `ksyms_mutex`. Local `struct ksyms` instances own dynamically allocated names, symbol arrays, and filtered symbol lists. Trace and proc reads do not persist state. Returned arrays must be freed through `free_kallsyms_local()` or caller-managed frees as documented by usage.

## Dependencies And Integration Points
It depends on procfs, tracefs/debugfs, libelf/gelf, libbpf internal hashmap/memory helpers, Linux perf/build-id constants, optional `PROCMAP_QUERY`, and architecture-specific uprobe semantics. It is used by kprobe/fentry/uprobe/fprobe tests and stack-symbolization helpers.

## Risks And Edge Cases
Kernel symbol visibility can be restricted by `kptr_restrict`, lockdown, or permissions. `ksym_search_local()` can read `syms[start]` when the key is above the last symbol if not carefully bounded by inputs. Tracefs paths differ by mount. `read_trace_pipe_iter()` has subtle precedence in `getline()` assignment and can spin on `EAGAIN`. Build-ID parsing trusts ELF note sizing and requires `BPF_BUILD_ID_SIZE`.

## Test Signals
Consumers fail with missing symbols, unresolved uprobe offsets, absent build IDs, inability to open tracefs files, or attach failures against filtered symbol sets. Verbose `PROCMAP_QUERY` output can help diagnose offset resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.c -->
