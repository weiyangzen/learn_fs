<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/config -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/config

Purpose: declares kernel configuration prerequisites for netconsole selftests.

Important entries: `CONFIG_CONFIGFS_FS=y`, `CONFIG_IPV6=y`, `CONFIG_NETCONSOLE=m`, `CONFIG_NETCONSOLE_DYNAMIC=y`, `CONFIG_NETCONSOLE_EXTENDED_LOG=y`, and `CONFIG_NETDEVSIM=m`.

Control flow: consumed by kselftest/config tooling rather than executed.

State/dependencies: requires configfs, dynamic/extended netconsole, IPv6, and netdevsim. Risks are tests being skipped or failing noisily if config fragments are not applied. Test signals are kernel config availability before running the shell tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/config -->
