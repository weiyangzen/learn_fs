# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_weak.c

Research item: `subset-b-006814` ordinal `51`. Source size: 1854 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_weak.c_research.md`.

## Purpose
The file validates BPF access to typed kernel symbols or kfunc calls, including nullable parameters, dynptr parameters, module symbols, and weak references. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_prog_active`, `bpf_task_acquire`, `bpf_testmod_test_mod_kfunc`, `bpf_link_fops1`, `bpf_link_fops2`, `bpf_per_cpu_ptr`, `bpf_ksym_exists`
- Declared maps: None visible in this compact source.
- Key local types: `struct rq`, `struct task_struct`
- Main functions/subprograms: `bpf_testmod_test_mod_kfunc`, `invalid_kfunc`, `pass_handler`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `bpf_testmod_test_mod_kfunc`, `invalid_kfunc`, `pass_handler`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `out__existing_typed`, `out__existing_typeless`, `out__non_existent_typeless`, `out__non_existent_typed`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
BTF availability, module load state, nullable contract enforcement, and read/write restrictions can change load outcomes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ksyms_weak.c` is a test fixture for kernel symbol/kfunc/BTF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `extern const void bpf_prog_active __ksym __weak; /* typeless */` | `struct task_struct *bpf_task_acquire(struct task_struct *p) __ksym __weak;` | `void bpf_testmod_test_mod_kfunc(int i) __ksym __weak;` | `extern const void bpf_link_fops1 __ksym __weak;` | `extern const int bpf_link_fops2 __ksym __weak;` | `SEC("raw_tp/sys_enter")` | `rq = (struct rq *)bpf_per_cpu_ptr(&runqueues, 0);` | `if (rq && bpf_ksym_exists(&runqueues))` | `out__existing_typeless = (__u64)&bpf_prog_active;` | and 10 more marker lines
