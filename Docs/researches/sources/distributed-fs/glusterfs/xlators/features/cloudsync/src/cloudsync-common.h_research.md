# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-common.h

## Purpose
Defines common cloudsync state structures, plugin function-pointer contracts, private translator state, and stack cleanup macros shared by translator and plugins.

## Important APIs, types, and functions
Key types are `cs_loc_xattr_t`, `cs_size_xattr_t`, `cs_local_t`, `cs_private_t`, `cs_remote_stores`, and `store_methods_t`. Function pointer contracts include plugin download, remote read, init, reconfigure, and fini hooks. `CS_STACK_UNWIND` and `CS_STACK_DESTROY` centralize frame-local cleanup.

## Control flow
Cloudsync fops allocate `cs_local_t`, set `local->fop`, request object status xattrs, and either wind to child or call plugin hooks. Plugins export a `store_ops` symbol matching `store_methods_t`; `cs_init()` loads it with `dlsym()`.

## State and persistence behavior
State is transient except that plugin hooks interpret persisted xattrs such as remote object path, archive UUID, and object status. `cs_private_t` holds the loaded plugin, plugin config, abort flag, spinlock, and remote-read mode.

## Dependencies and integration points
Depends on GlusterFS call-stub, syncop, compat errno, memory types, and message headers. It is the ABI boundary between cloudsync core and `cloudsyncs3`/`cvlt` plugin modules.

## Risks and test signals
The ABI is C-struct/function-pointer based, so field order and symbol visibility matter. Tests should load every plugin, verify missing hooks fail cleanly, and run fop error paths to confirm stack cleanup happens once.
