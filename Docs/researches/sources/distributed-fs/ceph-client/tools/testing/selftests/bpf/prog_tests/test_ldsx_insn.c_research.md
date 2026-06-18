<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ldsx_insn.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ldsx_insn.c

Purpose: verifies signed load-extension BPF instructions for map values, probed memory, cgroup socket context members, and narrow skb context fields.

Important APIs/types/functions: `test_map_val_and_probed_memory()`, `test_ctx_member_sign_ext()`, `test_ctx_member_narrow_sign_ext()`, `test__join_cgroup()`, `trigger_module_test_read()`, `bpf_program__attach_cgroup()`, and `bpf_prog_test_run_opts()`. It uses generated `test_ldsx_insn.skel.h`.

Control flow: each subtest opens a skeleton, skips if `skel->rodata->skip` is set, enables only the relevant programs, loads, and triggers execution through either bpf_testmod read, `getsockopt()` on a socket in a cgroup, or TC program test-run over `pkt_v4`. BSS fields record sign-extended results.

State and persistence: transient cgroup `/ldsx_test`, a socket fd, skeleton links, and BSS result fields. All handles are closed/destroyed in local cleanup paths.

Dependencies and integration: depends on BPF test module trigger support, cgroup setup helpers, networking helpers for `pkt_v4`, and kernel support for LDXSX instructions. Integrated as `test_ldsx_insn`.

Risks: skip gating hides unsupported-kernel failures. The module-read path requires bpf_testmod. Sign-extension assertions are sensitive to verifier/JIT codegen and context field widths.

Test signals: checks BSS `done*`, return flags, `int_member == -1`, cgroup `optlen`/`retval == -1`, and TC `set_mark == -2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ldsx_insn.c -->
