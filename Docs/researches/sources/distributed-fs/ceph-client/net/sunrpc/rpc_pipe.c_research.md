# sources/distributed-fs/ceph-client/net/sunrpc/rpc_pipe.c

## Purpose
`rpc_pipe.c` implements the `rpc_pipefs` pseudo-filesystem used by SUNRPC clients and authentication helpers to exchange upcalls and downcalls with userspace. It creates the pipefs superblock, standard service directories, per-client directories, cache helper directories, and the dummy `gssd` pipe used to detect a running rpc.gssd.

## Important APIs, Types, And Functions
Important exported APIs include `rpc_pipefs_notifier_register()`, `rpc_queue_upcall()`, `rpc_mkpipe_data()`, `rpc_mkpipe_dentry()`, `rpc_unlink()`, pipe directory object helpers, `rpc_create_client_dir()`, `rpc_remove_client_dir()`, cache directory helpers, `rpc_get_sb_net()`, `rpc_put_sb_net()`, `gssd_running()`, `register_rpc_pipefs()`, and `unregister_rpc_pipefs()`. Key local structures are `rpc_pipe`, `rpc_pipe_msg`, `rpc_inode`, `rpc_filelist`, `rpc_pipe_dir_head`, and `rpc_pipe_dir_object`.

## Control Flow
Pipe users allocate `rpc_pipe` data, create a pipe dentry under rpc_pipefs, and queue messages with `rpc_queue_upcall()`. Readers open the FIFO, `rpc_pipe_read()` moves one queued message to `in_upcall`, calls the pipe operation's `upcall`, and destroys the message once fully copied or failed. Writers call the pipe operation's `downcall`. Last reader close purges pending upcalls with `-EAGAIN`; unlink/removal closes the pipe, purges queues with `-EPIPE`, cancels timeout work, and clears inode ownership. Mount setup builds the root directories and dummy gssd tree, stores the per-net superblock under `pipefs_sb_lock`, and sends mount notifications; unmount clears the superblock and sends unmount notifications.

## State And Persistence
State is in per-pipe queues, reader/writer counts, `pipelen`, delayed timeout work, and borrowed dentries; per-inode private data points to callers or pipe state. Per-network namespace state stores `pipefs_sb`, `pipefs_sb_lock`, `pipe_version`, and `gssd_dummy`. Data is runtime-only and lives until pipefs unmount, client directory removal, or netns teardown.

## Dependencies And Integration Points
The file integrates with VFS simple filesystem helpers, fs_context mounting, blocking notifier chains, rpciod delayed work, SUNRPC cache pipefs files, `rpc_clnt` lifecycle, network namespace storage from `netns.h`, and auth/GSS userspace daemons. Notifier hooks let clients create or destroy pipefs entries when a namespace's rpc_pipefs mount appears or disappears.

## Risks And Edge Cases
The main risks are lifecycle and locking races among open file descriptors, dentries, pipe queue timeout work, and unmount. `RPC_PIPE_WAIT_FOR_OPEN` queues messages without readers only for a bounded timeout. `rpc_get_sb_net()` deliberately returns with `pipefs_sb_lock` held, so every successful caller must pair it with `rpc_put_sb_net()`. Pipe ops must correctly destroy messages on all purge paths. Dummy gssd state is inferred only from open counts, so it is a liveness signal rather than proof that upcalls will be serviced.

## Test Signals
Useful signals include rpc_pipefs mount/unmount in multiple net namespaces, GSS upcall/downcall integration, reader close and unlink while messages are queued, timeout purge with no readers, notifier registration ordering, cache directory population, per-client `info` file refcount behavior, and lockdep/KASAN coverage for concurrent unmount, open, read, write, and client teardown.
