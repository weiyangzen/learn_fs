# sources/distributed-fs/ceph-client/tools/perf/util/bpf-utils.c

Purpose: provides helper functions for retrieving `struct bpf_prog_info` plus selected variable-length arrays into one contiguous allocation, and for converting embedded array pointers to file-storable offsets and back.

Important APIs and functions: `get_bpf_prog_info_linear()` is the main API. It uses descriptors for arrays such as JITed instructions, translated instructions, map ids, JITed ksyms, function lengths, function info, line info, JITed line info, and program tags. `bpil_addr_to_offs()` rewrites array pointers as offsets from `info_linear->data`; `bpil_offs_to_addr()` restores them.

Control flow: the function first calls `bpf_obj_get_info_by_fd()` with an empty info struct to discover counts and record sizes. It filters requested arrays not supported by the returned info length, computes a rounded contiguous data size, allocates `struct perf_bpil + data`, points requested arrays into the data area, calls the BPF syscall again to fill data, validates that counts, sizes, and pointers match expectations, records info/data lengths, and returns the allocation.

State and persistence: returned `perf_bpil` is heap allocated and caller-owned. Pointer-to-offset conversion makes the blob suitable for storage in perf environment data or files; offset-to-pointer conversion must be done before dereferencing arrays.

Dependencies and integration points: uses libbpf/BPF syscall APIs, `struct bpf_prog_info`, perf debug logging, and header definitions from `bpf-utils.h`. BPF event synthesis stores these blobs in `perf_env`.

Risks: array sizing can race with program changes between the two info syscalls; validation catches mismatches and returns `-ERANGE`. Requested array bitmasks beyond `PERF_BPIL_LAST_ARRAY` are rejected. Old kernels with shorter `bpf_prog_info` silently drop unsupported arrays. Pointer arithmetic assumes all array pointers are inside the contiguous data block.

Test signals: tests against BPF programs with each supported array present/absent, old-kernel simulated short info lengths, mismatched counts via fault injection, pointer-offset round trips, invalid array bitmasks, and memory leak checks on all error paths.
