<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ns_current_pid_tgid.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ns_current_pid_tgid.c

Purpose: validates namespace-aware current pid/tgid helper behavior against userspace-created PID namespaces.

Important APIs and functions: the harness loads the companion skeleton, creates child processes/namespaces, triggers BPF programs, and checks BSS/map fields containing namespace pid/tgid values.

Control flow: setup skeleton, fork/clone or run namespace helper paths, trigger the BPF program in parent/child contexts, compare current pid/tgid in namespace and global views, then cleanup child processes and skeleton.

State and persistence: process namespace state and BPF result fields are transient. Child processes must be waited/reaped.

Dependencies and integration: depends on namespace privileges, process helpers, generated skeleton, and pid namespace helper semantics.

Risks and test signals: expected pid/tgid mappings are signals. Risks include environment restrictions on PID namespaces and races around child lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ns_current_pid_tgid.c -->
