<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_buf.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_buf.c

Purpose: verifies libbpf and raw BPF syscall log-buffer handling for object load, per-program load logs, `bpf_prog_load()`, and BTF load diagnostics.

Important APIs and functions: `libbpf_print_cb()` captures libbpf print output into a fixed buffer. `obj_load_log_buf()` tests object-level and per-program log buffers on `test_log_buf`, including a good and bad program. `bpf_prog_load_log_buf()` directly loads hand-written good/bad socket-filter instruction arrays. `bpf_btf_load_log_buf()` builds raw BTF and checks BTF load log behavior. The top-level test runs these subtests.

Control flow: first round uses object and per-program buffers and expects BPF object load failure with isolated program logs. Second round removes the object log buffer so bad-program verifier logs flow through the libbpf print callback. Raw program and BTF helpers check log level zero versus verbose log levels.

State and persistence: state is in heap log buffers, static capture buffers, and temporary program/BTF fds. All fds and skeletons are closed; the old libbpf print callback is restored.

Dependencies and integration: depends on `test_log_buf.skel.h`, libbpf print callback APIs, raw `bpf_prog_load`, BTF APIs, and stable verifier log fragments.

Risks and test signals: exact substrings such as program load banners, `R0 !read_ok`, and BTF/data-section diagnostics are the pass signals. Tests are sensitive to verifier log wording and log-level policy changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_buf.c -->
