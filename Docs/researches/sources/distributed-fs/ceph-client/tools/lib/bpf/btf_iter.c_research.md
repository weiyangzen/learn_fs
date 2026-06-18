# sources/distributed-fs/ceph-client/tools/lib/bpf/btf_iter.c

## Purpose
`btf_iter.c` provides a small iterator over mutable fields embedded in raw BTF type records. It abstracts the per-kind layout differences so callers can visit either type-id references or string-offset references without open-coding offsets for every BTF kind.

## APIs, Types, and Functions
The exported functions are `btf_field_iter_init()` and `btf_field_iter_next()`. The iterator state is `struct btf_field_iter` from the shared BTF internals, with a `btf_field_desc` describing top-level offsets, optional per-member record size, per-member offsets, current member index, current offset index, and vlen. `BTF_FIELD_ITER_IDS` enumerates fields that contain BTF type IDs, while `BTF_FIELD_ITER_STRS` enumerates fields that contain string-table offsets.

## Control Flow, State, and Persistence
Initialization clears the iterator and then selects a descriptor based on requested field kind and `btf_kind(t)`. ID iteration covers `type` fields on modifiers, pointers, typedefs, funcs, vars, tags, array element and index types, composite member types, function return and parameter types, and datasec variable references. String iteration covers `name_off` on type records plus enum enumerators, enum64 enumerators, composite members, and function parameters. `btf_field_iter_next()` first returns top-level fields, then advances into fixed-size member records using `btf_vlen(t)` until exhausted, at which point it nulls the cursor.

## Dependencies and Integration
The file is dual-use for userspace libbpf and kernel code. Under `__KERNEL__` it includes Linux BPF/BTF headers and maps `btf_var_secinfos()` to the kernel helper; otherwise it uses `btf.h` and `libbpf_internal.h`. `btf_relocate.c` uses the iterator to rewrite split BTF type IDs and string offsets without duplicating BTF-kind layout knowledge.

## Risks and Test Signals
Risks are concentrated in descriptor correctness: a wrong offset silently rewrites the wrong word in a BTF record, and missing support for a new BTF kind can break relocation or validation with `-EINVAL`. Because the iterator returns mutable `__u32 *` pointers into caller-owned BTF memory, callers must only use it on writable records. Test signals include relocating BTF containing every supported kind, ID and string iteration count checks, datasec/func-proto/composite coverage, and build coverage for both userspace and `__KERNEL__` include paths.
