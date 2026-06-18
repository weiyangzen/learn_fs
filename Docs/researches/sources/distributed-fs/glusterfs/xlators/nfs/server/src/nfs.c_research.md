# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs.c

## Purpose

`nfs.c` is the main Gluster NFS translator implementation. It initializes process-wide NFS state, configures the RPC service, registers MOUNT/NFSv3/NLM/ACL protocol programs, initializes per-subvolume inode tables, handles reconfiguration, and exposes xlator callbacks, dump operations, and volume options.

## Important APIs, types, and functions

- `nfs_init_state()` parses options and allocates `struct nfs_state`, the FOP-local mempool, gid cache, RPC service, auth/rmtab/statd settings, portmap registration policy, event-thread count, DRC prerequisites, and generation state.
- `nfs_add_all_initiators()`, `nfs_init_versions()`, `nfs_init_version()`, and `nfs_deinit_version()` manage protocol initializer records and RPC program registration.
- `nfs_init_subvolumes()` and `nfs_startup_subvolume()` create inode tables and perform root lookups before marking child xlators started.
- `nfs_user_create()`, `nfs_request_user_init()`, and `nfs_request_primary_user_init()` translate RPC credentials into `nfs_user_t`.
- `nfs_reconfigure_state()` and `reconfigure()` update live options and delegate to NFSv3, mount, RPC, and DRC reconfigure code.
- `init()`, `notify()`, and `fini()` are the xlator lifecycle entry points.
- `nfs_priv_to_dict()`, `nfs_priv()`, and `nfs_itable_dump()` support statedump/CLI inspection.
- `options[]` and `xlator_api` publish the translator's configuration and API.

## Control flow

`init()` calls `nfs_init_state()`, adds protocol initializers, initializes child inode tables, initializes mount and NLM state, registers protocol programs, initializes DRC, and reports service start. Child-up notifications call `nfs_startup_subvolume()`, which fills a root loc, issues a root lookup as root, and marks the subvolume started in a lock-protected `initedxl` array when the callback succeeds. Descendent up/down notifications increment `generation`, which is used by inode/share context consumers to detect topology changes.

Reconfigure first rejects options that require restart (`nfs.port`, transport type, mem-factor, and some unset transitions), then updates rmtab path, server aux-gids and gid-cache TTL, rdirplus, dynamic-volumes, ino32, NLM/ACL registration, event threads, NFSv3 state, mount state, RPC service options, portmap registration, outstanding RPC limits, and DRC configuration.

## State and persistence behavior

`struct nfs_state` is the central in-memory state. It tracks protocol versions, RPC service, mount/NFSv3/NLM state pointers, subvolume list, started-subvolume array, memfactor, auth settings, gid cache, statd paths, rmtab path, generation, and event-thread settings. Persistent side effects are indirect: rmtab is stored under `GLUSTERD_DEFAULT_WORKDIR/nfs/rmtab` by default unless disabled with `/-`; logs and portmap/rpcbind registrations outlive individual calls; backend filesystems hold actual export data.

## Dependencies and integration points

This file integrates Gluster xlator APIs, RPC service/DRC code, `mount3`, `nfs3`, `nlm4`, `acl3`, `nfs-fops`, gid cache, event pool, option parsing, memory accounting, and statedump. Its volume options are consumed by glusterd/CLI and downstream state initialization. NFSv3 helpers use `gf_nfs_this_private`/`gf_nfs_enable_ino32()` from `nfs.h`, so this file's private state must be initialized before protocol traffic.

## Risks and edge cases

- Partial failure cleanup is incomplete in several init branches: some allocated state is not fully deinitialized before returning failure.
- `nfs_startup_subvolume()` passes `nfsx->private` as the lookup cookie, but the callback treats `cookie` as an `xlator_t *` for logging while marking `this->private`; this looks suspicious and deserves targeted review.
- Live toggling of NLM/ACL registers or unregisters RPC programs and portmap entries; failures are logged but not deeply reconciled.
- `nfs.mem-factor` option validation in `options[]` allows up to 1024, wider than constants in `nfs.h`; code defaults to 15 but does not clamp the parsed value here.
- `fini()` unregisters protocols and frees `instance_name` but leaves several allocated substructures to version-specific cleanup or process teardown.

## Test signals

High-value tests include translator init with no children, normal multi-subvolume startup, root lookup failure, port override/portmap disabled, NLM disabled by option or invalid statd path, ACL/NLM live reconfigure, rmtab path disable/rewrite, dynamic-volumes and ino32 toggles, gid-cache reconfigure, event-thread reconfigure, and statedump of mount clients, DRC, NLM, and inode table.
