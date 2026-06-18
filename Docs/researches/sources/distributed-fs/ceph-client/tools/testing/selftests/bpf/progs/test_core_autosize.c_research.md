<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_autosize.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_autosize.c

Purpose: CO-RE autosize tests for reads into local structs whose source/target field sizes differ.

Important APIs/types/functions: Defines local real/samesize/downsize/signed structs and raw tracepoint handlers `handle_samesize`, `handle_downsize`, `handle_probed`, `handle_signed`.

Control flow: Handlers perform CO-RE reads and compare sign/size behavior, writing results for userspace.

State and persistence: Persistent state is BSS data/result globals.

Dependencies and integration: Depends on `BPF_CORE_READ`/CO-RE relocation and clang/BTF typing.

Risks: Autosized reads must not overrun destinations or mishandle sign extension.

Test signals: Tests feed input structs and verify output bytes/values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_autosize.c -->
