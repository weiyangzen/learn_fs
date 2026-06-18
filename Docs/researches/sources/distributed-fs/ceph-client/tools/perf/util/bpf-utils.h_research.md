# sources/distributed-fs/ceph-client/tools/perf/util/bpf-utils.h

Purpose: declares BPF utility helpers and the linearized `bpf_prog_info` storage format used by perf.

Important APIs and types: `ptr_to_u64()` converts pointers for kernel ABI fields. `LIBBPF_CURRENT_VERSION_GEQ()` and `HAVE_LIBBPF_STRINGS_SUPPORT` gate libbpf feature use. `enum perf_bpil_array_types` names retrievable `bpf_prog_info` arrays. `struct perf_bpil` records compiled info length, data length, included array bitmask, a `bpf_prog_info`, and a flexible data area. Public functions fetch linear info and convert addresses to offsets or offsets to addresses.

Control flow: no implementation flow; the declarations support BPF event code that needs to serialize/deserialize BPF program information.

State and persistence: `perf_bpil` is explicitly designed as a contiguous, persistable blob after pointer fields are converted to offsets.

Dependencies and integration points: only active under `HAVE_LIBBPF_SUPPORT`, includes libbpf headers and version macros. Used by `bpf-event.c` and any report path that reads stored BPF program info.

Risks: compile-time libbpf feature checks must match actual APIs. The blob format depends on the tool's compiled `struct bpf_prog_info` size, recorded in `info_len`, so readers must handle version skew.

Test signals: build with multiple libbpf versions, save/load `perf_bpil` blobs across pointer conversion, and verify every enum array type maps to the correct kernel info fields.
