# sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd_fail_nth.c

`iommufd_fail_nth.c` is a kernel-integrity selftest for IOMMUFD error unwinding. It sweeps Linux fault-injection points through known-good IOMMUFD operation sequences to expose WARN/OOPS/KASAN bugs, leaked references, and incomplete cleanup rather than to validate normal functional output.

Important pieces are `setup_fault_injection()`, `setup_buffer()`, `writeat()`, `struct fail_nth_state`, `fail_nth_first()`, `fail_nth_next()`, `__fail_nth_enable()`, and the `TEST_FAIL_NTH()` macro. The test uses debugfs knobs under `/sys/kernel/debug/fail*` plus `/proc/self/task/<pid>/fail-nth`, and it reuses the IOMMUFD command helpers from `iommufd_utils.h`.

Control flow starts by configuring fault injection and allocating anonymous/memfd buffers. Each `TEST_FAIL_NTH` wrapper runs the scenario once without injection, then repeats fixture teardown/setup while incrementing the fail-nth point. The loop ends when the kernel reports no injection point was consumed. Covered scenarios include IOAS allocation/range/allow/map/copy/unmap paths, mapping through one or two domains, file-backed mappings, access read/write, access pinning, access pinning with domains, and device paths for HWPT, vIOMMU, hardware queue, event queue, fault queue, and PASID attach/replace/detach.

Persistent state is deliberately partial and failure-prone: `/dev/iommu` fds, access fds, mock device ids, PASID state, mapped IOAS objects, and fault/event queue fds may exist at arbitrary failure positions. Teardown handles access fd close, PASID detach, and `teardown_iommufd()` reference checks.

Dependencies are kernel fault injection, debugfs, `/proc/self/task/.../fail-nth`, `/dev/iommu`, IOMMUFD selftest hooks, and root-like permissions. Risks include the hard-coded 1000-iteration guard becoming too small, cleanup itself being fault-injected, and noisy environment setup. Pass signals are exhaustion of all injected allocation points without assertions, leaked refs, dangling PASID mappings, or kernel warnings.
