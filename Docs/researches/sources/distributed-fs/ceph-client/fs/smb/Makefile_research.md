<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/Makefile -->
## sources/distributed-fs/ceph-client/fs/smb/Makefile

Purpose: top-level Kbuild dispatch for SMB filesystem subdirectories.

Important APIs and variables: `obj-$(CONFIG_SMBFS) += common/`, `obj-$(CONFIG_SMBDIRECT) += smbdirect/`, `obj-$(CONFIG_CIFS) += client/`, and `obj-$(CONFIG_SMB_SERVER) += server/`.

Control flow: Kbuild descends into common, SMB Direct, CIFS client, and server subdirectories depending on the matching Kconfig symbols. The file does not build objects directly.

State and persistence: no runtime state; it defines build graph persistence through Kbuild object lists.

Dependencies and integration: consumes symbols defined by the sibling Kconfig files. It is the bridge between aggregate `SMBFS` and implementation directories.

Risks: directory inclusion must match symbol ownership. A common-code symbol mismatch can produce link failures only in modular combinations.

Test signals: build all-y, all-m, client-only, server-only, and SMB Direct configurations; check that common objects are included for both client and server users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/Makefile -->
