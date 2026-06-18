# sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3-auth.h

## Purpose
Declares the mount authorization parameter object and public authorization API for Gluster's NFS MOUNTv3/NFS FOP paths.

## APIs, Types, and Functions
Defines logging domain `GF_MNT_AUTH` and `struct mnt3_auth_params`, which holds pointers to a netgroups file, exports file, and owning `mount3_state`. Declares `mnt3_auth_params_init()`, `mnt3_auth_set_netgroups_auth()`, `mnt3_auth_set_exports_auth()`, `mnt3_auth_host()`, `mnt3_auth_params_deinit()`, and `mnt3_auth_fop_options_verify()`.

## Control Flow, State, and Persistence
The header has no executable flow. It defines the in-memory authorization state that persists under `mount3_state` until reloaded or deinitialized. `mnt3_auth_host()` can optionally return the matched `export_item` through `save_item` for cache integration.

## Dependencies and Integration
Depends on NFS memory types, netgroups, exports, `mount3.h`, and `nfs.h`. It integrates mount3 request handling, exports parsing, netgroups parsing, and NFS file-handle authorization.

## Risks and Test Signals
Risks include header-level coupling across mount3, exports, and netgroups, and the declared `mnt3_auth_fop_options_verify()` lacking a corresponding implementation in the researched source set. Test signals are compile/link coverage for all declared functions, auth reload tests, and FOP authorization paths using `mnt3_auth_host()` with and without saved export items.
