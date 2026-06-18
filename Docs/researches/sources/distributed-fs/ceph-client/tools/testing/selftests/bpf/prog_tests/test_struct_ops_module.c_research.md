<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_module.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_module.c

Purpose: comprehensive module-backed struct_ops coverage using bpf_testmod: map BTF ownership, callback replacement, zeroed-field compatibility, incompatible signatures, nulling callbacks, forgotten callback diagnostics, link detach notification, and unsupported-ops delegation.

Important APIs/types/functions: `check_map_info()` verifies `btf_vmlinux_id` points to BTF object named `bpf_testmod`; `attach_ops_and_check()` attaches a struct_ops map and checks BSS callback results; `bpf_map__attach_struct_ops()`, `bpf_map_get_info_by_fd()`, `bpf_btf_get_fd_by_id()`, `bpf_btf_get_info_by_fd()`, libbpf log capture, `bpf_link__detach()`, and `epoll_wait()` are central.

Control flow: `test_struct_ops_load()` customizes struct_ops fields, disables unused autoload, loads, checks map info, and attaches two maps with expected results. `test_struct_ops_not_zeroed()` verifies zero-valued unknown fields are accepted while nonzero unknown values or non-null unknown ops are rejected. `test_struct_ops_incompatible()` loads and attaches a map whose program signature is intentionally left for kernel verifier enforcement. Other subtests null out supported callbacks, validate a useful libbpf error for an unreferenced struct_ops program then programmatically reference it, and detach a link while waiting for `EPOLLHUP`. `serial_test_struct_ops_module()` runs these serially and also runs `unsupported_ops`.

State and persistence: attaches struct_ops links to bpf_testmod and inspects skeleton BSS results. Epoll monitors a link fd. Log capture allocates a string that is freed. All skeletons/links/fds are destroyed or closed in cleanup.

Dependencies and integration: depends on bpf_testmod being loaded with BTF, generated skeletons, struct_ops link fds, epoll, libbpf log capture, and serial execution to avoid module-global interference. Entry point is `serial_test_struct_ops_module`, not a plain `test_` function.

Risks: kernel module availability and BTF naming are hard requirements. Unknown-field compatibility behavior is libbpf-version sensitive. Link-detach notification depends on fd lifetime and epoll semantics.

Test signals: map BTF name equality, callback result values (`0xdeadbeef`, `20`, `12`), accepted/rejected loads, libbpf diagnostic substring, detach success, single `EPOLLHUP`, and `RUN_TESTS(unsupported_ops)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_module.c -->
