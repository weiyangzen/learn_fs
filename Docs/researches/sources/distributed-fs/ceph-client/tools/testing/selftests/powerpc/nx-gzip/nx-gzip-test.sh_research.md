<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/nx-gzip-test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/nx-gzip-test.sh

Purpose: End-to-end shell harness for NX gzip hardware compression/decompression samples.

Important APIs and types: Checks `/dev/crypto/nx-gzip` writability, defines cleanup and `test_sizes`, creates random files with `dd`, runs `gzfht_test`, then `gunz_test`, and executes both serial and 16-way parallel loops.

Control flow: The script skips when the device is inaccessible, enables `set -e`, tests 4K/64K/1M/64M random inputs, removes temporary files on exit, and reports OK after all background jobs finish.

State and persistence: Creates temporary `nx-tempfile*`, `.nx.gz`, and `.nx.gunzip` outputs in the working directory until cleanup runs.

Dependencies and integration points: Depends on bash, `dd`, the two generated binaries, and NX gzip device permissions.

Risks: Parallel stress can be resource-heavy and assumes enough disk/time for 16 sets of large random files. Cleanup is filename-pattern based.

Test signals: Pass means all serial and parallel compression/decompression runs complete with matching checksums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/nx-gzip-test.sh -->
