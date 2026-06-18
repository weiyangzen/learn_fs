<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_legacy.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_legacy.h

## Purpose
This public header preserves legacy or discouraged libbpf APIs so applications prepared for or migrated through libbpf 1.0 can still compile without adopting newer names and behavior immediately.

## APIs, Types, and Functions
`enum libbpf_strict_mode` documents historical strict-mode bits including clean pointers, direct errors, strict section names, no object list, automatic memlock rlimit bumping, and strict map definitions. In libbpf 1.0+ `libbpf_set_strict_mode()` is intentionally retained but has no effect. `libbpf_get_error()` is retained for old ERR_PTR-style pointer error handling, although modern libbpf returns `NULL` and uses `errno`. `DECLARE_LIBBPF_OPTS` aliases `LIBBPF_OPTS`. Discouraged compatibility APIs include `libbpf_find_kernel_btf()`, `bpf_program__get_type()`, `bpf_program__get_expected_attach_type()`, `bpf_map__get_pin_path()`, `btf__get_raw_data()`, and `btf_ext__get_raw_data()`.

## Control Flow, State, and Persistence
This header only declares compatibility entry points. The important state behavior is semantic: strict-mode flags no longer change global runtime behavior, and `libbpf_get_error(NULL)` is only reliable if `errno` still reflects the preceding libbpf call. The discouraged accessor APIs expose existing object/program/map/BTF state without owning it.

## Dependencies and Integration
It includes Linux BPF UAPI types, C scalar headers, and `libbpf_common.h`, and is included by `libbpf.h`. It integrates with older libbpf callers and migration code that has not switched to modern names or direct errno checks.

## Risks and Test Signals
Risks include callers believing strict mode still toggles behavior, `errno` being overwritten before `libbpf_get_error()`, and new code copying discouraged naming patterns. Test signals are compile compatibility for legacy callers, runtime checks that `libbpf_set_strict_mode()` is harmless, and error-path tests documenting modern `NULL` plus `errno` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_legacy.h -->
