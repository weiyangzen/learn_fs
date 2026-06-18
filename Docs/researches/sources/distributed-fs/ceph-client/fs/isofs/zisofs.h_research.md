## sources/distributed-fs/ceph-client/fs/isofs/zisofs.h

Purpose: declares the compressed ISOFS interface when `CONFIG_ZISOFS` is enabled.

Important APIs: declares `zisofs_aops`, `zisofs_init`, and `zisofs_cleanup`. The header is included by core inode/module code and the compression implementation.

Control flow and state: no runtime logic. Conditional declarations mirror the optional build path selected by Kconfig/Makefile.

Dependencies and integration points: integrates Rock Ridge ZF parsing and inode operation selection with `compress.c` without exposing compression internals.

Risks and test signals: risk is conditional build mismatch. Test compilation with `CONFIG_ZISOFS=y` and disabled, plus mounting compressed media to verify `zisofs_aops` is selected.
