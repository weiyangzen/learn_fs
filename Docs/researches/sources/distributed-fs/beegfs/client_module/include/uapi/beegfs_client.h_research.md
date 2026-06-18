## sources/distributed-fs/beegfs/client_module/include/uapi/beegfs_client.h

### Purpose
Defines the BeeGFS client kernel module user-space ABI: ioctl request numbers, constants, and argument structures for file creation, mount/config queries, stripe info, inode/entry info, ping, and file-state changes.

### Important APIs, Types, and Functions
- Buffer and protocol constants define maximum config path, mount ID, node alias/type, filename, entry ID, ping counts, and stripe pattern values.
- `BEEGFS_IOCTYPE_ID` is `'f'`; `BEEGFS_IOCNUM_*` enumerate ioctl command numbers.
- `BEEGFS_IOC_*` macros use `_IOR` and `_IOW` to define ioctl request codes and associated structs.
- File creation structs: `BeegfsIoctl_MkFile_Arg`, `MkFileV2`, and `MkFileV3`, with increasing support for 32-bit owner/group IDs, buddy-mirrored parent flag, and storage pool override.
- Query structs: `GetCfgFile`, `GetStripeInfo`, `GetStripeTarget`, `GetStripeTargetV2`, `GetInodeID`, `GetEntryInfo`, and `PingNode`.
- `BeegfsIoctl_SetFileState_Arg` updates access/data state for a named file.

### Control Flow and State
No control flow. This header fixes memory layouts exchanged between user space and the kernel through ioctl calls. Kernel handlers copy in/out these structs and perform corresponding filesystem operations.

### Dependencies and Integration Points
Included by user-space tools and kernel module code. Relies on Linux ioctl macros and types such as `uid_t`, `gid_t`, `uint16_t`, and `uint32_t` from surrounding includes. Must stay ABI-compatible with existing BeeGFS tools.

### Risks and Edge Cases
ABI changes are high risk: struct field order, sizes, and ioctl numbers must not change unintentionally. `BEEGFS_IOCTL_TEST_BUFLEN` is documented as wrong for the exchanged string but retained for compatibility. Several structs contain user pointers and lengths; kernel handlers must validate copy lengths and nullability. Mixed 16-bit and 32-bit IDs reflect legacy compatibility and can truncate if misused.

### Test Signals
ABI tests should compare ioctl numbers and struct sizes across architectures, and integration tests should exercise each ioctl through user-space tooling against the client module.
