<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/shfl_hostintf.h -->
# sources/distributed-fs/ceph-client/fs/vboxsf/shfl_hostintf.h

Purpose: Defines the guest-to-host VirtualBox Shared Folders ABI used by vboxsf wrapper calls.

Important APIs, types, and functions: Declares SHFL function numbers, root and file handle sentinel values, `struct shfl_string`, mode/type flags, `struct shfl_fsobjattr`, `struct shfl_fsobjinfo`, `enum shfl_create_result`, create/access flags, `struct shfl_createparms`, `struct shfl_dirinfo`, volume/property structs, and HGCM parameter structs for map/unmap, create, close, read, write, list, readlink, information, remove, rename, and symlink. `shfl_string_buf_size()` computes wire buffer sizes.

Control flow: Runtime code fills these packed parameter structs with `vmmdev_hgcm_function_parameter` descriptors, then `vboxsf_call()` sends them to the host service. The host returns handles, result codes, byte counts, object info, directory entries, and volume information through these layouts.

State and persistence: The header defines protocol state but stores none itself. Its structs represent persistent host object attributes as observed or modified through the shared folder service, including times, size, allocation, mode, and optional Unix attributes.

Dependencies and integration points: Depends on `linux/vbox_vmmdev_types.h` and is consumed by all vboxsf implementation files. Layout assertions via `VMMDEV_ASSERT_SIZE` protect host ABI compatibility.

Risks and test signals: Risks are ABI layout drift, packed-struct alignment assumptions, wrong parameter direction tags, path length accounting, enum/value mismatch with the host, and oversized read/write buffers. Test against multiple VirtualBox host versions, 32-bit and 64-bit guests, symlink-capable and old hosts, long UTF-8 names, all file types, large I/O up to `SHFL_MAX_RW_COUNT`, and statfs volume info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/shfl_hostintf.h -->
