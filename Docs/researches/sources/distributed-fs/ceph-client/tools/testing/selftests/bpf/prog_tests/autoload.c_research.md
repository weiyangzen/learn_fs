# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/autoload.c

Purpose: verifies that disabling autoload for a broken program allows the rest of a skeleton to load and attach successfully.

Important APIs/types/functions: uses `test_autoload.skel.h`, `test_autoload__open_and_load`, `test_autoload__open`, `bpf_program__set_autoload`, `test_autoload__load`, and `test_autoload__attach`.

Control flow: first confirms full open-and-load unexpectedly fails because `prog3` is broken. It then opens without loading, disables autoload for `prog3`, loads and attaches, triggers with `usleep`, and checks that `prog1` and `prog2` were called while `prog3` was not.

State and persistence behavior: BSS fields track program calls. Skeleton owns loaded programs and links until destroy.

Dependencies and integration points: generated skeleton and libbpf autoload controls.

Risks: the test's first phase expects load failure for the full skeleton; if the paired BPF program changes and `prog3` is no longer broken, the test fails by design.

Test signals: expected failure of full open/load, successful selective load/attach, and BSS called flags.
