<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_module.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_module.c

Purpose: Covers module-backed bpf_testmod struct_ops loading, multiple callback signatures, optional callbacks, zeroed fields, and incompatible local struct flavors.

Important APIs/types/functions: Defines `test_1`, `test_2`, optional `test_3`, v2/zeroed/incompatible local ops structs, and several `.struct_ops.link` maps.

Control flow: Callbacks update globals or return computed values; most behavior is in load/link type matching and how zeroed/missing fields are interpreted.

State and persistence: Globals `test_1_result` and `test_2_result` persist callback effects; linked maps persist selected ops variants.

Dependencies and integration: Depends on bpf_testmod module BTF, libbpf CO-RE flavor matching, and struct_ops link creation.

Risks: Module BTF absence, incompatible callback prototypes, or optional section handling can change expected outcomes.

Test signals: Tests load valid maps, expect incompatible maps to fail when intended, and verify callback result globals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_module.c -->
