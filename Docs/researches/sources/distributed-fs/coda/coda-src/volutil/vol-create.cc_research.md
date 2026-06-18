## sources/distributed-fs/coda/coda-src/volutil/vol-create.cc

Purpose: `vol-create.cc` creates new read-write or replicated Coda volumes and initializes their root directory with administrator ACLs.

Important APIs/types/functions: RPC `S_VolCreate` handles volume allocation/creation. `ViceCreateRoot` creates the root large vnode and physical directory. It references `PrintVnode` for debug output and uses `PRS_ADMINGROUP`, `AL_AccessList`, `VnodeDiskObject`, and `vindex`.

Control flow: `S_VolCreate` initializes volutil, begins an RVM transaction, allocates or accepts a volume id, updates max id if needed, validates replicated group id, creates the volume, sets initial header fields/name/type, calls `ViceCreateRoot`, clears salvage/destroy state, updates/detaches the volume, commits, flushes RVM, disconnects, and returns the id. `ViceCreateRoot` resolves the admin group id, creates a directory handle and `.`/`..` root directory, builds an ACL granting all rights to administrators, fills vnode fields, commits the directory, optionally creates a resolution log, writes the vnode to the large vnode index, and updates disk usage.

State and persistence behavior: creates persistent RVM volume metadata, vnode index entries, directory inode data, ACL data, optional resolution log, and max volume id state. It runs the root creation and volume update in one transaction for version-vector consistency.

Dependencies/integration points: depends on volutil/RVM, partition and volume creation code, protection database lookup, directory/vnode commit APIs, resolution logging, and server globals such as `AllowResolution`.

Risks: user-supplied explicit volume ids can advance max volume id and may collide if external validation is incomplete. Root ACL creation fails if the PDB admin group is unavailable. `ViceCreateRoot` uses stack buffers cast to vnode types and assumes `SIZEOF_LARGEDISKVNODE`. Several operations assert after commit-related calls. The global `Error error` is file-scope.

Test signals: create non-replicated and replicated volumes, explicit and allocated ids, missing admin group failure, invalid replicated group id, root directory lookup, ACL rights, volume detach/reattach, and resolution-log creation when enabled.
