# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ns_current_pid_tgid.c

Research item: `subset-b-006814` ordinal `79`. Source size: 936 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ns_current_pid_tgid.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?tracepoint/syscalls/sys_enter_nanosleep`, `?cgroup/bind4`, `?sk_msg`
- BPF helpers/macros used: `bpf_helpers`, `bpf_pidns_info`, `bpf_get_ns_current_pid_tgid`, `bpf_sock_addr`
- Declared maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u32`
- Key local types: `struct bpf_pidns_info`, `struct bpf_sock_addr`, `struct sk_msg_md`
- Main functions/subprograms: `get_pid_tgid`, `tp_handler`, `cgroup_bind4`, `sk_msg`

## Control Flow
Entry programs are attached through `?tracepoint/syscalls/sys_enter_nanosleep`, `?cgroup/bind4`, `?sk_msg`. Control is organized around `get_pid_tgid`, `tp_handler`, `cgroup_bind4`, `sk_msg`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u32`. Global data/control fields include `user_pid`, `user_tgid`, `dev`, `ino`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `stdint.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ns_current_pid_tgid.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map SEC(".maps");` | `struct bpf_pidns_info nsdata;` | `if (bpf_get_ns_current_pid_tgid(dev, ino, &nsdata, sizeof(struct bpf_pidns_info)))` | `SEC("?tracepoint/syscalls/sys_enter_nanosleep")` | `SEC("?cgroup/bind4")` | `int cgroup_bind4(struct bpf_sock_addr *ctx)` | `SEC("?sk_msg")` | `return SK_PASS;` | and 1 more marker lines
