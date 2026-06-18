# sources/distributed-fs/ceph-client/tools/testing/selftests/nci/config

Purpose: Declares the kernel configuration needed to run the NCI virtual-device selftest.

Important APIs/types/functions: Requests `CONFIG_NFC=y`, `CONFIG_NFC_NCI=y`, and `CONFIG_NFC_VIRTUAL_NCI=y`.

Control flow: Kselftest configuration tooling reads this file when preparing a kernel config for the `nci` test group.

State and persistence behavior: No runtime state. It influences kernel build configuration, enabling NFC core, NCI protocol support, and the virtual NCI character device.

Dependencies and integration points: Directly supports `nci_dev.c`, which opens `/dev/virtual_nci`, uses NFC generic netlink commands, and creates AF_NFC sockets.

Risks: If any option is built as absent, the test will fail early at device open, generic netlink family lookup, or AF_NFC socket creation.

Test signals: Presence of `/dev/virtual_nci`, NFC generic netlink family registration, and successful `nci_dev` execution confirm this config is effective.
