# sources/distributed-fs/ceph-client/fs/hfsplus/Kconfig

Purpose: declares kernel configuration options for the HFS+ filesystem and its KUnit tests.

Important options: `HFSPLUS_FS` is a tristate block filesystem option for Apple Extended HFS support. It depends on `BLOCK` and selects `BUFFER_HEAD`, `NLS`, `NLS_UTF8`, and `LEGACY_DIRECT_IO`, matching the implementation's use of block buffers, charset conversion, UTF-8 handling, and direct I/O helpers. Help text documents HFS+ as MacOS 8-era extended HFS with data forks, creator codes, ownership, and permissions. `HFSPLUS_KUNIT_TEST` builds HFS+ KUnit tests when `HFSPLUS_FS` and `KUNIT` are enabled, defaulting under `KUNIT_ALL_TESTS`.

State and persistence: no runtime state is managed here. The selected config controls whether the HFS+ module and tests are built into the kernel or as modules.

Dependencies and integration: paired with `Makefile`, which builds `hfsplus.o` from the implementation files and `unicode_test.o` for test config. The selected dependencies correspond to headers and APIs used by files in this subset, especially `bitmap.c`, `inode.c`, `unicode.c`, and the btree code.

Risks and test signals: missing selected dependencies would surface as build failures. Config tests should verify `HFSPLUS_FS=m/y` builds the full object list and `HFSPLUS_KUNIT_TEST` pulls in only test code when KUnit is active.
