<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_prog_linfo.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_prog_linfo.c

## Purpose
`bpf_prog_linfo.c` builds a searchable representation of BPF program line information returned by `BPF_OBJ_GET_INFO_BY_FD`. It maps translated instruction offsets and JITed instruction addresses back to `struct bpf_line_info` records.

## Important APIs, types, and functions
`struct bpf_prog_linfo` stores raw xlated line info, optional raw JITed line info, per-JIT-function line counts, per-function start indexes, total line count, JIT function count, and record sizes. Public functions are `bpf_prog_linfo__new()`, `bpf_prog_linfo__free()`, `bpf_prog_linfo__lfind()`, and `bpf_prog_linfo__lfind_addr_func()`. `dissect_jited_func()` validates and partitions JITed line-info addresses by kernel symbol function ranges.

## Control flow
Construction validates that line info exists and has a minimum record size, copies raw xlated line info from addresses embedded in `struct bpf_prog_info`, then optionally copies JITed line info and builds per-function indexes if all required JIT metadata is present. Lookup by instruction offset or JIT address starts at an optional skip index and returns the last line record not greater than the query.

## State and persistence behavior
All state is heap-owned by `struct bpf_prog_linfo` and freed by `bpf_prog_linfo__free()`. It snapshots kernel-provided info at construction time; it does not refresh if the program changes or is unloaded.

## Dependencies and integration points
It depends on `linux/bpf.h`, `struct bpf_prog_info`, `struct bpf_line_info`, errno conventions, and libbpf allocation/error style. Higher-level libbpf consumers use it for symbolization and diagnostics.

## Risks and edge cases
The code treats numeric addresses from `bpf_prog_info` as user pointers via casts; callers must have populated the info buffers correctly. Pointer arithmetic on `void *` relies on GNU C. JIT validation assumes monotonically increasing addresses within each function. Constructor failures collapse several allocation/validation errors to `EINVAL`.

## Test signals
Load BPF programs with BTF line info, query info, construct linfo, and test lookups at exact offsets, between offsets, before first entry, with skip values, with and without JITed metadata, and with intentionally inconsistent JIT function ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_prog_linfo.c -->
