# sources/distributed-fs/ceph-client/fs/smb/server/Makefile

Purpose: defines the KSMBD module object composition and generated ASN.1 dependencies for the SMB3 server build.

Important APIs/types/functions: `obj-$(CONFIG_SMB_SERVER) += ksmbd.o` builds the aggregate module. `ksmbd-y` includes unicode, auth, VFS/cache, server, NDR, misc, oplock, connection, work, crypto context, management objects, SMB common/protocol handlers, IPC/TCP transports, ACL code, generated SPNEGO ASN.1 objects, and `asn1.o`. Conditional additions include `transport_rdma.o` for `CONFIG_SMB_SERVER_SMBDIRECT` and `proc.o` for `CONFIG_PROC_FS`.

Control flow: kbuild links all listed objects into `ksmbd.o`. Explicit dependencies ensure `asn1.o` sees generated SPNEGO token headers and that generated ASN.1 C/header pairs are built before their objects.

State and persistence behavior: no runtime state is defined. The Makefile controls which compiled code is present in the module.

Dependencies and integration points: integrates with kbuild, the kernel ASN.1 compiler for `ksmbd_spnego_negtokeninit.asn1` and `ksmbd_spnego_negtokentarg.asn1`, optional procfs reporting, and optional RDMA transport support.

Risks: missing an object from `ksmbd-y` can compile individual code but break link-time symbols or runtime features. Incorrect ASN.1 dependencies can create parallel-build races where generated headers are absent. Conditional objects must stay aligned with Kconfig and `#ifdef` guards.

Test signals: parallel kernel builds, module link checks, clean rebuilds after touching ASN.1 files, builds for all combinations of procfs/RDMA/Kerberos, and smoke tests that exercise negotiation, session setup, tree connect, VFS operations, and unload.
