# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lirc_mode2_kern.c

Research item: `subset-b-006814` ordinal `59`. Source size: 567 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lirc_mode2_kern.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lirc_mode2`
- BPF helpers/macros used: `bpf_helpers`, `bpf_decoder`, `bpf_rc_keydown`, `bpf_rc_pointer_rel`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `bpf_decoder`

## Control Flow
Entry programs are attached through `lirc_mode2`. Control is organized around `bpf_decoder`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `linux/lirc.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_lirc_mode2_kern.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `SEC("lirc_mode2")` | `int bpf_decoder(unsigned int *sample)` | `bpf_rc_keydown(sample, 0x40, duration & 0xffff, 0);` | `bpf_rc_pointer_rel(sample, (duration >> 8) & 0xff,` | `char _license[] SEC("license") = "GPL";`
