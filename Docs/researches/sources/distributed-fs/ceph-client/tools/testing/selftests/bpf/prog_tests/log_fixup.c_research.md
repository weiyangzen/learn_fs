<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_fixup.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_fixup.c

Purpose: validates verifier log fixups for BPF assembly/source metadata, ensuring loader and verifier diagnostics remain meaningful after instruction fixups.

Important APIs and functions: the file loads test BPF objects/program variants with libbpf options that capture verifier logs, toggles autoload as needed, and searches for expected strings. It uses selftest assertion macros, skeleton/object open/load APIs, and log buffers.

Control flow: subtests open the fixture object, select a program or scenario, attempt load, and compare the resulting log against expected fixed-up instruction/source references. Negative cases expect load failure; positive cases ensure fixups do not corrupt accepted loads.

State and persistence: state is limited to verifier log buffers and temporary BPF object/program fds. There is no lasting map or kernel object state after close/destroy.

Dependencies and integration: depends on companion BPF fixtures for log-fixup scenarios, libbpf verifier logging, and stable instruction/source diagnostics from the kernel verifier.

Risks and test signals: strong signals are exact fixed-up log fragments. Risk is high sensitivity to harmless verifier wording changes, compiler instruction layout changes, or BTF/source-line metadata changes in the BPF fixture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_fixup.c -->
