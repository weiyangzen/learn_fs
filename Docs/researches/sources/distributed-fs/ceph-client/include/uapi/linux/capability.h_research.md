
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/capability.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/capability.h

## Purpose
Defines Linux process and file capability UAPI. It specifies the capget/capset user structures, version constants, file xattr formats, all capability numbers, helper macros for validation and bit indexing, and the current `CAP_LAST_CAP`.

## APIs, Control Flow, and State
The header exports `_LINUX_CAPABILITY_VERSION_{1,2,3}` and word counts, `cap_user_header_t`, `struct __user_cap_data_struct`, file capability revision/size/flag constants, `struct vfs_cap_data`, `struct vfs_ns_cap_data`, and capability numbers from `CAP_CHOWN` through `CAP_CHECKPOINT_RESTORE`. The list covers traditional DAC/UID/GID/network/admin powers plus newer splits such as `CAP_SYSLOG`, `CAP_PERFMON`, `CAP_BPF`, and checkpoint/restore. Macros `cap_valid()`, `CAP_TO_INDEX()`, and `CAP_TO_MASK()` validate and address bitmaps. Runtime control flow is in credential management, LSMs, VFS xattr handling, namespaces, and syscall permission checks; persistent state includes process credentials, bounding/ambient/inheritable/effective/permitted sets, and file capability xattrs.

## Dependencies, Integration, Risks, and Tests
Depends on Linux fixed-width and endian types, and uses `__user` annotations. Integration points are `capget`, `capset`, exec credential calculation, file xattrs, user namespaces, container runtimes, LSM policy, and permission gates throughout the kernel. Risks include adding capabilities without updating `CAP_LAST_CAP`, overloading `CAP_SYS_ADMIN`, namespace-rootid handling for v3 file caps, incompatibility with old libcap/userspace versions, and security regressions when checks use the wrong capability. Test signals include libcap tests, capget/capset ABI tests, file capability xattr round trips across namespaces, container runtime capability sets, LSM integration tests, and targeted permission tests for `CAP_BPF`, `CAP_PERFMON`, and checkpoint/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/capability.h -->
