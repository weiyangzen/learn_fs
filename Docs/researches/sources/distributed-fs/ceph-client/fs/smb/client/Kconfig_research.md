<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/Kconfig -->
## sources/distributed-fs/ceph-client/fs/smb/client/Kconfig

Purpose: defines user-visible and internal configuration for the Linux SMB3/CIFS client module, including security, DFS, witness, xattrs, debugging, RDMA, FS-Cache, root filesystem, compression, and KUnit test options.

Important symbols: `CIFS` is the main tristate and selects networking, NLS, crypto, keyring, DNS, ASN.1/OID, and netfs support. Feature symbols include `CIFS_STATS2`, `CIFS_ALLOW_INSECURE_LEGACY`, `CIFS_UPCALL`, `CIFS_XATTR`, `CIFS_POSIX`, `CIFS_DEBUG`, `CIFS_DEBUG2`, `CIFS_DEBUG_DUMP_KEYS`, `CIFS_DFS_UPCALL`, `CIFS_SWN_UPCALL`, `CIFS_NFSD_EXPORT`, `CIFS_SMB_DIRECT`, `CIFS_FSCACHE`, `CIFS_ROOT`, `CIFS_COMPRESSION`, and `SMB1_KUNIT_TESTS`.

Control flow: options are dependency-gated. Some features select lower-level subsystems, such as `CIFS_SMB_DIRECT` selecting `SMBDIRECT`. `CIFS_ALLOW_INSECURE_LEGACY` controls SMB1 and SMB2.0 availability. `CIFS_UPCALL`, DFS, and SWN options enable user-space upcall integrations.

State and persistence: no runtime state, but selected options shape module contents, exported proc/debug behavior, allowed mount dialects, and security mechanisms.

Dependencies and integration: integrates with crypto API, keyrings/request-key, DNS resolver, ASN.1 parser generation, netfs, fscache, KUnit, and InfiniBand/RDMA.

Risks: defaults matter for security. Legacy dialect support defaults to enabled, while compression defaults disabled. `CIFS_DEBUG_DUMP_KEYS` intentionally exposes encryption keys and must remain clearly unsafe. Broken or overly broad dependencies can create impossible modular builds.

Test signals: build matrix with key feature combinations; confirm `vers=1.0/2.0` rejection when legacy support is disabled; verify SPNEGO/DFS/SWN userspace helper dependencies; run SMB KUnit tests with and without SMB1 support; test modular RDMA and FS-Cache combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/Kconfig -->
