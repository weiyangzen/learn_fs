<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_module.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_module.c

Purpose: CO-RE relocation test against bpf_testmod module BTF using raw_tp and tp_btf program variants.

Important APIs/types/functions: Defines module context/output structs and programs on `bpf_testmod_test_read` raw and BTF tracepoints.

Control flow: Programs read module-provided fields through CO-RE and store output.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on module BTF availability and bpf_testmod tracepoints.

Risks: Module not loaded or mismatched BTF will skip/fail tests; relocation target namespace is sensitive.

Test signals: Tests load bpf_testmod, trigger read hook, and inspect outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_module.c -->
