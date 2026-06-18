<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/Kconfig -->
## sources/distributed-fs/ceph-client/fs/smb/Kconfig

Purpose: top-level SMB filesystem Kconfig menu fragment. It pulls in client, server, and SMB Direct configuration and defines aggregate SMB infrastructure symbols.

Important APIs and symbols: `source "fs/smb/client/Kconfig"`, `source "fs/smb/server/Kconfig"`, `source "fs/smb/smbdirect/Kconfig"`, `config SMBFS`, and `config SMB_KUNIT_TESTS`.

Control flow: Kconfig includes feature-specific fragments first, then derives `SMBFS` as `y` or `m` when either the CIFS client or SMB server is enabled. `SMB_KUNIT_TESTS` depends on `SMBFS && KUNIT` and defaults to `KUNIT_ALL_TESTS`, acting as a shared test umbrella for SMB code.

State and persistence: no runtime state. Its persistent effect is build configuration, influencing which directories are entered by Kbuild and which conditional code compiles.

Dependencies and integration: integrates with `fs/smb/Makefile`, KUnit, the client Kconfig, server Kconfig, and SMB Direct Kconfig. `SMBFS` is intentionally hidden/tristate infrastructure rather than a user-facing filesystem choice.

Risks: incorrect defaulting of `SMBFS` can omit common SMB code when only client or server is modular. KUnit enablement depends on `SMBFS`, so build matrix coverage needs both client and server combinations.

Test signals: run Kconfig permutations for `CIFS=y/m/n`, `SMB_SERVER=y/m/n`, `SMBDIRECT`, and `KUNIT_ALL_TESTS`; verify `fs/smb/common/` builds whenever needed and SMB KUnit tests appear only when dependencies are satisfied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/Kconfig -->
