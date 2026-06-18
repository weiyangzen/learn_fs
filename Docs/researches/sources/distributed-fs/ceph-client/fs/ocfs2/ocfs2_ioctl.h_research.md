# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_ioctl.h

Purpose: defines OCFS2 user-space ioctl ABI structures and command numbers for space reservation, online resize group management, reflink, filesystem information queries, and extent movement/defragmentation.

Important APIs and types: `struct ocfs2_space_resv` mirrors XFS-style reservation arguments used by `OCFS2_IOC_RESVSP*` and `OCFS2_IOC_UNRESVSP*`; unsupported ALLOCSP/FREESP numbers are still reserved for completeness. `struct ocfs2_new_group_input` passes group descriptor data for online resize. `struct reflink_arguments` carries old path, new path, and preserve flag user pointers/values. The `ocfs2_info` family defines a multiplexed request array with per-request headers and typed outputs for cluster size, block size, slot count, label, UUID, features, journal size, free inode stats, and free-fragment stats. `struct ocfs2_move_extents` defines defrag/move input/output fields and operation flags.

Control flow: ioctl handlers copy these structures to or from user space, validate request magic/code/size, then dispatch to reservation, resize, reflink, info, or move-extents code. `OCFS2_INFO_FL_NON_COHERENT` is an input hint that allows the kernel to decide whether cluster locking can be skipped; `FILLED` and `ERROR` are kernel-populated result flags.

State and persistence: the header has no runtime storage, but commands can persistently reserve/unreserve extents, add allocation groups, create reflinks, and move extents. Info requests expose mounted filesystem state and on-disk feature/geometry fields.

Dependencies and integration: included by `ocfs2.h` and ioctl implementation code, and must stay ABI-compatible with user-space tools. It depends on ioctl encoding macros, fixed-width types, and constants such as `OCFS2_VOL_UUID_LEN`, `OCFS2_MAX_VOL_LABEL_LEN`, `OCFS2_MAX_SLOTS`.

Risks: structure packing, field size, command number, or semantic changes break user-space ABI. Pointer-sized path fields in `reflink_arguments` are encoded as `__u64`, so compat handling must be correct. Info request size/magic validation is important for forward/backward compatibility. Move-extents flags can fragment or relocate data incorrectly if validation is weak.

Test signals: ioctl ABI compile tests, 32-bit compat tests, reservation and unreservation xfstests, online resize group-add/extend tests, reflink preserve-mode tests, `OCFS2_IOC_INFO` with mixed known/unknown request codes and non-coherent hints, defragmentation/move-extents tests, and strace/ABI checks for command numbers.
