# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/config

Purpose: Kernel config fragment for generic driver network selftests.

Important entries: `CONFIG_CONFIGFS_FS`, `CONFIG_DEBUG_INFO_BTF`, `CONFIG_INET_PSP`, `CONFIG_IPV6`, `CONFIG_MACSEC`, `CONFIG_NETCONSOLE`, `CONFIG_NETCONSOLE_DYNAMIC`, `CONFIG_NETCONSOLE_EXTENDED_LOG`, `CONFIG_NETDEVSIM`, `CONFIG_VLAN_8021Q`, and `CONFIG_XDP_SOCKETS`.

Control flow: No executable flow; declares required kernel capabilities.

State and persistence: Build/test configuration only.

Dependencies and integration points: Supports PSP, MACsec, netconsole, netdevsim, VLAN, XDP socket, BTF, and IPv6 tests listed in the parent Makefile.

Risks and test signals: Missing entries convert tests into skips or build/run failures. BTF and netdevsim are especially important for Python driver tests and BPF-adjacent coverage.
