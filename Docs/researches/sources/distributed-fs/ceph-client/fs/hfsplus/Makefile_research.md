# sources/distributed-fs/ceph-client/fs/hfsplus/Makefile

Purpose: defines the build composition for the HFS+ filesystem object and HFS+ KUnit test object.

Important build rules: `obj-$(CONFIG_HFSPLUS_FS) += hfsplus.o` makes the filesystem build conditional on the config option. `hfsplus-objs` aggregates the module from super/options/inode/ioctl/extents/catalog/dir/btree/bnode/brec/bfind/tables/unicode/wrapper/bitmap/part_tbl/attributes/xattr and xattr namespace handlers. `obj-$(CONFIG_HFSPLUS_KUNIT_TEST) += unicode_test.o` builds tests separately.

State and persistence: no runtime state. The object list determines which source files are linked into the filesystem implementation and therefore which APIs are available across translation units.

Dependencies and integration: this subset covers many of the listed core objects: attributes, bfind, bitmap, bnode, brec, btree, catalog, dir, and extents. Other linked files provide superblock setup, options, raw definitions, Unicode conversion, wrapper/MDB handling, inode writeback, ioctl, and xattr glue.

Risks and test signals: build ordering is not explicit, so missing prototypes or config guards show up at compile/link time. Since `attributes.o` and xattr handlers are always included with HFS+, attribute-tree absence must be handled at runtime, as `attributes.c` does. Build tests should cover builtin, module, and KUnit-enabled variants.
