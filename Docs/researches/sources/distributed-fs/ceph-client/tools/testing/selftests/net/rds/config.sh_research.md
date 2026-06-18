<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/config.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/config.sh

## Purpose

`config.sh` programmatically configures a kernel tree for the RDS selftest. It enables RDS TCP and required network features, disables modules, and optionally enables targeted GCOV instrumentation for RDS.

## Important APIs, Types, and Functions

The script uses `scripts/config` with optional `--file <config>` from `-c`. `-g` sets `GENERATE_GCOV_REPORT=1`. It disables `CONFIG_MODULES`, enables `CONFIG_RDS`, `CONFIG_RDS_TCP`, `CONFIG_NET_NS`, `CONFIG_VETH`, and `CONFIG_NET_SCH_NETEM`, and either enables `CONFIG_GCOV_KERNEL` plus `GCOV_PROFILE_RDS` while disabling `GCOV_PROFILE_ALL`, or disables all GCOV options.

## Control Flow

After `set -e -u -x`, it parses `-g` and `-c`, builds an optional `FLAGS` array, then applies configuration edits in a fixed sequence: no modules, RDS, optional coverage, namespaces/veth, and netem. Invalid options print usage and exit nonzero.

## State and Persistence Behavior

It mutates the target kernel `.config` or the file specified by `-c`. It unsets `KBUILD_OUTPUT`, so path resolution is tied to the current tree unless `--file` is supplied.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include running from a kernel source tree with `scripts/config`. Integration is with `run.sh`, whose `check_conf` and `check_gcov_conf` expect these exact settings. Risks are unsetting `KBUILD_OUTPUT` in out-of-tree builds, disabling modules as a broad build-policy change, and configuring GCOV without rebuilding. Signals are subsequent `run.sh` checks passing and optional coverage data appearing under debugfs GCOV after a rebuilt kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/config.sh -->
