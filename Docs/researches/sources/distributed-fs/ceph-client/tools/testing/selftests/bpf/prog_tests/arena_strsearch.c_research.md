# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_strsearch.c

Purpose: narrow skeleton test for string-search logic implemented against BPF arena memory.

Important APIs/types/functions: `test_arena_str` opens/loads `arena_strsearch.skel.h`, runs the `arena_strsearch` program through `bpf_prog_test_run_opts`, and checks run and program return status.

Control flow: top-level `test_arena_strsearch` starts one subtest. The helper loads the skeleton, runs the BPF program, marks skip if the BPF side set `bss->skip`, then destroys the skeleton.

State and persistence behavior: any tested strings and results are owned inside the skeleton's BPF maps/BSS/arena. Userspace only observes the skip flag and run status in this file.

Dependencies and integration points: generated skeleton, arena support, compiler `arena_cast` support, and `test_progs.h`.

Risks: userspace does not inspect concrete match results, so most semantic checking must happen inside the paired BPF program by returning nonzero or setting skip.

Test signals: successful skeleton load, successful test run, zero BPF retval, or explicit skip on missing compiler support.
