# sources/distributed-fs/ceph-client/fs/smb/common/Makefile

Read coverage: full file.

## Purpose
This Makefile builds SMB common code shared by client and server components. In this subset it conditionally adds the CIFS MD4 implementation object.

## Important APIs, types, and functions
The only build rule is `obj-$(CONFIG_SMBFS) += cifs_md4.o`. It ties `cifs_md4.c` into the kernel build when SMB filesystem support is enabled.

## Control flow
Kbuild expands `obj-$(CONFIG_SMBFS)` based on the configuration value. When enabled as built-in or module, `cifs_md4.o` is compiled and linked into the corresponding SMB filesystem object set.

## State and persistence behavior
No runtime state exists. The persistent behavior is configuration-driven build inclusion.

## Dependencies and integration points
The Makefile integrates with Linux Kbuild and the `CONFIG_SMBFS` option. Its output object provides exported MD4 symbols used by SMB authentication code that needs NT hash compatible MD4 behavior.

## Risks and test signals
The main risk is configuration drift: if client or server code uses `cifs_md4_*` while `CONFIG_SMBFS` does not include this object, link failures result. Build tests should compile SMBFS as built-in and module, and ensure MD4 users resolve to `cifs_md4_init`, `cifs_md4_update`, and `cifs_md4_final`.
