# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func6.c

Research item: `subset-b-006814` ordinal `32`. Source size: 649 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func6.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `f1`, `f3`, `f2`, `global_func6`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `f1`, `f3`, `f2`, `global_func6`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func6.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `__failure __msg("modified ctx ptr R2")`
