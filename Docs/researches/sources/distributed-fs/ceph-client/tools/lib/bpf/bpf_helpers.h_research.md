<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_helpers.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_helpers.h

## Purpose
`bpf_helpers.h` is the primary convenience header for BPF C programs. It imports generated helper prototypes and defines macros for map definitions, ELF sections, attributes, common utilities, debug printing, open-coded iterators, and verifier-friendly loop constructs.

## Important APIs, types, and functions
It includes `bpf_helper_defs.h`, defines map declaration helpers (`__uint`, `__type`, `__array`, `__ulong`), `SEC()`, function attributes (`__always_inline`, `__noinline`, `__weak`, `__hidden`), BTF tags (`__kconfig`, `__ksym`, `__kptr*`, `__uptr`, `__arg_*`), `offsetof`, `container_of`, `barrier`, `barrier_var`, `__bpf_unreachable`, `bpf_tail_call_static()`, pin/tristate enums, `bpf_ksym_exists()`, formatting wrappers (`BPF_SEQ_PRINTF`, `BPF_SNPRINTF`, `bpf_printk`, `bpf_stream_printk`), and iterator macros `bpf_for_each`, `bpf_for`, and `bpf_repeat`.

## Control flow
Most behavior is compile-time macro expansion. Section and BTF tag macros shape the ELF/BTF that libbpf parses. Print wrappers build temporary `u64` argument arrays for helpers. Iterator macros use BPF open-coded iterator kfuncs plus cleanup attributes to create verifier-friendly loops.

## State and persistence behavior
The header itself has no persistent state, but its section macros define object-file state such as maps, program sections, `.kconfig`, and `.ksyms`. Print format strings may become static global data unless `BPF_NO_GLOBAL_DATA` is set.

## Dependencies and integration points
It depends on generated helper prototypes, compiler support for GNU attributes/pragmas, BPF target compilation, and kernel kfunc/helper availability. It is included by most libbpf-style BPF programs and by `bpf_core_read.h`/`bpf_tracing.h`.

## Risks and edge cases
Programs must include `vmlinux.h` or Linux types before this header so generated helper prototypes see `__u64` and peers. GCC and clang differ in attribute diagnostics and weak-symbol checks. `bpf_tail_call_static()` requires a constant slot. Iterator macros depend on cleanup attribute support and kfunc availability.

## Test signals
Compile BPF samples/selftests with clang and GCC, with and without global data, use map definition macros, print wrappers with more than three args, static tail calls, weak ksym existence checks, and open-coded iterator loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_helpers.h -->
