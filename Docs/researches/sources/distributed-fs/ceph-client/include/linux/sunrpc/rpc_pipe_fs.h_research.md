# sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_pipe_fs.h

Purpose: declares the rpc_pipefs infrastructure used by SUNRPC to exchange upcalls/downcalls with user-space helpers such as GSS daemons and cache managers.

Important APIs and types: `struct rpc_pipe_dir_head`, `rpc_pipe_dir_object`, and ops manage dynamic pipefs directory objects. `struct rpc_pipe_msg` tracks queued message data, bytes copied, and errno. `struct rpc_pipe_ops` defines upcall/downcall/open/release/destroy callbacks. `struct rpc_pipe` owns upcall/downcall queues, reader/writer counts, timeout work, ops, lock, and dentry. `struct rpc_inode` embeds VFS inode state. APIs cover pipefs notifier registration, per-net superblock management, generic upcalls, message queueing, client/cache directories, pipe data/dentry creation, unlinking, registration, and `gssd_running()`.

Control flow: kernel code creates pipefs objects, queues an upcall message, user space reads and writes responses, then downcall handlers update kernel state. Mount/umount notifiers and per-net superblock helpers manage visibility.

State and persistence: all state is runtime VFS/pipefs state; messages are transient and tied to readers/writers and dentries.

Dependencies and integration points: integrates with VFS inodes/dentries, workqueues, net namespaces, cache details, RPC clients, and GSS user-space daemons.

Risks and test signals: risks include stuck upcalls without readers, message lifetime races, namespace mount teardown, in-flight message detection, and cache directory leaks. Test with rpc_pipefs mount/unmount, gssd restarts, cache upcalls, per-net cleanup, and concurrent readers/writers.
