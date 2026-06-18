<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_core_read.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_core_read.h

## Purpose
`bpf_core_read.h` provides BPF CO-RE read, type, field, enum, and bitfield macros. It lets BPF programs read kernel data structures in a way that emits BTF relocations so libbpf can adapt offsets, sizes, signedness, and type IDs to the target kernel.

## Important APIs, types, and functions
The header defines relocation info enums (`bpf_field_info_kind`, `bpf_type_id_kind`, `bpf_type_info_kind`, `bpf_enum_value_kind`), field/type/enum helpers (`bpf_core_field_exists`, `bpf_core_type_exists`, `bpf_core_enum_value`, etc.), direct/probed bitfield macros, `bpf_core_read*()` wrappers, `bpf_core_cast()`, pointer-chasing internals, and high-level macros such as `BPF_CORE_READ()`, `BPF_CORE_READ_INTO()`, `BPF_CORE_READ_STR_INTO()`, plus user-space and non-CO-RE probe-read variants.

## Control flow
The macros expand at BPF program compile time. Clang/GCC builtins preserve access indices or type info, creating relocations in BTF sections. Runtime reads happen through helpers such as `bpf_probe_read_kernel()`, direct loads for eligible program types, or user-memory read helpers. Variadic macro machinery supports up to nine field accessors for pointer chasing.

## State and persistence behavior
There is no runtime persistent state in the header. It influences compiled BPF bytecode and relocation metadata persisted inside the BPF object file.

## Dependencies and integration points
It depends on `bpf_helpers.h`, compiler BTF builtins, kernel BTF, and libbpf CO-RE relocation processing. It integrates with BPF programs built from `vmlinux.h` or equivalent BTF-derived types.

## Risks and edge cases
CO-RE user reads still require kernel/UAPI types known to target BTF; arbitrary userspace structs are not relocatable. Big-endian bitfield reads need adjusted destination offsets. Compiler differences require separate clang/GCC type-reference paths. Deep pointer chains beyond macro limits are unsupported.

## Test signals
BPF selftests should cover field existence/offset/size, type matches, enum relocations, bitfields on little and big endian, pointer chasing, string reads, user reads, GCC and Clang builds, and fallback non-CO-RE macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_core_read.h -->
