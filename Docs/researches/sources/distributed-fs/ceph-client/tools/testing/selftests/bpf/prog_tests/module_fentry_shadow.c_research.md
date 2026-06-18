<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_fentry_shadow.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_fentry_shadow.c

Purpose: verifies fentry attachment to a module symbol when local/module BTF shadows or differs from vmlinux BTF.

Important APIs and functions: `get_bpf_testmod_btf_fd()` locates module BTF for `bpf_testmod`. `test_module_fentry_shadow()` loads a raw or skeleton program targeting `bpf_fentry_shadow_test`, configures expected attach BTF information, attaches, triggers the module path, and checks execution.

Control flow: obtain module BTF fd, open/load program with attach target metadata, attach fentry, trigger module function, assert result, cleanup.

State and persistence: temporary BTF fd, BPF program/link, and module-trigger state only.

Dependencies and integration: depends on `bpf_testmod`, module BTF availability, libbpf internal helpers, cgroup/test helpers, and symbol `bpf_fentry_shadow_test`.

Risks and test signals: successful load/attach and observed hit prove correct BTF target resolution. Risks include missing module BTF, symbol rename, and kernel BTF ID resolution changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_fentry_shadow.c -->
