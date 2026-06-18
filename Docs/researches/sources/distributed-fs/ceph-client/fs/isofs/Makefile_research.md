## sources/distributed-fs/ceph-client/fs/isofs/Makefile

Purpose: declares the ISOFS object composition for kbuild.

Important build rules: `obj-$(CONFIG_ISO9660_FS) += isofs.o`; the base object links `namei.o inode.o dir.o util.o rock.o export.o`. `joliet.o` is conditional on `CONFIG_JOLIET`; `compress.o` is conditional on `CONFIG_ZISOFS`.

Control flow and state: no runtime state. The file controls feature-dependent linkage and therefore whether optional APIs such as `get_joliet_filename` and `zisofs_aops` exist.

Dependencies and integration points: integrates with Kconfig symbols and the kernel module build. The base object must include Rock Ridge support unconditionally because Rock Ridge is core ISOFS behavior controlled at mount time.

Risks and test signals: build risk is unresolved symbols if conditional objects do not match preprocessor guards. Test by compiling all combinations of `ISO9660_FS`, `JOLIET`, and `ZISOFS`.
