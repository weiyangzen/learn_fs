# sources/distributed-fs/glusterfs/xlators/meta/src/meta.c

Purpose: top-level Gluster translator implementation for the synthetic `.meta` namespace. It intercepts lookup of the configured meta root, installs root metadata hooks, and forwards all later operations to the per-inode FOP table selected by hook modules.

Important APIs/types/functions: translator FOPs include `meta_lookup()`, `meta_opendir()`, `meta_open()`, `meta_readv()`, `meta_readdir()`, `meta_readdirp()`, `meta_readlink()`, `meta_writev()`, `meta_stat()`, truncation and fsync wrappers. Lifecycle functions are `mem_acct_init()`, `init()`, and `fini()`. Global exports are `struct xlator_fops fops`, `struct xlator_cbks cbks`, `struct volume_options options[]`, and `xlator_api_t xlator_api`.

Control flow: `meta_lookup()` special-cases lookup of the configured meta directory under the real root or lookup by the fixed meta-root GFID. It calls `meta_root_dir_hook()`, fills a directory iatt with `META_ROOT_GFID`, and replies directly. For all other lookups it chooses the parent inode when available and dispatches through `META_FOP`, which resolves `meta_fops_get()` and calls the inode-specific lookup implementation. All other FOP wrappers dispatch based on `loc->inode` or `fd->inode`.

State and persistence behavior: `init()` allocates `meta_priv_t`, reads the `meta-dir-name` option with default `.meta`, parses a fixed root GFID, and stores the private struct on the translator. No persistent files are created by this translator; it exposes runtime graph/process state through synthetic entries.

Dependencies and integration points: depends on Gluster xlator/default APIs, `meta.h`, `meta-mem-types.h`, and `meta-hooks.h`. It integrates into the Gluster translator stack through `xlator_api` with identifier `meta`, tech-preview category, fops/cbks, and one option.

Risks and edge cases: the dispatch macros assume an ops table or `default_fops` is valid; missing hooks can route operations to generic defaults. Root lookup synthesizes a zeroed parent iatt, which may be acceptable for virtual roots but should be tested with clients expecting parent attributes. `fini()` frees `this->private` but does not null it. The translator is category `GF_TECH_PREVIEW`, signaling a less stable integration surface.

Test signals: mount with default and custom `meta-dir-name`, lookup by name and GFID, traversal into all virtual subtrees, read/open/readdir/readlink/write dispatch, release/releasedir cleanup, mem accounting initialization failure handling, and absence of interference with non-meta paths.
