## sources/distributed-fs/ceph-client/fs/smb/smbdirect/Kconfig

Purpose: declares the shared SMBDirect kernel configuration option used by SMB RDMA support.

Important APIs and types: defines `config SMBDIRECT` as a tristate defaulting to disabled. It depends on `INFINIBAND` and `INFINIBAND_ADDR_TRANS`, additionally requiring module builds when InfiniBand is modular or built-in InfiniBand for built-in use, and selects `SG_POOL`.

Control flow: Kconfig dependency resolution decides whether the smbdirect object set can be built. Server-side `CONFIG_SMB_SERVER_SMBDIRECT` code imports the `SMBDIRECT` namespace and relies on these common objects being available.

State and persistence behavior: no runtime state; build-time configuration only.

Dependencies and integration points: integrates SMB client/server RDMA code with the Linux RDMA stack, scatter-gather pool support, and the `fs/smb/smbdirect/Makefile` object list.

Risks: dependency mismatches can produce unresolved symbols or unavailable RDMA support even when server code is enabled. Default `n` means RDMA paths may receive less build/test coverage than TCP.

Test signals: Kconfig resolution for `SMBDIRECT=m/y/n`, builds with InfiniBand disabled/modular/built-in, selected `SG_POOL`, and server SMBDirect namespace import linking.
