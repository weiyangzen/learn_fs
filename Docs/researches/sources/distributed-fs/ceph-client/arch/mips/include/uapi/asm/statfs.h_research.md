<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/statfs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/statfs.h

### Purpose
`statfs.h` defines filesystem statistics structures for MIPS user ABIs, including 32-bit large-file variants and 64-bit compat layout.

### Important APIs, Types, And Functions
It exports `fsid_t` for non-strict names, `struct statfs`, ABI32/NABI32 `struct statfs64`, ABI64 `struct statfs64`, and ABI64 `struct compat_statfs64`. `f_fstyp` aliases `f_type`.

### Control Flow
Compile-time branches select structures based on `_MIPS_SIM`. There is no executable flow.

### State, Persistence, And Dependencies
The persistent ABI includes field order for block counts, free counts, file counts, `f_fsid`, name length, flags, and spare words. Dependencies are Linux POSIX types and MIPS ABI macros.

### Integration Points
VFS `statfs`/`fstatfs` syscalls, compat syscall translation, libc, filesystem utilities, and distributed filesystems reporting capacity use these layouts.

### Risks
The 64-bit kernel has both native and compat layouts. Misusing native `long` layouts for compat calls can truncate or misalign filesystem capacity values.

### Test Signals
Validate structure sizes/offsets, large block counts, compat syscall results, and libc/kernel agreement for `statfs64` under O32, N32, and N64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/statfs.h -->
