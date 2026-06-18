# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_rdonly_maps.c

Research item: `subset-b-006814` ordinal `102`. Source size: 1757 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_rdonly_maps.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tracepoint/sys_enter:skip_loop`, `raw_tracepoint/sys_enter:part_loop`, `raw_tracepoint/sys_enter:full_loop`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct pt_regs`
- Main functions/subprograms: `skip_loop`, `part_loop`, `full_loop`

## Control Flow
Entry programs are attached through `raw_tracepoint/sys_enter:skip_loop`, `raw_tracepoint/sys_enter:part_loop`, `raw_tracepoint/sys_enter:full_loop`. Control is organized around `skip_loop`, `part_loop`, `full_loop`.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/ptrace.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_rdonly_maps.c` is a test fixture for BPF map operation selftest. Test signals are: feature/clang availability can mark the selftest skipped.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("raw_tracepoint/sys_enter:skip_loop")` | `SEC("raw_tracepoint/sys_enter:part_loop")` | `SEC("raw_tracepoint/sys_enter:full_loop")` | `char _license[] SEC("license") = "GPL";`
