<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods___mod_swap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods___mod_swap.c

## Purpose

BTF CO-RE relocation fixture for `mods___mod_swap` target type compatibility; it exists to produce BTF for libbpf relocation tests.

## Important APIs, Types, and Functions

- Important functions/callbacks: `f`
- Fixture type: `mods___mod_swap`; function prototypes intentionally reference `core_reloc_types.h` structs so BTF contains the desired target shape.

## Control Flow and Data Flow

There is no runtime BPF control flow. Compilation emits a function prototype using the named fixture struct, and libbpf CO-RE tests consume the resulting BTF as a target/object type layout.

## State and Persistence Behavior

Persistent state is the compiled BTF/type metadata. Runtime state is absent or limited to dummy function reachability; test results are produced by libbpf loaders comparing expected relocation or dumper output.

## Dependencies and Integration Points

Includes `core_reloc_types.h`. Depends on `core_reloc_types.h` and libbpf CO-RE relocation tests that match object BTF against target BTF variants.

## Risks and Edge Cases

Risk is mostly fixture drift: if `core_reloc_types.h`, clang BTF emission, or libbpf matching semantics change, this tiny file can stop representing the intended compatibility case.

## Test Signals

Load/attach success and verifier log expectations are primary signals. CO-RE test harness should report the expected pass/fail relocation result for the specific fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf__core_reloc_mods___mod_swap.c -->
