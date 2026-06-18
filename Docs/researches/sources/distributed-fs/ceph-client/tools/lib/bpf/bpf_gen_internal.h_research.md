<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_gen_internal.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_gen_internal.h

## Purpose
`bpf_gen_internal.h` declares libbpf's internal generated-loader state and operations. This machinery builds BPF instruction/data blobs that can recreate object loading steps in a generated loader program.

## Important APIs, types, and functions
`struct ksym_relo_desc` records extern/kernel-symbol relocations by name, kind, instruction index, weakness, typeless status, and LD64 status. `struct ksym_desc` stores resolved/generated ksym metadata. `struct bpf_gen` owns loader options, data and instruction buffers, endian state, cleanup label, program/map counts, log level, error, ksym and CO-RE relocation arrays, attach target, fd array bookkeeping, and hash instruction offsets. Declared functions initialize, finish, free, load BTF, create maps, load programs, update/freeze maps, record attach targets, record externs, record CO-RE relocations, and populate outer maps.

## Control flow
Higher-level libbpf code initializes `bpf_gen`, records object-load operations as it parses maps/programs/relocations, then finishes the generated loader. The functions declared here append data and instructions while tracking errors in the `bpf_gen` state.

## State and persistence behavior
State is entirely in `struct bpf_gen` and its heap arrays/buffers. It persists across one object-generation session and is freed by `bpf_gen__free()`. Generated blobs can persist as skeleton or loader artifacts outside this header.

## Dependencies and integration points
It includes `bpf.h` and `libbpf_internal.h`, uses SHA256 sizing and `struct bpf_core_relo`, and is consumed by libbpf generator implementation files, not external applications.

## Risks and edge cases
This is an internal ABI between libbpf source files; field layout changes must be synchronized. Endianness, cleanup labels, fd-array indexing, and relocation counts are easy to corrupt because they coordinate generated instructions and runtime object indexes.

## Test signals
Build generated-loader/selftest paths, load objects with maps, inner maps, extern ksyms, weak symbols, CO-RE relocations, BTF, attach targets, and endian-swapped targets. Memory-leak tests should exercise early-error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_gen_internal.h -->
