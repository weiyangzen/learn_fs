<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/kernel/version_test.go -->
## sources/control-plane/ceph-csi/pkg/util/kernel/version_test.go

Purpose: tests kernel version retrieval, parsing, and support matching.

Coverage: `GetKernelVersion` must return a non-empty, non-NUL-suffixed string. Parser rejects malformed releases and accepts documented suffix/extraversion forms with expected numeric tuples. Support checks include generic minimum kernels and RHEL `.el7`/`.el8` backports for quota and deep-flatten feature examples.

State and dependencies: one test depends on the host kernel syscall; remaining tests are pure.

Integration: confirms support rules can represent both upstream and vendor-backported features.

Risks and gaps: host-dependent test could fail only on unusual Unix environments. No tests for multiple supported rules with overlapping distro substrings beyond current examples.

Test signal quality: good coverage for parser behavior and feature support policy.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/kernel/version_test.go -->
