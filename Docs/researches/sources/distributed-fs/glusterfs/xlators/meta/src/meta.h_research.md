# sources/distributed-fs/glusterfs/xlators/meta/src/meta.h

Purpose: public internal contract for the `meta` translator. It defines the virtual entry model, hook signature, per-translator private state, per-frame local state, per-fd cache, operation table extension, and dispatch/unwind macros used by all meta modules.

Important APIs/types/functions: key types are `meta_hook_t`, `meta_local_t`, `meta_priv_t`, `struct meta_dirent`, `struct meta_ops`, and `meta_fd_t`. Constants include `DEFAULT_META_DIR_NAME`, `META_ROOT_GFID`, `DOT_DOTDOT`, and `COUNT()`. Macros `META_STACK_UNWIND` and `META_FOP` centralize cleanup and per-inode dispatch. Function prototypes cover iatt fill, inode discovery, ops/context storage, fd caching, default initialization, direct-io xdata, file/dir fill, and fixed-dirent counting.

Control flow: directory modules declare fixed or dynamic `struct meta_dirent` arrays whose hook functions call `meta_ops_set()` and optional `meta_ctx_set()`. FOP wrappers call `META_FOP` to dispatch to the current inode's fops. Default handlers call `META_STACK_UNWIND` so any `meta_local_t` xdata is detached and freed after the Gluster stack reply.

State and persistence behavior: the header describes runtime-only state. `meta_priv_t` stores translator options and root GFID; `meta_fd_t` stores generated content for an fd; inode context stores ops and arbitrary per-entry payloads.

Dependencies and integration points: includes `glusterfs/strfd.h` and relies on Gluster core types from surrounding includes. Every source file in `xlators/meta/src` shares this header, so its structs are the ABI within the translator.

Risks and edge cases: macros hide control flow and assume fop names exist in the selected table. `struct meta_ops` embeds full fops/cbks, so static ops instances are modified by `meta_defaults_init()` on first use; this is intentional but means ops tables should not be treated as immutable. Context payloads are not type checked.

Test signals: compile all hook modules against the header, exercise `META_STACK_UNWIND` cleanup with allocated xdata, and verify every static `meta_ops` table remains valid after repeated `meta_ops_set()` calls.
