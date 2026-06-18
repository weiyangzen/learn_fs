<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_map_in_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_map_in_map.c

Purpose: Comprehensive BTF-defined map-in-map test covering array/hash outer maps, dynamic inner specs, and sockmap/sockhash variants.

Important APIs/types/functions: Defines many inner/outer map structs and raw_tp handler `handle__sys_enter`.

Control flow: The handler exists mainly to keep maps/program loadable; userspace validates map definitions and map-in-map creation.

State and persistence: Persistent state is the set of inner/outer maps and their initial values.

Dependencies and integration: Depends on BTF map definitions, inner-map templates, and socket map types.

Risks: Inner map size/type mismatch and dynamic template handling are common risks.

Test signals: Tests inspect created maps and update/lookup nested maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_btf_map_in_map.c -->
