# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms.c

Research item: `subset-b-006814` ordinal `46`. Source size: 825 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms.c_research.md`.

## Purpose
The file validates BPF access to typed kernel symbols or kfunc calls, including nullable parameters, dynptr parameters, module symbols, and weak references. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_link_fops`, `bpf_link_fops1`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `handler`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `handler`.

## State And Persistence Behavior
Global data/control fields include `out__bpf_link_fops`, `out__bpf_link_fops1`, `out__btf_size`, `out__per_cpu_start`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stdbool.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
BTF availability, module load state, nullable contract enforcement, and read/write restrictions can change load outcomes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ksyms.c` is a test fixture for kernel symbol/kfunc/BTF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__u64 out__bpf_link_fops = -1;` | `__u64 out__bpf_link_fops1 = -1;` | `extern const void bpf_link_fops __ksym;` | `extern const void bpf_link_fops1 __ksym __weak;` | `SEC("raw_tp/sys_enter")` | `out__bpf_link_fops = (__u64)&bpf_link_fops;` | `out__bpf_link_fops1 = (__u64)&bpf_link_fops1;` | `char _license[] SEC("license") = "GPL";`
