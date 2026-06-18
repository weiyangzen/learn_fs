## sources/distributed-fs/beegfs/client_module/source/os/OsCompat.c

**Purpose:** Provides compatibility implementations for Linux kernel APIs missing or differently shaped on supported older kernels. It lets the BeeGFS client module compile across a wide kernel-version matrix.

**Important APIs/types/functions:** Implements fallback `memdup_user`, `bdi_setup_and_register`, old `find_get_pages_tag`, `d_make_root`, `d_materialise_unique`, `OsCompat_initKmemCache`, postorder rbtree helpers, `os_generic_write_checks`, and fallback `have_submounts`/`d_walk`.

**Control flow:** Most functions are compiled conditionally behind `KERNEL_HAS_*` feature macros. Allocation/copy shims mimic upstream behavior. `OsCompat_initKmemCache` chooses the proper `kmem_cache_create` signature and flags. `have_submounts` walks the dentry tree under rename seqlock and dentry locks, searching for a mount point.

**State and persistence behavior:** No persistent state is kept. `bdi_setup_and_register` uses a static atomic sequence to create unique BDI registration names on kernels lacking the helper.

**Dependencies and integration points:** Depends on kernel mm, backing-dev, pagemap, uio, writeback, rbtree, dcache, and BeeGFS logging/config headers. It is used by module init, inode/dentry/page paths, and memory-cache setup.

**Risks:** Compatibility code must match kernel locking rules for each era; the fallback `d_walk` is especially sensitive to rename locking and dentry list layout differences. Feature macro mistakes can create duplicate symbol definitions or missing shims. `os_generic_write_checks` adapts iterator-based APIs and must update both offset and size correctly.

**Test signals:** Build against representative old/new kernels, run dentry submount tests under rename pressure, test BDI registration/unregistration, validate write-check behavior, and exercise fallback cache creation signatures.
