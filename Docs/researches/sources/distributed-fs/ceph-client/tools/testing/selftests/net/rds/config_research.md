<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/config

## Purpose

This kselftest config fragment lists the kernel features needed for the RDS TCP selftest.

## Important APIs, Types, and Functions

The fragment enables network namespaces, netem qdisc, RDS core, RDS TCP transport, and veth. These match the runtime topology and packet impairment features used by `test.py`.

## Control Flow

There is no executable flow. Kernel config tooling can merge the options into a test kernel configuration.

## State and Persistence Behavior

The file persists build-time configuration requirements only.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are kernel support for `CONFIG_RDS`, `CONFIG_RDS_TCP`, `CONFIG_NET_NS`, `CONFIG_VETH`, and `CONFIG_NET_SCH_NETEM`. Integration is with kselftest config fragments and with `run.sh` validation. Risks include module-vs-built-in mismatches because `run.sh` also expects `CONFIG_MODULES` disabled for its coverage-oriented environment. Test signal is that `run.sh` configuration checks pass rather than skipping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/config -->
