# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_set_remove_xattr.c

Research item: `subset-b-006814` ordinal `112`. Source size: 3662 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_set_remove_xattr.c_research.md`.

## Purpose
The program attaches to file-security hooks or tracing points to validate xattr, fsverity, and inode metadata helper behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/inode_getxattr`, `lsm.s/inode_setxattr`
- BPF helpers/macros used: `bpf_tracing`, `bpf_kfuncs`, `bpf_misc`, `bpf_probe_read_kernel`, `bpf_strncmp`, `bpf_set_dentry_xattr`, `bpf_remove_dentry_xattr`, `bpf_dynptr`, `bpf_get_current_pid_tgid`, `bpf_dynptr_from_mem`, `bpf_get_dentry_xattr`, `bpf_set_dentry_xattr_locked`, `bpf_remove_dentry_xattr_locked`
- Declared maps: None visible in this compact source.
- Key local types: `struct dentry`, `struct bpf_dynptr`, `struct mnt_idmap`
- Main functions/subprograms: `name_match_foo`, `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/inode_getxattr`, `lsm.s/inode_setxattr`. Control is organized around `name_match_foo`, `BPF_PROG`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `monitored_pid`, `xattr_foo`, `xattr_bar`, `xattr_selinux`, `value_bar`, `read_value`, `set_security_bpf_bar_success`, `remove_security_bpf_bar_success`, `set_security_selinux_fail`, and 6 more.. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`, `bpf_kfuncs.h`, `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Kernel VFS, LSM hook signature, and helper permission changes can alter verifier acceptance or expected errno/data capture.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_set_remove_xattr.c` is a test fixture for LSM/file metadata BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_tracing.h>` | `#include "bpf_kfuncs.h"` | `#include "bpf_misc.h"` | `char _license[] SEC("license") = "GPL";` | `bool set_security_bpf_bar_success;` | `bool remove_security_bpf_bar_success;` | `bpf_probe_read_kernel(name_buf, sizeof(name_buf), name);` | `return !bpf_strncmp(name_buf, sizeof(xattr_foo), xattr_foo);` | `/* Test bpf_set_dentry_xattr and bpf_remove_dentry_xattr */` | `SEC("lsm.s/inode_getxattr")` | and 17 more marker lines
