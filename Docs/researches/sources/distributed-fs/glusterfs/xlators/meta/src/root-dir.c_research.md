# sources/distributed-fs/glusterfs/xlators/meta/src/root-dir.c

Purpose: defines the fixed top-level contents of the `.meta` root directory.

Important APIs/types/functions: `root_dir_dirents` contains entries for `graphs`, `frames`, `logging`, `process_uuid`, `version`, `cmdline`, `mallinfo`, `root`, `measure_latency`, and dot entries. `meta_root_dir_hook()` attaches `meta_root_dir_ops` with that fixed dirent array.

Control flow: `meta.c::meta_lookup()` calls `meta_root_dir_hook()` when the synthetic root is looked up. Subsequent lookup/readdir uses default directory behavior over `root_dir_dirents`, and each child hook installs its own ops/context.

State and persistence behavior: no mutable state in this file. It statically defines root layout; runtime data is produced by child modules.

Dependencies and integration points: depends on `meta-hooks.h` declarations for child hooks. It is the entry point connecting top-level meta lookup to the rest of the virtual tree.

Risks and edge cases: fixed entries must match available hook implementations. Adding/removing entries changes user-visible meta ABI. `measure_latency` is writable in its own module, so exposing it at root creates a tuning surface.

Test signals: top-level readdir ordering/content, lookup of every root entry, and link/build checks for all referenced hooks.
