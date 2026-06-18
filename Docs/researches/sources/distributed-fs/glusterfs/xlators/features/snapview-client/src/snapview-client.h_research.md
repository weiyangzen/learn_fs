# sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client.h

Purpose: declares snapview-client frame-local, private, fd-context, and inode-type data structures plus helper macros.

Important APIs/types: `svc_local_t` stores copied loc, chosen subvolume, fd, cookie, xdata, and revalidation flag. `SVC_STACK_UNWIND` unwinds and frees local state. `SVC_ENTRY_POINT_SET` ensures xdata exists and marks entry-point lookup for snapview-server. `SVC_GET_SUBVOL_FROM_CTX` fetches inode type and maps it to a child. `svc_private_t` stores entry-point configuration and lock. `svc_fd_t` stores readdir offset/special-dir flags. `inode_type_t` declares `NORMAL_INODE` and `VIRTUAL_INODE`. `gf_svc_special_dir_revalidate_lookup()` is exposed for callback reuse.

Control flow/state: macros are central to error paths and memory cleanup. The local struct is allocated from `this->local_pool`, while fd/private structs use memory accounting types.

Dependencies/integration: includes GlusterFS base, logging, dict, defaults, and the local mem/message headers. It assumes the translator has exactly two children and that inode contexts contain values from `inode_type_t`.

Risks/test signals: macro gotos require callers to have matching local variable names and labels. Tests should cover error unwinds to ensure `svc_local_free()` releases loc/fd/xdata exactly once.
