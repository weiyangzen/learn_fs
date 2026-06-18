# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_probe_user.c

Research item: `subset-b-006814` ordinal `96`. Source size: 1217 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_probe_user.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `ksyscall/connect`, `ksyscall/socketcall`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_core_read`, `bpf_misc`, `bpf_get_current_pid_tgid`, `bpf_probe_read_user`, `bpf_probe_write_user`, `bpf_target_s390`
- Declared maps: None visible in this compact source.
- Key local types: `struct test_pro_bss`, `struct sockaddr_in`
- Main functions/subprograms: `handle_sys_connect_common`, `BPF_KSYSCALL`

## Control Flow
Entry programs are attached through `ksyscall/connect`, `ksyscall/socketcall`. Control is organized around `handle_sys_connect_common`, `BPF_KSYSCALL`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `bss`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`.
Local test dependencies: `vmlinux.h`, `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_probe_user.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include <bpf/bpf_core_read.h>` | `#include "bpf_misc.h"` | `__u32 cur = bpf_get_current_pid_tgid() >> 32;` | `bpf_probe_read_user(&bss.old, sizeof(bss.old), uservaddr);` | `bpf_probe_write_user(uservaddr, &new, sizeof(new));` | `SEC("ksyscall/connect")` | `#if defined(bpf_target_s390)` | `SEC("ksyscall/socketcall")` | and 2 more marker lines
