<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/99-nx-gzip.rules -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/99-nx-gzip.rules

Purpose: udev rule for making the NX gzip accelerator device accessible to selftests.

Important APIs and types: Contains a single rule matching `SUBSYSTEM=="nxgzip"` and `KERNEL=="nx-gzip"`, setting `MODE="0666"`.

Control flow: udev applies the rule when the device node is created, affecting permissions before tests open `/dev/crypto/nx-gzip`.

State and persistence: Persistent state is system device-node permissions managed by udev, not by the test binary.

Dependencies and integration points: Integrates with the NX gzip kernel driver and the selftest deployment environment.

Risks: Broad world-writable mode is appropriate for test machines but may be undesirable on production systems.

Test signals: Test signal is unprivileged ability to open `/dev/crypto/nx-gzip`; the shell wrapper skips when it is not writable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/99-nx-gzip.rules -->
