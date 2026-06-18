<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/vboxsf_wrappers.c -->
# sources/distributed-fs/ceph-client/fs/vboxsf/vboxsf_wrappers.c

Purpose: Wraps VirtualBox guest HGCM calls into typed vboxsf operations for mapping folders, opening/creating objects, I/O, metadata, directory listing, removal, rename, symlink, and protocol feature setup.

Important APIs, types, and functions: Defines global `vboxsf_client_id`, `vboxsf_connect()`, `vboxsf_disconnect()`, `vboxsf_call()`, `vboxsf_map_folder()`, `vboxsf_unmap_folder()`, `vboxsf_create()`, `vboxsf_close()`, `vboxsf_remove()`, `vboxsf_rename()`, `vboxsf_read()`, `vboxsf_write()`, `vboxsf_dirinfo()`, `vboxsf_fsinfo()`, `vboxsf_readlink()`, `vboxsf_symlink()`, `vboxsf_set_utf8()`, and `vboxsf_set_symlinks()`.

Control flow: `vboxsf_connect()` obtains the VirtualBox guest device and connects to the `VBoxSharedFolders` service, storing the client id. Each wrapper constructs the relevant `shfl_*` parameter block, marks pointer directions and sizes, calls `vboxsf_call()`, then copies back output fields such as root handles, byte counts, file counts, or host status. `vboxsf_call()` translates guest-device or host status failures into Linux errno values.

State and persistence: Persistent guest-side state is the HGCM client id. Host-side state includes mapped root handles and open object handles that must be closed or unmapped by callers.

Dependencies and integration points: Depends on `vboxguest` APIs (`vbg_get_gdev()`, `vbg_hgcm_connect()`, `vbg_hgcm_call()`, `vbg_hgcm_disconnect()`), VirtualBox status translation, and ABI structs from `shfl_hostintf.h`. Higher vboxsf layers depend on these wrappers for every host-visible operation.

Risks and test signals: Risks include wrong parameter type/direction, stale client id after device removal, missed output length updates, host status translation changes, and handle leaks from caller error paths. Test old host map-folder behavior, guest-device hot removal, read/write short counts, end-of-directory mapping from `VERR_NO_MORE_FILES`, statfs info, symlink feature negotiation, and all wrappers under host permission failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/vboxsf_wrappers.c -->
