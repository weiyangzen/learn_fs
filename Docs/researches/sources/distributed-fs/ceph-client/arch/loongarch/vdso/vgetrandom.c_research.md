<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom.c

### Purpose
`vgetrandom.c` exposes the LoongArch vDSO `getrandom()` entry point.

### Important APIs, Types, And Functions
The function is `__vdso_getrandom(void *buffer, size_t len, unsigned int flags, void *opaque_state, size_t opaque_len)`.

### Control Flow
It forwards all arguments directly to generic `__cvdso_getrandom()`.

### State, Persistence, And Dependencies
State is in caller buffer and opaque vDSO random state managed by generic code. Dependencies include `linux/types.h`, generic vDSO getrandom implementation included by the build, and optional ChaCha helper assembly.

### Integration Points
Exported by `vdso.lds.S` and built by the vDSO Makefile. Userspace libc can call this instead of the syscall when supported.

### Risks
The wrapper is thin; risk is mainly ABI signature drift with generic `__cvdso_getrandom()` or missing arch helper linkage.

### Test Signals
Run vDSO getrandom selftests, compare syscall fallback behavior for flags/lengths, and verify symbol export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom.c -->
