# sources/distributed-fs/ceph-client/fs/smb/server/Kconfig

Purpose: exposes kernel configuration for KSMBD, the in-kernel SMB3 server, including base server support, optional SMB Direct/RDMA transport, optional capability gating for server control, and Kerberos support.

Important APIs/types/functions: `config SMB_SERVER` is a tristate that depends on `INET`, `MULTIUSER`, and `FILE_LOCKING`, selects NLS, UTF-8/UCS-2 helpers, crypto primitives, AEAD modes, ASN.1/OID support, and CRC32, and builds the module as `ksmbd`. `config SMB_SERVER_SMBDIRECT` enables RDMA/SMB Direct when InfiniBand support is compatible. `config SMB_SERVER_CHECK_CAP_NET_ADMIN` controls network-admin capability checks for starting the server. `config SMB_SERVER_KERBEROS5` enables Kerberos 5 authentication support.

Control flow: Kconfig selection determines which source files and code paths compile. Enabling `SMB_SERVER` pulls in the core server and required crypto/parser dependencies. `SMB_SERVER_SMBDIRECT` adds RDMA transport objects through the Makefile. `SMB_SERVER_KERBEROS5` changes authentication header sizing and compiles Kerberos IPC paths.

State and persistence behavior: no runtime state exists in Kconfig. The selected options shape the kernel image/module and therefore the available protocol features after boot.

Dependencies and integration points: integrates with the Linux build system, KSMBD userspace tooling (`ksmbd-tools`), crypto API, ASN.1 compiler, OID registry, network stack, NLS/unicode handling, and optional InfiniBand/RDMA stack.

Risks: missing selected crypto or ASN.1 dependencies would lead to link or runtime negotiation failures. Enabling SMB_SERVER without a matching userspace daemon leaves login/share configuration unavailable. The RDMA dependency expression must avoid impossible module/built-in combinations. Disabling the CAP_NET_ADMIN check lowers the barrier for local server-control attempts.

Test signals: build as built-in and module, with and without Kerberos, with and without RDMA, and verify startup through ksmbd-tools, NTLM/Kerberos session setup, SMB3 encryption/signing negotiation, and module load/unload dependency cleanup.
