<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup1_hierarchy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup1_hierarchy.c

Purpose: Tests cgroup v1 hierarchy access from LSM and fentry programs.

Important APIs/types/functions: Defines cgroup local struct declarations, `bpf_link_create_verify`, LSM `bpf`, sleepable LSM, and fentry programs.

Control flow: Programs validate cgroup hierarchy/id properties when BPF links are created.

State and persistence: No maps; globals record validation results if present.

Dependencies and integration: Depends on LSM/fentry hooks and cgroup struct BTF.

Risks: Cgroup v1/v2 hierarchy assumptions and sleepable context differences are risks.

Test signals: Tests create cgroup links and verify expected hierarchy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup1_hierarchy.c -->
