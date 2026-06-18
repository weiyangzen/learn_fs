# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_binary_stats_test.c

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_binary_stats_test.c

Purpose: executable selftest for KVM's fd-based binary statistics ABI. It validates header layout, descriptor layout, data layout, descriptor flags, exponent rules, data reads, and stats fd cleanup for KVM, VM, and vCPU stats.

Important APIs/types/functions: `stats_test(int stats_fd)`, `DEFAULT_NUM_VM`, `DEFAULT_NUM_VCPU`, and `main`. It uses `read_stats_header`, `get_stats_descriptor_size`, `read_stats_descriptors`, `get_stats_descriptor`, `read_stat_data`, VM/vCPU creation, and stats-fd helpers from `kvm_util.h`.

Control flow and state: `stats_test` reads the stats header, validates the ID string starts with `kvm`, checks descriptor/data offsets do not overlap invalidly, reads all descriptors, validates descriptor names, type/unit/base ranges, exponent rules, nonzero sizes, histogram bucket constraints, computes required data size, reads the bulk data block, then reads each stat individually. It frees allocations, closes the stats fd, and verifies the fd is closed. `main` parses optional VM/vCPU counts and runs the same validation for KVM-level, VM-level, and vCPU-level stats fds.

Dependencies and integration: depends on KVM binary stats uAPI (`struct kvm_stats_header`, `struct kvm_stats_desc`, flag masks), common test assertions, and KVM VM/vCPU creation utilities.

Risks: ABI layout assumptions are intentionally strict. Kernels adding new stat units/types must keep values within advertised max constants or update the test. The test allows no stats but prints a message and returns early.

Test signals: pass confirms binary stats fd structure is self-consistent, descriptor metadata is valid, data can be read both bulk and per-stat, and fd lifecycle is correct. Failures identify malformed offsets, flags, names, exponents, sizes, or read behavior.
