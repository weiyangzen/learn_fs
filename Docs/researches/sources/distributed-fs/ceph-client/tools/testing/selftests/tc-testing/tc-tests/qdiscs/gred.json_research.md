# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/gred.json

Purpose: 7 GRED tests for default setup, `grio`, `limit`, `ecn`, `harddrop`, parameter change, and class display.

APIs and control flow: Uses `$TC qdisc add|change|show` and `$TC class show`. Cases configure `setup vqs`, `default`, flags, and a VQ change with min/max/burst/probability parameters.

State/dependencies: State is GRED virtual queue configuration and RED thresholds. Requires sch_gred and `nsPlugin`.

Risks/test signals: Nested VQ output and unit conversion are version-sensitive. All cases expect exit `0`; class display expects zero class matches.
