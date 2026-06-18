# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/memstress.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/memstress.h

Purpose: shared memory-stress workload interface for KVM selftests. It defines guest/host data structures and setup helpers for tests that fault, write, or verify large guest memory ranges with multiple vCPUs.

Important APIs/types/functions: declares memory stress argument structures, guest workload entry points, per-vCPU setup helpers, VM creation/setup routines, argument parsing/help helpers, and synchronization helpers used by dirty-log, page-fault, demand-paging, and memory-attribute tests.

Control flow and state: host code configures a `memstress` workload, creates a VM with requested memory backing and vCPU count, places per-vCPU arguments in guest memory, runs workers, and collects progress through ucalls or shared state. Guest state includes working-set addresses, page counts, stride/randomization policy, and write/read verification data.

Dependencies and integration: depends on `kvm_util.h`, `test_util.h`, guest modes, memory backing source parsing, and ucall synchronization. It integrates with userfaultfd, dirty logging, private memory, and NUMA-sensitive tests.

Risks: stress tests are sensitive to host memory availability, backing source page size, vCPU scheduling, and NUMA balancing. Incorrect page-count conversion or guest address placement can produce false memory corruption or mapping failures.

Test signals: memory stress consumers validate this header by running workload loops under different backing sources, vCPU counts, and access patterns. Failures usually appear as guest assertion failures, unexpected exits, or data mismatch reports.
