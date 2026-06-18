<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/Makefile -->
## sources/distributed-fs/ceph-client/fs/smb/client/Makefile

Purpose: Kbuild recipe for the CIFS/SMB2/SMB3 client module and related generated protocol mapping files and tests.

Important variables and rules: `obj-$(CONFIG_CIFS) += cifs.o`; `cifs-y` lists core objects such as transport, inode, file, directory, SMB2 operations, cached directory handles, Unicode conversion, ASN.1 support, and namespace/reparse handling. Conditional `cifs-$(CONFIG_...)` appends xattr, SPNEGO, DFS, SWN, FS-Cache, SMB Direct, rootfs, legacy SMB1, and compression objects. Generated targets include `smb1_mapping_table.c`, `smb1_err_*_map.c`, and `smb2_mapping_table.c`.

Control flow: the build always compiles core client logic when `CONFIG_CIFS` is enabled, then conditionally links feature objects. ASN.1-generated headers gate `asn1.o`. Perl generators convert protocol status headers into C mapping tables under Kbuild dependency tracking. KUnit test objects are compiled separately under SMB test symbols.

State and persistence: no runtime state; generated C files are build artifacts listed in `targets` for cleaning/tracking.

Dependencies and integration: integrates with Kbuild ASN.1 generation, SMB common status headers, feature Kconfig symbols, trace events include path, and KUnit.

Risks: generated mapping tables must be rebuilt when source status headers or generator scripts change. Feature object ordering affects unresolved symbols for conditional code paths. Legacy SMB1 rules are guarded by a non-empty config check, so both `y` and `m` must work.

Test signals: incremental builds after touching `nterr.h`, `smberr.h`, `smb2status.h`, and generators; all feature permutations; module link checks; KUnit test builds; and clean targets removing generated mapping files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/Makefile -->
