<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_no_cfi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_no_cfi.c

Purpose: loads a kernel module that self-tests struct_ops registration with and without CFI stubs, ensuring unsupported no-CFI registration fails while the module as a whole succeeds only if expected outcomes occur.

Important APIs/types/functions: `open("bpf_test_no_cfi.ko")`, `finit_module()`, `delete_module("bpf_test_no_cfi")`, and `testing_helpers.h`.

Control flow: open module file, call `finit_module`, close fd, then delete the module. The module's init path performs the actual registration checks.

State and persistence: temporarily loads kernel module `bpf_test_no_cfi`; removes it at end if load succeeded.

Dependencies and integration: requires module file in working directory, CAP_SYS_MODULE, loadable module support, and struct_ops CFI registration code. Integrated as subtest `load_bpf_test_no_cfi`.

Risks: can leave a module loaded if `delete_module` fails. Will fail in lockdown or module-disabled environments. Most logic lives inside the module, not visible here.

Test signals: successful module open, `finit_module`, and `delete_module`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_no_cfi.c -->
