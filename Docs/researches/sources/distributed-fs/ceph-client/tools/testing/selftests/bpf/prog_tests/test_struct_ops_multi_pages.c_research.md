<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_pages.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_pages.c

Purpose: verifies struct_ops trampoline allocation/attachment when callbacks span more than one page of generated trampoline code.

Important APIs/types/functions: generated `struct_ops_multi_pages` skeleton, `bpf_map__attach_struct_ops()`, and `bpf_link__destroy()`.

Control flow: open/load skeleton, attach `skel->maps.multi_pages`, assert link creation, destroy link and skeleton.

State and persistence: transient struct_ops link only.

Dependencies and integration: depends on architecture/kernel trampoline allocation behavior and generated large callback set. Integrated as subtest `multi_pages`.

Risks: comment notes the page-size condition is at least true for x86; coverage may be weaker or different on other architectures. It tests attach success, not callback execution results.

Test signals: skeleton load and struct_ops attach success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_pages.c -->
