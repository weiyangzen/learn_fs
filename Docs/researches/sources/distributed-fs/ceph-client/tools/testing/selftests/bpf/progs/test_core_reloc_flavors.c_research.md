<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_flavors.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_flavors.c

Purpose: CO-RE flavor matching test for local types with suffix variants.

Important APIs/types/functions: Defines `core_reloc_flavors` plus reversed/weird flavors and handler `test_core_flavors`.

Control flow: Program reads fields through a local flavor and relies on libbpf matching compatible target flavors.

State and persistence: State is output globals.

Dependencies and integration: Depends on CO-RE type flavor matching conventions.

Risks: Wrong flavor selection can map fields to incompatible layouts.

Test signals: Tests load with multiple target flavors and validate outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_flavors.c -->
