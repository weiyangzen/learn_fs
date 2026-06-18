# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sig_in_xattr.c

Research item: `subset-b-006814` ordinal `113`. Source size: 2726 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sig_in_xattr.c_research.md`.

## Purpose
The program attaches to file-security hooks or tracing points to validate xattr, fsverity, and inode metadata helper behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/file_open`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_kfuncs`, `bpf_get_fsverity_digest`, `bpf_dynptr`, `bpf_key`, `bpf_get_current_pid_tgid`, `bpf_dynptr_from_mem`, `bpf_get_file_xattr`, `bpf_lookup_user_key`, `bpf_verify_pkcs7_signature`, `bpf_key_put`
- Declared maps: None visible in this compact source.
- Key local types: `struct fsverity_digest`, `struct file`, `struct bpf_dynptr`, `struct bpf_key`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/file_open`. Control is organized around `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `digest`, `monitored_pid`, `sig`, `sig_size`, `user_keyring_serial`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`, `bpf_kfuncs.h`, `err.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Kernel VFS, LSM hook signature, and helper permission changes can alter verifier acceptance or expected errno/data capture.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sig_in_xattr.c` is a test fixture for LSM/file metadata BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include "bpf_kfuncs.h"` | `char _license[] SEC("license") = "GPL";` | `* and the rest of it is filled by bpf_get_fsverity_digest.` | `SEC("lsm.s/file_open")` | `struct bpf_dynptr digest_ptr, sig_ptr;` | `struct bpf_key *trusted_keyring;` | `pid = bpf_get_current_pid_tgid() >> 32;` | `bpf_dynptr_from_mem(digest + MAGIC_SIZE, sizeof(digest) - MAGIC_SIZE, 0, &digest_ptr);` | and 7 more marker lines
