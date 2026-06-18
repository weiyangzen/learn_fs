<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sysmips.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sysmips.h

### Purpose
`sysmips.h` defines the command numbers for the deprecated MIPS-specific `sysmips(2)` syscall subset that Linux still supports for compatibility.

### Important APIs, Types, And Functions
The ABI constants are `SETNAME`, `FLUSH_CACHE`, `MIPS_FIXADE`, `MIPS_RDNVRAM`, and `MIPS_ATOMIC_SET`.

### Control Flow
There is no runtime logic. The kernel syscall implementation switches on these constants elsewhere.

### State, Persistence, And Dependencies
The persistent state is compatibility numbering for old MIPS software. The header has no dependencies beyond its include guard.

### Integration Points
Legacy userspace, libc syscall wrappers, cache-flush tools, unaligned-access policy control, and kernel `sys_sysmips` handling depend on these values.

### Risks
Because the syscall is deprecated, coverage may be thin, but changing command numbers would break old binaries. `MIPS_ATOMIC_SET` has concurrency semantics implemented outside this header.

### Test Signals
Compatibility tests should invoke supported `sysmips` commands, verify unsupported commands fail predictably, and check unaligned-access and cache-flush behavior on real or emulated MIPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sysmips.h -->
