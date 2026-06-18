# sources/distributed-fs/glusterfs/xlators/meta/src/private-file.c

Purpose: implements the virtual `private` file for an xlator, dumping translator-private state through Gluster's statedump formatter.

Important APIs/types/functions: `private_file_fill()` retrieves the target `xlator_t *` from inode context and calls `gf_proc_dump_xlator_private(xl, strfd)`. `meta_private_file_hook()` installs `private_file_ops` and copies parent xlator context.

Control flow: lookup under an xlator directory binds the same xlator context to the file. Readv uses the default generated-file path to invoke the statedump callback and cache its text.

State and persistence behavior: output reflects volatile in-memory private state at first read on an fd. Nothing is stored by this module.

Dependencies and integration points: depends on `glusterfs/statedump.h`, `strfd`, and each xlator's statedump/private dump support. Integrated through `xlator-dir.c` fixed dirents.

Risks and edge cases: private dumps may expose sensitive or large operational state. A translator without safe private dump behavior could produce incomplete output or fail. Cached fd output may not track changing private state.

Test signals: read `private` for representative xlators, compare with statedump expectations, test large output reads with offsets, and verify no crash for xlators with minimal private state.
