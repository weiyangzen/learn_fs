# sources/distributed-fs/ceph-client/kernel/bpf/inode.c

## Purpose

`inode.c` implements bpffs, the pseudo filesystem used to pin and retrieve BPF maps, programs, and links through filesystem paths. It provides inode creation, object typing, seq_file display for maps, user-facing `BPF_OBJ_PIN`/`BPF_OBJ_GET` path operations, mount option parsing, optional preload population, and filesystem registration.

## Important APIs, Types, And Functions

`enum bpf_type` distinguishes `BPF_TYPE_PROG`, `BPF_TYPE_MAP`, and `BPF_TYPE_LINK`. `bpf_any_get()` and `bpf_any_put()` apply the matching reference operation for each object type. `bpf_fd_probe_obj()` tries a user fd as map, then program, then link.

`bpf_get_inode()` creates bpffs inodes for directories, regular pinned objects, and symlinks. `bpf_inode_type()` uses inode operation table identity (`bpf_prog_iops`, `bpf_map_iops`, `bpf_link_iops`) to recover the object kind.

Map display uses `struct map_iter`, `map_seq_start()`, `map_seq_next()`, `map_seq_show()`, `bpffs_map_open()`, and `bpffs_map_release()`. It uses `map_get_next_key()` and optional `map_seq_show_elem()` support to make `cat /sys/fs/bpf/...` useful for maps that expose debug output.

Pinning uses `bpf_mkobj_ops()`, `bpf_mkprog()`, `bpf_mkmap()`, `bpf_mklink()`, `bpf_obj_do_pin()`, and `bpf_obj_pin_user()`. Retrieval uses `bpf_obj_do_get()` and `bpf_obj_get_user()`, returning new fds through `bpf_prog_new_fd()`, `bpf_map_new_fd()`, or `bpf_link_new_fd()`.

Filesystem operations include `bpf_mkdir()`, `bpf_symlink()`, `bpf_lookup()`, `bpf_dir_iops`, `bpf_super_ops`, `bpf_fill_super()`, `bpf_get_tree()`, `bpf_init_fs_context()`, `bpf_kill_super()`, and `bpf_init()`.

Mount delegation parsing uses `struct bpf_mount_opts`, `find_bpffs_btf_enums()`, `find_btf_enum_const()`, `seq_print_delegate_opts()`, `bpf_show_options()`, and `bpf_parse_param()`. Options include uid, gid, mode, and delegation masks for commands, map types, program types, and attach types.

Preload support uses exported `bpf_preload_ops`, `bpf_preload_mod_get()`, `bpf_preload_mod_put()`, `populate_bpffs()`, and `bpf_iter_link_pin_kernel()` to pin kernel-created iterator links into a new bpffs mount.

## Control Flow

For pinning, `bpf_obj_pin_user()` first resolves the fd to a referenced BPF object, then `bpf_obj_do_pin()` creates a dentry with `start_creating_user_path()`, verifies the parent is a bpffs directory, applies `security_path_mknod()`, and invokes `vfs_mkobj()` with the right object constructor. On failure after fd probing, the object reference is released.

For lookup, `bpf_obj_get_user()` validates requested flags, resolves the path, checks path permissions, verifies the inode operation table corresponds to a pinned BPF object, takes a new object reference, touches atime, and creates the matching fd. Link retrieval requires `O_RDWR`.

Map read control flow is a seq_file iterator. The first output line is a warning header, then `map_seq_next()` walks map keys under RCU using `map_get_next_key()`, and `map_seq_show()` delegates element formatting to `map->ops->map_seq_show_elem()`.

Mount creation allocates a fs context with defaults from current fsuid/fsgid and mode `0777`, parses parameters, then `bpf_fill_super()` requires privileges for non-init user namespaces, initializes a simple superblock, sets root ownership/mode, optionally populates preload links, and finally enables sticky bit plus requested mode.

## State And Persistence Behavior

Pinned objects persist through inode `i_private` and object references. `bpf_destroy_inode()` releases pinned object references based on inode type and frees symlink targets. Unlinking removes the filesystem entry and inode release drops the BPF object reference.

bpffs mount options persist in `sb->s_fs_info` for the lifetime of the mount. Root inode uid/gid/mode reflect parsed options. Delegation masks are displayed in `/proc/mounts` using BTF enum names when available.

Preloaded links are pinned into the root of a bpffs instance during mount population. The preload module is temporarily referenced while the kernel calls its preload operations.

## Dependencies And Integration Points

This file depends on VFS helpers, fs_context parsing, Linux security hooks, BPF object fd/reference APIs, map operation callbacks, BTF enum introspection, and the optional `bpf_preload` module. It exports `bpf_prog_get_type_path()` for kernel users that need to open a pinned program by path and verify a program type.

## Risks And Edge Cases

The inode operation pointer is the object type discriminator, so any future inode operation change must preserve this invariant or update `bpf_inode_type()`. Reference mismatches in pin/get/error paths would leak BPF objects or prematurely free them.

Name handling reserves dots in non-private bpffs directories; changing that policy could conflict with future special files created by `populate_bpffs()`. Mount delegation parsing uses BTF enum names and hex fallback; malformed masks or privilege bypasses would affect BPF token delegation.

Map `cat` output is explicitly debug-only and format-unstable. It depends on maps safely implementing `map_seq_show_elem()` and `map_get_next_key()` under RCU.

## Test Signals

Useful tests include BPF selftests for pin/get/unpin of maps, programs, and links; permission and flag validation; link `O_RDWR` enforcement; map seq output; bpffs mount uid/gid/mode/delegation options; preload link population; and cleanup of object references after unlink and unmount.
