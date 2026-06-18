# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/autoattach.c

Purpose: verifies per-program skeleton auto-attach control.

Important APIs/types/functions: uses `test_autoattach.skel.h`; calls `bpf_program__set_autoattach`, `bpf_program__autoattach`, and `test_autoattach__attach`.

Control flow: open/load skeleton, disable autoattach for `prog2`, assert `prog1` remains autoattachable and `prog2` does not, attach the skeleton, trigger via `usleep`, and assert only `prog1_called` is set.

State and persistence behavior: skeleton BSS booleans record whether each BPF program ran. Link state is owned by the skeleton and cleaned up by destroy.

Dependencies and integration points: generated skeleton and libbpf autoattach APIs.

Risks: relies on the paired BPF object's attach points being triggered by `usleep`. The test intentionally mutates autoattach before attach; changing skeleton defaults can alter expectations.

Test signals: boolean autoattach flags before attach and BSS called flags after trigger.
